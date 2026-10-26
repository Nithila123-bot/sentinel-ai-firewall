
const $ = (id) => document.getElementById(id);

let auditRecords = [];

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function normalizeDecision(value) {
    const decision = String(value ?? "UNKNOWN")
        .toUpperCase().replaceAll(" ", "_");

    if (decision === "ALLOW" || decision === "DENY") return decision;
    if (decision === "REQUIRE_APPROVAL") return decision;
    return "UNKNOWN";
}

function decisionBadge(value) {
    const decision = normalizeDecision(value);
    const styles = {
        ALLOW: ["allow", "Allowed"],
        DENY: ["deny", "Blocked"],
        REQUIRE_APPROVAL: ["review", "Needs review"],
        UNKNOWN: ["unknown", "Unknown"]
    };

    const [style, label] = styles[decision];
    return `<span class="pill ${style}">${label}</span>`;
}

function showToast(message) {
    const toast = $("toast");
    toast.textContent = message;
    toast.classList.add("show");

    clearTimeout(showToast.timer);
    showToast.timer = setTimeout(() => {
        toast.classList.remove("show");
    }, 2800);
}

function showPage(pageName) {
    document.querySelectorAll(".page").forEach(page => {
        page.classList.toggle("active", page.id === pageName);
    });

    document.querySelectorAll(".nav-item").forEach(button => {
        button.classList.toggle(
            "active",
            button.dataset.page === pageName
        );
    });

    const names = {
        overview: "Overview",
        simulator: "Policy simulator",
        audit: "Audit history"
    };

    $("breadcrumb").textContent = names[pageName] || "Overview";
}

document.querySelectorAll("[data-page]").forEach(button => {
    button.addEventListener("click", () => {
        showPage(button.dataset.page);
    });
});

document.querySelectorAll("[data-go]").forEach(button => {
    button.addEventListener("click", () => {
        showPage(button.dataset.go);
    });
});

function getField(record, keys) {
    for (const key of keys) {
        if (record[key] !== undefined && record[key] !== null) {
            return record[key];
        }
    }
    return "";
}

function formatTime(value) {
    if (!value) return "—";

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);

    return date.toLocaleString();
}

function recordRow(record) {
    const timestamp = getField(record, ["timestamp", "time", "created_at"]);
    const tool = getField(record, ["tool"]);
    const operation = getField(record, ["operation", "action"]);
    const source = getField(record, ["source"]);
    const decision = getField(record, ["decision", "result", "status"]);

    return `
        <tr>
            <td>${escapeHTML(formatTime(timestamp))}</td>
            <td>${escapeHTML(tool || "—")}</td>
            <td>${escapeHTML(operation || "—")}</td>
            <td>${escapeHTML(source || "—")}</td>
            <td>${decisionBadge(decision)}</td>
        </tr>`;
}

function renderRows(targetId, records) {
    const target = $(targetId);

    if (!records.length) {
        target.innerHTML =
            '<tr><td colspan="5" class="empty">No audit records found.</td></tr>';
        return;
    }

    target.innerHTML = records.map(recordRow).join("");
}

function renderChart(data) {
    const total = Number(data.total) || 0;
    const allowed = Number(data.allowed) || 0;
    const denied = Number(data.denied) || 0;
    const review = Number(data.review) || 0;

    $("chartTotal").textContent = total;
    $("legendAllowed").textContent = allowed;
    $("legendDenied").textContent = denied;
    $("legendReview").textContent = review;

    if (!total) {
        $("donut").style.background =
            "conic-gradient(#e8edf4 0deg 360deg)";
        return;
    }

    const allowedEnd = allowed / total * 360;
    const deniedEnd = (allowed + denied) / total * 360;

    $("donut").style.background = `conic-gradient(
        #18865b 0deg ${allowedEnd}deg,
        #d93025 ${allowedEnd}deg ${deniedEnd}deg,
        #e8a126 ${deniedEnd}deg 360deg
    )`;
}

async function loadOverview() {
    try {
        const response = await fetch("/api/overview");
        if (!response.ok) throw new Error("Could not load dashboard data.");

        const data = await response.json();

        $("total").textContent = data.total ?? 0;
        $("allowed").textContent = data.allowed ?? 0;
        $("denied").textContent = data.denied ?? 0;
        $("review").textContent = data.review ?? 0;

        auditRecords = Array.isArray(data.records) ? data.records : [];

        renderChart(data);
        renderRows("recentRows", auditRecords.slice(0, 6));
        renderAudit();

    } catch (error) {
        showToast(error.message || "Unable to load dashboard.");
    }
}

function renderAudit() {
    const query = $("searchInput").value.trim().toLowerCase();
    const filter = $("filterDecision").value;

    const filtered = auditRecords.filter(record => {
        const decision = normalizeDecision(
            getField(record, ["decision", "result", "status"])
        );

        const searchable = [
            getField(record, ["timestamp", "time"]),
            record.tool,
            record.operation,
            record.source,
            decision
        ].join(" ").toLowerCase();

        const matchesSearch = searchable.includes(query);
        const matchesFilter = filter === "all" || decision === filter;

        return matchesSearch && matchesFilter;
    });

    renderRows("auditRows", filtered);
    $("auditCount").textContent =
        `${filtered.length} record${filtered.length === 1 ? "" : "s"}`;
}

$("searchInput").addEventListener("input", renderAudit);
$("filterDecision").addEventListener("change", renderAudit);

$("refreshBtn").addEventListener("click", loadOverview);

$("simulatorForm").addEventListener("submit", async event => {
    event.preventDefault();

    const button = event.currentTarget.querySelector("button[type=submit]");
    button.disabled = true;
    button.textContent = "Evaluating…";

    const payload = {
        tool: $("tool").value,
        operation: $("operation").value,
        source: $("source").value
    };

    try {
        const response = await fetch("/api/check", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Policy check failed.");
        }

        const decision = normalizeDecision(data.decision);
        const results = {
            ALLOW: {
                title: "Request allowed",
                symbol: "✓",
                background: "#e4f5ed",
                color: "#18865b"
            },
            DENY: {
                title: "Request blocked",
                symbol: "⊘",
                background: "#fce8e6",
                color: "#d93025"
            },
            REQUIRE_APPROVAL: {
                title: "Approval required",
                symbol: "!",
                background: "#fff2d7",
                color: "#a96d0c"
            }
        };

        const result = results[decision] || {
            title: "Evaluation completed",
            symbol: "◇",
            background: "#eaf2ff",
            color: "#1a73e8"
        };

        $("resultSymbol").textContent = result.symbol;
        $("resultSymbol").style.background = result.background;
        $("resultSymbol").style.color = result.color;
        $("resultTitle").textContent = result.title;
        $("resultMessage").textContent = data.message;

        $("resultDetails").innerHTML = `
            <div><span>Tool</span><b>${escapeHTML(data.tool)}</b></div>
            <div><span>Operation</span><b>${escapeHTML(data.operation)}</b></div>
            <div><span>Source</span><b>${escapeHTML(data.source)}</b></div>
            <div><span>Decision</span><b>${decisionBadge(decision)}</b></div>
        `;

        showToast("Policy evaluation completed.");
        await loadOverview();

    } catch (error) {
        showToast(error.message || "Could not evaluate this request.");
    } finally {
        button.disabled = false;
        button.textContent = "Run policy check →";
    }
});

loadOverview();

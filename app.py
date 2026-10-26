
import csv
import html
import io
import json

import streamlit as st
from sentinel.policy_engine import check_action
from sentinel.audit_log import log_decision, LOG_FILE


# ---------- Page configuration ----------
st.set_page_config(
    page_title="Sentinel Security",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------- Professional styling ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --blue: #1a73e8;
        --navy: #17365d;
        --green: #188038;
        --red: #d93025;
        --amber: #b06000;
        --text: #202124;
        --muted: #5f6368;
        --border: #dadce0;
        --surface: #ffffff;
        --page: #f8fafd;
    }

    .stApp {
        background: var(--page);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e8eaed;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #3c4043;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    h1, h2, h3 {
        color: var(--text) !important;
        letter-spacing: -0.5px;
    }

    .brand {
        font-size: 23px;
        font-weight: 800;
        letter-spacing: -0.8px;
        margin-bottom: 3px;
    }

    .brand span { color: var(--blue); }

    .subtitle {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.6;
    }

    .section-label {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--muted);
        margin: 24px 0 12px 0;
    }

    .panel {
        background: var(--surface);
        border: 1px solid #e8eaed;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 16px;
    }

    .metric-label {
        font-size: 13px;
        color: var(--muted);
        font-weight: 500;
    }

    .metric-number {
        font-size: 30px;
        font-weight: 700;
        color: var(--text);
        margin-top: 8px;
        letter-spacing: -1px;
    }

    .metric-note {
        color: var(--muted);
        font-size: 12px;
        margin-top: 6px;
    }

    .metric-icon {
        font-size: 20px;
        margin-bottom: 12px;
    }

    .status-pill {
        display: inline-block;
        padding: 7px 12px;
        background: #e6f4ea;
        color: #137333;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 600;
    }

    .decision-box {
        border: 1px solid #e8eaed;
        background: #ffffff;
        padding: 18px;
        border-radius: 14px;
        margin: 12px 0;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 9px;
        font-weight: 600;
        min-height: 42px;
        border: 1px solid #dadce0;
    }

    .stButton > button[kind="primary"] {
        background: #1a73e8;
        border-color: #1a73e8;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        border-radius: 9px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #e8eaed;
        border-radius: 12px;
        overflow: hidden;
    }

    hr {
        border-color: #e8eaed;
    }

    .footer {
        border-top: 1px solid #e8eaed;
        padding-top: 18px;
        margin-top: 35px;
        font-size: 12px;
        color: #80868b;
    }

    @media (max-width: 700px) {
        .block-container {
            padding: 1rem;
        }
        .metric-number {
            font-size: 24px;
        }
    }
</style>
""", unsafe_allow_html=True)


# ---------- Audit log ----------
def load_records():
    records = []

    if LOG_FILE.exists():
        with LOG_FILE.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    record = json.loads(line)
                    if isinstance(record, dict):
                        records.append(record)
                except json.JSONDecodeError:
                    continue

    return records


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(
        '<div class="brand">SENTINEL<span>.</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("AI SECURITY PLATFORM")
    st.divider()

    page = st.radio(
        "WORKSPACE",
        ["Overview", "Test Security", "Audit History"],
        label_visibility="visible",
    )

    st.divider()
    st.markdown("**Protection status**")
    st.markdown(
        '<span class="status-pill">● Policy engine available</span>',
        unsafe_allow_html=True,
    )
    st.caption("Prototype mode · Actions are simulated")

    if st.button("↻ Refresh data", use_container_width=True):
        st.rerun()


# ---------- Load statistics ----------
records = load_records()

allowed = sum(r.get("decision") == "ALLOW" for r in records)
denied = sum(r.get("decision") == "DENY" for r in records)
approval = sum(
    r.get("decision") == "REQUIRE_APPROVAL" for r in records
)
total = len(records)


# ---------- Header ----------
header_left, header_right = st.columns([4, 1])

with header_left:
    st.markdown(
        '<div class="brand">Security Command Center</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtitle">Monitor AI-agent requests, review policy '
        'decisions, and inspect security events.</div>',
        unsafe_allow_html=True,
    )

with header_right:
    st.markdown(
        '<div style="text-align:right;padding-top:8px">'
        '<span class="status-pill">● DEMO MODE</span></div>',
        unsafe_allow_html=True,
    )


# ---------- Reusable metric card ----------
def metric_card(icon, label, value, note):
    st.markdown(
        f"""
        <div class="panel">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{html.escape(label)}</div>
            <div class="metric-number">{value:,}</div>
            <div class="metric-note">{html.escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- Overview ----------
if page == "Overview":
    st.markdown(
        '<div class="section-label">Security overview</div>',
        unsafe_allow_html=True,
    )

    cards = st.columns(4, gap="medium")

    metrics = [
        ("📊", "Total requests", total, "Recorded events"),
        ("🟢", "Allowed", allowed, "Permitted by policy"),
        ("🔴", "Denied", denied, "Rejected by policy"),
        ("🟠", "Needs approval", approval, "Approval decision"),
    ]

    for column, metric in zip(cards, metrics):
        with column:
            metric_card(*metric)

    left, right = st.columns([1.4, 1], gap="large")

    with left:
        st.markdown(
            '<div class="section-label">Decision analytics</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.subheader("Request distribution")
            st.caption("Breakdown of recorded policy decisions")

            if total:
                st.bar_chart(
                    {
                        "Requests": {
                            "Allowed": allowed,
                            "Denied": denied,
                            "Needs approval": approval,
                        }
                    },
                    color="#1a73e8",
                )
            else:
                st.info("No events yet. Test a request to populate analytics.")

    with right:
        st.markdown(
            '<div class="section-label">Policy summary</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.subheader("Decision breakdown")

            for label, count, color in [
                ("Allowed", allowed, "#188038"),
                ("Denied", denied, "#d93025"),
                ("Needs approval", approval, "#b06000"),
            ]:
                percentage = count / total * 100 if total else 0

                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;'
                    f'margin-top:20px;margin-bottom:7px;font-size:14px">'
                    f'<span>{label}</span><b>{count} · {percentage:.1f}%</b>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                st.progress(percentage / 100)

            st.divider()
            st.caption(
                "Percentages reflect recorded decisions, not all possible attacks."
            )

    st.markdown(
        '<div class="section-label">Recent security events</div>',
        unsafe_allow_html=True,
    )

    if records:
        st.dataframe(
            list(reversed(records[-10:])),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Your audit history will appear here after the first test.")


# ---------- Test Security ----------
elif page == "Test Security":
    st.markdown(
        '<div class="section-label">Policy evaluation</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Evaluate an AI-agent request")
    st.write(
        "Choose a tool, operation, and source to check the configured security policy."
    )

    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            tool = st.selectbox(
                "Tool",
                ["calculator", "file", "email", "unknown"],
            )

        with col2:
            operation = st.selectbox(
                "Operation",
                ["calculate", "read", "send", "delete", "execute"],
            )

        with col3:
            source = st.selectbox(
                "Request source",
                ["trusted", "untrusted"],
            )

        if st.button("Evaluate security policy", type="primary"):
            decision = check_action(tool, operation, source)
            log_decision(tool, operation, source, decision)

            st.session_state["last_decision"] = {
                "tool": tool,
                "operation": operation,
                "source": source,
                "decision": decision,
            }

    result = st.session_state.get("last_decision")

    if result:
        st.markdown(
            '<div class="section-label">Latest evaluation</div>',
            unsafe_allow_html=True,
        )

        if result["decision"] == "ALLOW":
            st.success("ALLOW — The configured policy permits this request.")
        elif result["decision"] == "DENY":
            st.error("DENY — The configured policy rejects this request.")
        else:
            st.warning(
                "REQUIRE_APPROVAL — The policy requires approval. "
                "An actual approval workflow is not implemented."
            )

        st.json(result)
        st.caption(
            "This is a policy evaluation only. The selected action was not executed."
        )


# ---------- Audit History ----------
elif page == "Audit History":
    st.markdown(
        '<div class="section-label">Event investigation</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Persistent audit history")
    st.caption("Search and filter recorded policy decisions.")

    filter_choice = st.selectbox(
        "Decision",
        ["ALL", "ALLOW", "DENY", "REQUIRE_APPROVAL"],
    )

    query = st.text_input(
        "Search events",
        placeholder="Search by tool, operation, or source",
    )

    filtered = []

    for record in reversed(records):
        decision = record.get("decision", "")

        searchable = " ".join(
            str(record.get(key, ""))
            for key in ["tool", "operation", "source", "decision"]
        )

        if (
            (filter_choice == "ALL" or decision == filter_choice)
            and query.lower() in searchable.lower()
        ):
            filtered.append(record)

    st.caption(f"{len(filtered)} matching events · {total} total events")

    if filtered:
        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
        )

        output = io.StringIO()
        fieldnames = list(dict.fromkeys(
            key for record in filtered for key in record.keys()
        ))

        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(filtered)

        st.download_button(
            "Download filtered events (CSV)",
            data=output.getvalue(),
            file_name="sentinel_audit_export.csv",
            mime="text/csv",
        )
    else:
        st.info("No matching events found.")

    if LOG_FILE.exists():
        st.download_button(
            "Download complete audit log (JSONL)",
            data=LOG_FILE.read_bytes(),
            file_name="sentinel_audit.jsonl",
            mime="application/x-ndjson",
        )


# ---------- Footer ----------
st.markdown(
    '<div class="footer">SENTINEL SECURITY · Educational prototype · '
    'Policy evaluation only; real-world actions are not executed.</div>',
    unsafe_allow_html=True,
)

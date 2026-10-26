
import csv
import io
import json

import streamlit as st
from sentinel.policy_engine import check_action
from sentinel.audit_log import log_decision, LOG_FILE


st.set_page_config(
    page_title="Sentinel AI Firewall",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ Sentinel AI Firewall")
st.caption("AI-Agent Security Monitoring and Policy Dashboard")

st.info(
    "Demo mode: actions are evaluated against security policies. "
    "No real-world actions are executed."
)


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


# Sidebar
st.sidebar.title("🛡️ Sentinel Controls")
st.sidebar.caption("Security monitoring")

if st.sidebar.button("🔄 Refresh dashboard"):
    st.rerun()


# Action testing
st.header("Test a Security Request")

col1, col2, col3 = st.columns(3)

with col1:
    tool = st.selectbox(
        "Select tool",
        ["calculator", "file", "email", "unknown"],
    )

with col2:
    operation = st.selectbox(
        "Select operation",
        ["calculate", "read", "send", "delete", "execute"],
    )

with col3:
    source = st.selectbox(
        "Request source",
        ["trusted", "untrusted"],
    )

if st.button("🔍 Check Security", type="primary"):
    decision = check_action(tool, operation, source)
    log_decision(tool, operation, source, decision)

    if decision == "ALLOW":
        st.success(f"✅ Decision: {decision}")
    elif decision == "REQUIRE_APPROVAL":
        st.warning(f"⚠️ Decision: {decision}")
    else:
        st.error(f"🚫 Decision: {decision}")

    st.caption(
        "This demo records the decision; it does not execute the action."
    )

st.divider()

# Load audit records
records = load_records()

allowed = sum(
    r.get("decision") == "ALLOW" for r in records
)
denied = sum(
    r.get("decision") == "DENY" for r in records
)
approval = sum(
    r.get("decision") == "REQUIRE_APPROVAL" for r in records
)
total = len(records)

# Analytics
st.header("📊 Security Analytics")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Total Requests", total)
m2.metric("Allowed", allowed)
m3.metric("Denied", denied)
m4.metric("Needs Approval", approval)

if total:
    st.subheader("Decision Distribution")

    st.bar_chart(
        {
            "Requests": {
                "Allowed": allowed,
                "Denied": denied,
                "Needs Approval": approval,
            }
        }
    )

    st.caption(
        f"Allowed: {allowed / total * 100:.1f}% · "
        f"Denied: {denied / total * 100:.1f}% · "
        f"Needs approval: {approval / total * 100:.1f}%"
    )
else:
    st.info("No audit records yet. Test a request to begin monitoring.")

st.divider()

# Audit history
st.header("📋 Audit History")

decision_filter = st.selectbox(
    "Filter by decision",
    ["ALL", "ALLOW", "DENY", "REQUIRE_APPROVAL"],
)

search_text = st.text_input(
    "Search tool, operation, or source",
    placeholder="Example: email or untrusted",
)

filtered_records = []

for record in reversed(records):
    decision = record.get("decision", "")

    searchable_text = " ".join(
        str(record.get(key, ""))
        for key in ["tool", "operation", "source"]
    )

    matches_decision = (
        decision_filter == "ALL"
        or decision == decision_filter
    )
    matches_search = search_text.lower() in searchable_text.lower()

    if matches_decision and matches_search:
        filtered_records.append(record)

st.caption(f"Showing {len(filtered_records)} of {total} records")

if filtered_records:
    st.dataframe(
        filtered_records,
        use_container_width=True,
        hide_index=True,
    )

    # Download filtered records as CSV
    output = io.StringIO()
    fieldnames = list(
        dict.fromkeys(
            key
            for record in filtered_records
            for key in record.keys()
        )
    )

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore",
    )
    writer.writeheader()
    writer.writerows(filtered_records)

    st.download_button(
        "⬇️ Download filtered audit history (CSV)",
        data=output.getvalue(),
        file_name="sentinel_audit_export.csv",
        mime="text/csv",
    )
else:
    st.write("No records match the selected filter.")

# Download original JSONL audit log
if LOG_FILE.exists():
    st.download_button(
        "⬇️ Download full audit log (JSONL)",
        data=LOG_FILE.read_bytes(),
        file_name="sentinel_audit.jsonl",
        mime="application/x-ndjson",
    )

st.divider()

st.caption(
    "Sentinel AI Firewall | Educational security prototype | "
    "Actions are simulated, not executed."
)

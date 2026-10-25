
import json
import streamlit as st
from sentinel.policy_engine import check_action
from sentinel.audit_log import log_decision, LOG_FILE

st.set_page_config(
    page_title="Sentinel AI Firewall",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ Sentinel AI-Agent Security Guard")
st.caption("Policy-based security checks for simulated AI-agent actions")
st.info("Demo mode: actions are evaluated, not executed.")

st.subheader("Test an AI-agent action")

col1, col2, col3 = st.columns(3)

with col1:
    tool = st.selectbox(
        "Tool", ["calculator", "file", "email", "unknown"]
    )

with col2:
    operation = st.selectbox(
        "Operation", ["calculate", "read", "send", "delete", "execute"]
    )

with col3:
    source = st.selectbox(
        "Request source", ["trusted", "untrusted"]
    )

if st.button("Check security", type="primary"):
    decision = check_action(tool, operation, source)
    log_decision(tool, operation, source, decision)

    if decision == "ALLOW":
        st.success(f"Decision: {decision}")
    elif decision == "REQUIRE_APPROVAL":
        st.warning(f"Decision: {decision}")
    else:
        st.error(f"Decision: {decision}")

st.divider()
st.subheader("Security overview")

records = []
if LOG_FILE.exists():
    with LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

allowed = sum(r["decision"] == "ALLOW" for r in records)
denied = sum(r["decision"] == "DENY" for r in records)
approval = sum(
    r["decision"] == "REQUIRE_APPROVAL" for r in records
)

m1, m2, m3 = st.columns(3)
m1.metric("Allowed", allowed)
m2.metric("Denied", denied)
m3.metric("Needs approval", approval)

st.subheader("Persistent audit history")

if records:
    st.dataframe(
        list(reversed(records)),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.write("No security decisions recorded yet.")

st.caption("Sentinel prototype • Simulated actions only")

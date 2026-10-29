🚀 **Live Demo:** [Open Sentinel AI Firewall](https://sentinel-ai-firewall-haj8guagbre2tiiasgxqj.streamlit.app)

# Sentinel — AI Agent Security Firewall

## Overview
Sentinel is a Python-based prototype that checks proposed AI-agent actions against security policies before execution.

It returns one of three decisions:
- **ALLOW:** The action is permitted by the configured rules.
- **DENY:** The action is rejected.
- **REQUIRE_APPROVAL:** Human approval is required before the action can proceed.

## Problem
AI agents can encounter malicious instructions or untrusted content that may influence their actions. Sentinel demonstrates how policy checks can help restrict unauthorized tool use.

## Features
- Rule-based action authorization
- Trusted and untrusted source labels
- Denial of unknown actions
- JSON Lines audit logging
- Interactive Streamlit dashboard
- Automated policy tests
- Simulated security benchmark

## Technology
- Python
- Streamlit
- JSON
- Git and GitHub

## Run the Project

Install Streamlit:

```bash
py -m pip install streamlit
```

Launch the dashboard:

```bash
py -m streamlit run app.py
```

Run the tests in another terminal:

```bash
py test_policy.py
```

Run the benchmark:

```bash
py benchmark.py
```

## Limitations
Sentinel is an educational prototype, not a production-ready security system. Request sources are labelled manually, human approval is not yet implemented, and actions are simulated rather than executed. Passing the current tests does not prove protection against all attacks.

## Future Work
- Implement human approval
- Expand security scenarios
- Compare policy approaches
- Improve provenance validation
- Add more automated tests

## Goal
Evaluate whether policy-based authorization can reduce unauthorized AI-agent actions while keeping legitimate actions usable.

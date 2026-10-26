
import csv
import io
import json

from flask import Flask, jsonify, render_template, request, Response

from sentinel.policy_engine import check_action
from sentinel.audit_log import log_decision, LOG_FILE

app = Flask(__name__)


def read_audit_logs():
    records = []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    record = json.loads(line.strip())
                    if isinstance(record, dict):
                        records.append(record)
                except json.JSONDecodeError:
                    continue
    except (FileNotFoundError, TypeError, OSError):
        pass

    return records


def get_decision(record):
    for key in ("decision", "result", "status"):
        value = record.get(key)
        if value:
            return str(value).upper()
    return "UNKNOWN"


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/api/overview")
def overview():
    records = read_audit_logs()

    allowed = sum(get_decision(r) == "ALLOW" for r in records)
    denied = sum(get_decision(r) == "DENY" for r in records)
    review = sum(
        get_decision(r) in ("REQUIRE_APPROVAL", "REQUIRE APPROVAL")
        for r in records
    )

    return jsonify({
        "total": len(records),
        "allowed": allowed,
        "denied": denied,
        "review": review,
        "records": list(reversed(records[-100:]))
    })


@app.post("/api/check")
def simulate():
    data = request.get_json(silent=True) or {}

    tool = data.get("tool", "")
    operation = data.get("operation", "")
    source = data.get("source", "")

    allowed_values = {
        "tool": {"calculator", "file", "email", "unknown"},
        "operation": {"calculate", "read", "send", "delete", "execute"},
        "source": {"trusted", "untrusted"}
    }

    if (
        tool not in allowed_values["tool"]
        or operation not in allowed_values["operation"]
        or source not in allowed_values["source"]
    ):
        return jsonify({"error": "Please select valid simulation options."}), 400

    try:
        decision = check_action(tool, operation, source)
        decision_text = (
            decision.value
            if hasattr(decision, "value")
            else str(decision)
        ).upper()

        log_decision(tool, operation, source, decision)

        return jsonify({
            "decision": decision_text,
            "tool": tool,
            "operation": operation,
            "source": source,
            "message": {
                "ALLOW": "The policy permits this simulated request.",
                "DENY": "The policy blocks this simulated request.",
                "REQUIRE_APPROVAL": "Human approval is required."
            }.get(decision_text, "Policy evaluation completed.")
        })
    except Exception:
        app.logger.exception("Policy simulation failed")
        return jsonify({
            "error": "Policy evaluation failed. Check your policy engine."
        }), 500


@app.get("/api/export.csv")
def export_csv():
    records = read_audit_logs()
    output = io.StringIO()
    fields = ["timestamp", "tool", "operation", "source", "decision"]

    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()

    for record in records:
        writer.writerow({
            "timestamp": record.get("timestamp", ""),
            "tool": record.get("tool", ""),
            "operation": record.get("operation", ""),
            "source": record.get("source", ""),
            "decision": get_decision(record)
        })

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=sentinel-audit.csv"
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)

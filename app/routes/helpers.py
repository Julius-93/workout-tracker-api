"""Reusable request parsing to keep endpoints concise."""
from flask import abort, request


def read_json_object():
    """Require a JSON object, not malformed JSON, a list, or plain text."""
    if not request.is_json:
        abort(415, description="Content-Type must be application/json.")
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        abort(400, description="Request body must be a valid JSON object.")
    return payload

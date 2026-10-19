"""Consistent machine-readable errors, including schema and database violations."""
from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from .extensions import db


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def schema_validation_error(error):
        db.session.rollback()
        return jsonify({"error": "Validation failed.", "details": error.messages}), 400

    @app.errorhandler(ValueError)
    def model_validation_error(error):
        db.session.rollback()
        return jsonify({"error": str(error)}), 400

    @app.errorhandler(IntegrityError)
    def integrity_error(_error):
        # Never expose raw database error details in the HTTP response.
        db.session.rollback()
        return jsonify({"error": "Database constraint violated."}), 409

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify({"error": error.description}), error.code

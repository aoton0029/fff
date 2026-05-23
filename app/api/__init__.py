from flask import Blueprint

api_bp = Blueprint("api", __name__)


@api_bp.route("/ping")
def ping() -> dict:
    return {"status": "ok"}


from . import files  # noqa: E402 — registers routes on api_bp

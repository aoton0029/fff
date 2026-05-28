import logging

from flask import jsonify, render_template, request

logger = logging.getLogger(__name__)


def _wants_json() -> bool:
    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    return best == "application/json"


def register_error_handlers(app) -> None:
    @app.errorhandler(400)
    def bad_request(e):
        if _wants_json():
            return jsonify({"status": "error", "data": None, "message": str(e)}), 400
        return render_template("errors/400.html"), 400

    @app.errorhandler(403)
    def forbidden(e):
        if _wants_json():
            return jsonify({"status": "error", "data": None, "message": "権限がありません"}), 403
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        if _wants_json():
            return jsonify({"status": "error", "data": None, "message": "リソースが見つかりません"}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error("Internal server error", exc_info=True)
        if _wants_json():
            return jsonify({"status": "error", "data": None, "message": "サーバーエラーが発生しました"}), 500
        return render_template("errors/500.html"), 500

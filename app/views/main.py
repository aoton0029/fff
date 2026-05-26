# Deprecated: use app.home.views
from ..home.views import main_bp  # noqa: F401

__all__ = ["main_bp"]


@main_bp.route("/")
@login_required
def index():
    return render_template("main/index.html")

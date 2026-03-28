from flask import Blueprint, render_template, session
from app.routes_auth import login_required
from app.models.app_registry import App

apps_bp = Blueprint('apps', __name__)


@apps_bp.route('/apps')
@login_required
def selector():
    """App selector landing page."""
    allowed_app_ids = session.get('allowed_apps', [])
    apps = App.query.filter(App.id.in_(allowed_app_ids)).all() if allowed_app_ids else []
    return render_template('apps/selector.html', apps=apps, username=session.get('display_name'))

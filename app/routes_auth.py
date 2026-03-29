import re
from functools import wraps
from urllib.parse import unquote
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db, limiter
from app.models.user import User
from app.models.shared_key import SharedKey
from app.models.app_registry import App

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            session['redirect_after_login'] = request.full_path
            redirect_param = request.args.get('redirect', '')
            return redirect(url_for('auth.login', redirect=redirect_param))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Access denied. Admin role required.', 'danger')
            return redirect(url_for('apps.selector'))
        return f(*args, **kwargs)
    return decorated


def app_access_required(app_id):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            allowed_apps = session.get('allowed_apps', [])
            if app_id not in allowed_apps:
                flash(f'Access denied to {app_id}', 'danger')
                return redirect(url_for('apps.selector'))
            return f(*args, **kwargs)
        return decorated
    return decorator


def validate_password(pw):
    """Validate password/key complexity: 1 uppercase, 1 lowercase, 1 digit, 1 special char"""
    return (re.search(r'[A-Z]', pw) and
            re.search(r'[a-z]', pw) and
            re.search(r'\d', pw) and
            re.search(r'[!@#$%^&*]', pw))


def validate_key(key):
    """Validate shared key: 5–8 characters and meets complexity rules"""
    return 5 <= len(key) <= 8 and validate_password(key)


def get_safe_redirect(redirect_param, allowed_apps):
    """Validate and return safe redirect target."""
    if not redirect_param:
        return None

    # Open redirect protection: must start with / and not start with //
    if not redirect_param.startswith('/') or redirect_param.startswith('//'):
        return None

    # Extract app ID from path (e.g., "/otl/data" -> "otl")
    parts = redirect_param.strip('/').split('/')
    if not parts or not parts[0]:
        return None

    target_app = parts[0]

    # Check if user has access to target app
    if target_app not in allowed_apps:
        return None

    return redirect_param


@auth_bp.route('/')
def index():
    """Root route redirects to apps or login."""
    if 'user_id' in session:
        return redirect(url_for('apps.selector'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per 15 minutes")
def login():
    redirect_param = request.args.get('redirect', '')
    app_name = None

    # Look up app name for contextual message
    if redirect_param:
        parts = redirect_param.strip('/').split('/')
        if parts and parts[0]:
            app = App.query.get(parts[0])
            if app:
                app_name = app.name

    if request.method == 'POST':
        login_method = request.form.get('login_method', 'password')

        if login_method == 'password':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            user = User.query.filter_by(username=username, active=True).first()
            if user and user.check_password(password):
                allowed_apps = user.get_allowed_apps()

                if not allowed_apps:
                    flash('No applications assigned to your account.', 'danger')
                    return render_template('login.html', redirect=redirect_param, app_name=app_name)

                # Set session
                session['user_id'] = user.id
                session['username'] = user.username
                session['display_name'] = user.display_name or user.username
                session['role'] = user.role
                session['allowed_apps'] = allowed_apps

                # Handle redirect
                return handle_post_login_redirect(allowed_apps, redirect_param)

            flash('Invalid username or password', 'danger')

        elif login_method == 'key':
            raw_key = request.form.get('key', '').strip()

            key_record = None
            for key in SharedKey.query.filter_by(active=True).all():
                if key.is_valid() and key.check_key(raw_key):
                    key_record = key
                    break

            if key_record:
                allowed_apps = key_record.get_allowed_apps()

                if not allowed_apps:
                    flash('No applications assigned to this key.', 'danger')
                    return render_template('login.html', redirect=redirect_param, app_name=app_name)

                # Set session for shared key
                session['user_id'] = None
                session['username'] = f"SharedKey-{key_record.id}"
                session['display_name'] = f"Shared Key #{key_record.id}"
                session['role'] = 'user'
                session['allowed_apps'] = allowed_apps

                # Handle redirect
                return handle_post_login_redirect(allowed_apps, redirect_param)

            flash('Invalid shared key', 'danger')

    return render_template('login.html', redirect=redirect_param, app_name=app_name)


def handle_post_login_redirect(allowed_apps, redirect_param):
    """Handle post-login redirect logic based on allowed apps.

    Default: redirect to /apps (app selector)
    Exception: if explicit redirect URL is provided and validated, use that instead
    """
    # Check if no apps assigned
    if len(allowed_apps) == 0:
        flash('No applications assigned to your account.', 'danger')
        session.clear()
        return redirect(url_for('auth.login'))

    # Try to use explicit redirect if provided
    session_redirect = session.pop('redirect_after_login', None)
    target = None

    if session_redirect:
        target = get_safe_redirect(session_redirect, allowed_apps)
    elif redirect_param:
        target = get_safe_redirect(redirect_param, allowed_apps)

    # If explicit redirect validated, use it
    if target:
        return redirect(target)

    # Default: always redirect to /apps (app selector)
    return redirect(url_for('apps.selector'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

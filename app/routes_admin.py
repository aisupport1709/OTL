import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from app import db
from app.routes_auth import login_required, admin_required
from app.models.user import User
from app.models.shared_key import SharedKey
from app.models.app_registry import App

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def validate_password(pw):
    """Validate password/key complexity: 1 uppercase, 1 lowercase, 1 digit, 1 special char"""
    return (re.search(r'[A-Z]', pw) and
            re.search(r'[a-z]', pw) and
            re.search(r'\d', pw) and
            re.search(r'[!@#$%^&*]', pw))


def validate_key(key):
    """Validate shared key: exactly 5 characters and meets complexity rules"""
    return len(key) == 5 and validate_password(key)


# ─── Dashboard ────────────────────────────────────────────────────────

@admin_bp.route('/', methods=['GET'])
@login_required
@admin_required
def dashboard():
    """Admin dashboard with stats."""
    total_users = User.query.count()
    active_users = User.query.filter_by(active=True).count()
    total_keys = SharedKey.query.count()
    active_keys = SharedKey.query.filter_by(active=True).count()
    registered_apps = App.query.count()

    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         active_users=active_users,
                         total_keys=total_keys,
                         active_keys=active_keys,
                         registered_apps=registered_apps)


# ─── Users ────────────────────────────────────────────────────────────

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def list_users():
    """List all users."""
    users = User.query.all()
    all_apps = App.query.all()
    return render_template('admin/users.html',
                           users=users,
                           all_apps=all_apps,
                           users_json=[u.to_dict() for u in users],
                           all_apps_json=[a.to_dict() for a in all_apps])


@admin_bp.route('/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    """Add a new user."""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'user')

    # Validate inputs
    if not username or not password:
        flash('Username and password are required.', 'danger')
        return redirect(url_for('admin.list_users'))

    if not validate_password(password):
        flash('Password must contain uppercase, lowercase, digit, and special character.', 'danger')
        return redirect(url_for('admin.list_users'))

    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'danger')
        return redirect(url_for('admin.list_users'))

    if role not in ['admin', 'user']:
        role = 'user'

    # Get allowed apps from form checkboxes
    allowed_apps = request.form.getlist('allowed_apps')

    # Create user
    user = User(username=username, role=role, active=True)
    user.set_password(password)
    user.set_allowed_apps(allowed_apps)
    db.session.add(user)
    db.session.commit()

    flash(f'User {username} created successfully.', 'success')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details."""
    user = User.query.get_or_404(user_id)

    # Update role
    role = request.form.get('role', user.role)
    if role in ['admin', 'user']:
        user.role = role

    # Update allowed apps
    allowed_apps = request.form.getlist('allowed_apps')
    user.set_allowed_apps(allowed_apps)

    db.session.commit()
    flash(f'User {user.username} updated successfully.', 'success')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    """Toggle user active status."""
    user = User.query.get_or_404(user_id)
    user.active = not user.active
    db.session.commit()

    status = 'activated' if user.active else 'deactivated'
    flash(f'User {user.username} {status}.', 'success')
    return redirect(url_for('admin.list_users'))


# ─── Shared Keys ──────────────────────────────────────────────────────

@admin_bp.route('/keys', methods=['GET'])
@login_required
@admin_required
def list_keys():
    """List all shared keys."""
    keys = SharedKey.query.all()
    all_apps = App.query.all()
    return render_template('admin/keys.html',
                           keys=keys,
                           all_apps=all_apps,
                           all_apps_json=[a.to_dict() for a in all_apps])


@admin_bp.route('/keys/add', methods=['POST'])
@login_required
@admin_required
def add_key():
    """Add a new shared key."""
    key_input = request.form.get('key', '').strip()
    expires_at = request.form.get('expires_at', '')

    # Validate key format
    if not key_input:
        flash('Key is required.', 'danger')
        return redirect(url_for('admin.list_keys'))

    if not validate_key(key_input):
        flash('Key must be exactly 5 characters with uppercase, lowercase, digit, and special character.', 'danger')
        return redirect(url_for('admin.list_keys'))

    # Get allowed apps from form checkboxes
    allowed_apps = request.form.getlist('allowed_apps')

    if not allowed_apps:
        flash('At least one app must be assigned to the key.', 'danger')
        return redirect(url_for('admin.list_keys'))

    # Hash the key and create record
    from werkzeug.security import generate_password_hash
    key_hash = generate_password_hash(key_input, method='pbkdf2:sha256', salt_length=16)

    key_record = SharedKey(key_hash=key_hash, active=True)
    key_record.set_allowed_apps(allowed_apps)

    # Set expiry if provided
    if expires_at:
        try:
            from datetime import datetime
            key_record.expires_at = datetime.fromisoformat(expires_at)
        except (ValueError, TypeError):
            pass

    # Set creator
    key_record.created_by = session.get('user_id')

    db.session.add(key_record)
    db.session.commit()

    flash(f'Shared key created successfully.', 'success')
    return redirect(url_for('admin.list_keys'))


@admin_bp.route('/keys/<int:key_id>/revoke', methods=['POST'])
@login_required
@admin_required
def revoke_key(key_id):
    """Revoke a shared key."""
    key = SharedKey.query.get_or_404(key_id)
    key.active = False
    db.session.commit()

    flash(f'Shared key #{key_id} revoked.', 'success')
    return redirect(url_for('admin.list_keys'))


# ─── Apps ────────────────────────────────────────────────────────────

@admin_bp.route('/apps', methods=['GET'])
@login_required
@admin_required
def list_apps():
    """List all registered apps."""
    apps = App.query.all()
    return render_template('admin/apps.html',
                           apps=apps,
                           apps_json=[a.to_dict() for a in apps])


@admin_bp.route('/apps/add', methods=['POST'])
@login_required
@admin_required
def add_app():
    """Add a new app to the registry."""
    app_id = request.form.get('id', '').strip()
    app_name = request.form.get('name', '').strip()
    app_path = request.form.get('path', '').strip()
    description = request.form.get('description', '').strip()

    # Validate inputs
    if not app_id or not app_name or not app_path:
        flash('ID, name, and path are required.', 'danger')
        return redirect(url_for('admin.list_apps'))

    if App.query.get(app_id):
        flash('App ID already exists.', 'danger')
        return redirect(url_for('admin.list_apps'))

    # Create app
    app = App(id=app_id, name=app_name, path=app_path, description=description or None)
    db.session.add(app)
    db.session.commit()

    flash(f'App {app_id} created successfully.', 'success')
    return redirect(url_for('admin.list_apps'))


@admin_bp.route('/apps/<app_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_app(app_id):
    """Edit app details."""
    app = App.query.get_or_404(app_id)

    app.name = request.form.get('name', app.name).strip()
    app.path = request.form.get('path', app.path).strip()
    app.description = request.form.get('description', '').strip() or None

    db.session.commit()
    flash(f'App {app_id} updated successfully.', 'success')
    return redirect(url_for('admin.list_apps'))

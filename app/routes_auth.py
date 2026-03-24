from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username, is_active=True).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['display_name'] = user.display_name or user.username
            return redirect(url_for('main.dashboard'))

        flash('Invalid username or password', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        display_name = request.form.get('display_name', '').strip()

        if not username or not password:
            flash('Username and password are required', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
        else:
            user = User(username=username, display_name=display_name or username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Account created. Please log in.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

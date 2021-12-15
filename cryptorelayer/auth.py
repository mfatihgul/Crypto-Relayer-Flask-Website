import functools
from logging import error
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from cryptorelayer.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/adminregister', methods=('GET', 'POST'))
def adminregister():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Kullanıcı adı gerekli.'
        elif not password:
            error = 'Şifre gerekli.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.adminlogin"))

        flash(error)

    return render_template('blog.index')

@bp.route('/adminlogin', methods=('GET', 'POST'))
def adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Kullanıcı adı yanlış.'
        elif not check_password_hash(user['password'], password):
            error = 'Şifre yanlış.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('blog'))

        flash(error)

    return render_template('admin-panel/adminlogin.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.adminlogin'))

        return view(**kwargs)

    return wrapped_view
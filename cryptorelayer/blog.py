from os import error
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename, send_from_directory
from cryptorelayer.auth import login_required
from cryptorelayer.db import get_db
bp = Blueprint('blog', __name__)



@bp.route('/blog')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, image, created, author_id, username, category'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall() 
    return render_template('blog/blog.html', posts=posts)

@bp.route('/blog/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        uploaded_file = request.files['blogPhoto']
        selection = request.form['selection']
        filename = secure_filename(uploaded_file.filename)
        if selection == 'Kategori seç':
            error = "Category needed"
            flash("Kategori Gerekli")
            return redirect(url_for('blog.create'))

        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            uploaded_file.save(os.path.join(current_app.config['UPLOAD_PATH'], filename))

        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, image, category, author_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (title, body, filename, selection, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, image, created, author_id, username, category'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,) 
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(current_app.config['UPLOAD_PATH'], filename)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        uploaded_file = request.files['blogPhoto']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            uploaded_file.save(os.path.join(current_app.config['UPLOAD_PATH'], filename))

        error = None


        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            if filename != '':
                db = get_db()
                db.execute(
                    'UPDATE post SET title = ?, body = ?, image = ?'
                    ' WHERE id = ?',
                    (title, body, filename, id)
                )
                db.commit()
            elif filename == '':
                db = get_db()
                db.execute(
                    'UPDATE post SET title = ?, body = ?'
                    ' WHERE id = ?',
                    (title, body, id)
                )
                db.commit()

            return redirect(url_for('blog.index'))
            
    return render_template('blog/update.html', post=post)

#MY CODE
@bp.route('/<int:id>/blogpost', methods=('GET', 'POST'))
def blogpost(id):
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, image, created, author_id, username, category'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC LIMIT 3'
    ).fetchall() 
    post = get_post(id)
    
    return render_template('blog/blogpost.html', post=post, posts=posts)



@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/search', methods=('GET', 'POST'))
def search():
    db = get_db()
    word = request.args.get('search')
    posts = db.execute(
        "SELECT p.id, title, body, image, created, author_id, username, category"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE body LIKE '%' || ? || '%' OR title LIKE '%' || ? || '%' LIMIT 10 ",
        [word, word]
    ).fetchall()
    return render_template('blog/search.html', posts = posts)
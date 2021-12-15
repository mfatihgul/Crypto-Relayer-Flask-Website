from datetime import timedelta
import os
from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'cryptorelayer.sqlite'),
        MAX_CONTENT_LENGTH = 2048 * 2048,
        UPLOAD_EXTENSIONS = ['.jpg', '.png', 'jpeg'],
        UPLOAD_PATH = "/home/mfg7ix/Belgeler/cryptorelayer.com/cryptorelayer/static/uploads"
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello Crypto Relayer!'


    from flask import render_template
    from cryptorelayer.db import get_db
    @app.route('/')
    def index():
        db = get_db()
        posts = db.execute(
            'SELECT p.id, title, body, image, created, author_id, username, category'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' ORDER BY created DESC LIMIT 3'
        ).fetchall() 
        return render_template('index.html', posts=posts)
    
    @app.route('/about')
    def about():
        return render_template('about.html', title="About Us")

    @app.route('/services')
    def services():
        return render_template('services.html', title="Services")

    # @app.route('/blog')
    # def blog():
    #     return render_template('blog/blog.html', title="Blog")
    # @app.route('/blog_details')
    # def blog_details():
    #     return render_template('blog/blog-details.html')
    @app.route('/faq')
    def faq():
        return render_template('faq.html', title="FAQ")
    @app.route('/contact')
    def contact():
        return render_template('contact.html', title="Contact")
 
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/blog', endpoint='blog')

    ################################################3

    return app
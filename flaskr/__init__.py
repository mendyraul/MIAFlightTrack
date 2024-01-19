import os

from flask import Flask, render_template



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')
    app.config['SECRET_KEY'] = secret_key

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Import and register the authentication blueprint
    from . import auth
    app.register_blueprint(auth.bp)
    

    # Import and register the flights blueprint
    from .flights import bp as flights_bp
    app.register_blueprint(flights_bp, url_prefix='/flights')

    @app.route('/')
    def index():
        return render_template('auth/index.html')
    
    return app

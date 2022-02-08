import os
from flask import Flask


def create_app(test_config=None):
    """This is an app factory, which creates a flask app from the blueprints
    in each script."""
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import record
    app.register_blueprint(record.bp)
    app.add_url_rule('/', endpoint='index')

    from . import instructions
    app.register_blueprint(instructions.bp)
    app.add_url_rule('/', endpoint='instructions')

    from . import audio
    app.register_blueprint(audio.bp)
    app.add_url_rule('/', endpoint='audio')

    from . import survey
    app.register_blueprint(survey.bp)
    app.add_url_rule('/', endpoint='survey')

    from . import demo
    app.register_blueprint(demo.bp)
    app.add_url_rule('/', endpoint='demo')

    return app



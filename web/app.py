import os

from flask import Flask, send_from_directory

from .misc import misc_bp


__all__ = ['create_app']


def create_app():
    app = Flask(__name__)
    configure_app(app)
    register_blueprints(app)

    if app.config['DEBUG']:
        @app.route('/favicon.ico')
        def favicon():
            return send_from_directory(os.path.join(app.root_path, 'static'),
                'favicon.ico', mimetype='image/vnd.microsoft.icon')

    return app


def configure_app(app):
    app.config.from_object('web.config')
    if os.environ.get('MQTTWS_CONFIG', ''):
        app.config.from_envvar('MQTTWS_CONFIG')


def register_blueprints(app):
    app.register_blueprint(misc_bp)

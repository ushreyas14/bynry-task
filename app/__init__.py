from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, migrate
from app.routes.alerts import alerts_bp
from app.routes.health import health_bp
from app.routes.products import products_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(health_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(alerts_bp)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": str(error)}), 400

    return app

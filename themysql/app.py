import config
from flask import Flask
from extensions import db, login_manager

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config)
    app.secret_key = config.SECRET_KEY
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    from blueprints.auth import auth_bp
    from blueprints.vehicles import vehicles_bp
    from blueprints.drivers import drivers_bp
    from blueprints.tasks import tasks_bp
    from blueprints.accidents import accidents_bp
    from blueprints.stats import stats_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(vehicles_bp, url_prefix="/vehicles")
    app.register_blueprint(drivers_bp, url_prefix="/drivers")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(accidents_bp, url_prefix="/accidents")
    app.register_blueprint(stats_bp, url_prefix="/stats")

    with app.app_context():
        try:
            print("DEBUG: SQLAlchemy engine:", db.engine)
            print("DEBUG: SQLAlchemy session bind:", db.session.get_bind())
        except Exception as e:
            print("DEBUG: db binding check failed:", e)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
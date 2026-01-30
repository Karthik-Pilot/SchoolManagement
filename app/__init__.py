from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return db.session.get(User, int(user_id))


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.teachers import teachers_bp
    from app.routes.students import students_bp
    from app.routes.fees import fees_bp
    from app.routes.reports import reports_bp
    from app.routes.exams import exams_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(teachers_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(fees_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(exams_bp)

    from app.errors import not_found, forbidden, server_error
    app.register_error_handler(404, not_found)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(500, server_error)

    with app.app_context():
        # IMPORTANT: don't use `import app.models` here, it would overwrite the local
        # Flask app variable named `app` with the `app` python package/module.
        from app import models  # noqa: F401 - register all models and tables
        db.create_all()
        from app.models.user import User
        if User.query.count() == 0:
            admin = User(
                username="admin",
                email="admin@school.local",
                role="super_admin",
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

    return app

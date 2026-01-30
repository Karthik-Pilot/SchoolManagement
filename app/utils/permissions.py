from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)
            if current_user.role not in roles:
                return abort(403)
            return f(*args, **kwargs)
        return inner
    return decorator


def admin_required(f):
    return role_required("super_admin", "head_teacher")(f)


def super_admin_required(f):
    return role_required("super_admin")(f)

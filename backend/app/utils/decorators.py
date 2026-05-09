from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask import jsonify

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            allowed_roles = []

            for r in roles:
                if isinstance(r, str):
                    allowed_roles.append(r)
                else:
                    allowed_roles.append(r.value)

            if claims.get("role") not in allowed_roles:
                return jsonify({"msg": "No permission"}), 403
                
            return fn(*args, **kwargs)
        return decorator
    return wrapper
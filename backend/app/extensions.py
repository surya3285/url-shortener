from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Shared extension instances, defined here to avoid circular imports
# between the app factory and the route module.
limiter = Limiter(key_func=get_remote_address)

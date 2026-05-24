# This file makes the 'routes' directory a Python package
from .analyze import router as analyze_router
from .logs import router as logs_router
from .chat import router as chat_router
# app/forms/__init__.py
from flask import Blueprint

bp = Blueprint('forms', __name__)

from app.forms import routes

from flask import Blueprint
from core import limiter

bp = Blueprint('api', __name__)

def set_limiter(limit):
    limiter.limit(limit)(bp)

from app.api import routes
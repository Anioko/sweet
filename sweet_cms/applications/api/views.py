from flask import Blueprint
from flask_restful import Api

blueprint = Blueprint('api', __name__, url_prefix="/api")
main_api = Api(blueprint)

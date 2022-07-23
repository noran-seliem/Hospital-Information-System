from flask import Blueprint
from  flask_autoindex import AutoIndexBlueprint

auto = Blueprint('auto_bp', __name__)
AutoIndexBlueprint(auto,'./static/uploads/prescriptions')

auto_2=Blueprint('auto_bp2', __name__)
AutoIndexBlueprint(auto_2,'./static/uploads/scans')

auto_3=Blueprint('auto_bp3', __name__)
AutoIndexBlueprint(auto_3,'./static/uploads/reports')
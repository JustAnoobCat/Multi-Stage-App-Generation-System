from flask import Blueprint, request, jsonify, session
from models import db
from functools import wraps

api = Blueprint('api', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@api.route('/login', methods=['POST'])
def post_login():
    data = request.get_json()
    # TODO: implement logic
    return jsonify({'message': 'success'}), 200

@api.route('/register', methods=['POST'])
def post_register():
    data = request.get_json()
    # TODO: implement logic
    return jsonify({'message': 'success'}), 200

@api.route('/contacts', methods=['GET'])
@login_required
def get_contacts():
    # TODO: implement logic
    return jsonify({'message': 'success'}), 200

@api.route('/sales', methods=['GET'])
@login_required
def get_sales():
    # TODO: implement logic
    return jsonify({'message': 'success'}), 200

@api.route('/reports', methods=['GET'])
@login_required
def get_reports():
    # TODO: implement logic
    return jsonify({'message': 'success'}), 200

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

users = []

@auth_bp.route('/signup', methods=['POST'])
def signup():

    data = request.json

    hashed_password = generate_password_hash(data['password'])

    users.append({
        "email": data['email'],
        "password": hashed_password
    })

    return jsonify({"message":"User created"})
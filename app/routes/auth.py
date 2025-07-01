from flask import Blueprint, request , jsonify

auth_bp=Blueprint('auth',__name__,url_prefix='/api/auth')

@auth_bp.route('/signup',methods=['POST'])
def signup():
    return jsonify({'message': 'signup endpoind woeking'}),200

@auth_bp.route('/signin',methods=['POST'])
def signin():
    return jsonify({'message':'signin endpoint working'})


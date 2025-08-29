from jose import jwt
import jose
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify


SECRET_KEY = 'super secret secrets'

def encode_token(user_id, role='user'):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1), #Set an expiration date of 1 hour from now
        'iat': datetime.now(timezone.utc),
        'sub': str(user_id), #VERY IMPORTANT, SET YOUR USER ID TO A STR
        'role': role #You will probably not have role unless ytou add it to your models
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def token_required(f): #f stands for the function that is getting wrapped
    @wraps(f)
    def decoration(*args, **kwargs): #The function that runs before the function that we're wrapping
    
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1] #Accesses the headers, then the "Bearer token" string, we then split into ['Bearer', 'token'] we then index into token

        if not token:
            return jsonify({"error": "token missing from authorization headers"}), 401
        
        try:

            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_id = int(data['sub']) #Adding the user_id from the token to the request.
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'token is expired'}), 403
        except jose.exceptions.JWTError:
            return jsonify({'message': 'invalid token'}), 403
        
        return f(*args, **kwargs)
    
    return decoration

def admin_required(f): #f stands for the function that is getting wrapped
    @wraps(f)
    def decoration(*args, **kwargs): #The function that runs before the function that we're wrapping
    
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1] #Accesses the headers, then the "Bearer token" string, we then split into ['Bearer', 'token'] we then index into token

        if not token:
            return jsonify({"error": "token missing from authorization headers"}), 401
        
        try:

            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_id = int(data['sub']) #Adding the user_id from the token to the request.
            if data['role'].lower() != 'admin':
                return jsonify({"message": "Admin permissions required."})
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'token is expired'}), 403
        except jose.exceptions.JWTError:
            return jsonify({'message': 'invalid token'}), 403
        
        return f(*args, **kwargs)
    
    return decoration



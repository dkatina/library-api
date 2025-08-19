from app.blueprints.users import users_bp
from .schemas import user_schema, users_schema
from flask import request, jsonify, render_template
from marshmallow import ValidationError
from app.models import Users, db
from app.extensions import limiter


#CREATE USER ROUTE
@users_bp.route('', methods=['POST']) #route servers as the trigger for the function below.
@limiter.limit("5 per day")
def create_user():
    try:
        data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    
    new_user = Users(**data) #Creating User object
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201

#Read Users
@users_bp.route('', methods=['GET']) #Endpoint to get user information
def read_users():
    users = db.session.query(Users).all()
    return users_schema.jsonify(users), 200


#Read Individual User - Using a Dynamic Endpoint
@users_bp.route('<int:user_id>', methods=['GET'])
@limiter.limit("15 per hour")
def read_user(user_id):
    user = db.session.get(Users, user_id)
    return user_schema.jsonify(user), 200


#Delete a User
@users_bp.route('<int:user_id>', methods=['DELETE'])
@limiter.limit("5 per day")
def delete_user(user_id):
    user = db.session.get(Users, user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted user {user_id}"}), 200


#Update a User
@users_bp.route('<int:user_id>', methods=['PUT'])
@limiter.limit("1 per month")
def update_user(user_id):
    user = db.session.get(Users, user_id) #Query for our user to update

    if not user: #Checking if I got a user
        return jsonify({"message": "user not found"}), 404  #if not return error message
    
    try:
        user_data = user_schema.load(request.json) #Validating updates
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    for key, value in user_data.items(): #Looping over attributes and values from user data dictionary
        setattr(user, key, value) # setting Object, Attribute, Value to replace

    db.session.commit()
    return user_schema.jsonify(user), 200
    
#Query the user by id
#Validate and Deserialze the updates that they are sending in the body of the request
#for each of the values that they are sending, we will change the value of the queried object
#commit the changes
#return a response


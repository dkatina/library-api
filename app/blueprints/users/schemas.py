from app.extensions import ma
from app.models import Users


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users #Creates a schema that validates the data as defined by our Users Model

user_schema = UserSchema() 
users_schema = UserSchema(many=True) #Allows this schema to translate a list of User objects all at once
login_schema = UserSchema(exclude=['username','DOB','address','role'])
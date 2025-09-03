from app.models import db
from app import create_app
import os



app = create_app('ProductionConfig') #Make sure you are in production mode


with app.app_context():
    # db.drop_all() 
    db.create_all() #Creating our database tables


#SMall comment before deploy

#Triggering re-deploy to see if service goes down fully





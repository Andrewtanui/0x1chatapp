from flask_sqlalchemy import SQLAlchemy
from server import app

db = SQLAlchemy(app)

class User(db.Model):
  """User model for storing user data"""
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), unique=True, nullable=False)
  password = db.Column(db.String(128))
  email = db.Column(db.String(120), unique=True)
  def __init__(self, username, password, email):
    self.username = username
    self.password = password
    self.email = email
  
  @staticmethod
  def create_user(username, password, email):
    new_user = User(username=username, password=password, email=email)
    db.session.add(new_user)
    db.session.commit()
    return app.logger.log("User created")
from flask import Flask, jsonify, render_template, request, flash, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import uuid
from dotenv import load_dotenv,find_dotenv
import os
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.db'
db = SQLAlchemy(app)
# Set up the application context
app.app_context().push()

load_dotenv(find_dotenv())
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

bcrypt = Bcrypt(app)
class User(UserMixin, db.Model):
    """User model for storing user data"""
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    fullname = db.Column(db.String(64), unique=False, nullable=False)
    password = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)
    groups = db.relationship('Group', backref='creator', lazy=True)

    def __init__(self, username, fullname, password, email):
        self.username = username
        self.fullname = fullname
        self.password = password
        self.email = email


class Group(db.Model):
    """Group model for storing group data"""
    __tablename__ = 'groups'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    unique_link = db.Column(db.String(36), unique=True, nullable=False)

    def __init__(self, name, description, creator_id):
        self.name = name
        self.description = description
        self.creator_id = creator_id
        self.unique_link = str(uuid.uuid4())  # Generate a unique link for the group

    @staticmethod
    def create_group(name, description, creator_id):
        new_group = Group(name=name, description=description, creator_id=creator_id)
        db.session.add(new_group)
        db.session.commit()
        return new_group.unique_link
    
class Message(db.Model):
    """Message model for storing chat messages"""
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.String(36), db.ForeignKey('groups.id'), nullable=False)

    user = db.relationship('User', backref='messages', lazy=True)
    group = db.relationship('Group', backref='messages', lazy=True)

    def __init__(self, content, user_id, group_id):
        self.content = content
        self.user_id = user_id
        self.group_id = group_id

@app.route('/')
def home():
  hello = {
    "message":"Hello group whatever"
  }
  return render_template("index.html",
                         title="Chap app project",
                         hello=hello["message"])
  
@app.route('/chat')
@login_required
def chat():

  return render_template("chat.html",
                         title="Chap app project",
                         chat=True)
  


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        fullname = request.form['fullname']
        password = request.form['password']
        email = request.form['email']

        # Check if the username or email is already registered
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Email or username already exists.', category='error')
            return redirect(url_for('register'))

        # Generate a password hash using Flask-Bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        new_user = User(username=username,fullname=fullname, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()

        # Redirect to a success page or login page
        flash(f'Thank you! {new_user.username}, for creating an account wit us.', category='success')
        return render_template('login.html', username=new_user.fullname)


    return render_template('register.html',
                           title="Create an account")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not email or not password:
            flash('Both email and password are required.', category='error')
        if user:
            if bcrypt.check_password_hash(user.password, password):
                login_user(user, remember=True)
                next_page = request.args.get('next')            
                # Redirect to the page specified in query string parameter "next" (if exists), otherwise go back home
                if next_page:
                    flash(f'{current_user.username} You can now access this route!', category='success')
                    return redirect(next_page)
                flash(f'Welcome back {current_user.username}!', category='success')
                return redirect(url_for('chat'))
            flash('Login failed. Please check your email and password.', category='error')    
    return render_template('login.html',user=current_user)



@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

    
if __name__ == '__main__':
  app.run(debug=True)
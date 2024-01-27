import io
from flask import Flask, jsonify, render_template, request, flash, redirect,url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import uuid
from dotenv import load_dotenv,find_dotenv
import os
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.db'
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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


class Profile(db.Model):
    """Profile model for storing user profiles"""
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(255),nullable=True)

    activities = db.relationship('Activity', backref=db.backref('user_profile', lazy=True))
    user = db.relationship('User', backref='profile', uselist=False, lazy=True)

    def __init__(self, user_id, bio=None, profile_picture=None):
        self.user_id = user_id
        self.bio = bio
        self.profile_picture = profile_picture





class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)

    profile_id = db.Column(db.String(36), db.ForeignKey('profiles.id'), nullable=False)

    def __init__(self, user_id, activity_type, profile_id):
        self.user_id = user_id
        self.activity_type = activity_type
        self.profile_id = profile_id


class Group(db.Model):
    """Group model for storing group data"""
    __tablename__ = 'groups'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid1()), unique=True, nullable=False)
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


@app.route('/profile')
@login_required
def profile():
    user = current_user
    profile = Profile.query.filter_by(user_id=user.id).first()
    # Retrieve activities for the user's profile
    activities = Activity.query.filter_by(user_id=user.id).all()  # Get all activities for the user
    group = Group.query.filter_by(creator_id=user.id).all()  # Get all activities for the user

    return render_template("profile.html",
                           title="Chap app project",
                           user=user,
                           profile=profile,
                           group=group,
                           activities=activities)  # Pass activities to the template
  
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user
    profile = Profile.query.filter_by(user_id=user.id).first()
    if request.method == 'POST':
        bio = request.form['bio']
        profile_picture = request.files['profile_picture']

        
         # Handle profile picture upload
        # Grab image name 
        pic_filename = secure_filename(profile_picture.filename)

        # set filename uuid 
        pic_name = str(uuid.uuid4()) + "_" + pic_filename
        # Save image
        profile_picture.save(
            os.path.join(app.config['UPLOAD_FOLDER'],pic_name)
        )
        # Chnage to string to save to db 
         
        profile_picture = pic_name
        # Create or update the user's profile
        user_profile = Profile.query.filter_by(user_id=current_user.id).first()
        if user_profile:
            user_profile.bio = bio
            user_profile.profile_picture = pic_name
        else:
            create_profile = Profile(user_id=current_user.id, bio=bio, profile_picture=pic_name)
            db.session.add(create_profile)
            db.session.commit()

            activity = Activity(user_id=current_user.id, activity_type='Profile Completion', profile_id=current_user.id)
            db.session.add(activity)
            db.session.commit()
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html',
                            profile=profile)

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
        email_or_username = request.form.get('email_or_username')
        password = request.form.get('password')

        user = User.query.filter_by(email=email_or_username).first() or User.query.filter_by(username=email_or_username).first()

        if not email_or_username or not password:
            flash('Both email/username and password are required.', category='error')
        if user:
            if bcrypt.check_password_hash(user.password, password):
                login_user(user, remember=True)
                next_page = request.args.get('next')            
                # Redirect to the page specified in query string parameter "next" (if exists), otherwise go back home
                if next_page:
                    flash(f'{current_user.username} You can now access this route!', category='success')
                    return redirect(next_page)
                flash(f'Welcome back {current_user.username}!', category='success')
                activity = Activity(user_id=current_user.id, activity_type='Login', profile_id=current_user.id)
                db.session.add(activity)
                db.session.commit()
                return redirect(url_for('profile'))
            flash('Login failed. Please check your email and password.', category='error')    
    return render_template('login.html',user=current_user)


@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    user=current_user
    group = Group.query.filter_by(creator_id=user.id).all()  # Get all groups for the user
    if group:
        flash('Sorry! You can only create one group for now. Sorry for the inconvinience.','error')
        return redirect(url_for('profile'))
    user_profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not user_profile:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('edit_profile'))
    if request.method == 'POST':
        name = request.form['group-name']
        description = request.form['description']

        # Create a new group
        new_group = Group(name=name, description=description, creator_id=current_user.id)
        db.session.add(new_group)
        db.session.commit()

        user_profile = Profile.query.filter_by(user_id=current_user.id).first()

        # Check if the user has a profile
        if user_profile:
            activity = Activity(user_id=current_user.id, activity_type='Group Creation', profile_id=user_profile.id)
            db.session.add(activity)
            db.session.commit()
        else:
            # Handle the case where the user's profile is not found
            flash('Error: User profile not found. Please complete your profile first to unlock Create room', 'error')
            return redirect(url_for('edit_profile'))

        # Redirect to the group's page or a success page
        flash('Group created successfully!', 'success')
        return redirect(url_for('chat', group_id=new_group.id))

    return render_template('create_group.html')


# Join Group route
@app.route('/join_group/<group_link>', methods=['GET', 'POST'])
@login_required
def join_group(group_link):
    group = Group.query.filter_by(unique_link=group_link).first()

    if not group:
        flash('Invalid group link. The group does not exist.', 'error')
        return redirect(url_for('chat'))

    if request.method == 'POST':
        # Check if the user is already a member of the group
        if group in current_user.groups:
            flash('You are already a member of this group.', 'info')
            return redirect(url_for('group', group_id=group.id))

        # Add the user to the group
        current_user.groups.append(group)
        db.session.commit()

        flash(f'You have joined the group "{group.name}"!', 'success')
        return redirect(url_for('group', group_id=group.id))

    return render_template('register.html', group=group)

# @app.route('/chat/message')
# @login_required
# def start_message():
#     group_id = request.args['group_id']
#     return f"{group_id} created successfully"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

    
if __name__ == '__main__':
  app.run(debug=True)
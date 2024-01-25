from flask import Flask, jsonify, render_template
from models import User

app = Flask(__name__)

@app.route('/')
def home():
  hello = {
    "message":"Hello group whatever"
  }
  return render_template("index.html",
                         title="Chap app project",
                         hello=hello["message"])
  
  
@app.route('/chat')
def chat():

  return render_template("chat.html",
                         title="Chap app project",
                         chat=True)
  
  
@app.route('/login')
def login():

  return render_template("login.html",
                         title="Chap app project")

if __name__ == '__main__':
  app.run(debug=True)
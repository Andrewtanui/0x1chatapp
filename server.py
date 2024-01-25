from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
  hello = {
    "message":"Hello group whatever"
  }
  return render_template("index.html",
                         title="Chap app project",
                         hello=hello["message"])

if __name__ == '__main__':
  app.run(debug=True)
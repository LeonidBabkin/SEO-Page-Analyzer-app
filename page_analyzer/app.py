from flask import Flask, render_template
import os
from dotenv import load_dotenv


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route("/")
def hello_world():
    data = {'url': ''}
    return render_template('index.html', data=data)


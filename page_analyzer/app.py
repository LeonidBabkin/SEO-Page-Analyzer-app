from flask import Flask, render_template, request
import os
from dotenv import load_dotenv


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route("/")
def hello_template():
    data = {'url': ''}
    return render_template('index.html', data=data)


@app.route('/', methods=['POST'])
def hello_url():
    datum = request.form.to_dict()
    url = datum['url']
    return render_template('page.html', url=url)

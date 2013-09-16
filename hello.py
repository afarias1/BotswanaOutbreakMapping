import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Yo Yo whats up dis Tony Farias\' Heroku webapp. Kenny\'s a bitch, namsayin'




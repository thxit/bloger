from flask import Flask, render_template
from flask_script import Manager
from flask_moment import Moment
from datetime import datetime
from flask_bootstrap import Bootstrap

app = Flask(__name__)
manager = Manager(app)
moment = Moment(app)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html',current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

if __name__ == '__main__':
    manager.run()

from flask import Flask, render_template
from flask_script import Manager
from flask_moment import Moment
from datetime import datetime
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

app = Flask(__name__)
manager = Manager(app)
moment = Moment(app)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'hard to guess'

class NameForm(Form):
    name = StringField(u'你的名字是?',validators=[Required()])
    submit = SubmitField(u'确定')


@app.route('/', methods = ['GET','POST'])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.data.name
        form.data.name = ''
    return render_template('index.html', form = form ,name = name)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

if __name__ == '__main__':
    manager.run()

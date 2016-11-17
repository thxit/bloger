#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask, render_template, url_for, session, redirect, flash
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
    name = StringField('你的名字是?',validators=[Required()])
    submit = SubmitField('确定')


@app.route('/', methods = ['GET','POST'])
def index():
    form = NameForm()

    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('你已更改了名字')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

if __name__ == '__main__':
    manager.run()

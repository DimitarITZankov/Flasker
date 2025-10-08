from flask import Flask,render_template,flash
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField
from wtforms.validators import DataRequired #requires to put data,nullable=false
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app=Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')

app.config['SECRET_KEY'] = 'mysecretkey'
db = SQLAlchemy(app)

#Create Model
class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(120),nullable=False,unique=True)
    date_added = db.Column(db.DateTime,default=datetime.utcnow)

    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name

class UserForm(FlaskForm):
    name = StringField("Name:",validators=[DataRequired()])
    email = StringField("Email:",validators=[DataRequired()])
    submit = SubmitField("Submit")

#Create a From Class
class NamerForm(FlaskForm):
    name = StringField("What's your name?",validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/user/add',methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_users=our_users)

@app.route('/')
def index():
    first_name = "Dimitar"
    safe_filter = "This is a <strong>Bold</strong> text!"
    list_example = ["pizza","cheese","Listed",67]
    return render_template('index.html',
                           first_name=first_name,
                           safe_filter_example=safe_filter,
                           list_example=list_example)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',user_name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/name',methods=['GET','POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully")
    return render_template('name.html',
                           name=name,
                           form=form,)
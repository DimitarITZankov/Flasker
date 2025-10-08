from flask import Flask,render_template,flash,request
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField
from wtforms.validators import DataRequired #requires to put data,nullable=false
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from werkzeug.security import generate_password_hash,check_password_hash


app=Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')

app.config['SECRET_KEY'] = 'mysecretkey'
db = SQLAlchemy(app)
migrate = Migrate(app,db)

#Create Model
class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(120),nullable=False,unique=True)
    favourite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime,default=datetime.utcnow)
    #Do soome password stuff!
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("password is not a readable")
    
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    
    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name

class UserForm(FlaskForm):
    name = StringField("Name:",validators=[DataRequired()])
    email = StringField("Email:",validators=[DataRequired()])
    favourite_color = StringField("Favourite Color:")
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
            user = Users(name=form.name.data, email=form.email.data,favourite_color=form.favourite_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favourite_color.data = ''
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
@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_color = request.form['favourite_color']
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("update.html",form=form,
                name_to_update=name_to_update)
        except:
            flash("ERROR! Looks like there was a problem.Try again!")
            return render_template("update.html",form=form,
                name_to_update=name_to_update)
    else:
        return render_template("update.html",form=form,
                name_to_update=name_to_update,id=id)

#Create a route to delete a user
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!!!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
        form=form,name=name,our_users=our_users)
    except:
        flash("Whoops!There was a problem deleting user,try again...")
        return render_template("add_user.html",
        form=form,name=name,our_users=our_users)
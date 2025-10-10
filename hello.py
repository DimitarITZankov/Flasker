from flask import Flask,render_template,flash,request,redirect,url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,PasswordField,BooleanField,ValidationError
from wtforms.validators import DataRequired,EqualTo,Length #requires to put data,nullable=false
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import date
from wtforms.widgets import TextArea
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user

app=Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')

app.config['SECRET_KEY'] = 'mysecretkey'
db = SQLAlchemy(app)
migrate = Migrate(app,db)
#Create a blog post model
class Posts(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime,default=datetime.utcnow)
    slug = db.Column(db.String(255))

#Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#Create a post form
class PostForm(FlaskForm):
    title = StringField("Title",validators=[DataRequired()])
    content = StringField("Content",validators=[DataRequired()],widget=TextArea())
    author = StringField("Author",validators=[DataRequired()])
    slug = StringField("Slug",validators=[DataRequired()])
    submit =SubmitField("Submit")

#Create Login Form
class LoginForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Submit")

#Add Post Page
@app.route('/add-post',methods=["GET","POST"])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data,content=form.content.data,author=form.author.data,slug=form.slug.data)
        #Clear the form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        #Add to database
        db.session.add(post)
        db.session.commit()
        #Return a message
        flash("Blog Post Submited Successfully!")
    return render_template("add_post.html",form=form)

'''#Create a Posts page
@app.route('/posts',methods=["GET","POST"])
def get_all_posts():
    posts = None
    if request.method == "GET":
        posts = Posts.query.all()
    return render_template("posts.html",posts=posts)'''
@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html",posts=posts)

#Create Model
class Users(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),nullable=False,unique=True)
    name = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(120),nullable=False,unique=True)
    favourite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime,default=datetime.utcnow)
    #Do some password stuff!
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("password is not readable")
    
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
    username = StringField("Username:",validators=[DataRequired()])
    email = StringField("Email:",validators=[DataRequired()])
    favourite_color = StringField("Favourite Color:")
    password_hash = PasswordField('Password',validators=[DataRequired(),EqualTo('password_hash2',message ='Passwords Must Match')])
    password_hash2 =PasswordField('Confirm Password',validators=[DataRequired()])
    submit = SubmitField("Submit")

#Create a From Class
class NamerForm(FlaskForm):
    name = StringField("What's your name?",validators=[DataRequired()])
    submit = SubmitField("Submit")

class PasswordForm(FlaskForm):
    email = StringField("What's your email?",validators=[DataRequired()])
    password_hash= PasswordField("What's your password?",validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/user/add',methods=['GET','POST'])
def add_user():
    name = None
    hashed_pw = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            #Hash Password
            hashed_pw = generate_password_hash(form.password_hash.data, method='pbkdf2:sha256')
            user = Users(name=form.name.data,username=form.username.data, email=form.email.data,favourite_color=form.favourite_color.data,password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        form.favourite_color.data = ''
        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_users=our_users,
                           password_hash=hashed_pw)

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

#Create Password Test Page
@app.route('/test_pw',methods=['GET','POST'])
def test_pw():
    email=None
    password = None
    pw_to_check = None  
    passed = None  
    form = PasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        pw_to_check = Users.query.filter_by(email=email).first()
        #Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash,password)
    return render_template('test_pw.html',
                           email=email,
                           password=password,
                           pw_to_check= pw_to_check,
                           passed =passed,
                           form=form)

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

#Return in a JSON format
@app.route('/date')
def get_current_date():
    fav_pizza = {"John" : "Pepperoni",
                "Marry" : "Cheese",
                "Mitko" : "Brownies"}
    return fav_pizza


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html',post=post)


#Edit Posts
@app.route('/posts/edit/<int:id>',methods=["POST","GET"])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data  
        post.slug = form.slug.data
        post.content = form.content.data
        db.session.add(post)
        db.session.commit()
        flash("Successfully Editted The Post")
        return redirect(url_for('post',id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html',form=form)


@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post_to_delete=Posts.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        #Return a message 
        flash("Blog Post Was Deleted")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html",posts=posts)
    except:
        flash("Whoops,There was a problem deleting the post")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html",posts=posts)


#Create Login Page
@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #Check the hash
            if check_password_hash(user.password_hash,form.password.data):
                login_user(user)
                flash("Login Successfully")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong password")
        else:
            flash("That user doesn't exist,Try again!")
    return render_template('login.html',form=form)

#Create Dashbard Page
@app.route('/dashboard',methods=["GET","POST"])
@login_required
def dashboard():
    return render_template('dashboard.html')

#Create Logout function
@app.route('/logout',methods=["GET","POST"])
@login_required
def logout():
    logout_user
    flash("You have been logged out")
    return redirect(url_for('login'))
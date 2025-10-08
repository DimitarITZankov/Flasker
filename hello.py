from flask import Flask,render_template,flash
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField
from wtforms.validators import DataRequired #requires to put data,nullable=false
app=Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
#Create a From Class
class NamerForm(FlaskForm):
    name = StringField("What's your name?",validators=[DataRequired()])
    submit = SubmitField("Submit")

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
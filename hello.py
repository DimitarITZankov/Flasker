from flask import Flask,render_template
app=Flask(__name__)

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
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'Llpzdoen89(6@c54?tuw'

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(600))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password




@app.route('/login', methods=['POST', 'GET'])
def login():
    if  request.method == 'POST':   
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password is incorrect, or user does not exist', 'error')
            return render_template('login.html')
    else:
        return render_template("login.html")

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_copy = request.form['password_copy']
        if len(username) < 3 or len(username) > 20  or " " in username:
            error1 = "Please enter a valid username."
            return render_template("signup.html",  error1=error1 )
        if len(password) < 3 or len(password) > 20 or " " in password:
            error2 = "Please enter a valid password."
            return render_template("signup.html", name=username, error2 =error2)
        if password_copy != password:
            error3 = "Please make sure your password matches your confirmation password"
            return render_template("signup.html", name = username, error3=error3)

        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            return redirect('/login')
        
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
            return redirect('/newpost')

    else:
        return render_template('signup.html')

@app.route('/logout')   
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():

    users = User.query.all()
    return render_template("names_display.html", users = users)


@app.route('/blog', methods=['POST', 'GET'])
def blog_posts():
    if request.args.get('id'):
        blog_id = int(request.args.get('id'))
        clicked_blog = Blog.query.get(blog_id)
        clicked_owner = clicked_blog.owner
        username = clicked_owner.username
        return render_template("indiv_display.html", title=clicked_blog.title, body=clicked_blog.body, blog=clicked_blog, name = username)

    if request.args.get('user'):
        clicked_username = request.args.get('user')
        owner = User.query.filter_by(username = clicked_username).first()
        blogs = Blog.query.filter_by(owner=owner).all()
        return render_template("display.html", blogs=blogs)

    blogs = Blog.query.all()
    return render_template("display.html", blogs=blogs)

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','blog_posts','index','logout' ]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/newpost', methods =['POST', 'GET'])

def new_post():

    if request.method == 'GET':
        return render_template("add_post.html")


    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        


        if blog_title == "" or  blog_body =="":
            error_1 = "Please fill in a title"
            error_2 = "Please write a blog entry"
            if blog_title == "":
                return render_template("add_post.html", error_1=error_1, blog_body = blog_body)
            else:
                return render_template("add_post.html", error_2 = error_2, blog_title = blog_title)
                

        else:
            owner =  User.query.filter_by(username=session['username']).first()                
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            
            
            return redirect('/blog?id=' + str(new_blog.id))

if __name__ == '__main__':
    app.run()

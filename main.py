from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(600))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['POST', 'GET'])
def blog_posts():
    if request.args.get('id'):
        blog_id = int(request.args.get('id'))
        clicked_blog = Blog.query.get(blog_id)
        return render_template("indiv_display.html", blog_title=clicked_blog.title, blog_body=clicked_blog.body)
    blogs = Blog.query.all()
    return render_template("display.html", blogs=blogs)



@app.route('/newpost', methods =['GET', 'POST'])

def addpost():

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
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            
            
            return redirect('/blog?id=' + str(new_blog.id))

if __name__ == '__main__':
    app.run()

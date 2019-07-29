from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route("/index")
def index():
    users = User.query.all()
    return render_template('index.html', users=users, header='Blog Users')

@app.route('/blog')
def blog():
    posts = Blog.query.all()
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    
    if user_id:
        posts = Blog.query.filter_by(owner_id=user_id)
        return render_template('singleUser.html', posts=posts, header="User Posts")
    if blog_id:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post )

    return render_template('blog.html', posts=posts, header='All Blog Posts')

   
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-entry']
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = "Please enter a blog title"
        if not blog_body:
            body_error = "Please enter a blog entry"

        if not body_error and not title_error:
            new_entry = Blog(blog_title, blog_body, owner)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', title='New Entry', title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', title='New Entry')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/index')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash ('This is a duplicate account','error')

        elif len(email) > 30 or len(email) < 3: 
            flash('Not a valid email.', 'error')
            email = ''

        elif len(password) < 3 or len(password) > 30:
            flash('Password must be longer than 3 characters and less than 20 and cannot contain any spaces.', 'error')
            password = ''

        elif password != verify: 
            flash('These two passwords do not match', 'error')
            veriry = ''

        else:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/index')
                

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')

if __name__ == '__main__':
    app.run()
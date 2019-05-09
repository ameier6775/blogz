from flask import Flask, request, redirect, render_template, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blueberries123$@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'FGnbfnGNreth6h'

db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(1000))
    exist = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) 

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.exist = True
        self.owner = owner

    def __repr__(self):
        return '<Blog {0}>'.format(self.title)

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(150))
    blogs = db.relationship('Blog', backref='owner')
    exist = db.Column(db.Boolean)

    def __init__(self, username, password):
        self.username = username  
        self.password = password
        self.exist = True

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'get_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')        

@app.route('/author')
def get_author():
    print('🧐', request.args)
    user = request.args.get("user")
    print('😙', user)
    if request.method == 'GET':
        if(user is not None):
            users = User.query.filter_by(exist=True, id=user).all()
            blogs = Blog.query.filter_by(exist=True).all()
            user = User.query.get(user)
            return render_template('authors.html', user=user, blogs=blogs)

@app.route('/blogs')
def get_blogs():

    blogs = Blog.query.filter_by(exist=True).all()

    return render_template('blogs.html', blogs=blogs)

@app.route('/blog')
def get_blog():
    id = request.args.get("id", str)

    if request.method == 'GET':
        if(id is None):
            blog = Blog('NA', 'NA')
            blog.id = 1
            return render_template('blog.html', id=blog.id, title=blog.title, content=blog.content)
        elif(id is not None):
            blog = Blog.query.get(id)
            user_num = blog.owner_id
            user = User.query.filter_by(id=user_num).first()
            return render_template('blog.html', user=user, id=blog.id, title=blog.title, content=blog.content)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    title_error = ""
    content_error = ""
    errors = []
        
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        owner = User.query.filter_by(username=session['username']).first()
        if title == "":
            title_error = "PLEASE ENTER A VALUE"
            errors.append(title_error)
        if content == "":
            content_error = "PLEASE ENTER A VALUE"
            errors.append(content_error)
        if len(errors) > 0:
            return render_template('newpost.html', title_error=title_error, content_error=content_error, title=title, content=content)     
        new_blog = Blog(title, content, owner)
        db.session.add(new_blog)
        db.session.commit()
        print(new_blog.id)
        return redirect(url_for('get_blog' , id=new_blog.id))
    else:
        return render_template('newpost.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blogs')

@app.route('/')
def index():
    users = User.query.filter_by(exist=True).all()
    blogs = Blog.query.filter_by(exist=True).all()
    return render_template('index.html', users=users, blogs=blogs)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':  
        mes_errors = []  
        user_error = ""
        pass_error = ""
        username = request.form['username']
        password = request.form['password']   
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        elif user and user.password != password:
            pass_error = "Password is incorrect"
            mes_errors.append(pass_error)
        else:
            user_error = "User does not exist"
            mes_errors.append(user_error)
        if len(mes_errors) > 0:
            return render_template('login.html', pass_error=pass_error, user_error=user_error)
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        one_error = ""
        two_error = ""
        three_error = ""
        errors = []
        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            if username == "" or len(username) < 3:
                one_error = "Please enter valid username"
                errors.append(one_error)
            if password == "" or len(password) < 3:
                two_error = "Please enter valid password"
                errors.append(two_error)
            if verify != password:
                three_error = "Passwords dont match"
                errors.append(three_error)
            if len(errors) > 0:
                return render_template('signup.html', one_error=one_error, two_error=two_error, three_error=three_error)
            else:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
        else:
            user_exist_mess = "User already exists!"
            return render_template('signup.html', user_exist_mess=user_exist_mess)

    return render_template('signup.html')

if __name__ == "__main__":
    app.run()


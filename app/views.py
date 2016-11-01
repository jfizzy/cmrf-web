#package references

#file references
from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/login')
def login():
    return "Login page"

@app.route('/register')
def register():
    return "Registration page"

@app.route('/news')
def news():
    return "News feed"

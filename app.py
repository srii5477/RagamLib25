from flask import Flask, redirect, session, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import date
from flask_bcrypt import Bcrypt 


app = Flask(__name__)
app.secret_key = 'secret123'
app.config['JWT_SECRET_KEY'] = 'abc123'
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

books = []
users = []
premium_amount = '500'

class Membership_Type():
    REGULAR = 1
    PREMIUM = 2
    
@app.route('/')
def home():
    return 'Welcome to RagamLibrary@25!'

@app.route('/add-book', methods=['POST'])
def add_book():
    new_id = len(books)
    title = request.form.get('title')
    author = request.form.get('author')
    published_year = request.form.get('published_year')
    genre = request.form.get('genre')
    available_copies = request.form.get('available_copies')
    new_book = {'id': new_id, 'title': title, 'author': author, 
                'published_year': published_year, 'genre': genre,
                'available_copies': available_copies}
    books.append(new_book)
    return new_book

@app.route('/view-books', methods=['GET'])
def view_books():
    return books

@app.route('/update-book', methods=['PATCH'])
def update_book(id, title, author, published_year, genre, available_copies):
    books[id]['title'] = title
    books[id]['author'] = author
    books[id]['published_year'] = published_year
    books[id]['genre'] = genre
    books[id]['available_copies'] = available_copies
    return books[id]

@app.route('/add-user', methods=['POST'])
def add_user():
    new_id = len(users)
    name = request.form.get('name')
    email = request.form.get('email')
    membership_type = request.form.get('membership_type')
    password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
    today = date.today()
    if membership_type == 'Premium':
        session['new_details'] = {'id': new_id, 'name': name, 'email': email, 
                'membership_type': membership_type, 'registered_date': today,
                'password': password }
        session['payment'] = request.form.get('amount_paid')
        return redirect('/make-premium-payment')
    new_user = {'id': new_id, 'name': name, 'email': email, 
                'membership_type': membership_type, 'registered_date': today, 'password':
                    password}
    users.append(new_user)
    return new_user

@app.route('/make-premium-payment', methods=['GET'])
def make_premium_payment():
    if session.get('payment', {}) == premium_amount:
        return redirect('/continue-add-user')
    else:
        return 'Premium account creation failed!'
    
@app.route('/continue-add-user', methods=['GET'])
def continue_add_user():
    users.append(session.get('new_details', {}))
    return session.get('new_details', {})

@app.route('/view-users', methods=['GET'])
def view_users():
    return users

@app.route('/update-user', methods=['PATCH'])
def update_user(id, name, email, membership_type, registered_date):
    users[id]['name'] = name or users[id]['name']
    users[id]['email'] = email or users[id]['email']
    users[id]['membership_type'] = membership_type or users[id]['membership_type']
    users[id]['registered_date'] = registered_date or users[id]['registered_date']
    return users[id]

@app.route('/forgot-password', methods=['PATCH'])
def update_password(id):
    new_password = request.form.get('password')
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    users[id]['password'] = hashed_password 
    return 'Successful updation.'
    
    
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('name')
    password = request.form.get('password')
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    flag = 0
    found_id = -1
    for i in range(len(users)):
        if users[i]['name'] == username:
            flag = 1
            found_id = i
            if not bcrypt.check_password_hash(hashed_password, users[i]['password']):
                return 'Incorrect password!'
    if flag == 0:
        return 'No user matching your entry was found!'
    access_token = create_access_token(identity = found_id)
    return 'Successful login.'

@app.route('/delete-book', methods=['DELETE'])
@jwt_required
def delete_book(id):
    del users[id]
    for j in range(len(books)):
        books[j]['id'] = j
    return 'Successful deletion.'


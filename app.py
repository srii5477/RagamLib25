from flask import Flask, redirect, session, request, jsonify
from flask_jwt_extended import get_jwt_identity, JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import date
from flask_bcrypt import Bcrypt, check_password_hash

app = Flask(__name__, template_folder='static')
app.secret_key = 'secret123'
app.config['JWT_SECRET_KEY'] = 'abc123'
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

global_book_id = 0
global_user_id = 1
books = []
users = [{'id': 0, 'name': 'Sridevi', 'email': 'abc@yz.in', 'membership_type': 'Regular',
          'password': '$2b$12$vXiRpeZ5I3Y2Pn1c/qguEeDYWqM1KsjzsFcJ6mdfR5boLOZUGg98e', 
          'registered_date': '12312323'}]
premium_amount = '500'

class Membership_Type():
    REGULAR = 1
    PREMIUM = 2
    
@app.route('/', methods=['GET'])
def home():
    return 'Welcome to RagamLib25!'

@app.route('/add-book', methods=['POST'])
@jwt_required()
def add_book():
    new_id = global_book_id
    global_book_id += 1
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
@jwt_required()
def update_book():
    update_id = request.args.get('id')
    title = request.form.get('title')
    author = request.form.get('author')
    published_year = request.form.get('published_year')
    genre = request.form.get('genre')
    available_copies = request.form.get('available_copies')
    books[update_id]['title'] = title
    books[update_id]['author'] = author
    books[update_id]['published_year'] = published_year
    books[update_id]['genre'] = genre
    books[update_id]['available_copies'] = available_copies
    return books[update_id]

@app.route('/add-user', methods=['POST'])
def add_user():
    global global_user_id
    new_id = global_user_id
    global_user_id += 1
    name = request.form.get('name')
    email = request.form.get('email')
    membership_type = request.form.get('membership_type')
    password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
    today = date.today()
    user_type = 'User'
    if membership_type == 'Premium':
        session['new_details'] = {'id': new_id, 'name': name, 'email': email, 
                'membership_type': membership_type, 'registered_date': today,
                'password': password, 'user_type': user_type}
        session['payment'] = request.form.get('amount_paid')
        return redirect('/make-premium-payment')
    new_user = {'id': new_id, 'name': name, 'email': email, 
                'membership_type': membership_type, 'registered_date': today, 'password':
                    password, 'user_type': user_type}
    users.append(new_user)
    return new_user

@app.route('/promote-to-admin', methods=['PATCH'])
@jwt_required()
def promote_to_admin():
    promote_id = request.args.get('id')
    if True: #this request needs to be verified by another admin
        users[promote_id]['user_type'] = 'Admin'
    return 'Successful promotion to admin.'

@app.route('/make-premium-payment', methods=['GET'])
def make_premium_payment():
    if session.get('payment', {}) == premium_amount:
        return redirect('/continue-add-user')
    else:
        return 'Premium account creation failed!', 401
    
@app.route('/continue-add-user', methods=['GET'])
def continue_add_user():
    users.append(session.get('new_details', {}))
    return session.get('new_details', {})

@app.route('/view-users', methods=['GET'])
@jwt_required()
def view_users():
    return users

@app.route('/update-user', methods=['PATCH'])
@jwt_required()
def update_user():
    update_id = request.args.get('id')
    name = request.form.get('name')
    email = request.form.get('email')
    membership_type = request.form.get('membership_type')
    registered_date = date.today()
    users[update_id]['name'] = name or users[update_id]['name']
    users[update_id]['email'] = email or users[update_id]['email']
    users[update_id]['membership_type'] = membership_type or users[update_id]['membership_type']
    users[update_id]['registered_date'] = registered_date or users[update_id]['registered_date']
    return users[id]

@app.route('/forgot-password', methods=['PATCH'])
def update_password():
    new_password = request.form.get('password')
    update_id = request.args.get('id')
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    users[update_id]['password'] = hashed_password 
    return 'Successful updation.'
    
    
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('name')
    password = request.form.get('password')
    flag = 0
    found_id = -1
    for i in range(len(users)):
        if users[i]['name'] == username:
            flag = 1
            found_id = i
            if not check_password_hash(users[i]['password'].encode('utf-8'), password.encode('utf-8')):
                flag = 0
    if flag == 0:
        return 'Incorrect credentials!', 401
    access_token = create_access_token(identity = found_id)
    return jsonify(access_token=access_token), 200

#protected endpoints
@app.route('/delete-book', methods=['DELETE'])
@jwt_required()
def delete_book():
    delete_id = request.form.get('id')
    user_id = get_jwt_identity()
    for i in range(len(users)):
        if users[i]['id'] == user_id:
            if users[i]['user_type'] == 'Admin':
                if delete_id < 0 or delete_id >= global_book_id:
                    return 'Invalid book ID.'
                del books[delete_id]
                return 'Successful deletion of book.'
            else:
                break
                 
    return 'You are not authorized to perform this operation.', 401
    

@app.route('/delete-user', methods=['DELETE'])
@jwt_required()
def delete_user():
    delete_id = request.form.get('id')
    user_id = get_jwt_identity()
    if delete_id == user_id:
        return "Can't delete this user profile because you are currently logged in to it."
    for i in range(len(users)):
        if users[i]['id'] == user_id:
            if users[i]['user_type'] == 'Admin':
                if delete_id < 0 or delete_id >= global_user_id:
                    return 'Invalid user ID.'
                del users[delete_id]
                return 'Successful deletion of user profile.'
            else:
                break
    return 'You are not authorized to perform this operation.', 401

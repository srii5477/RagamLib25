from flask import Flask, redirect, session, request, jsonify, url_for, flash
from flask_jwt_extended import (
    get_jwt_identity,
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from datetime import date
from flask_bcrypt import Bcrypt, check_password_hash
from waitress import serve

app = Flask(__name__, template_folder="static")
app.secret_key = "secret123"
app.config["JWT_SECRET_KEY"] = "abc"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False


jwt = JWTManager(app)
bcrypt = Bcrypt(app)


class Membership_Type:
    REGULAR = 1
    PREMIUM = 2


class User_Type:
    USER = 1
    ADMIN = 2


global_book_id = 1
global_user_id = 1
books = [{"id": 0, "title": "The Famous Five", "author": "Enid Blyton"}]
users = [
    {
        "id": 0,
        "name": "Sridevi",
        "email": "abc@yz.in",
        "membership_type": Membership_Type.REGULAR,
        "password": "$2b$12$vXiRpeZ5I3Y2Pn1c/qguEeDYWqM1KsjzsFcJ6mdfR5boLOZUGg98e",
        "registered_date": "12312323",
        "user_type": User_Type.ADMIN,
    }
]
premium_amount = 500


@app.route("/", methods=["GET"])
def home():
    return "Welcome to RagamLib25!"


@app.route("/add-book", methods=["POST"])
@jwt_required()
def add_book():
    global global_book_id
    new_id = global_book_id
    global_book_id += 1
    title = request.form.get("title")
    if not title:
        return "Provide the title name."
    author = request.form.get("author")
    if not author:
        return "Provide the author name."
    published_year = request.form.get("published_year")
    genre = request.form.get("genre")
    available_copies = request.form.get("available_copies")
    new_book = {
        "id": new_id,
        "title": title,
        "author": author,
        "published_year": published_year,
        "genre": genre,
        "available_copies": available_copies,
    }
    books.append(new_book)
    return new_book


@app.route("/view-books", methods=["GET"])
def view_books():
    return books


@app.route("/update-book", methods=["PATCH"])
@jwt_required()
def update_book():
    update_id = request.args.get("id")
    if not update_id:
        return "Provide an id in the parameter."
    update_id = int(update_id)
    title = request.form.get("title")
    author = request.form.get("author")
    published_year = request.form.get("published_year")
    genre = request.form.get("genre")
    available_copies = request.form.get("available_copies")
    books[update_id]["title"] = title
    books[update_id]["author"] = author
    books[update_id]["published_year"] = published_year
    books[update_id]["genre"] = genre
    books[update_id]["available_copies"] = available_copies
    return books[update_id]


@app.route("/add-user", methods=["POST"])
def add_user():
    global global_user_id
    new_id = global_user_id
    global_user_id += 1
    name = request.form.get("name")
    if name == None:
        return "Please provide your name."
    email = request.form.get("email")
    membership_type = request.form.get("membership_type").lower()
    if membership_type == "regular":
        membership_type = Membership_Type.REGULAR
    if request.form.get("password") == None:
        return "Please provide a password."
    password = bcrypt.generate_password_hash(request.form.get("password")).decode(
        "utf-8"
    )
    today = date.today()
    user_type = User_Type.USER
    if membership_type == "premium":
        session["new_details"] = {
            "id": new_id,
            "name": name,
            "email": email,
            "membership_type": membership_type,
            "registered_date": today,
            "password": password,
            "user_type": user_type,
        }
        session["payment"] = request.form.get("payment")
        return redirect("/make-premium-payment")
    new_user = {
        "id": new_id,
        "name": name,
        "email": email,
        "membership_type": membership_type,
        "registered_date": today,
        "password": password,
        "user_type": user_type,
    }
    users.append(new_user)
    return new_user


# the only way to update a user_type
@app.route("/promote-to-admin", methods=["PATCH"])
@jwt_required()
def promote_to_admin():
    promote_id = request.args.get("id")
    if not promote_id:
        return "Provide an id in the parameter."
    if False:  # this request needs to be verified by another admin
        users[promote_id]["user_type"] = User_Type.ADMIN
        return "Successful promotion to admin."
    else:
        return "You are not permitted to hold admin privilege."


@app.route("/make-premium-payment", methods=["GET"])
def make_premium_payment():
    if int(session.get("payment", {})) == premium_amount:
        return redirect("/continue-add-user")
    else:
        return "Premium account creation failed!", 401


@app.route("/continue-add-user", methods=["GET"])
def continue_add_user():
    users.append(session.get("new_details", {}))
    session.get("new_details", {})["membership_type"] = Membership_Type.PREMIUM
    return session.get("new_details", {})


@app.route("/view-users", methods=["GET"])
@jwt_required()
def view_users():
    return users

@app.route('/view-book', methods=['GET'])
@jwt_required()
def view_book():
    if not request.args.get('id'):
        return 'Provide id in the parameter.'
    book_id = int(request.args.get('id'))
    if book_id < global_book_id and book_id >= 0:
        return books[book_id]
    else:
        return 'Invalid id!'


@app.route("/update-premium-payment", methods=["GET"])
@jwt_required()
def update_premium_payment():
    if int(session.get("payment", {})) == premium_amount:
        users[int(session.get("update_id", {}))][
            "membership_type"
        ] = Membership_Type.PREMIUM
        return redirect("/continue-update-user")
    else:
        return "Premium account creation failed!", 401


@app.route("/continue-update-user", methods=["GET"])
def continue_update_user():
    update_details = session.get("update_details", {})
    update_id = int(session.get("update_id", {}))
    if update_details["name"]:
        users[update_id]["name"] = update_details["name"]
    if update_details["email"]:
        users[update_id]["email"] = update_details["email"]
    return "Successful updation."


@app.route("/logout", methods=["POST"])
def logout():
    resp = jsonify({"logout": True})
    unset_jwt_cookies(resp)
    return resp, 200


@app.route("/update-user", methods=["PATCH"])
@jwt_required()
def update_user():
    update_id = request.args.get("id")
    if update_id:
        update_id = int(update_id)
    else:
        return "Provide an id in the parameter."
    user_id = int(get_jwt_identity())
    if update_id != user_id:
        return "You aren't permitted to change another user's details"
    name = request.form.get("name")
    email = request.form.get("email")
    payment = request.form.get("payment")
    if payment:
        payment = int(payment)
    membership_type = request.form.get("membership_type")
    if membership_type:
        membership_type = membership_type.lower()
        if membership_type == "premium":
            session["update_id"] = update_id
            session["payment"] = payment
            session["update_details"] = {"name": name, "email": email}
            return redirect("/update-premium-payment")
    users[update_id]["name"] = name or users[update_id]["name"]
    users[update_id]["email"] = email or users[update_id]["email"]
    users[update_id]["membership_type"] = (
        membership_type or users[update_id]["membership_type"]
    )
    return users[update_id]


@app.route("/forgot-password", methods=["PATCH"])
def update_password():
    new_password = request.form.get("password")
    if not new_password or new_password == "":
        return "Enter a valid new password."
    update_id = request.args.get("id")
    if not update_id:
        return "Provide an id in the parameter."
    update_id = int(update_id)
    hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
    users[update_id]["password"] = hashed_password
    flash(
        "Successful updation of password. You will directed to logout, after which you should login with your new password."
    )
    return redirect("/logout")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("name")
    password = request.form.get("password")
    flag = 0
    found_id = -1
    for i in range(len(users)):
        if users[i]["name"] == username:
            flag = 1
            found_id = i
            if not check_password_hash(
                users[i]["password"].encode("utf-8"), password.encode("utf-8")
            ):
                flag = 0
    if flag == 0:
        return "Incorrect credentials!", 401
    access_token = create_access_token(identity=str(found_id))
    resp = jsonify({"login": "Successful."})
    print("here")
    set_access_cookies(resp, access_token)
    return resp, 200


# protected endpoints
@app.route("/delete-book", methods=["DELETE"])
@jwt_required()
def delete_book():
    delete_id = request.args.get("id")
    if not delete_id:
        return "Provide an id in the parameter."
    delete_id = int(delete_id)
    user_id = int(get_jwt_identity())
    for i in range(len(users)):
        if users[i]["id"] == user_id:
            print(users[i]["user_type"])
            if users[i]["user_type"] == User_Type.ADMIN:
                if delete_id < 0 or delete_id >= global_book_id:
                    return "Invalid book ID."
                del books[delete_id]
                return "Successful deletion of book."
            else:
                break

    return "You are not authorized to perform this operation.", 401


@app.route("/delete-user", methods=["DELETE"])
@jwt_required()
def delete_user():
    delete_id = request.args.get("id")
    if not delete_id:
        return "Provide an id in the parameter."
    user_id = int(get_jwt_identity())
    if delete_id == user_id:
        return (
            "Can't delete this user profile because you are currently logged in to it."
        )
    for i in range(len(users)):
        if users[i]["id"] == user_id:
            if users[i]["user_type"] == User_Type.ADMIN:
                if delete_id < 0 or delete_id >= global_user_id:
                    return "Invalid user ID."
                del users[delete_id]
                return "Successful deletion of user profile."
            else:
                break
    return "You are not authorized to perform this operation.", 401

if __name__ == "__main__":
   serve(app, host='0.0.0.0', port=8000)
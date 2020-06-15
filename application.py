import os
from flask import jsonify


from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from flask import Flask, render_template, request
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
from comment import comment_detail

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")


# @app.route("/sign_in_form")
# def sign_in_form():
#     return render_template("sign_in.html")


@app.route("/sign_in",  methods=["POST"])
def sign_in():

    username = request.form.get("username")
    pwd = request.form.get("pwd")
    # print(username)
    user = db.execute("SELECT * FROM user_table WHERE username = :username AND password = :pwd",
                      {"username": username, "pwd": pwd}).fetchone()
    if user is None:
        return render_template("index.html", message="Wrong user input. Please try again")
    else:
        session["username"] = username
        session["password"] = pwd
        return render_template("search.html")


# @app.route("/sign_up_form")
# def sign_up_form():
#     return render_template("sign_up.html")


@app.route("/sign_up",  methods=["POST", "GET"])
def sign_up():
    if request.method == 'GET':
        return render_template("sign_up.html")
    elif request.method == 'POST':
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        user = db.execute("SELECT * FROM user_table WHERE username = :username ",
                          {"username": username}).fetchone()
        if user is None:
            db.execute("INSERT INTO user_table (username,password) VALUES (:username, :pwd)",
                       {"username": username, "pwd": pwd})
            db.commit()
            return render_template("index.html")
        else:
            return render_template("sign_up.html", message="Username already exists.Please try again.")


@app.route("/logout")
def logout():
    session["username"] = None
    session["password"] = None
    return render_template("index.html")


@app.route("/search", methods=["GET"])
def search():
    input = request.args.get("input")
    books = db.execute("SELECT * FROM books WHERE (isbn LIKE :isbn OR title LIKE :title OR author_name LIKE :author_name)",
                       {"isbn": '%'+input+'%', "title": '%'+input+'%', "author_name": '%'+input+'%'}).fetchall()

    # db.commit()
    # print(books)
    if len(books) == 0:
        return render_template("book.html", message="No matched result.")
    else:
        return render_template("book.html", books=books)


@app.route("/detail/<isbn>", methods=["GET", "POST"])
def detail(isbn):
    if request.method == 'GET':
        param = comment_detail(isbn)
        
        return render_template("detail.html", **param, message="No review.")

    elif request.method == 'POST':
        if 'username' in session:
            username = session['username']
            comment = request.form.get("comment")
            rate = request.form.get("rating")
            # print(isbn)
            userId = db.execute("SELECT user_id FROM user_table WHERE username = :username",
                                {"username": username}).fetchone()
            
            # print(param)
            if db.execute("SELECT *FROM comments WHERE user_id = :user_id AND isbn = :isbn",
                          {"user_id": userId[0], "isbn": isbn}).rowcount == 0:
                db.execute("INSERT INTO comments(isbn,user_id,comment_body,rating) VALUES (:isbn, :id, :comment_body, :rating)",
                           {"isbn": isbn, "id": userId[0], "comment_body": comment, "rating": rate})

                db.commit()
                param = comment_detail(isbn)
                return render_template("detail.html", **param)
            else:
                return render_template("error.html",  message="Sorry you can give review only once.")


@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):
    param = comment_detail(isbn)

    return jsonify(title=param["book"][1],
                   author=param["book"][2],
                   year=param["book"][3],
                   isbn=param["book"][0],
                   review_count=param["rating"],
                   average_score=param["avg_rating"]
                   )

# @app.route("/flights/<int:flight_id>")
# def flight(flight_id):
# """Lists details about a single flight."""

# Make sure flight exists.
# flight = db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).fetchone()
# if flight is None:
#     return render_template("error.html", message="No such flight.")
# @app.route("/")
# def index():
#     flights = db.execute("SELECT * FROM flights").fetchall()
#     return render_template("index.html", flights=flights)

# @app.route("/book", methods=["POST"])
# def book():
#     """Book a flight."""

#     # Get form information.
#     name = request.form.get("name")
#     try:
#         flight_id = int(request.form.get("flight_id"))
#     except ValueError:
#         return render_template("error.html", message="Invalid flight number.")

#     # Make sure the flight exists.
#     if db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).rowcount == 0:
#         return render_template("error.html", message="No such flight with that id.")
#     db.execute("INSERT INTO passengers (name, flight_id) VALUES (:name, :flight_id)",
#             {"name": name, "flight_id": flight_id})
#     db.commit()
#     return render_template("success.html")

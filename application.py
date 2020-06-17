import os
from flask import jsonify


from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from flask import Flask, render_template, request, redirect, url_for
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



@app.route("/sign_in",  methods=["POST"])
def sign_in():

    username = request.form.get("username")
    pwd = request.form.get("pwd")
    user = db.execute("SELECT * FROM user_table WHERE username = :username AND password = :pwd",
                      {"username": username, "pwd": pwd}).fetchone()
    if user is None:
        return render_template("index.html", message="Wrong user input. Please try again")
    else:
        session["username"] = username
        session["password"] = pwd
        return render_template("search.html")



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

    if len(books) == 0:
        return render_template("book.html", message="No matched result.")
    else:
        return render_template("book.html", books=books)


@app.route("/detail/<isbn>", methods=["GET", "POST", "PATCH"])
def detail(isbn):
    if request.method == 'GET':
        if 'username' in session:
            username = session['username']
            param = comment_detail(isbn)
            if not param["body"]:
                return render_template("detail.html", message="No review.", **param)
            else:
                return render_template("detail.html", session_username=username, **param)

    elif request.method == 'POST':
        if 'username' in session:
            username = session['username']
            comment = request.form.get("comment")
            rate = request.form.get("rating")
            userId = db.execute("SELECT user_id FROM user_table WHERE username = :username",
                                {"username": username}).fetchone()

            if db.execute("SELECT *FROM comments WHERE user_id = :user_id AND isbn = :isbn",
                          {"user_id": userId[0], "isbn": isbn}).rowcount == 0:
                db.execute("INSERT INTO comments(isbn,user_id,comment_body,rating) VALUES (:isbn, :id, :comment_body, :rating)",
                           {"isbn": isbn, "id": userId[0], "comment_body": comment, "rating": rate})

                db.commit()
                param = comment_detail(isbn)
                return render_template("detail.html", session_username=username, **param)
            else:
                return render_template("error.html",  message="Sorry you can give review only once.")



@app.route("/deletecomment/<comment_id>/<isbn>", methods=["GET"])
def deletecomment(comment_id, isbn):
    
    if 'username' in session:
        username = session['username']

        userId = db.execute("SELECT user_id FROM user_table WHERE username = :username",
                            {"username": username}).fetchone()
        print(userId)
        comment = db.execute("SELECT *FROM comments WHERE comment_id = :comment_id",
                             {"comment_id": int(comment_id)}).fetchone()
        db.commit()  
        print(comment_id)               
        print(comment)
        if comment[2] == userId[0]:
            db.execute("DELETE FROM comments WHERE comment_id = :comment_id",
                       {"comment_id": int(comment_id)})   
            db.commit()          
            return redirect(url_for('detail',isbn=isbn))
        else:
            return "You cannot remove comment"

    else:
        return "You cannot remove comment"

@app.route("/editcomment/<comment_id>/<isbn>", methods=["GET", "POST"])
def editcomment(comment_id, isbn):
    if 'username' in session:
        username = session['username']
        if request.method == 'GET':
            userId = db.execute("SELECT user_id FROM user_table WHERE username = :username",
                                {"username": username}).fetchone()
       
            comment = db.execute("SELECT *FROM comments WHERE comment_id = :comment_id",
                                {"comment_id": int(comment_id)}).fetchone()
            db.commit()                  
            
            if comment[2] == userId[0]:  
                
                param = comment_detail(isbn)
                print( param)
                return render_template("detail.html", comment_id=int(comment_id) , **param)        
                   
            else:
                return "You cannot edit the comment"
        elif request.method == 'POST':
            comment_body = request.form.get("edit")
            print(comment_body)
            db.execute("UPDATE comments SET comment_body=:comment_body WHERE comment_id = :comment_id",
                                {"comment_body": comment_body,"comment_id": int(comment_id)})
            db.commit()          
            return redirect(url_for('detail',isbn=isbn))

    else:
        return "You cannot remove comment"


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


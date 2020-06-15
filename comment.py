import os
import requests

from sqlalchemy import create_engine
from flask import Flask, render_template, request
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime


if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def comment_detail(isbn):
    key = 'mbXdObG1EplHcXiUKLzBpA'

    payload = {'key': key, 'isbns': isbn, 'format': 'json'}
    # payload1 = {'format': 'json', 'user_id': 116197367, 'isbns': isbn}
    r = requests.get(
        'https://www.goodreads.com/book/review_counts.json', params=payload)
    # r1 = requests.get(
        # 'https://www.goodreads.com/book/isbn/'+isbn, params=payload1)
    if r is None:
        return render_template("error.html",  message="Sorry no details found.")
    else:
        result = r.json()
        # result1 = r1.json()
        # print(result)
        rating = result["books"][0]["work_ratings_count"]

        avg_rating = result["books"][0]["average_rating"]

        # img= result1[]

        book = db.execute("SELECT * FROM books WHERE isbn= :isbn",
                          {"isbn": isbn}).fetchone()

        comment = db.execute("SELECT comments.comment_body,comments.comment_date,user_table.username FROM comments INNER JOIN user_table ON comments.user_id=user_table.user_id WHERE comments.isbn= :isbn",
                             {"isbn": isbn}).fetchall()

        db.commit()
        details = {"body": comment, "book": book,
                   "rating": rating, "avg_rating": avg_rating}
        return details

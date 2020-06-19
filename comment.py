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
    r = requests.get('https://www.goodreads.com/book/review_counts.json', params=payload)
    if r is None:
        return render_template("error.html",  message="Sorry no details found.")
    else:
        result = r.json()
        # print(result)
        # total rating from goodread
        total_rating = result["books"][0]["work_ratings_count"] 

        # find avg_rating from database
        sum = 0
        n=0
        rating_count = db.execute("SELECT rating FROM comments WHERE isbn = :isbn",
                                {"isbn": isbn}).fetchall()

        # print(rating_count)
        for each_rating in rating_count:
            sum += each_rating[0]
            n += 1

        goodread_sum = float(result["books"][0]["average_rating"])* total_rating
        # print(goodread_sum)
        total_sum = goodread_sum + sum
        total_number = n + total_rating
        # final avg_rating
        avg_rating =  total_sum/total_number

        # count= db.execute("SELECT COUNT( DISTINCT comment_id) FROM comments WHERE isbn = :isbn",
        #                         {"isbn": isbn}).fetchall()
        # print(count)
        # total_rating = result["books"][0]["work_ratings_count"] 

        # final total rating_count
        total_rating_count = total_rating + n 

        book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                          {"isbn": isbn}).fetchone()

        comment = db.execute("SELECT comments.comment_body,comments.comment_date,user_table.username,comments.comment_id FROM comments INNER JOIN user_table ON comments.user_id=user_table.user_id WHERE comments.isbn= :isbn",
                             {"isbn": isbn}).fetchall()

        db.commit()
        details = {"body": comment, "book": book,
                   "rating": total_rating_count, "avg_rating": avg_rating}
        return details

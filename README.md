
# Web Programming with Python and JavaScript

1. Users will be able to register and then log in using their username and password.
2. Once they log in, they will be able to search for books, leave reviews for individual books, and see the reviews made by other people.
3. Users can also edit and delete their existing comment.
4. Users will be able to query for book details programmatically via API.

   * HTTP Method : GET    
   * URL : `/api/<isbn>`

        Where `<isbn>` is the ISBN of the book
   * Sample Request: `/api/0385339097`
   * Sample output ( json format) :
         
        ```            
        {
            author: "John Grisham",

            average_score: 3.8400116157974846,

            isbn: "0385339097",

            review_count: 99864,

            title: "The Street Lawyer",

            year: 1998
        }
        ```         

# Requirments
 * Pyhton 3.6
 * pip


# How to run

 * Run ` pip3 install -r requirements.txt ` in terminal window to make sure that all of the necessary Python packages (Flask and SQLAlchemy, for instance) are installed.

 * On a Mac or on Linux, the command to set the environment variable FLASK_APP to be application.py  ` export FLASK_APP=application.py `. On Windows, the command is instead `set FLASK_APP=application.py `

 * Set the environment variable `DATABASE_URL` to be the URI of your database
 * Run ` flask run ` to start up your Flask application
 * Navigate to the URL provided by flask




    


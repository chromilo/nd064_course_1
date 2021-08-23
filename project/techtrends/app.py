from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

import sqlite3
import logging

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    Flask.dbcount += 1
    ## log line
    app.logger.info('Connection successful')

    return render_template('index.html', posts=posts)

# Define the /healthz endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    ## log line
    app.logger.info('Healthz request successful')
    return response

# Define the /metric endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    Flask.dbcount += 1
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy","db_connection_count": + Flask.dbcount, "post_count": + len(posts)}),
            status=200,
            mimetype='application/json'
    )

    ## log line
    app.logger.info('Metrics request successful')
    return response

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    Flask.dbcount += 1
    if post is None:
      ## log line
      app.logger.info('A non-existing article is accessed.')

      return render_template('404.html'), 404
    else:
      ## log line
      app.logger.info('Found article titled ' + post['title'])

      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    ## log line
    app.logger.info('About page retrieved.')

    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
            ## log line
            app.logger.info('Title is required')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            Flask.dbcount += 1

            ## log line
            app.logger.info('New article created titled' + title)
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
Flask.dbcount = 0
if __name__ == "__main__":
   logging.basicConfig(level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')

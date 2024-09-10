#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, redirect, flash, url_for, session, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from functools import wraps
from forms import *
from data import *
from datetime import timedelta
import time
import os

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
KEY = False


@app.before_request
def create_tables():
    print('''\n\nlogged out\n\n''')
    logout_user()
    session['logged_in'] = False
    app.before_request_funcs[None].remove(create_tables)


#----------------------------------------------------------------------------#
# Login.
#----------------------------------------------------------------------------#

login_manager = LoginManager()
login_manager.init_app(app)

class LoginUser(UserMixin):
    @property
    def is_admin(self):
        return True


@login_manager.user_loader
def user_loader(username):
    user = LoginUser()
    user.id = username
    return user

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def home():
    return render_template('pages/home.html')


@app.route('/about')
def about():
    return render_template('pages/about.html')


@app.route('/gallery')
def gallery():
    images = image_fetch()
    return render_template('pages/gallery.html', image_urls=images)


@app.route('/forum')
def forum():
    parents = forum_query("SELECT * FROM Parent ORDER BY Date DESC")
    return render_template('pages/forum.html', parents=parents)


@app.route('/secret')
def secret():
    global KEY
    if not KEY:
        abort(403)

    KEY = False
    return render_template('pages/secret.html')


@app.route('/trigger', methods=['GET', 'POST'])
def trigger():
    global KEY
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        abort(403)
    
    KEY = True
    return jsonify({'redirect': url_for('secret')})


#----------------------------------------------------------------------------#
# Forum Functionality
#----------------------------------------------------------------------------#


@app.route('/post/<int:post_id>')
def post(post_id):
    parent = forum_query("SELECT * FROM Parent WHERE ID = ?", (post_id,))[0]

    if not parent:
        return "Post not found", 404

    children = forum_query("SELECT ID, Message, Date, Author FROM Child WHERE ParentID = ? ORDER BY Date DESC", (post_id,))

    unapproved = [ x+tuple([False]) for x in 
                 forum_query("SELECT ID, Message, Date, Author FROM Unapproved WHERE ParentID = ? ORDER BY Date DESC", (post_id,))]

    return render_template('forms/post.html', parent=parent, children=children, unapproved=unapproved)


@app.route('/submit_post', methods=['GET', 'POST'])
def submit_post():
    if request.method == 'POST':

        title = request.form['title']
        message = request.form['message']
        author = request.form['author']
        parent_id = request.form.get('parent_id')  # None if it's a new thread
        if not author:
            author = "None"

        forum_update("INSERT INTO Unapproved (Title, Message, Date, Author, ParentID) VALUES (?, ?, datetime('now'), ?, ?)",
                    (title, message, author, parent_id))

        flash('Your post has been submitted for approval.', "success")
        return redirect(url_for('forum'))
    return render_template('forms/submit.html')


@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):

    forum_update("DELETE FROM Unapproved WHERE ID = ?", (post_id,))
    forum_update("DELETE FROM Parent WHERE ID = ?", (post_id,))
    
    flash('Post deleted successfully.', "success")
    return redirect(url_for('forum'))


@app.route('/delete_reply/<int:reply_id>', methods=['POST'])
@login_required
def delete_reply(reply_id):

    forum_update("DELETE FROM Unapproved WHERE ID = ?", (reply_id,))
    forum_update("DELETE FROM Child WHERE ID = ?", (reply_id,))
    
    flash('Reply deleted successfully.', "success")
    return redirect(request.referrer or url_for('forum'))


@app.route('/approve_posts', methods=['GET', 'POST'])
@login_required
def approve_posts():

    unapproved_posts = approve_posts_filter()
    
    return render_template('pages/approve.html', unapproved_posts=unapproved_posts)


@app.route('/approve/<int:post_id>', methods=['POST'])
@login_required
def approve(post_id):

    post = forum_query("SELECT * FROM Unapproved WHERE ID = ?", (post_id,))[0]

    if post:
        if post[5] is None:
            forum_update("INSERT INTO Parent (Title, Message, Date, Author) VALUES (?, ?, ?, ?)",
                        (post[4], post[1], post[2], post[3]))
        else:
            forum_update("INSERT INTO Child (Message, Date, Author, ParentID) VALUES (?, ?, ?, ?)",
                        (post[1], post[2], post[3], post[5]))

        forum_update("DELETE FROM Unapproved WHERE ID = ?", (post_id,))

    flash('Post approved successfully.', "success")
    return redirect(request.referrer or url_for('approve_posts'))


@app.route('/submit_reply/<int:parent_id>', methods=['POST'])
def submit_reply(parent_id):
    if request.method == 'POST':

        message = request.form['message']
        author = request.form["author"]
        if not author:
            author = "None"
        
        forum_update("INSERT INTO Unapproved (Message, Date, Author, ParentID) VALUES (?, datetime('now'), ?, ?)",
                        (message, author, parent_id))

        flash('Your reply has been submitted for approval.', "success")
        return redirect(url_for('post', post_id=parent_id))
    return redirect(url_for('forum'))







#----------------------------------------------------------------------------#
# Login / Logout
#----------------------------------------------------------------------------#


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        login_credentials = credentials()
        if form.username.data in login_credentials.keys():
            if form.password.data == login_credentials[form.username.data]:
                flash("Login Successful", "success")
                luser = LoginUser()
                luser.id = form.username.data
                if login_user(luser, remember=True):
                    session['logged_in'] = True
                    return redirect(url_for('home'))
                else: return "bad"
            else:
                flash("Incorrect Login Credentials", "error")
        else:
            flash("Unknown Username", "error")
    return render_template('forms/login.html', form=form)


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    session.pop('logged_in', None)
    flash("You Have Been Logged Out", 'info')
    return ('', 204) if request.method == 'POST' else redirect(url_for('home'))


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    session.modified = True  # Refresh session timeout
    return '', 204  # Return no content

# Error handlers ------------------------------------------------------------#

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(401)
def forbidden_error(error):
    return render_template('errors/401.html'), 401


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

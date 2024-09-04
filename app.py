#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from forms import *
from data import *
import os

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
#db.init_app(app)

#----------------------------------------------------------------------------#
# Blueprints.
#----------------------------------------------------------------------------#

# from __ import __
# app.register_blueprint(__)

#----------------------------------------------------------------------------#
# Flask_Admin.
#----------------------------------------------------------------------------#

#panel = Admin(
#    app,
#    name='Admin Control Panel',
#    template_mode='bootstrap3',
#)
#panel.add_link(MenuLink(name='Logout', category='', url='/logout'))
#panel.add_view(DefaultModelView(User, db.session, column_searchable_list=['username', 'email']))

#----------------------------------------------------------------------------#
# Login.
#----------------------------------------------------------------------------#

login_manager = LoginManager()
login_manager.init_app(app)

class LoginUser(UserMixin):
    @property
    def is_admin(self):
        return self.is_authenticated and self.id == 'admin' 


@login_manager.user_loader
def user_loader(username):
    user = LoginUser()
    user.id = username
    return user

#----------------------------------------------------------------------------#
# Controllers.
#    I suggest you create Blueprints for your routes to keep them tidy (up there),
#    but I won't to that here.
#----------------------------------------------------------------------------#

@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/forum')
def forum():
    import sqlite3
    con = sqlite3.connect('forum.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM Parent ORDER BY Date DESC")
    parents = cur.fetchall()
    con.close()

    return render_template('pages/forum.html', parents=parents)


@app.route('/post/<int:post_id>')
def post(post_id):
    import sqlite3
    con = sqlite3.connect('forum.db')
    cur = con.cursor()
    # Fetch the parent post
    cur.execute("SELECT * FROM Parent WHERE ID = ?", (post_id,))
    parent = cur.fetchone()

    if not parent:
        return "Post not found", 404

    # Fetch all replies (Child posts) associated with this Parent post
    cur.execute("SELECT * FROM Child WHERE ParentID = ? ORDER BY Date ASC", (post_id,))
    children = cur.fetchall()
    con.close()

    return render_template('pages/post.html', parent=parent, children=children)



@app.route('/submit', methods=['POST'])
def submit_post():
    
    if request.method == 'POST':
        import sqlite3
        con = sqlite3.connect('forum.db')
        cur = con.cursor()

        title = request.form['title']
        message = request.form['message']
        parent_id = request.form.get('parent_id')  # None if it's a new thread

        # Insert the post into the Unapproved table
        cur.execute("INSERT INTO Unapproved (Title, Message, Date, ParentID) VALUES (?, ?, datetime('now'), ?)",
                        (title, message, parent_id))
        con.commit()
        con.close()

        flash('Your post has been submitted for approval.')
        return redirect(url_for('forum'))
    return render_template('forms/submit.html')


@app.route('/approve_post/<int:post_id>', methods=['POST'])
def approve_post(post_id):
    
    import sqlite3
    con = sqlite3.connect('forum.db')
    cur = con.cursor()
    # Fetch the post from Unapproved table
    cur.execute("SELECT * FROM Unapproved WHERE ID = ?", (post_id,))
    post = cur.fetchone()

    if post:
        if post['ParentID'] is None:
            # If it's a Parent post, insert into Parent table
            cur.execute("INSERT INTO Parent (Title, Message, Date) VALUES (?, ?, ?)",
                           (post['Title'], post['Message'], post['Date']))
        else:
            # If it's a Child post, insert into Child table
            cur.execute("INSERT INTO Child (Message, Date, ParentID) VALUES (?, ?, ?)",
                           (post['Message'], post['Date'], post['ParentID']))
        
        # Remove the post from the Unapproved table
        cur.execute("DELETE FROM Unapproved WHERE ID = ?", (post_id,))
        con.commit()

    con.close()
    flash('Post approved successfully.')
    return redirect(url_for('approve'))




@app.route('/gallery')
def gallery():
    return render_template('pages/gallery.html', image_urls=["https://example.com/image1.jpg",
                                                             "https://example.com/image1.jpg",
                                                             "https://example.com/image1.jpg",
                                                             "https://example.com/image1.jpg",
                                                             "https://example.com/image1.jpg",
                                                             "https://example.com/image1.jpg",
                                                             "https://example.com/image1.jpg",
                                                             "https://example.com/image1.jpg",
                                                             "https://example.com/image1.jpg",
                                                             "https://example.com/image1.jpg",
                                                             "https://example.com/image1.jpg",
                                                             "https://example.com/image1.jpg"])


#@app.route('/forum/approval')
#@login_required


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


# Error handlers ------------------------------------------------------------#

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

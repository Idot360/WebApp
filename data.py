import sqlite3
import os
from flask import url_for


def credentials():
    import numpy as np
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM Credential")
    login_credentials = {x[1]: x[2] for x in cur.fetchall()}

    con.close()
    return login_credentials


def image_fetch():
    image_folder = os.path.join('static', 'img')
    images = sorted([url_for('static', filename=f'img/{filename}') 
                     for filename in os.listdir(image_folder) 
                     if filename.endswith(('.png', '.jpg', '.jpeg', '.gif'))])
    return images


#----------------------------------------------------------------------------#
# Forum Data
#----------------------------------------------------------------------------#


def forum_query(statement: str, params: tuple = "") -> list:
    con = sqlite3.connect('forum.db')
    cur = con.cursor()
    if params:
        cur.execute(statement, params)
    else:
        cur.execute(statement)
    result = cur.fetchall()
    con.close()
    return result


def forum_update(statement: str, params: tuple = "") -> None:
    con = sqlite3.connect('forum.db')
    cur = con.cursor()
    if params:
        cur.execute(statement, params)
    else:
        cur.execute(statement)
    con.commit()
    con.close()


def approve_posts_filter():
    statement = """
        SELECT Unapproved.ID, Unapproved.Message, Unapproved.Date, Unapproved.ParentID, Unapproved.Author, Unapproved.Title,
               Parent.Title, Parent.Message, Parent.Author, Parent.Date
        FROM Unapproved
        LEFT JOIN Parent ON Unapproved.ParentID = Parent.ID
        ORDER BY Unapproved.Date DESC
    """
    
    unapproved_posts_data = forum_query(statement)

    unapproved_posts = []
    for post in unapproved_posts_data:
        if post[6] is None:  
            unapproved_posts.append({
                'id': post[0],
                'message': post[1],
                'date': post[2],
                'author': post[4],
                'is_child': False,
                'title': post[5]  
            })
        else:  
            unapproved_posts.append({
                'id': post[0],
                'message': post[1],
                'date': post[2],
                'author': post[4],
                'is_child': True,
                'parent_title': post[6],
                'parent_message': post[7],
                'parent_author': post[8],
                'parent_date': post[9]
            })
    return unapproved_posts
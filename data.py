import sqlite3
import os
from flask import url_for


def credentials():
    con = sqlite3.connect('mysite/data.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM Credential")
    login_credentials = {x[1]: x[2] for x in cur.fetchall()}

    con.close()
    return login_credentials


def image_fetch():
    image_folder = os.path.join('mysite','static', 'img')
    images = sorted([url_for('static', filename=f'img/{filename}')
                     for filename in os.listdir(image_folder)
                     if filename.endswith(('.png', '.jpg', '.jpeg', '.gif'))])
    return images


print(credentials())
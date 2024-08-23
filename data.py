import sqlite3


def image_fetch():
    con = sqlite3.connect('.db')
    cur = con.cursor()
    cur.execute("SELECT url FROM images")
    urls = cur.fetchall()

    con.close()

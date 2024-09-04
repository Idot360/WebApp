import sqlite3


def credentials():
    import numpy as np
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM Credential")
    login_credentials = {x[1]: x[2] for x in cur.fetchall()}

    con.close()
    return login_credentials

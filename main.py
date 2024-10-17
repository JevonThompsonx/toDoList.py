"""
A CLI to do list application
For practicing using python flags, sqlite3 for the database
Also to be use a skeleton for a later React to do list
    w/ bunsqlite, typescript and hono backend 
"""
import argparse # for handling flags
import sqlite3 # for db
import textwrap # for wrapping epilog

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """Custom formatter that combines default values and raw description formatting."""
parser = argparse.ArgumentParser(
                    prog='To do list',
                    formatter_class=CustomFormatter,
                    description='A simple to do list cli app',
                    epilog=textwrap.dedent('''\
                    Thank you for using!
                    Check out more projects at:
                    https://github.com/JevonThompsonx?tab=repositories
                    '''),
                    )
parser.add_argument('-u','--user', type=str, required=True, dest='username',help="""
                    Username to use in finding, creating, deleting etc your personal to do list.                    If the desired username has a space in it, just wrap it in qoutes like so: 'Jack Thomas'
                    """)

args = parser.parse_args()
with sqlite3.connect('todolist.db') as conn:
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    userid INTEGER PRIMARY KEY,
    username TEXT NOT NULL
    )"""
    )
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks(
                taskid PRIMARY KEY,
                task TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (userid)
                )
                """)
    if args.username:
        cursor.execute("SELECT * FROM users WHERE username=?", (args.username,))
        usercheck = cursor.fetchone()
        if usercheck:
            print('User already exists\n')
        else:
            print("Inserting new user...\n")
            cursor.execute("""
            INSERT INTO users(
            username
            )
            VALUES(?)
            """, (args.username,))
    print("Current users:")
    cursor.execute("SELECT * FROM users")
    conn.commit()
    print(cursor.fetchall())

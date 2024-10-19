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
parser.add_argument('-l', '--list', dest='list', action='store_true', help="""
                    Command to list all tasks on to do list (requires username)
                    """)
parser.add_argument('-d', '--delete', dest='delete', help="""
                    Command to delete a task on the to do list. 
                    Will list all tasks then delete the selected id (requires username)                 
                    """)
parser.add_argument('-a', '--add', dest='add', help="""
                     Command to add a task to the to do list (requires username)
                    """)

args = parser.parse_args()
with sqlite3.connect('todolist.db') as conn:
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY
    )"""
    )
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks(
                taskid INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                username TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users (username)
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
    if args.username and args.add:
        cursor.execute("""
                       INSERT INTO tasks(task, username)
                       VALUES(?,?)
                       """,(args.add, args.username))

    elif args.username and args.list:
        cursor.execute("""
                       SELECT tasks.task, tasks.taskid FROM tasks 
                       LEFT JOIN users 
                       ON users.username=tasks.username
                       """)
        for task in cursor.fetchall():
            print(f"{task[1]}.{task[0]}")
    conn.commit()

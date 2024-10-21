"""
A CLI to do list application
For practicing using python flags, sqlite3 for the database
Also to be use a skeleton for a later React to do list
    w/ bunsqlite, typescript and hono backend 
"""
import argparse # for handling flags
import sqlite3 # for db
import textwrap # for wrapping epilog
import sys
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
parser.add_argument('-u','--user', type=str, dest='username',help="""
                    Username to use in finding, creating, deleting etc your personal to do list. 
                    If the desired username has a space in it, just wrap it in qoutes like so: 'Jack Thomas'
                    """)
parser.add_argument('-l', '--list', dest='list', action='store_true', help="""
                    Command to list all tasks on to do list (requires username)
                    """)
parser.add_argument('-d', '--delete', dest='delete', action='store_true',help="""
                    Command to delete a task on the to do list. 
                    Will list all tasks then delete the selected id (requires username)                 
                    """)
parser.add_argument('-a', '--add', dest='add', help="""
                     Command to add a task to the to do list (requires username)
                    """)
parser.add_argument("-mc", "--mark_complete", dest="mark_complete", help="""
                    Used to mark tasks as complete or incomplete. Will present a list of tasks to be marked by their id 
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
                status TEXT check(status IN ("complete", "incomplete")) NOT NULL DEFAULT "incomplete",
                FOREIGN KEY (username) REFERENCES users (username)
                )
                """)
    if args.username:
        cursor.execute("SELECT * FROM users WHERE username=?", (args.username,))
        usercheck = cursor.fetchone()
        username = args.username
        if usercheck:
            print(f'User {username} already exists\n')
        else:
            print(f"Inserting new user {username}...\n")
            cursor.execute("""
            INSERT INTO users(
            username
            )
            VALUES(?)
            """, (args.username,))
            print("User inserted")
        def list_tasks():
            """
            List all tasks recieved from cursor numbered
             """
            cursor.execute("""
                            SELECT users.username , tasks.task , tasks.status 
                            FROM tasks 
                            INNER JOIN users 
                            ON users.username=tasks.username
                            WHERE users.username=?
                         """, (username,))
            task_num = 0
            for individual in cursor.fetchall():
                task_num = task_num+1
                match individual:
                    case individual if individual[2] == 'incomplete':
                        print(f"{task_num}. {individual[1]} []")
                    case individual if individual[2] == 'complete':
                        print(f"{task_num}. {individual[1]} [x]")
        def list_tasks_with_task_id():
            """
            List all tasks attached to current user 
            with their task id            """
            cursor.execute("""
                               SELECT tasks.taskid, tasks.task
                               FROM tasks 
                               INNER JOIN users 
                               ON users.username = tasks.username 
                               WHERE users.username = ? 
                               ORDER BY tasks.taskid
                        """, (username,) )
            if len(result := cursor.fetchall()) > 0:
                for i in result:
                    print(f"{i[0]}. {i[1]}")
                return True
            print("Task list empty")
            return False
        match args:
            case args if args.add:
                cursor.execute("""
                                SELECT users.username, tasks.task FROM tasks
                                INNER JOIN users
                                ON users.username=tasks.username
                                WHERE users.username=?
                            """, (args.username,))
                currentTasks = []
                for task in cursor.fetchall():
                    currentTasks.append(task[1])
                newTask = args.add
                if newTask in currentTasks:
                    print("Task is already exists in your list\n")
                else:
                    print("Adding new task...")
                    cursor.execute("""
                                   INSERT INTO tasks(task, username)
                                   VALUES(?,?)
                                   """,(newTask, username))
                print("Current list: ")
                list_tasks()
            case args if args.list:
                list_tasks()
            case args if args.delete:
                print("""
All tasks are given a unique id 
To delete your task, give me it's ID from the list below:\n
                      """)
                DELETING = True
                while DELETING is True:
                    deleteTuple = ('done', 'quit', 'exit')
                    if list_tasks_with_task_id() is True:
                        print("\nYou can delete as many from the list as needed\n")
                        print(f"Enter any of the following when complete: {deleteTuple}\n")
                        selected_id = input("Select a task by id: ")
                        if selected_id in deleteTuple:
                            print("\nDone deletin!")
                            break
                        try:
                            if (deleted_task_id := int(selected_id)):
                                if deleted_task_id < 0:
                                    print("Id cannot be a negative number")
                                try:
                                    cursor.execute("""
                                                   DELETE FROM tasks
                                                   WHERE taskid=? AND username=?
                                                   """,(deleted_task_id,username))
                                    if cursor.rowcount:
                                        print("Task deleted")
                                    else:
                                        print("Not a valid task id, try again\n")
                                except sqlite3.Error:
                                    print("Not a num")
                            else:
                                raise ValueError("Not a number")
                        except ValueError:
                            print("Selected id needs to be a number & greater than 0")
                    else:
                        print('\nNothing to delete')
                        DELETING =False
            #case args if args.mark_complete:
                #insert list tasks by their id

   # if args.list:
    #    cursor.execute("""
     #                   SELECT username FROM users
      #                  """)
      #  print("Current users:")
       # for u in cursor.fetchall():
        #    print(u[0])
    conn.commit()

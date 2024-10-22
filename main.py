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
    exit_tuple = ('done', 'quit', 'exit')
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
    def check_user(username):
        """
        Checks if the given user is currently in the database
        """
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        usercheck = cursor.fetchone()
        if usercheck:
            print(f'Welcome back {username}\n')
        else:
            print(f"Inserting new user {username}...\n")
            cursor.execute("""
            INSERT INTO users(
            username
            )
            VALUES(?)
            """, (username,))
            print("User inserted")
            conn.commit()
    def list_tasks(username):
        """
        List all tasks recieved from cursor numbered
        """
        cursor.execute("""
                        SELECT users.username , tasks.task , tasks.status, tasks.taskid
                        FROM tasks 
                        INNER JOIN users 
                        ON users.username=tasks.username
                        WHERE users.username=?
                        """, (username,))
        if len(result := cursor.fetchall()) > 0:
            for individual in result:
                match individual:
                    case individual if individual[2] == 'incomplete':
                        print(f"{individual[3]}. {individual[1]} []")
                    case individual if individual[2] == 'complete':
                        print(f"{individual[3]}. {individual[1]} [x]")
        else:
            print("No tasks to list")
    def add_task(username, interactive_task = ''):
        """
        Adds a task to the given user's list
        """
        cursor.execute("""
                        SELECT users.username, tasks.task FROM tasks
                        INNER JOIN users
                        ON users.username=tasks.username
                        WHERE users.username=?
                        """, (username,))
        current_tasks = []
        for task in cursor.fetchall():
            current_tasks.append(task[1])

        if interactive_task != '':
            new_task = interactive_task
        else:
            new_task = args.add
        if new_task in current_tasks:
            print("Task is already exists in your list\n")
        else:
            print(f"Adding {new_task} to list...")
            cursor.execute("""
                            INSERT INTO tasks(task, username)
                            VALUES(?,?)
                            """,(new_task, username))
            conn.commit()
        print("Current list: ")
        list_tasks(username)
    def delete_task(username):
        """
        Promps user to delete tasks by starting a delete loop until exited
        """
        print("""
        All tasks are given a unique id 
        To delete your task, give me it's ID from the list below:\n
            """)
        deleting = True
        while deleting is True:
            list_tasks(username)
            print("\nYou can delete as many from the list as needed\n")
            print(f"Enter any of the following when complete: {exit_tuple}\n")
            selected_id = input("Select a task by id: ")
            if selected_id in exit_tuple:
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
                            conn.commit()
                        else:
                            print("Not a valid task id, try again\n")
                    except sqlite3.Error:
                        print("Not a num")
                else:
                    raise ValueError("Not a number")
            except ValueError:
                print("Selected id needs to be a number & greater than 0")
        else:
            print('\nNothing to delete. Exiting...')
            deleting =False

    if flag_user:= args.username:
        check_user(flag_user)
        match args:
            case args if args.add:
                add_task(flag_user)
            case args if args.list:
                list_tasks(flag_user)
            case args if args.delete:
                delete_task(flag_user)
            #case args if args.mark_complete:
                #insert list tasks by their id
    else:
        INTERACTIVE = True
        while INTERACTIVE is True:
            print("""
Hello! Welcome to my interactive to do list!\n 
You are currently in the interactive mode of this app
To run commands from the command line in a noninteractive way, 
Please check the help menu by running this application with the help flag:
`python main.py -h` or `python main.py --help`
""")
            print("""
If you'd like to continue in interactive mode,
feel free to do so. We'll need a username to continue
                  """)
            check_user(interactive_user := input("Please enter your username: "))


            MODE_SELECT = True
            while MODE_SELECT is True:
                mode_options = ('add_task', 'delete_task', 'list_tasks')
                mode_alts = ('delete', 'add', 'list')
                mode = input(f"""
You can exit at any time by typing any of the following:
{exit_tuple}

Here are you interactive options:
{mode_options}

Please select a mode to continue: """).lower()
                if mode in mode_options or mode in mode_alts:
                    match mode:
                        case 'add_task' | 'add':
                            INTERACTIVE_ADDING = True
                            while INTERACTIVE_ADDING is True:
                                task_to_add_interactively = input("New task: ")
                                if task_to_add_interactively.lower() in exit_tuple:
                                    INTERACTIVE_ADDING = False
                                    break
                                add_task(interactive_user,interactive_task = task_to_add_interactively)
                        case 'delete_task' | 'delete':
                            delete_task(interactive_user)
                        case 'list_tasks' | 'list':
                            list_tasks(interactive_user)
                elif mode in exit_tuple:
                    print('exiting...')
                    INTERACTIVE = False
                    MODE_SELECT = False
                else:
                    print("Sorry not a valid mode in this app")

   # if args.list:
    #    cursor.execute("""
     #                   SELECT username FROM users
      #                  """)
      #  print("Current users:")
       # for u in cursor.fetchall():
        #    print(u[0])

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

                    This project also has an interactive mode 
                    To use, run the main.py script 

                    Thank you for checking this project out!
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
parser.add_argument("-mc", "--mark_complete", dest="mark_complete", action='store_true', help="""
                    Used to mark tasks as complete or incomplete. Will present a list of tasks to be marked by their id (requires username)
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
    def print_border(border:str):
        """
        A simple func that prints a border for the given values
        """
        print(border * 25)
    def print_star():
        """
        prints stars w/ print_border
        """
        print_border('*')
    def print_line():
        """
        Prints a straight line w/ print border
        """
        print_border('-')
    def check_user(username):
        """
        Checks if the given user is currently in the database
        """
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        usercheck = cursor.fetchone()
        if usercheck:
            print(f'Welcome back {username}\n')
        else:
            print_line()
            print(f"Inserting new user {username}...\n")
            print_line()
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

        Returns True for a valid listing and false for an empty listing
        """
        cursor.execute("""
                        SELECT users.username , tasks.task , tasks.status, tasks.taskid
                        FROM tasks 
                        INNER JOIN users 
                        ON users.username=tasks.username
                        WHERE users.username=?
                        """, (username,))
        if len(result := cursor.fetchall()) > 0:
            print_line()
            for individual in result:
                match individual:
                    case individual if individual[2] == 'incomplete':
                        print(f"{individual[3]}. {individual[1]} []")
                    case individual if individual[2] == 'complete':
                        print(f"{individual[3]}. {individual[1]} [x]")
            print_line()
            return True
        print_star()
        print("No tasks to list")
        print_star()
        return False
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
            print_star()
            print("Task is already exists in your list\n")
            print_star()
        else:
            print_line()
            print(f"Adding {new_task} to list...")
            cursor.execute("""
                            INSERT INTO tasks(task, username)
                            VALUES(?,?)
                            """,(new_task, username))
            print_line()
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
            if list_tasks(username) is False:
                print('Exiting...')
                deleting = False
                break
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
                        print('*' * 25)
                    try:
                        cursor.execute("""
                                    DELETE FROM tasks
                                    WHERE taskid=? AND username=?
                                    """,(deleted_task_id,username))
                        if cursor.rowcount:
                            print('-' * 25)
                            print("Task deleted")
                            conn.commit()
                        else:
                            print_star()
                            print("Not a valid task id, try again")
                            print_star()
                    except sqlite3.Error:
                        print("Not a num")
                else:
                    raise ValueError("Not a number")
            except ValueError:
                print("Selected id needs to be a number & greater than 0")
        else:
            print('\nNothing to delete. Exiting...')
            print_star()
            deleting =False
    def mark_complete(username):
        """
        Interactively prompts user to mark tasks off as complete of incomplete
        """
        marking = True
        while marking is True:
            print("""
Let's get a list of tasks to mark as complete...

Note: 
You can exit at any time by typing any of the following: 
{exit_tuple}
""")
            if list_tasks(username) is False:
                print("Exiting...")
                marking = False
                break
            task_to_mark = input('Select the id of the task to mark complete/incomplete: ').lower()
            if task_to_mark.strip() in exit_tuple:
                marking = False
                break
            try:
                task_to_mark = int(task_to_mark)
                cursor.execute("""
                               SELECT tasks.status
                               FROM tasks
                               INNER JOIN users
                               ON tasks.username = users.username
                               WHERE tasks.taskid= ? AND users.username = ?

                               """, (task_to_mark, username,)
                               )
                if (result:= cursor.fetchall())==0:
                    raise KeyError
                current_status = result[0]
                current_status = current_status[0]
                if current_status == 'incomplete':
                    cursor.execute("""
                                    UPDATE tasks
                                    SET status = 'complete'
                                    WHERE taskid = ? AND username IN (
                                    SELECT username FROM users WHERE username = ?
                                    )
                               """, (task_to_mark, username,)
                                   )

                elif current_status == 'complete':
                    cursor.execute("""
                                    UPDATE tasks
                                    SET status = 'incomplete'
                                    WHERE taskid=? AND username IN (
                                    SELECT username FROM users WHERE username = ?
                                    )
                               """, (task_to_mark, username,)
                                   )
                print('Marking...')
                conn.commit()
            except (KeyError, IndexError):
                print_star()
                print('Not a listed task id. Try again...')
                print_star()
            except ValueError:
                print('Invalid value')
            except sqlite3.Error as e:
                print('Woah buddy')
                print(e)
    if flag_user:= args.username:
        check_user(flag_user)
        match args:
            case args if args.add:
                add_task(flag_user)
            case args if args.list:
                list_tasks(flag_user)
            case args if args.delete:
                delete_task(flag_user)
            case args if args.mark_complete:
                mark_complete(flag_user)
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

Note: Usernames will be lowercased
                  """)
            check_user(interactive_user := input("Please enter your username: ").lower())


            MODE_SELECT = True
            while MODE_SELECT is True:
                mode_options = ('add_task', 'delete_task', 'list_tasks', 'mark_complete')
                mode_alts = ('add', 'list', 'delete', 'mark')
                mode = input(f"""
You can exit at any time by typing any of the following:
{sorted(exit_tuple)}

Here are you interactive options:
{sorted(mode_options)}
    or 
{sorted(mode_alts)}

Please select a mode to continue: """).lower()
                if mode in mode_options or mode in mode_alts:
                    match mode:
                        case 'add_task' | 'add':
                            INTERACTIVE_ADDING = True
                            while INTERACTIVE_ADDING is True:
                                task_to_add_interactively = input("New task: ").lower()
                                if task_to_add_interactively in exit_tuple:
                                    INTERACTIVE_ADDING = False
                                    break
                                add_task(interactive_user,interactive_task = task_to_add_interactively)
                        case 'delete_task' | 'delete':
                            delete_task(interactive_user)
                        case 'list_tasks' | 'list':
                            list_tasks(interactive_user)
                        case 'mark_complete' | 'mark':
                            mark_complete(interactive_user)
                elif mode in exit_tuple:
                    print('exiting...')
                    INTERACTIVE = False
                    MODE_SELECT = False
                else:
                    print_star()
                    print("Sorry not a valid mode in this app")
                    print_star()
    cursor.execute("PRAGMA OPTIMIZE")

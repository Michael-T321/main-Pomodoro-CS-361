import threading
import time
import os

def clear_screen():
    """Clears the terminal screen for Windows, Linux, and macOS."""
    # Check the operating system name
    if os.name == 'nt':
        # Command for Windows
        _ = os.system('cls')
    else:
        # Command for Linux/macOS (posix is the name for non-Windows systems)
        _ = os.system('clear')

# Call the function to clear the screen


def do_something():
    print("Sleeping 1 second...")
    time.sleep(1)
    print("Done Sleeping...")
    

t1 = threading.Thread(target=do_something)
t2 = threading.Thread(target=do_something)

t1.start()
t2.start()

clear_screen()
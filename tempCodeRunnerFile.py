import time
from art import *
import sys
from contextlib import redirect_stdout
import io
import threading
import os
# ==============================================================================================

# | Welcome to the Pomodoro Timer! This Pomodoro Timer helps you focus using timed   |
# | work and break sessions.       
# | Enter 'Start' to begin the timer:     
# 

def clear_screen():
    # Check the operating system name
    if os.name == 'nt':
        # Command for Windows
        _ = os.system('cls')
    else:
        # Command for Linux/macOS (posix is the name for non-Windows systems)
        _ = os.system('clear')

# Call the function to clear the screen


def replace_previous_block(lines):
    if lines <= 0:
        return

    # Go to top of previous block
    print(f"\033[{lines}A", end="")

    # Clear each line, moving DOWN through the block
    for i in range(lines):
        print("\033[2K\r", end="")          # clear whole line + carriage return
        if i < lines - 1:
            print("\033[1B", end="")       # move down 1 line

    # Go back up to the top of the cleared block
    if lines > 1:
        print(f"\033[{lines - 1}A", end="")


def count_printed_lines(func):
    # create an in-memory text buffer
    captured_output = io.StringIO()

    #redirect stdout to the buffer while the function runs
    with redirect_stdout(captured_output):
        func()

    #get the entire value printed to the buffer as a string
    output_string = captured_output.getvalue()

    # Close the buffer 
    captured_output.close()
    
    # Handle the case where the function prints nothing (output_string is empty)
    if output_string == "":
        return 0
        
    return len(output_string.splitlines())

line = line(length=94, height=1, char="=")
lineWidth = 94

def welcomeScreen():
    welcome = text2art(" Pomodoro Timer ")

    print(line)
    print(welcome.rstrip('\n'))
    print(line)

    print("| Welcome to the Pomodoro Timer! This Pomodoro Timer helps you focus using timed             |")
    print("| work and break sessions.                                                                   |")
    print("|                                                                                            |")
    print("| 1. Start Work Session                                                                      |")
    print("| 2. Settings / Help / About                                                                 |")
    print("| 3. Quit                                                                                    |")
    print(line)

line_count = count_printed_lines(welcomeScreen)

welcomeScreen()

def workSession(time):

    workTitle = text2art(" Work Session ")

    if workTitle.endswith("\n"):
        workTitle = workTitle[:-1]

    centerTitle = "\n".join(line.center(lineWidth) for line in workTitle.split("\n"))
    print(line)
    print(centerTitle)
    print(line)
    print(f"| Enter the corresponding number to select!".ljust(lineWidth-1) + "|")
    print(f"|".ljust(lineWidth - 1) + "|")
    print(f"| State: RUNNING".ljust(lineWidth-1) + "|")  # ADD THIS LINE
   # print(f"| Time Remaining: {time}".ljust(lineWidth-1) + "|")
    print(f"|".ljust(lineWidth - 1) + "|")
    print(f"| Session x of x".ljust(lineWidth - 1) + "|")
    print(f"| 1. Pause".ljust(lineWidth - 1) + "|")
    print(f"| 2. Home".ljust(lineWidth - 1) + "|")
    print(f"| 3. Help ".ljust(lineWidth - 1) + "|")
    print(line)

 
homeInput = int(input("Enter adjacent number of your choosing: "))
clear_screen()
homeCommands = [1, 2, 3]


class Session():
    
    def __init__(self, session_type, total_duration, status):
        self.session_type = session_type
        self.total_duration = int(total_duration) * 60 
        self.status = status

        self.stop_event = threading.Event()
        self.pause_event = threading.Event()

        self.remaining_seconds = self.total_duration

    def info(self):
        return '{} {} {}'.format(self.session_type, self.total_duration, 
                                     self.status)
    
    # def start(self):
    #     while self.remaining_seconds > 0 and not self.stop_event.is_set():
    #         if self.pause_event.is_set():
    #             time.sleep(0.1)
    #             continue

    #         formatted = self.format_time(self.remaining_seconds)
    #         timer_line = (f"| Time Remaining: {formatted}".ljust(lineWidth-1) + "|")
    #         status_line = (f"| State: {self.status}".ljust(lineWidth-1) + "|")
            
    #         # Move up 8 lines to timer
    #         print(f"\033[7A\r", end="")
    #         # Clear line and print timer
    #         print("\033[2K", end="")
    #         print(timer_line, end="")
            
    #         # Move up 1 more line to status
    #         print(f"\033[1A\r", end="")
    #         # Clear line and print status
    #         print("\033[2K", end="")
    #         print(status_line, end="", flush=True)
            
    #         # Move back down to starting position (9 lines down)
    #         print(f"\033[8B\r", end="", flush=True)

    #         time.sleep(1)
    #         self.remaining_seconds -= 1

    def start(self):
        while self.remaining_seconds > 0 and not self.stop_event.is_set():
            if self.pause_event.is_set():
                time.sleep(0.1)
                continue

            formatted = self.format_time(self.remaining_seconds)
            timer_line = (f"| Time Remaining: {formatted}".ljust(lineWidth-1) + "|")
            status_line = (f"| State: {self.status}".ljust(lineWidth-1) + "|")
            
            # Move up 7 lines to status line
            print(f"\033[7A\r", end="")
            # Clear and print status (with end="" to stay on same line)
            print("\033[2K", end="")
            print(status_line, end="")
            
            # Move down 1 line to the empty line after status
            print(f"\033[1B\r", end="")
            # Clear and print timer
            print("\033[2K", end="")
            print(timer_line, end="")
            
            # Move back down to starting position (6 lines down from timer)
            print(f"\033[6B\r", end="", flush=True)

            time.sleep(1)
            self.remaining_seconds -= 1

    def stop(self):
        self.stop_event.set()

    def toggle_pause(self):
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.status = "RUNNING"
        else:
            self.pause_event.set()
            self.status = "PAUSED"

    def format_time(self, remaining_seconds):
        seconds = int(remaining_seconds % 60)
        minutes = int(remaining_seconds / 60) % 60
        hours = int(remaining_seconds / 3600)
        return (f"{hours:02}:{minutes:02}:{seconds:02}")


session_work = Session('WORK', '50', 'RUNNING')
session_break = Session('BREAK', '10', 'READY')

#print(session_work.info())
#print(session_break.info())
clear_screen()
while homeInput not in homeCommands:
    print("That command does not exist. Please try again!")
    homeInput = int(input("Enter adjacent number of your choosing: "))
    line_count += 2 
else:
    if homeInput == homeCommands[0]:
        workSession(session_work.format_time(session_work.total_duration))
        print()  # Add a blank line for the command prompt
        
        # start timer in background thread
        timer_thread = threading.Thread(
            target=session_work.start,
            daemon=True
        )
        timer_thread.start()
        
        # Give the timer thread a moment to start
        time.sleep(0.1)

        while timer_thread.is_alive():
            # Print prompt on the dedicated command line
            print("\033[1A\r\033[2K", end="")  # Move up 1, go to start, clear line
            print("Command: ", end="", flush=True)
            
            cmd = input().strip()
            
            if cmd == "1":
                session_work.toggle_pause()

            elif cmd == "2":
                session_work.stop()
                break

            elif cmd == "3":
                print("\033[1A\r\033[2K", end="")
                print("Help: 1=pause/resume, 2=home, 3=help", flush=True)
                time.sleep(2)

            else:
                if cmd:
                    print("\033[1A\r\033[2K", end="")
                    print("Invalid command. Try 1, 2, or 3.", flush=True)
                    time.sleep(1.5)

    elif homeInput == homeCommands[1]:
        print("Settings / About / Help")
    else:
        print("Are you sure you want to quit?")
        



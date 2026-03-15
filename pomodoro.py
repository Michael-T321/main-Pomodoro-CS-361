import time
import threading
import os
import tkinter as tk
from tkinter import messagebox

import requests
from art import *
from playsound3 import playsound

AUTH_URL = "http://localhost:4000"
CRUD_URL = "http://localhost:5001"
QUOTES_URL = "http://localhost:6001"
NOTIFICATION_URL = "http://localhost:6002"
LOGGER_URL ="http://localhost:6003"
USERNAME = "pomodoro_user"
PASSWORD = "pomodoro123"

# sound files
sound_files = {
    "chime": "sounds/chime.mp3",
    "doorbell": "sounds/electric-doorbell.mp3",
    "bell": "sounds/hotel-bell-ding.mp3",
    "alarm clock": "sounds/digital-alarm-clock-buzzer.mp3",
}
# play sounds
def play_alert(token):
    alert_sound = get_alert(token)
    file_path = sound_files.get(alert_sound)
    if file_path:
        threading.Thread(target=playsound, args=(file_path,), daemon=True).start()

# get logs
def get_log(token):
    response = requests.get(f"{LOGGER_URL}/log", headers={"Authorization": token})
    data = response.json()
    return data.get("log")

# create a new log
def log_sessions(token, session_type, duration):
    response = requests.post(f"{LOGGER_URL}/log", headers={"Authorization": token}, json={"session_type": session_type, "duration": duration})
    data = response.json()
    return data.get("entry")

# delete logs
def clear_log(token):
    response = requests.delete(f"{LOGGER_URL}/log", headers={"Authorization": token})
    data = response.json()
    return data.get("message")

# get all sounds
def get_sound():
    response = requests.get(f"{NOTIFICATION_URL}/sound")
    data = response.json()
    return data.get("sounds")

# get users sound
def get_alert(token):
    response = requests.get(f"{NOTIFICATION_URL}/alert", headers={"Authorization": token})
    alert = response.json()
    return alert.get("sound")

# change user setting sound
def change_sound(token, sound):
    response = requests.put(f"{NOTIFICATION_URL}/alert/sound", headers={"Authorization": token}, json={"sound": sound})
    data = response.json()
    return data.get("sound")

# get quot
def get_quote():
    response = requests.get(f"{QUOTES_URL}/quote")
    data = response.json()
    return data.get("quote")

# Get quote status (ON/OFF)
def get_quote_status(token):
    response = requests.get(f"{QUOTES_URL}/quote/settings", headers={"Authorization": token})
    data = response.json()
    return data.get("quote")

# change quote status 
def change_quote_status(token, status):
    response = requests.put(f"{QUOTES_URL}/quote/settings", headers={"Authorization": token}, json={"quote": status})
    data = response.json()
    return data.get("quote")

# check login
def login():
    # try to register first, ignore if already exists
    requests.post(f"{AUTH_URL}/register", json={"username": USERNAME, "password": PASSWORD})
    
    # Login and get token
    response = requests.post(f"{AUTH_URL}/login", json={"username": USERNAME, "password": PASSWORD})
    data = response.json()
    return data.get("token")

# get settings
def load_settings(token):
    response = requests.get(f"{CRUD_URL}/items?type=settings", headers={"Authorization": token})
    items = response.json()
    if items:
        data = items[0]["data"]
        if "session_nums" not in data:
            data["session_nums"] = 2
        return data  
    return {"work_duration": 50, "break_duration": 10, "session_nums": 2}  # defaults

# savve settings
def save_settings(token, work_duration, break_duration, session_nums):
    # First check if settings already exist
    response = requests.get(f"{CRUD_URL}/items?type=settings", headers={"Authorization": token})
    items = response.json()
    
    if items:
        # Update existing settings
        item_id = items[0]["_id"]
        requests.put(f"{CRUD_URL}/items/{item_id}", 
                    headers={"Authorization": token},
                    json={"type": "settings", "data": 
                          {"work_duration": work_duration, "break_duration": break_duration, "session_nums": session_nums}})
    else:
        # Create new settings
        requests.post(f"{CRUD_URL}/items",
                     headers={"Authorization": token},
                     json={"type": "settings", "data": 
                           {"work_duration": work_duration, "break_duration": break_duration, "session_nums": session_nums}})


# show timer settings screen
def showTimerSettings(token, settings):
    clear_screen()
    settingsTitle = text2art(" Settings ")
    
    if settingsTitle.endswith("\n"):
        settingsTitle = settingsTitle[:-1]
    
    centerSettingsTitle = "\n".join(line.center(lineWidth) for line in settingsTitle.split("\n"))
    
    print(line)
    print(centerSettingsTitle)
    print(line)
    print(f"|                                                                                            |")
    print(f"| Current Work Duration: {settings['work_duration']} minutes".ljust(lineWidth-1) + "|")
    print(f"| Current Break Duration: {settings['break_duration']} minutes".ljust(lineWidth-1) + "|")
    print(f"| Current Number of Sessions: {settings['session_nums']} session/s".ljust(lineWidth-1) + "|")
    print(f"|                                                                                            |")
    print(line)
    
    # get new work duration
    while True:
        try:
            work_input = input("Enter new work duration (in minutes): ")
            new_work_duration = int(work_input)
            if new_work_duration <= 0:
                print("Please enter a positive number!")
                continue
            break
        except ValueError:
            print("Invalid input! Please enter a number.")
    
    # Get new break duration
    while True:
        try:
            break_input = input("Enter new break duration (in minutes): ")
            new_break_duration = int(break_input)
            if new_break_duration <= 0:
                print("Please enter a positive number!")
                continue
            break
        except ValueError:
            print("Invalid input! Please enter a number.")
    
    # get new number of sessions
    while True:
        try:
            session_input = input("Enter new number of sessions you would like: ")
            new_session_amount = int(session_input)
            if new_session_amount <= 0:
                print("Please enter a positive number!")
                continue
            break
        except ValueError:
            print("Invalid input! Please enter a number.")
    
    # show what they're about to save
    clear_screen()
    print(line)
    print("| CONFIRM CHANGES".ljust(lineWidth-1) + "|")
    print(line)
    print(f"| Old Work Duration: {settings['work_duration']} → New: {new_work_duration}".ljust(lineWidth-1) + "|")
    print(f"| Old Break Duration: {settings['break_duration']} → New: {new_break_duration}".ljust(lineWidth-1) + "|")
    print(f"| Old Number of Sessions: {settings['session_nums']} → New: {new_session_amount}".ljust(lineWidth) + "|")
    print(line)
    
    confirm = Confirmations("Confirm", "askyesno", 
                            f"Change work to {new_work_duration} min, break to {new_break_duration} min and the number of sessions to {new_session_amount}?")
    
    if confirm.window():
        save_settings(token, new_work_duration, new_break_duration, new_session_amount)
        print("Settings saved!")
        time.sleep(1.5)
    else:
        print("Settings not saved.")
        time.sleep(1.5)

# notificaiton setting screen
def showNotificationSettings(token):
    clear_screen()
    current_sound = get_alert(token)
    available_sounds = get_sound()
    notifications = text2art(" Notifications ")
    if notifications.endswith("\n"):
        notifications = notifications[:-1]
    centerNotifications = "\n".join(line.center(lineWidth) for line in notifications.split("\n"))

    print(line)
    print(centerNotifications)
    print(line)
    print(f"| Enter the corresponding number to select!".ljust(lineWidth-1) + "|")
    print(f"|".ljust(lineWidth-1) + "|")
    print(f"| Current Notification Sound: {current_sound}".ljust(lineWidth-1) + "|")
    print(f"|".ljust(lineWidth-1) + "|")
    print(f"| Available Sounds:".ljust(lineWidth-1) + "|")
        
    for i, sound in enumerate(available_sounds, 1):
        print(f"| {i}. {sound}".ljust(lineWidth-1) + "|")
        
    print(line)
        
    choice = input("Pick a number: ")
    index = int(choice) - 1
        
    if 0 <= index < len(available_sounds):
        new_sound = available_sounds[index]
        change_sound(token, new_sound)
        print(f"Sound changed to {new_sound}!")
        time.sleep(.5)

# Quote setting screen
def showQuoteSettings(token):
    clear_screen()
    current_status = get_quote_status(token)
    quoteSettings = text2art(" Quote Settings ")
    if quoteSettings.endswith("\n"):
        quoteSettings = quoteSettings[:-1]
    centerQuoteSettings = "\n".join(line.center(lineWidth) for line in quoteSettings.split("\n"))
    print(line)
    print(centerQuoteSettings)
    print(line)
    print(f"| Enter the corresponding number to select!".ljust(lineWidth-1) + "|")
    print(f"|".ljust(lineWidth-1) + "|")
    print(f"| Current Quote Status: {current_status}".ljust(lineWidth-1) + "|")
    print(f"|".ljust(lineWidth-1) + "|")
    print(f"| Commands: ".ljust(lineWidth-1) + "|")
    print(f"| 1 → Toggle".ljust(lineWidth-1) + "|")
    print(f"| 2 → Keep Current".ljust(lineWidth-1) + "|")
    print(line)
    quoteChoice = input("Choose a number: ")
    if quoteChoice == "1":
        if current_status == "ON":
            new_status = "OFF"
        else:
            new_status = "ON"
        change_quote_status(token, new_status)
        print(f"Quotes are now: {new_status}")
        time.sleep(.5)

# User logs screen
def showLogs(token):
    clear_screen()
    logs = get_log(token)
    
    logsTitle = text2art(" Session Logs ")
    if logsTitle.endswith("\n"):
        logsTitle = logsTitle[:-1]
    centerLogsTitle = "\n".join(line.center(lineWidth) for line in logsTitle.split("\n"))
    
    print(line)
    print(centerLogsTitle)
    print(line)
    if not logs:
        print(f"| No sessions logged yet.".ljust(lineWidth-1) + "|")
    else:
        for i, entry in enumerate(logs, 1):
            print(f"| {i}. {entry['session_type']} — {entry['duration']} min — {entry['date']}".ljust(lineWidth-1) + "|")
    
    print(line)
    choice = input("Press ENTER to continue, or 'c' to clear logs: ")
    if choice.lower() == "c":
        clear_log(token)
        print("Logs cleared!")
        time.sleep(1)

# clear terminal
def clear_screen():
    # Check the operating system name
    if os.name == 'nt':
        # for Windows
        _ = os.system('cls')
    else:
        #  Linux/macOS
        _ = os.system('clear')

line = line(length=94, height=1, char="=")
lineWidth = 94

# help screen
def showHelp():
    help = text2art(" Help ")
    if help.endswith("\n"):
        help = help[:-1]
    centerHelp= "\n".join(line.center(lineWidth) for line in help.split("\n"))
    clear_screen()
    print(line)
    print(centerHelp.rstrip('\n'))
    print(line)
    print("|                                                                                            |")
    print("| Before you start, here is exactly what will happen:                                        |")
    print("|                                                                                            |")
    print("|  Step 1: You will be taken to the Work Session screen.                                     |")
    print("|          The timer will begin counting down from x minutes automatically.                  |")
    print("|                                                                                            |")
    print("|  Step 2: While the timer runs, you can:                                                    |")
    print("|          - Enter '1' or 'p'  → Pause the timer (you will be asked to confirm)              |")
    print("|          - Enter '2' or '?'  → Open Help screen                                            |")
    print("|          - Enter '3' or 'h'  → Return to Home   (you will be asked to confirm)             |")
    print("|                                                                                            |")
    print("|  Step 3: If you pause, the timer freezes. Enter '1' or 'p' again to resume.                |")
    print("|                                                                                            |")
    print("|  Step 4: When the timer reaches 00:00, your session ends automatically                     |")
    print("|          and you will be returned to the home screen or the break screen.                  |")
    print("|                                                                                            |")
    print("|  Step 5: While the break screen timer runs you can:                                        |")
    print("|          - Enter '1' or 'p'  → Pause the timer (you will be asked to confirm)              |")
    print("|          - Enter '2' or '?'  → Open Help screen                                            |")
    print("|          - Enter '3' or 'sk' → Skip Break")
    print("|          - Enter '3' or 'h'  → Return to Home   (you will be asked to confirm)             |")
    print("|                                                                                            |")
    print("|  NOTE: Going Home mid-session will end your current session.                               |")
    print("|        You will receive a confirmation warning before this happens.                        |")
    print("|                                                                                            |")
    print(line)
    input("Press ENTER when you are ready to begin your session...")

# welcome screen
def welcomeScreen():
    clear_screen()
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

# work session screen 
def workSession(timeStr, current_session, total_sessions):
    clear_screen()
    workTitle = text2art(" Work Session ")
    if workTitle.endswith("\n"):
        workTitle = workTitle[:-1]
    centerTitle = "\n".join(line.center(lineWidth) for line in workTitle.split("\n"))
    print(line)
    print(centerTitle)
    print(line)
    print(f"| Enter the corresponding number to select!".ljust(lineWidth-1) + "|")
    print(f"|".ljust(lineWidth - 1) + "|")
    print(f"| State: RUNNING".ljust(lineWidth-1) + "|")
    print(f"| Time Remaining: {timeStr}".ljust(lineWidth-1) + "|")
    print(f"| Session {current_session} of {total_sessions}".ljust(lineWidth - 1) + "|")
    print(f"|".ljust(lineWidth - 1) + "|")
    print(f"| Commands: ".ljust(lineWidth -1) + "|")
    print(f"| 1 or 'p' → Pause".ljust(lineWidth - 1) + "|")
    print(f"| 2 or '?' → Help ".ljust(lineWidth - 1) + "|")
    print(f"| 3 or 'h' → Home".ljust(lineWidth - 1) + "|")
    print(line)

# pause screen
def pauseSession(timeStr, current_session, total_sessions, status="PAUSED"):
    clear_screen()
    pauseTitle = text2art(" Paused ")

    if pauseTitle.endswith("\n"):
        pauseTitle = pauseTitle[:-1]

    centerPauseTitle = "\n".join(line.center(lineWidth) for line in pauseTitle.split("\n"))
    print(line)
    print(centerPauseTitle)
    print(line)
    print(f"| Enter the corresponding number to select!".ljust(lineWidth-1) + "|")
    print(f"|".ljust(lineWidth - 1) + "|")
    print(f"| State: {status}".ljust(lineWidth-1) + "|") 
    print(f"| Time Remaining: {timeStr}".ljust(lineWidth-1) + "|")
    print(f"| Session {current_session} of {total_sessions}".ljust(lineWidth - 1) + "|")
    print(f"|".ljust(lineWidth - 1) + "|")
    print(f"| Commands: ".ljust(lineWidth -1) + "|")
    print(f"| 1 or 'p' → Resume".ljust(lineWidth - 1) + "|")
    print(f"| 2 or '?' → Help ".ljust(lineWidth - 1) + "|")
    print(f"| 3 or 'h' → Home".ljust(lineWidth - 1) + "|")
    print(line)

# break screen 
def breakSession (timeStr, current_session, total_sessions, quote):
    clear_screen()
    breakTitle = text2art(" Break ")

    if breakTitle.endswith("\n"):
        breakTitle = breakTitle[:-1]  

    centerbreakTitle = "\n".join(line.center(lineWidth) for line in breakTitle.split("\n"))
    centerQuote = "\n".join(line.center(lineWidth) for line in quote.split("\n"))
    print(line)
    print(centerbreakTitle)
    if quote:
        print(line)
        print(f"{centerQuote}")
    print(line)
    print(f"| Enter the corresponding number to select!".ljust(lineWidth-1) + "|")
    print(f"|".ljust(lineWidth - 1) + "|")
    print(f"| State: BREAK".ljust(lineWidth-1) + "|") 
    print(f"| Time Remaining: {timeStr}".ljust(lineWidth-1) + "|")
    print(f"| Session {current_session} of {total_sessions}".ljust(lineWidth - 1) + "|")
    print(f"|".ljust(lineWidth - 1) + "|")
    print(f"| Commands: ".ljust(lineWidth -1) + "|")
    print(f"| 1 or 'p'  → Pause Break".ljust(lineWidth - 1) + "|")
    print(f"| 2 or '?'  → Help ".ljust(lineWidth - 1) + "|")
    print(f"| 3 or 'sk' → Skip Break".ljust(lineWidth - 1) + "|")
    print(f"| 4 or 'h'  → Home".ljust(lineWidth - 1) + "|")
    print(line)

# main settings screen
def settingsHelpAbout(settings):
    clear_screen()

    settingsInfo = text2art(" Settings/Info ")

    if settingsInfo.endswith("\n"):
        settingsInfo = settingsInfo[:-1]

    centerSettingsInfo = "\n".join(line.center(lineWidth) for line in settingsInfo.split("\n"))
    print(line)
    print(centerSettingsInfo)
    print(line)
    print(f"| Enter the corresponding number to select!".ljust(lineWidth-1) + "|")
    print(f"|".ljust(lineWidth - 1) + "|")
    print(f"| Commands:".ljust(lineWidth - 1) + "|")
    print(f"| '1' or 's' → Timer Settings".ljust(lineWidth - 1) + "|")
    print(f"| '2' or 'n' → Change Notification Sounds".ljust(lineWidth - 1) + "|")
    print(f"| '3' or 'q' → Quotes ON/OFF".ljust(lineWidth - 1) + "|")
    print(f"| '4' or '?' → Help".ljust(lineWidth - 1) + "|")
    print(f"| '5' or 'a' → About".ljust(lineWidth - 1) + "|")   
    print(f"| '6' or 'l' → User Logs".ljust(lineWidth - 1) + "|")    
    print(f"| '7' or 'h' → Return to Home".ljust(lineWidth - 1) + "|")    
    print(line)
    settingsInput = input("Enter the corresponding number to execute the action: ")
    return settingsInput

# show about screen 
def showAbout(): # same as other help screen without pausing timer
    clear_screen()
    aboutTitle = text2art(" About ")
    if aboutTitle.endswith("\n"):
        aboutTitle = aboutTitle[:-1]
    centerAboutTitle = "\n".join(line.center(lineWidth) for line in aboutTitle.split("\n"))
    
    print(line)
    print(centerAboutTitle)
    print(line)
    print("|                                                                                        |")
    print("| WHAT IS THE POMODORO TECHNIQUE?                                                        |")
    print("|   The Pomodoro Technique breaks your work into focused intervals (usually 25-50 min)   |")
    print("|   followed by short breaks. This helps improve focus and reduce mental fatigue.        |")
    print("|                                                                                        |")
    print("| CONTROLS (unless otherwise stated):                                                    |")
    print("|   Pause / Resume  →  Enter '1'  OR  Enter 'p'                                          |")
    print("|   Open this Help  →  Enter '2'  OR  Enter '?'  (timer pauses while help is open)       |")
    print("|   Go to Home      →  Enter '3'  OR  Enter 'h'  (will warn you before ending session)   |")
    print("|                                                                                        |")
    print("| SETTINGS MENU:                                                                         |")
    print("|   You can customize your notification sound, toggle motivational quotes on/off,        |")
    print("|   and view your session logs from the Settings menu.                                   |")
    print("|                                                                                        |")
    print("| TIPS:                                                                                  |")
    print("|   - Use the step-by-step guide (shown before starting) to learn the full flow.         |")
    print("|   - If you go home by accident, you will always see a confirmation popup first.        |")
    print("|   - The timer auto-pauses while this help screen is open — no time is lost.            |")
    print("|                                                                                        |")
    print(line)
    input("| Press ENTER to return to Settings menu...                                             ")

# help screen
def showHelpScreen(session, session_num, total_sessions):
    
    was_paused = session.pause_event.is_set()
    if not was_paused:
        session.pause_event.set()  # pause the countdown while reading help

    helpTitle = text2art(" Help ")

    if helpTitle.endswith("\n"):
        helpTitle = helpTitle[:-1]

    centerHelpTitle = "\n".join(line.center(lineWidth) for line in helpTitle.split("\n"))

    clear_screen()
    print(line)
    print(centerHelpTitle)
    print(line)
    print("|                                                                                        |")
    print("| WHAT IS THE POMODORO TECHNIQUE?                                                        |")
    print("|   The Pomodoro Technique breaks your work into focused intervals (usually 25-50 min)   |")
    print("|   followed by short breaks. This helps improve focus and reduce mental fatigue.        |")
    print("|                                                                                        |")
    print("| CONTROLS (two ways to perform each action):                                            |")
    print("|   Pause / Resume  →  Enter '1'  OR  Enter 'p'                                          |")
    print("|   Open this Help  →  Enter '2'  OR  Enter '?'  (timer pauses while help is open)       |")
    print("|   Go to Home      →  Enter '3'  OR  Enter 'h'  (will warn you before ending session)   |")
    print("|                                                                                        |")
    print("| SETTINGS MENU:                                                                         |")
    print("|   You can customize your notification sound, toggle motivational quotes on/off,        |")
    print("|   and view your session logs from the Settings menu.                                   |")
    print("|                                                                                        |")
    print("| TIPS:                                                                                  |")
    print("|   - Use the step-by-step guide (shown before starting) to learn the full flow.         |")
    print("|   - If you go home by accident, you will always see a confirmation popup first.        |")
    print("|   - The timer auto-pauses while this help screen is open — no time is lost.            |")
    print("|                                                                                        |")
    print(line)
    input("| Press ENTER to close Help and return... ")

    # Resume timer only if it wasn't paused before help was opened
    if session:
        if not was_paused:
            session.pause_event.clear()

# times up screen - after work session
def timesUpScreen(timeStr, current_session, total_sessions):
    clear_screen()
    play_alert(token)

    timesUp = text2art(" Times Up! ")

    if timesUp.endswith("\n"):
        timesUp = timesUp[:-1]  

    centerTimesUpTitle = "\n".join(line.center(lineWidth) for line in timesUp.split("\n"))
    print(line)
    print(centerTimesUpTitle)
    print(line)
    print(f"| Press ENTER to start the break...".ljust(lineWidth-1) + "|")

# shwos screen after break
def breakOverScreen(timeStr, current_session, total_sessions):
    clear_screen()
    play_alert(token)
    breaksOver = text2art(" Break is over! ")

    if breaksOver.endswith("\n"):
        breaksOver = breaksOver[:-1]  

    centerBreaksOver= "\n".join(line.center(lineWidth) for line in breaksOver.split("\n"))
    print(line)
    print(centerBreaksOver)
    print(line)
    print(f"| Press ENTER to start the next work session...".ljust(lineWidth-1) + "|")

# confirmation class           
class Confirmations():

    def __init__(self, tk_title, tk_type, message):
        self.tk_title = tk_title
        self.tk_type = tk_type
        self.message = message

    def window(self):

        root = tk.Tk()
        root.title("Confirm")
        root.geometry("1x1+600+500") # make main window small, move window close to center screen
        root.attributes('-topmost', True)  # bring to front
        root.update()

        method = getattr(messagebox, self.tk_type)
        result = method(self.tk_title, self.message, parent=root)
        
        root.destroy()
        return result
# session class, 
class Session():
    
    def __init__(self, session_type, total_duration, status, on_complete=None, line_offset=9):
        self.session_type = session_type
        self.total_duration = int(total_duration) * 60 
        self.status = status
        self.on_complete = on_complete
        self.line_offset = line_offset

        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.completion_event = threading.Event()
        self.print_lock = threading.Lock()  # "printing in progress" lock

        self.remaining_seconds = self.total_duration

    def info(self):
        return '{} {} {}'.format(self.session_type, self.total_duration, 
                                     self.status)


    def start(self):
        while self.remaining_seconds > 0 and not self.stop_event.is_set():
            if self.pause_event.is_set():
                time.sleep(0.5)
                continue

            time.sleep(1)
            self.remaining_seconds -= 1

            formatted = self.format_time(self.remaining_seconds)
            timer_line = (f"| Time Remaining: {formatted}".ljust(lineWidth-1) + "|")
            status_line = (f"| State: {self.status}".ljust(lineWidth-1) + "|")

            if self.pause_event.is_set():
                continue
            
            # Acquire lock before printing 
            with self.print_lock:
                print(f"\033[{self.line_offset}A\r\033[2K", end="")
                print(status_line)
                print("\r\033[2K", end="")
                print(timer_line, end="", flush=True)
                print(f"\033[{self.line_offset - 1}B", end="", flush=True)
            # lock automatically released here

        if not self.stop_event.is_set():
            self.completion_event.set() 
            if self.on_complete:
                with self.print_lock:
                    self.on_complete()

    def stop(self):
        self.stop_event.set()

    def toggle_pause(self):
        if self.pause_event.is_set():
            self.pause_event.clear()
            if self.session_type == "BREAK":
                self.status = "BREAK"
            else:
                self.status = "RUNNING"
        else:
            self.pause_event.set()
            if self.session_type == "BREAK":
                self.status  = "PAUSED BREAK"
            else:
                self.status = "PAUSED"

    def format_time(self, remaining_seconds):
        seconds = int(remaining_seconds % 60)
        minutes = int(remaining_seconds / 60) % 60
        hours = int(remaining_seconds / 3600)
        return (f"{hours:02}:{minutes:02}:{seconds:02}")
    
# pauses timer
def handlePauseCommand(session, session_num, total_sessions, session_type="WORK", quote=""):
    if not session.pause_event.is_set():  # currently running
        if confirm_pause.window():
            session.toggle_pause()
            with session.print_lock:
                clear_screen()
                pauseSession(session.format_time(session.remaining_seconds), session_num, total_sessions)
    else:
        if confirm_unpause.window():
            session.toggle_pause()
            with session.print_lock:
                clear_screen()
                if session_type == "WORK":
                    workSession(session.format_time(session.remaining_seconds), session_num, total_sessions)
                else:
                    breakSession(session.format_time(session.remaining_seconds), session_num, total_sessions, quote)


confirm_pause = Confirmations("Confirm", "askyesno", "Are you sure you want to pause the timer?")
confirm_unpause = Confirmations("Confirm", "askyesno", "Are you sure you want to unpause the timer?")
confirm_home = Confirmations("Confirm", "askyesno", "Are you sure you want to return Home?\n\nWARNING: This will end your current session and all progress will be lost.")
cmd_invalid = Confirmations("Input Invalid", "showerror", "That command does not exist. Please try again!")
confirm_quit = Confirmations("Confirm", "askyesno", "Are you sure you want to quit?")


token = login()
settings = load_settings(token)


while True:
    clear_screen()
    welcomeScreen()

    homeInput = (input("Enter the corresponding number to execute the action: "))
    homeCommands = ["1", "2", "3"]

    while homeInput not in homeCommands:
        if cmd_invalid.window():
            homeInput = (input("Enter the corresponding number to execute the action: "))
    else:

        if homeInput == homeCommands[0]:

            session_num = 1
            total_sessions = settings["session_nums"]

            while session_num <= total_sessions:
                # Creates a freash session object each time, without if the user returns to home and tries to start it again,
                # wont work properly
                session_work = Session('WORK', str(settings["work_duration"]), 'RUNNING',
                                       on_complete=lambda: timesUpScreen("00:00:00", session_num, total_sessions))
                session_break = Session('BREAK', str(settings["break_duration"]), 'BREAK',
                                        on_complete = lambda: breakOverScreen("00:00:00", session_num, total_sessions), line_offset=10)

                # work session
                clear_screen()
                if session_num == 1:
                    showHelp()

                clear_screen() 
                workSession(session_work.format_time(session_work.total_duration), session_num, total_sessions)
                
                # start timer in background thread
                timer_thread = threading.Thread(
                    target=session_work.start,
                    daemon=True
                )
                timer_thread.start()
                # Give the timer thread a moment to start
                time.sleep(1.1)

                while timer_thread.is_alive():
                    # Check if timer naturally completed
                    if session_work.completion_event.is_set():
                        break  # Exit immediately without waiting for input

                    print("\r\033[2K", end="")
                    print("Enter the corresponding number to execute the action: ", end="", flush=True)
                    
                    cmd = input().strip().lower()
                    print("\033[1A\r\033[2K", end="", flush=True)  # Move up 1 to cancel Enter's newline, then clear
                    print("\r\033[2K", end="")

                    if cmd in ("1", "p"):
                        handlePauseCommand(session_work, session_num, total_sessions, "WORK") 
                        clear_screen()
                        # redraw with session numbe
                        with session_work.print_lock:
                            if session_work.pause_event.is_set():
                                pauseSession(session_work.format_time(session_work.remaining_seconds), session_num, total_sessions)
                            else:
                                workSession(session_work.format_time(session_work.remaining_seconds), session_num, total_sessions)
                    elif cmd in ("2", "?"):
                        clear_screen()
                        showHelpScreen(session_work, session_num, total_sessions)
                        clear_screen()
                        # redraw with session numbe
                        with session_work.print_lock:
                            if session_work.pause_event.is_set():
                                pauseSession(session_work.format_time(session_work.remaining_seconds), session_num, total_sessions)
                            else:
                                workSession(session_work.format_time(session_work.remaining_seconds), session_num, total_sessions)
                    elif cmd in ("3", "h"):
                        if confirm_home.window():
                            session_work.stop()
                            clear_screen()
                            print("Returning to home screen...")
                            time.sleep(1)
                            break
                    else:
                        if cmd:
                            cmd_invalid.window()
                    
                # check if user quit mid-session
                if session_work.stop_event.is_set():
                    break

                # Break session (unless it's the last session)
                if session_num < total_sessions:
                    skip_break = False
                    log_sessions(token, "WORK", settings["work_duration"])
                    clear_screen()
                    quote_status = get_quote_status(token)
                    if quote_status == "ON":
                        quote = get_quote()
                    else:
                        quote = ""
                    offset = 12 if quote else 10
                    session_break = Session('BREAK', str(settings["break_duration"]), 'BREAK',
                            on_complete=lambda: breakOverScreen("00:00:00", session_num, total_sessions),
                            line_offset=offset)
                    breakSession(session_break.format_time(session_break.remaining_seconds), session_num, total_sessions, quote)
                    
                    timer_thread = threading.Thread(
                        target=session_break.start,
                        daemon=True
                    )
                    timer_thread.start()
                    time.sleep(1.1)
                    
                    while timer_thread.is_alive():
                    # Check if timer naturally completed
                        if session_break.completion_event.is_set():
                            break  # Exit immediately without waiting for input

                        print("\r\033[2K", end="")
                        print("Enter the corresponding number to execute the action: ", end="", flush=True)
                        
                        cmd = input().strip().lower()
                        print("\033[1A\r\033[2K", end="", flush=True)  # Move up 1 to cancel Enter's newline, then clear
                        print("\r\033[2K", end="")

                        if cmd in ("1", "p"):
                            handlePauseCommand(session_break, session_num, total_sessions, "BREAK", quote)
                            # redraw with session numbe
                            with session_break.print_lock:
                                if session_break.pause_event.is_set():
                                    pauseSession(session_break.format_time(session_break.remaining_seconds), session_num, total_sessions, session_break.status)
                                else:
                                    breakSession(session_break.format_time(session_break.remaining_seconds), session_num, total_sessions, quote)
                        elif cmd in ("2", "?"):
                            clear_screen()
                            showHelpScreen(session_break, session_num, total_sessions)
                            # redraw with session numbe
                            with session_break.print_lock:
                                if session_break.pause_event.is_set():
                                    pauseSession(session_break.format_time(session_break.remaining_seconds), session_num, total_sessions, session_break.status)
                                else:
                                    breakSession(session_break.format_time(session_break.remaining_seconds), session_num, total_sessions, quote)
                        elif cmd in ("3", "sk"):
                            skip_break = True
                            session_break.stop()
                            clear_screen()
                            print("Skipping break...")
                            time.sleep(1)
                            break
                        elif cmd in ("4", "h"):
                            if confirm_home.window():
                                session_break.stop()
                                clear_screen()
                                print("Returning to home screen...")
                                time.sleep(1)
                                break
                        else:
                            if cmd:
                                cmd_invalid.window()
                            time.sleep(0.5)
                if session_break.stop_event.is_set() and not skip_break:
                    break
                session_num += 1
            if not session_work.stop_event.is_set():
                log_sessions(token, "WORK", settings["work_duration"])
            clear_screen()
            print(line)
            print("| All Sessions Complete! ".ljust(lineWidth - 1) + "|")
            print(line)
            input("Press Enter to return to home...")
            showLogs(token)

        elif homeInput == homeCommands[1]:
            clear_screen()
            settingsInput = settingsHelpAbout(settings)
            while settingsInput not in ("7", "h"):
                if settingsInput in ("1", "s"):
                    showTimerSettings(token, settings)
                    settings = load_settings(token)
                elif settingsInput in ("2", "n"):
                    clear_screen()
                    showNotificationSettings(token)
                elif settingsInput in ("3", "q"):
                    clear_screen()
                    showQuoteSettings(token)
                elif settingsInput in ("4", "?"):
                    clear_screen()
                    showHelp()
                elif settingsInput in ("5", "a"):
                    clear_screen()
                    showAbout()
                elif settingsInput in ("6", "l"):
                    clear_screen()
                    showLogs(token)
                settingsInput = settingsHelpAbout(settings)

                
            session_work = Session('WORK', str(settings["work_duration"]), 'RUNNING')
            session_break = Session('BREAK', str(settings["break_duration"]), 'BREAK')


        elif homeInput == "3":
            if confirm_quit.window():
                break
            
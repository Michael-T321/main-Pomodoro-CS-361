import threading
import time

def do_something():
    print("Sleeping 1 second...")
    time.sleep(1)
    print("Done Sleeping...")
    

t1 = threading.Thread(target=do_something)
t2 = threading.Thread(target=do_something)

t1.start()
t2.start()
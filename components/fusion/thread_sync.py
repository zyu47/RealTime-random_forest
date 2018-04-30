import Queue
import threading

# Setup a FIFO queue for sharing received data across threads
synced_msgs = Queue.Queue()

remote_events = Queue.Queue()

remote_connected = threading.Event()

gui_events = Queue.Queue()

gui_connected = threading.Event()

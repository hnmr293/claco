from queue import Queue, Empty as QueueEmpty
import time


class MessageQueue:
    def __init__(self, maxsize=1):
        self._q = Queue(maxsize=maxsize)
        self._closed = False

    def post(self, message):
        self._q.put(message)

    def receive(self):
        while True:
            try:
                return self._q.get_nowait()
            except QueueEmpty:
                time.sleep(0.05)

    def try_receive(self):
        try:
            return self._q.get_nowait()
        except QueueEmpty:
            return None

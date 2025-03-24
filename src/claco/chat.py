from queue import Queue, Empty as QueueEmpty
import time

from claco.sender import Sender
from claco.receiver import UDPReceiver
from claco.config import IP_ADDR, PORT, SENDER_PATH


class MessageQueue:
    def __init__(self):
        self._q = Queue(maxsize=1)
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


class ClaudeSender(Sender):
    def __init__(
        self,
        exe_path,
        sink_prompt="返事は Sink ツールを使用して書き出してください。Sink ツールは一文ごとに区切って呼び出してください。すべての文章を Sink ツールで書き出し終わったら、最後に <exit> と書き出してください。",
    ):
        super().__init__(exe_path)
        self.sink_prompt = sink_prompt

    def send(self, target, message, raw=False):
        message = message.splitlines()

        for i, line in enumerate(message):
            h, e = super().send(target, line.strip(), raw=False)
            if not h:
                print(f"[ERROR] Failed to send message: {e}")
                return False, e
            if i < len(message) - 1:
                h, e = super().send(target, "+{ENTER}", raw=True)
                if not h:
                    print(f"[ERROR] Failed to send message: {e}")
                    return False, e

        h, e = super().send(target, "+{ENTER}+{ENTER}" + self.sink_prompt + "{ENTER}", raw=True)
        if not h:
            print(f"[ERROR] Failed to send message: {e}")
            return False, e

        return True, None


def main():
    target = "Claude"
    messages = MessageQueue()
    sender = ClaudeSender(SENDER_PATH)

    with UDPReceiver(IP_ADDR, PORT) as receiver:

        def post(message, address, timestamp):
            messages.post(message)

        receiver.register_callback(post)

        while True:
            try:
                print(">", end=" ")
                message = input()

                # post
                h, e = sender.send(target, message)
                if not h:
                    continue

                # receive
                message = messages.receive()
                print(message)
            except KeyboardInterrupt:
                print("Ctrl+C pressed. closing...")
                break


if __name__ == "__main__":
    main()

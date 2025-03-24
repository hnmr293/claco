from claco.sender import Sender
from claco.receiver import UDPReceiver
from claco.config import IP_ADDR, PORT, SENDER_PATH
from claco.msg import MessageQueue


class ClaudeMessageQueue(MessageQueue):
    def __init__(self, maxsize=1, exit_tag="<exit>"):
        super().__init__(maxsize)
        self.exit_tag = exit_tag

    def receive_all(self):
        while True:
            msg = self.receive()
            if msg.strip() == self.exit_tag:
                break
            yield msg


class ClaudeSender(Sender):
    def __init__(
        self,
        exe_path,
        sink_prompt='返事は Sink ツールを使用して書き出してください。Sink ツールは一文ごとに区切って呼び出してください。段落の区切りでは "</>" とだけ書き出してください。すべての文章を Sink ツールで書き出し終わったら、最後に Sink ツールで <exit> とだけ書き出してください。',
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
    messages = ClaudeMessageQueue(maxsize=8)
    sender = ClaudeSender(SENDER_PATH)

    with UDPReceiver(IP_ADDR, PORT) as receiver:

        def post(message, address, timestamp):
            messages.post(message)

        receiver.register_callback(post)

        while True:
            try:
                print(">", end=" ", flush=True)
                message = input()

                # post
                h, e = sender.send(target, message)
                if not h:
                    continue

                # receive
                for message in messages.receive_all():
                    if message.strip() == "</>":
                        print(flush=True)
                        continue
                    print(message, end=" ", flush=True)
                print(flush=True)
            except KeyboardInterrupt:
                print("Ctrl+C pressed. closing...")
                break


if __name__ == "__main__":
    main()

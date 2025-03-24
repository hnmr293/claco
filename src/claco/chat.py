from claco.receiver import UDPReceiver
from claco.config import CLACO_UDP_ADDR, CLACO_UDP_PORT, CLACO_SENDER_PATH
from claco.queue.claude import ClaudeMessageQueue
from claco.sender.claude import ClaudeSender


def main():
    target = "Claude"
    messages = ClaudeMessageQueue(maxsize=8)
    sender = ClaudeSender(CLACO_SENDER_PATH)

    with UDPReceiver(CLACO_UDP_ADDR, CLACO_UDP_PORT) as receiver:

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

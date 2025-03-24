from claco.comm import create_communicator
from claco.config import CLACO_UDP_ADDR, CLACO_UDP_PORT, CLACO_SENDER_PATH


def main():
    TARGET = "Claude"

    with create_communicator(
        TARGET,
        CLACO_SENDER_PATH,
        CLACO_UDP_ADDR,
        CLACO_UDP_PORT,
    ) as comm:
        while True:
            try:
                print(">", end=" ", flush=True)
                message = input()

                # comm.communicate(message):
                #   1. comm.send(message)
                #   2. comm.receive()

                for message in comm.communicate(message):
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

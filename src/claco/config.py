import os
from dotenv import load_dotenv

load_dotenv(override=True)

CLACO_UDP_ADDR = os.getenv("IP_ADDR")
CLACO_UDP_PORT = int(os.getenv("PORT"))

CLACO_SENDER_PATH = os.getenv("SENDER_PATH")

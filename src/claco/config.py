import os
from dotenv import load_dotenv

load_dotenv()

CLACO_UDP_ADDR = os.getenv("CLACO_UDP_ADDR")
CLACO_UDP_PORT = int(os.getenv("CLACO_UDP_PORT"))
CLACO_SENDER_PATH = os.getenv("CLACO_SENDER_PATH")

import os
from dotenv import load_dotenv

load_dotenv(override=True)

CLACO_IP_ADDR = os.getenv("IP_ADDR")
CLACO_PORT = int(os.getenv("PORT"))

CLACO_SENDER_PATH = os.getenv("SENDER_PATH")

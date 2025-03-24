import os
from dotenv import load_dotenv

load_dotenv(override=True)

IP_ADDR = os.getenv("IP_ADDR")
PORT = int(os.getenv("PORT"))

SENDER_PATH = os.getenv("SENDER_PATH")

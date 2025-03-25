# server.py
import os
import sys
import socket
import datetime
import traceback

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv


load_dotenv()
CLACO_UDP_ADDR = os.getenv("CLACO_UDP_ADDR")
CLACO_UDP_PORT = os.getenv("CLACO_UDP_PORT")

if CLACO_UDP_ADDR is None:
    raise ValueError("CLACO_UDP_ADDR is not set")

if CLACO_UDP_PORT is None:
    raise ValueError("CLACO_UDP_PORT is not set")


# Create an MCP server
mcp = FastMCP("Sink")


@mcp.tool()
def sink(message: str) -> None:
    print(f"[Sink] serving: {CLACO_UDP_ADDR}:{CLACO_UDP_PORT}", file=sys.stderr)

    # UDP ソケット作成
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # メッセージをエンコードして送信
    try:
        msg = message.encode("utf-8")
        print(f"[Sink] sending: {message}", file=sys.stderr)
        sock.sendto(msg, (CLACO_UDP_ADDR, int(CLACO_UDP_PORT)))
        print(f"[Sink] completed", file=sys.stderr)
    except Exception as e:
        error_message = f"failed to send message: {e}"
        print(f"[Sink] {error_message}", file=sys.stderr)
        traceback.print_exception(e, file=sys.stderr)

        # 例外をログファイルに記録
        log_directory = "logs"
        os.makedirs(log_directory, exist_ok=True)
        log_file_path = os.path.join(log_directory, "sink_error.log")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp}] {error_message}\n")
            log_file.write(f"Message content: {message}\n")
            log_file.write(f"{traceback.format_exc()}\n")
            log_file.write("-" * 50 + "\n")
    finally:
        sock.close()

# server.py
import os
import socket
import datetime
import os
import traceback
from mcp.server.fastmcp import FastMCP
from clako.config import IP_ADDR, PORT


# Create an MCP server
mcp = FastMCP("Sink")


# ローカルホスト（マシン内）のアドレスとポートを指定


# Add an addition tool
@mcp.tool()
def sink(message: str) -> None:
    # UDP ソケット作成
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # メッセージをエンコードして送信
    try:
        sock.sendto(message.encode("utf-8"), (IP_ADDR, PORT))
    except Exception as e:
        error_message = f"Failed to send message: {e}"
        # print(error_message)

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

"""
UDPメッセージ受信サーバ
UDP経由でメッセージを受信し、登録されたコールバック関数で処理します。
"""

import socket
import datetime
import time
import threading
from typing import Callable, List, Any, Optional, Tuple


class UDPReceiver:
    """
    UDPメッセージを受信し、登録されたコールバック関数で処理するクラス
    コンテキストマネージャー（with文）とスレッドでの実行をサポート
    """

    def __init__(self, ip: str, port: int, buffer_size: int = 4096):
        """
        UDPレシーバーの初期化

        Args:
            ip: 受信するIPアドレス
            port: 受信するポート
            buffer_size: 受信バッファサイズ
        """
        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size
        self.callbacks: List[Callable[[str, Tuple, datetime.datetime], Any]] = []
        self.running = False
        self.sock: Optional[socket.socket] = None
        self.receiver_thread: Optional[threading.Thread] = None

    def register_callback(self, callback: Callable[[str, Tuple, datetime.datetime], Any]) -> None:
        """
        メッセージを受信した時に呼び出されるコールバック関数を登録する

        Args:
            callback: 呼び出される関数。引数は (message, address, timestamp) の形式
        """
        self.callbacks.append(callback)

    def _receive_loop(self):
        """
        メッセージ受信ループ - 別スレッドで実行される
        """
        try:
            # ソケットをアドレスとポートにバインド
            self.sock.bind((self.ip, self.port))

            # メインループ
            while self.running:
                try:
                    # データを受信
                    data, address = self.sock.recvfrom(self.buffer_size)

                    # 受信時刻
                    timestamp = datetime.datetime.now()

                    # データをデコード
                    try:
                        message = data.decode("utf-8")
                    except UnicodeDecodeError:
                        logger.exception(f"Failed to decode message: {data}")
                        message = str(data)[2:-1]  # デコード失敗時はバイト列をそのまま文字列として扱う

                    # 登録されたすべてのコールバック関数を呼び出す
                    for callback in self.callbacks:
                        try:
                            callback(message, address, timestamp)
                        except Exception as e:
                            print(f"コールバック実行エラー: {e}")

                except socket.timeout:
                    # タイムアウトは正常、ループを継続
                    continue
                except Exception as e:
                    if self.running:  # 停止処理中でなければエラーを表示
                        print(f"受信エラー: {e}")
                        time.sleep(0.1)  # 少し待機

        except Exception as e:
            if self.running:  # 停止処理中でなければエラーを表示
                print(f"Error: {e}")

    def start(self, threaded: bool = True):
        """
        UDPメッセージ受信サーバを起動する

        Args:
            threaded: 別スレッドで受信ループを実行するかどうか
        """
        # 既に実行中の場合は何もしない
        if self.running:
            print("Receiver is already running.")
            return

        # UDPソケットの作成
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # ソケットの再利用を有効化
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # タイムアウトを設定して、定期的にループをチェックできるようにする
        self.sock.settimeout(0.5)

        print(f"Starting UDP receiver on {self.ip}:{self.port}")
        print("Press Ctrl+C to exit.")

        # 実行フラグをセット
        self.running = True

        if threaded:
            # 別スレッドで受信ループを開始
            self.receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receiver_thread.start()
        else:
            # 同じスレッドで受信ループを実行（以前の動作）
            self._receive_loop()
            self.cleanup()  # 同期モードの場合は終了時にクリーンアップ

    def stop(self):
        """
        レシーバーを停止する
        """
        if not self.running:
            return

        self.running = False

        # スレッドが存在し、現在のスレッドでない場合は待機
        if (
            self.receiver_thread
            and self.receiver_thread.is_alive()
            and threading.current_thread() != self.receiver_thread
        ):
            self.receiver_thread.join(timeout=2.0)  # 最大2秒待機

        self.cleanup()

    def cleanup(self):
        """
        リソースをクリーンアップする
        """
        if self.sock:
            self.sock.close()
            self.sock = None

        self.receiver_thread = None
        print("Server closed.")

    def __enter__(self):
        """
        with文での開始時に呼ばれる

        Returns:
            self: このインスタンス
        """
        self.start(threaded=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        with文の終了時に呼ばれる

        Args:
            exc_type: 例外の種類
            exc_val: 例外の値
            exc_tb: トレースバック
        """
        self.stop()


# 使用例
def main():
    """メイン関数 - 使用例を示す"""
    ip = "127.0.0.1"
    port = 9999

    # 例1: withステートメントを使う方法
    print("Example 1: Using with statement")
    with UDPReceiver(ip, port) as receiver:
        # withブロック内ではレシーバーは既に起動している
        print("Receiver is running in the background...")
        # ここで他の処理を行う
        time.sleep(10)  # 10秒間受信する
    # withブロックを抜けるとレシーバーは自動的に停止する
    print("Receiver stopped automatically")

    # 例2: 明示的にstart/stopを呼び出す方法
    print("\nExample 2: Manual start/stop")
    receiver = UDPReceiver(ip, port)
    receiver.start()  # デフォルトで別スレッドで実行される

    # ここで他の処理を行う
    time.sleep(10)  # 10秒間受信する

    # 明示的に停止
    receiver.stop()
    print("Receiver stopped manually")


if __name__ == "__main__":
    main()

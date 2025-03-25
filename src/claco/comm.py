import logging
from typing import Iterator, AsyncIterator

from claco.queue import MessageQueue, AsyncMessageQueue
from claco.sender import Sender
from claco.receiver import UDPReceiver


logger = logging.getLogger(__name__)


class CommError(Exception):
    pass


class PostError(CommError):
    pass


class RecvError(CommError):
    pass


class _Sender:
    # ターゲットに送る側の処理を担当する

    def __init__(self, target: str, sender: Sender):
        self.target = target
        self.sender = sender

    def send(self, message: str):
        h, e = self.sender.send(self.target, message)
        if not h:
            raise PostError(e)

    async def asend(self, message: str):
        h, e = await self.sender.asend(self.target, message)
        if not h:
            raise PostError(e)

    def clear(self):
        if hasattr(self.sender, "send_clear"):
            self.sender.send_clear(self.target)

    async def aclear(self):
        if hasattr(self.sender, "asend_clear"):
            await self.sender.asend_clear(self.target)


class _Receiver:
    # ターゲットから返事をもらう側の処理を担当する

    def __init__(self, receiver: UDPReceiver, queue: MessageQueue):
        self.receiver = receiver
        self.messages = queue
        self.receiver.register_callback(self._post)

    def _post(self, message, address, timestamp):
        self.messages.post(message)

    def __enter__(self):
        self.receiver.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.receiver.__exit__(exc_type, exc_value, traceback)

    def receive(self) -> Iterator[str]:
        try:
            for message in self.messages.receive_all():
                yield message
        except Exception as e:
            raise RecvError() from e


class _AsyncReceiver:
    # ターゲットから返事をもらう側の処理を担当する

    def __init__(self, receiver: UDPReceiver, queue: AsyncMessageQueue):
        self.receiver = receiver
        self.messages = queue
        self.receiver.register_callback(self._post)

    def _post(self, message, address, timestamp):
        # 今のところ UDPReceiver のコールバックが同期呼び出しを前提としているので
        # ここも同期呼び出しにする
        self.messages.post(message)

    def __enter__(self):
        self.receiver.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.receiver.__exit__(exc_type, exc_value, traceback)

    async def receive(self) -> AsyncIterator[str]:
        try:
            async for message in self.messages.receive_all():
                yield message
        except Exception as e:
            raise RecvError() from e


class Communicator:
    def __init__(
        self,
        target: str,
        sender: Sender,
        receiver: UDPReceiver,
        queue: MessageQueue,
    ):
        self.sender = _Sender(target, sender)
        self.receiver = _Receiver(receiver, queue)

    def __enter__(self):
        self.receiver.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.receiver.__exit__(exc_type, exc_value, traceback)

    def send(self, message):
        logger.debug(f"[{self.__class__.__name__}] send: {message}")
        self.sender.send(message)

    def receive(self):
        logger.debug(f"[{self.__class__.__name__}] start receiving")
        return self.receiver.receive()

    def clear(self):
        self.sender.clear()

    def communicate(self, message: str) -> Iterator[str]:
        logger.debug(f"[{self.__class__.__name__}] communicate: {message}")
        self.send(message)
        return self.receive()


class AsyncCommunicator:
    def __init__(
        self,
        target: str,
        sender: Sender,
        receiver: UDPReceiver,
        queue: AsyncMessageQueue,
    ):
        self.sender = _Sender(target, sender)
        self.receiver = _AsyncReceiver(receiver, queue)

    def __enter__(self):
        self.receiver.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.receiver.__exit__(exc_type, exc_value, traceback)

    def send(self, message):
        # 今のところ UDPReceiver のコールバックが同期呼び出しを前提としているので
        # ここも同期呼び出しにする
        logger.debug(f"[{self.__class__.__name__}] send: {message}")
        self.sender.send(message)

    def receive(self):
        logger.debug(f"[{self.__class__.__name__}] start receiving")
        return self.receiver.receive()

    async def clear(self):
        self.sender.aclear()

    def communicate(self, message: str) -> AsyncIterator[str]:
        logger.debug(f"[{self.__class__.__name__}] communicate: {message}")
        self.send(message)
        return self.receive()


def create_communicator(
    target: str,
    udp_addr: str,
    udp_port: int,
    udp_bufsize: int = 4096,
    queue_max_size: int = 8,
    exe_path: str | None = None,
    sink_prompt: str | None = None,
) -> Communicator:
    from claco.sender import ClaudeSender
    from claco.queue import ClaudeMessageQueue

    sender_args = {}
    if exe_path is not None:
        sender_args["exe_path"] = exe_path
    if sink_prompt is not None:
        sender_args["sink_prompt"] = sink_prompt
    sender = ClaudeSender(**sender_args)

    queue = ClaudeMessageQueue(maxsize=queue_max_size)
    receiver = UDPReceiver(udp_addr, udp_port, buffer_size=udp_bufsize)
    return Communicator(target, sender, receiver, queue)


def create_async_communicator(
    target: str,
    udp_addr: str,
    udp_port: int,
    udp_bufsize: int = 4096,
    queue_max_size: int = 8,
    exe_path: str | None = None,
    sink_prompt: str | None = None,
) -> AsyncCommunicator:
    from claco.sender import ClaudeSender
    from claco.queue import AsyncClaudeMessageQueue

    sender_args = {}
    if exe_path is not None:
        sender_args["exe_path"] = exe_path
    if sink_prompt is not None:
        sender_args["sink_prompt"] = sink_prompt
    sender = ClaudeSender(**sender_args)

    queue = AsyncClaudeMessageQueue(maxsize=queue_max_size)
    receiver = UDPReceiver(udp_addr, udp_port, buffer_size=udp_bufsize)
    return AsyncCommunicator(target, sender, receiver, queue)

import queue
from asyncio import queues as aqueue, sleep as asleep
import time
import logging
from typing import Iterator, AsyncIterator


logger = logging.getLogger(__name__)


class MessageQueue:
    def __init__(self, maxsize=1):
        self._q = queue.Queue(maxsize=maxsize)
        self._closed = False

    def post(self, message: str) -> None:
        logger.debug(f"[{self.__class__.__name__}] post: {message=}")
        self._q.put(message)

    def receive(self) -> str:
        while True:
            try:
                message = self._q.get_nowait()
                logger.debug(f"[{self.__class__.__name__}] receive: {message=}")
                return message
            except queue.Empty:
                time.sleep(0.05)

    def try_receive(self) -> str | None:
        try:
            message = self._q.get_nowait()
            logger.debug(f"[{self.__class__.__name__}] try_receive: {message=}")
            return message
        except queue.Empty:
            return None

    def receive_all(self) -> Iterator[str]:
        logger.debug(f"[{self.__class__.__name__}] start receive_all")

        while True:
            msg = self.receive()
            yield msg


class AsyncMessageQueue:
    def __init__(self, maxsize=1):
        self._q = aqueue.Queue(maxsize)
        self._closed = False

    async def post(self, message: str) -> None:
        logger.debug(f"[{self.__class__.__name__}] post: {message=}")
        await self._q.put(message)

    async def receive(self) -> str:
        while True:
            try:
                message = await self._q.get()
                logger.debug(f"[{self.__class__.__name__}] receive: {message=}")
                return message
            except aqueue.QueueEmpty:
                await asleep(0.05)

    async def try_receive(self) -> str | None:
        try:
            message = await self._q.get_nowait()
            logger.debug(f"[{self.__class__.__name__}] try_receive: {message=}")
            return message
        except aqueue.QueueEmpty:
            return None

    async def receive_all(self) -> AsyncIterator[str]:
        logger.debug(f"[{self.__class__.__name__}] start receive_all")

        while True:
            msg = await self.receive()
            yield msg

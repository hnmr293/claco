import queue
from asyncio import queues as aqueue, sleep as asleep
import time


class MessageQueue:
    def __init__(self, maxsize=1):
        self._q = queue.Queue(maxsize=maxsize)
        self._closed = False

    def post(self, message: str) -> None:
        self._q.put(message)

    def receive(self) -> str:
        while True:
            try:
                return self._q.get_nowait()
            except queue.Empty:
                time.sleep(0.05)

    def try_receive(self) -> str | None:
        try:
            return self._q.get_nowait()
        except queue.Empty:
            return None


class AsyncMessageQueue:
    def __init__(self, maxsize=1):
        self._q = aqueue.Queue(maxsize)
        self._closed = False

    async def post(self, message: str) -> None:
        await self._q.put(message)

    async def receive(self) -> str:
        while True:
            try:
                return await self._q.get()
            except aqueue.QueueEmpty:
                await asleep(0.05)

    async def try_receive(self) -> str | None:
        try:
            return await self._q.get_nowait()
        except aqueue.QueueEmpty:
            return None

import logging
from typing import override

from .base import MessageQueue, AsyncMessageQueue


logger = logging.getLogger(__name__)


class ClaudeMessageQueue(MessageQueue):
    def __init__(self, maxsize=1, exit_tag="<exit>"):
        super().__init__(maxsize)
        self.exit_tag = exit_tag

    @override
    def receive_all(self):
        logger.debug(f"[{self.__class__.__name__}] start receive_all")

        while True:
            msg = self.receive()
            if msg.strip() == self.exit_tag:
                break
            yield msg


class AsyncClaudeMessageQueue(AsyncMessageQueue):
    def __init__(self, maxsize=1, exit_tag="<exit>"):
        super().__init__(maxsize)
        self.exit_tag = exit_tag

    @override
    async def receive_all(self):
        logger.debug(f"[{self.__class__.__name__}] start receive_all")

        while True:
            msg = await self.receive()
            if msg.strip() == self.exit_tag:
                break
            yield msg

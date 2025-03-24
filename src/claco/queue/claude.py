from claco.queue.base import MessageQueue, AsyncMessageQueue


class ClaudeMessageQueue(MessageQueue):
    def __init__(self, maxsize=1, exit_tag="<exit>"):
        super().__init__(maxsize)
        self.exit_tag = exit_tag

    def receive_all(self):
        while True:
            msg = self.receive()
            if msg.strip() == self.exit_tag:
                break
            yield msg


class AsyncClaudeMessageQueue(AsyncMessageQueue):
    def __init__(self, maxsize=1, exit_tag="<exit>"):
        super().__init__(maxsize)
        self.exit_tag = exit_tag

    async def receive_all(self):
        while True:
            msg = await self.receive()
            if msg.strip() == self.exit_tag:
                break
            yield msg

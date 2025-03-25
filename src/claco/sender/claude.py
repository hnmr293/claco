import logging
from typing import override

from .base import Sender


logger = logging.getLogger(__name__)


_IGNORE = object()


class ClaudeSender(Sender):
    def __init__(
        self,
        exe_path: str | None = None,
        sink_prompt='返事は Sink ツールを使用して書き出してください。Sink ツールは一文ごとに区切って呼び出してください。段落の区切りでは "</>" とだけ書き出してください。すべての文章を Sink ツールで書き出し終わったら、最後に Sink ツールで <exit> とだけ書き出してください。',
    ):
        super().__init__(exe_path)
        logger.debug(f"[{self.__class__.__name__}] {exe_path=} {sink_prompt=}")
        self.sink_prompt = sink_prompt

    def __create_send_argss(self, message: str):
        message = message.splitlines()

        args = []
        for i, line in enumerate(message):
            args.append((line.strip(), False))
            if i < len(message) - 1:
                args.append(("+{ENTER}", True))

        args.append(("+{ENTER}+{ENTER}", True))
        args.append((self.sink_prompt, False))
        args.append(("{ENTER}", True))
        return args

    @override
    def send(self, target: str, message: str, raw=_IGNORE):
        logger.debug(f"[{self.__class__.__name__}] send: {target=} {message=} {raw=}")

        args = self.__create_send_argss(message)
        h, e = super().sends(target, args)
        if not h:
            logger.error(f"[{self.__class__.__name__}] failed to send message: {e}")
            return False, e

        return True, None

    @override
    async def asend(self, target: str, message: str, raw=_IGNORE):
        logger.debug(f"[{self.__class__.__name__}] asend: {target=} {message=} {raw=}")

        args = self.__create_send_argss(message)
        h, e = await super().asends(target, args)
        if not h:
            logger.error(f"[{self.__class__.__name__}] failed to send message: {e}")
            return False, e

        return True, None

    def send_clear(self, target: str):
        logger.debug(f"[{self.__class__.__name__}] send_clear {target=}")

        # ^A does not work
        h, e = super().send(target, "_^{END}+^{HOME}{DEL}", raw=True)
        if not h:
            logger.error(f"[{self.__class__.__name__}] failed to send message: {e}")
            return False, e

        return True, None

    async def asend_clear(self, target: str):
        logger.debug(f"[{self.__class__.__name__}] asend_clear {target=}")

        # ^A does not work
        h, e = await super().asend(target, "_^{END}+^{HOME}{DEL}", raw=True)
        if not h:
            logger.error(f"[{self.__class__.__name__}] failed to send message: {e}")
            return False, e

        return True, None

from typing import override

from .base import Sender


_IGNORE = object()


class ClaudeSender(Sender):
    def __init__(
        self,
        exe_path,
        sink_prompt='返事は Sink ツールを使用して書き出してください。Sink ツールは一文ごとに区切って呼び出してください。段落の区切りでは "</>" とだけ書き出してください。すべての文章を Sink ツールで書き出し終わったら、最後に Sink ツールで <exit> とだけ書き出してください。',
    ):
        super().__init__(exe_path)
        self.sink_prompt = sink_prompt

    @override
    def send(self, target, message, raw=_IGNORE):
        message = message.splitlines()

        for i, line in enumerate(message):
            h, e = super().send(target, line.strip(), raw=False)
            if not h:
                print(f"[ERROR] Failed to send message: {e}")
                return False, e
            if i < len(message) - 1:
                h, e = super().send(target, "+{ENTER}", raw=True)
                if not h:
                    print(f"[ERROR] Failed to send message: {e}")
                    return False, e

        h, e = super().send(target, "+{ENTER}+{ENTER}", raw=True)
        if not h:
            print(f"[ERROR] Failed to send message: {e}")
            return False, e

        h, e = super().send(target, self.sink_prompt, raw=False)
        if not h:
            print(f"[ERROR] Failed to send message: {e}")
            return False, e

        h, e = super().send(target, "{ENTER}", raw=True)
        if not h:
            print(f"[ERROR] Failed to send message: {e}")
            return False, e

        return True, None

    @override
    async def asend(self, target, message, raw=_IGNORE):
        message = message.splitlines()

        for i, line in enumerate(message):
            h, e = await super().asend(target, line.strip(), raw=False)
            if not h:
                print(f"[ERROR] Failed to send message: {e}")
                return False, e
            if i < len(message) - 1:
                h, e = await super().asend(target, "+{ENTER}", raw=True)
                if not h:
                    print(f"[ERROR] Failed to send message: {e}")
                    return False, e

        h, e = await super().asend(target, "+{ENTER}+{ENTER}", raw=True)
        if not h:
            print(f"[ERROR] Failed to send message: {e}")
            return False, e

        h, e = await super().asend(target, self.sink_prompt, raw=False)
        if not h:
            print(f"[ERROR] Failed to send message: {e}")
            return False, e

        h, e = await super().asend(target, "{ENTER}", raw=True)
        if not h:
            print(f"[ERROR] Failed to send message: {e}")
            return False, e

        return True, None

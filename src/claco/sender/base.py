import subprocess
import asyncio
from locale import getdefaultlocale
import re
from typing import Literal


def _decode(x: bytes) -> str:
    try:
        return x.decode(getdefaultlocale()[1])
    except UnicodeDecodeError:
        return str(x)


def _get_error_message(out: str, target: str) -> str:
    err_msg = out

    if f"Process '{target}' was not found." in out:
        err_msg = f"Process '{target}' was not found."
    elif f"Window handle is invalid." in out:
        err_msg = f"Target window is minimized."
        r = re.compile("handle\s*=\s*([0-9A-Fa-f]+)")
        if handles := r.findall(out):
            err_msg += "\nfound window handles:"
            for handle in handles:
                err_msg += f"\n  handle = {handle}"


class Sender:
    def __init__(self, exe_path: str):
        self.exe_path = exe_path

    def send(
        self,
        target: str,
        message: str,
        raw: bool = False,
    ) -> tuple[Literal[True], None] | tuple[Literal[False], str]:
        # execute command `{exe_path} {message}`
        args = [self.exe_path, target, message]
        if raw:
            args.insert(1, "--raw")
        x = subprocess.run(
            args,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        e = x.returncode

        if e == 0:
            return True, None

        out, err = _decode(x.stdout), _decode(x.stderr)

        err_msg = _get_error_message(out, target)

        return False, err_msg

    async def asend(
        self,
        target: str,
        message: str,
        raw: bool = False,
    ) -> tuple[Literal[True], None] | tuple[Literal[False], str]:
        # execute command `{exe_path} {message}`
        args = [self.exe_path, target, message]
        if raw:
            args.insert(1, "--raw")
        x = await asyncio.subprocess.create_subprocess_shell(
            args,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        out, err = await x.communicate()

        e = x.returncode

        if e == 0:
            return True, None

        out, err = _decode(x.stdout), _decode(x.stderr)

        err_msg = _get_error_message(out, target)

        return False, err_msg

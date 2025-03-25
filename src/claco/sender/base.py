import os
import subprocess
import asyncio
from locale import getdefaultlocale
import re
import logging
from typing import Literal


logger = logging.getLogger(__name__)


def _decode(x: bytes) -> str:
    try:
        return x.decode(getdefaultlocale()[1])
    except UnicodeDecodeError:
        return str(x)[2:-1]


def _get_error_message(out: str, target: str) -> str:
    err_msg = out

    if f"Process '{target}' was not found." in out:
        err_msg = f"Process '{target}' was not found."
    elif f"Window handle is invalid." in out:
        err_msg = f"Target window is minimized."
        r = re.compile(r"handle\s*=\s*([0-9A-Fa-f]+)")
        if handles := r.findall(out):
            err_msg += "\nfound window handles:"
            for handle in handles:
                err_msg += f"\n  handle = {handle}"


class Sender:
    def __init__(self, exe_path: str):
        self.exe_path = exe_path
        logger.debug(f"[{self.__class__.__name__}] {exe_path=}")
        if not os.path.exists(exe_path):
            logger.warning(f"[{self.__class__.__name__}] {exe_path!r} does not exist; may not work properly")

    def send(
        self,
        target: str,
        message: str,
        raw: bool = False,
    ) -> tuple[Literal[True], None] | tuple[Literal[False], str]:
        # execute command `{exe_path} {message}`
        logger.debug(f"[{self.__class__.__name__}] send: {target=} {message=} {raw=}")

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

        logger.debug(f"[{self.__class__.__name__}] stdout: {out}")
        logger.debug(f"[{self.__class__.__name__}] stderr: {out}")

        err_msg = _get_error_message(out, target)

        return False, err_msg

    async def asend(
        self,
        target: str,
        message: str,
        raw: bool = False,
    ) -> tuple[Literal[True], None] | tuple[Literal[False], str]:
        # execute command `{exe_path} {message}`
        logger.debug(f"[{self.__class__.__name__}] asend: {target=} {message=} {raw=}")

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

        logger.debug(f"[{self.__class__.__name__}] stdout: {out}")
        logger.debug(f"[{self.__class__.__name__}] stderr: {out}")

        err_msg = _get_error_message(out, target)

        return False, err_msg

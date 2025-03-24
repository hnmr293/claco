import subprocess
from locale import getdefaultlocale
import re


class Sender:
    def __init__(self, exe_path: str):
        self.exe_path = exe_path

    def send(self, target: str, message: str, raw: bool = False) -> tuple[bool, str | None]:
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

        try:
            err = x.stderr.decode(getdefaultlocale()[1])
        except UnicodeDecodeError:
            err = str(x.stderr)

        try:
            out = x.stdout.decode(getdefaultlocale()[1])
        except UnicodeDecodeError:
            out = str(x.stdout)

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

        return False, err_msg

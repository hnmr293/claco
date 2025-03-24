import subprocess


class Sender:
    def __init__(self, exe_path: str):
        self.exe_path = exe_path

    def send(self, target: str, message: str, raw: bool = False) -> None:
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
        if e != 0:
            try:
                err = x.stderr.decode()
            except UnicodeDecodeError:
                err = str(x.stderr)
            if f"Process '{target}' was not found." in err:
                return False

            try:
                out = x.stdout.decode()
            except UnicodeDecodeError:
                out = str(x.stdout)

            print(f"Error: {e}")
            print(f"stdout: {out}")
            print(f"stderr: {err}")

        x.check_returncode()
        return True

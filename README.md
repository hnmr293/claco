For my own use.

usage:
```bash
# install claco
$ cd /d D:\dev
$ uv init claude-chat-cli
$ cd claude-chat-cli
$ uv add git+https://github.com/hnmr293/claco
$ curl -L -O https://github.com/hnmr293/ClaudeTools/releases/download/v0.1.0/ClaudeTools.Cui.exe

# configuration
$ echo CLACO_SENDER_PATH="D:/dev/claude-chat-cli/ClaudeTools.Cui.exe" >.env
$ echo CLACO_IP_ADDR="127.0.0.1" >>.env
$ echo CLACO_PORT=9999 >>.env

# start chat
$ uv run chat
```

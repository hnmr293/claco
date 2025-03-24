For my own use.

usage:
```python
# install claco
$ cd /d D:\dev
$ uv init claude-chat-cli
$ uv add git+https://github.com/hnmr293/claco
$ curl -L -O https://github.com/hnmr293/ClaudeTools/releases/download/v0.1.0/ClaudeTools.Cui.exe
# configuration
$ echo SENDER_PATH="D:/dev/claude-chat-cli/ClaudeTools.Cui.exe" >.env
$ echo IP_ADDR="127.0.0.1" >>.env
$ echo PORT=9999 >>.env
# start chat
$ uv run chat
```

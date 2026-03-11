import sys
import subprocess


def run_cmd(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, shell=(sys.platform == "win32"), **kwargs)

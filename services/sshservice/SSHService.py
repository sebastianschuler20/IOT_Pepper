from typing import Optional, Tuple

import spur
from spur import ssh


class SSHService:
    def __init__(
        self,
        host: str,
        username: str,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        port: int = 22,
        timeout: int = 10,
    ):
        self.host = host
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.port = port
        self.timeout = timeout
        self.shell: Optional[spur.ssh.SshShell] = None

    def connect(self) -> None:
        if self.shell:
            return

        self.shell = spur.SshShell(
            hostname=self.host,
            username=self.username,
            password=self.password,
            private_key_file=self.key_filename,
            port=self.port,
            connect_timeout=self.timeout,
            missing_host_key=ssh.MissingHostKey.accept,
        )

    def close(self) -> None:
        self.shell = None

    def _ensure_shell(self) -> spur.ssh.SshShell:
        if not self.shell:
            raise RuntimeError("SSH connection not established. Call connect() first.")
        return self.shell

    def execute(self, command: str) -> Tuple[str, str, int]:
        """
        Execute a raw command on the remote device.
        """
        shell = self._ensure_shell()
        result = shell.run(
            ["bash", "-lc", command],
            stdout=ssh.PIPE,
            stderr=ssh.PIPE,
            allow_error=True,
        )
        stdout = result.output.decode() if result.output else ""
        stderr = result.stderr_output.decode() if result.stderr_output else ""
        return stdout, stderr, result.return_code

    def execute_dance(self) -> Tuple[str, str, int]:
        """
        Placeholder: hier das NAOqi-Modul reinschreiben, das den Tanz ausführt.
        """
        return self.execute("echo 'Hier das NAOqi-Modul reinschreiben (Dance).'")

    def execute_talk(self, text: str) -> Tuple[str, str, int]:
        """
        Placeholder: hier das NAOqi-Modul reinschreiben, das den Text sprechen lässt.
        """
        return self.execute(f"echo 'Hier das NAOqi-Modul reinschreiben (Talk): {text}'")

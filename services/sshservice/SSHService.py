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
            ["sh", "-c", command],  # oder ["bash", "-lc", command] falls vorhanden
            allow_error=True,
            # optional: encoding direkt hier setzen, falls du in __init__ keins setzt
            encoding="utf-8",
        )

        # Wenn encoding gesetzt ist, sind output/stderr_output schon str
        stdout = result.output or ""
        stderr = result.stderr_output or ""
        return stdout, stderr, result.return_code

    def execute_talk(self, text: str) -> Tuple[str, str, int]:
        command = f'qicli call ALTextToSpeech.say "{text}"'

        return self.execute(command)

    def execute_wave(self) -> Tuple[str, str, int]:
        """
        Lässt Pepper mit dem rechten Arm winken.
        """
        command = (
            'qicli call ALMotion.setStiffnesses "RArm" 1.0 && '
            'qicli call ALMotion.setAngles "RShoulderPitch" -0.4 0.2 && '
            'qicli call ALMotion.setAngles "RElbowRoll" 1.0 0.2 && '
            'qicli call ALMotion.setAngles "RWristYaw" 1.0 0.3 && '
            'sleep 0.3 && '
            'qicli call ALMotion.setAngles "RWristYaw" -1.0 0.3'
        )
        return self.execute(command)
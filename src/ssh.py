from fastapi import WebSocket
from io import StringIO

import paramiko
import asyncio


k_types = {
    "RSA": paramiko.RSAKey,
    "ECDSA": paramiko.ECDSAKey,
    "Ed25519": paramiko.Ed25519Key,
    "ed25519": paramiko.Ed25519Key,
}

class SSHSession:
    def __init__(
        self,
        ws: WebSocket,
        host: str,
        port: int,
        username: str,
        password: str = None,
        pkey: str = None,
        key_type: str = None,
        passphrase: str = None,
        termsize: dict | None = None,
    ):
        self.ws = ws
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pkey = pkey
        self.key_type = key_type
        self.passphrase = passphrase
        self.termsize = termsize or {"cols": 80, "rows": 24}

        self.ssh: paramiko.SSHClient | None = None
        self.chan = None
        self.loop = None
        self.stop_event: asyncio.Event | None = None
        self.queue: asyncio.Queue | None = None

    async def connect(self) -> bool:
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            kwargs = {
                "hostname": self.host,
                "port": self.port,
                "username": self.username,
                "timeout": 120,
                "password": self.password,
                "pkey": None,
                "passphrase": self.passphrase.encode() if self.passphrase else None,
            }

            if self.pkey:
                if self.key_type not in k_types:
                    raise ValueError("Unsupported key type")
                key_file = StringIO(self.pkey)
                kwargs["pkey"] = k_types[self.key_type](
                    file_obj=key_file,
                    password=self.passphrase.encode() if self.passphrase else None,
                )

            await asyncio.to_thread(self.ssh.connect, **kwargs)

            self.chan = self.ssh.invoke_shell(term="xterm")
            self.chan.setblocking(True)
            self.chan.resize_pty(self.termsize["cols"], self.termsize["rows"])

            self.loop = asyncio.get_running_loop()
            self.stop_event = asyncio.Event()
            self.queue = asyncio.Queue(maxsize=100)

            return True

        except Exception as e:
            try:
                await self.ws.close(code=1011, reason="SSH connection failed")
            except Exception:
                pass
            if self.ssh:
                try:
                    self.ssh.close()
                except Exception:
                    pass
            return False

    def ssh_reader(self):
        try:
            while not self.stop_event.is_set():
                data = self.chan.recv(1024)
                
                if not data:
                    break

                asyncio.run_coroutine_threadsafe(self.queue.put(data), self.loop)

        except Exception:
            pass

    async def ws_writer(self):
        try:
            while True:
                data = await self.queue.get()
                await self.ws.send_bytes(data)
        except asyncio.CancelledError:
            pass

    async def close(self):
        try:
            if self.chan:
                try:
                    self.chan.close()
                except Exception:
                    pass
            if self.ssh:
                try:
                    self.ssh.close()
                except Exception:
                    pass
        except Exception:
            pass

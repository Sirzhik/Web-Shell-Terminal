from time import time
from fastapi import WebSocket, APIRouter
from starlette.websockets import WebSocketDisconnect
from db.db import get_full_table, VirtualUsers, get_session_by_session_str, decrypt_string, get_virtual_user_by_id, get_group_by_user_id, is_group_linked
from io import StringIO

import paramiko
import asyncio


router = APIRouter(prefix='/ws', tags=['WebSocket'])

@router.websocket('/ssh/{virtual_user_id}')
async def websocket_endpoint(ws: WebSocket, virtual_user_id: int):
    try:
        virt_usr = await get_virtual_user_by_id(virtual_user_id)
    except Exception as e:
        await ws.close(code=1008, reason="Virtual user not found")
        return

    if not virt_usr:
        await ws.close(code=1008, reason="Virtual user not found")
        return

    host = virt_usr.domain
    user = virt_usr.username
    port = virt_usr.port
    password = await decrypt_string(virt_usr.password) if virt_usr.password else None
    key = await decrypt_string(virt_usr.ssh_key) if virt_usr.ssh_key else None
    passphrase = await decrypt_string(virt_usr.passphrase) if virt_usr.passphrase else None
    key_type = virt_usr.ssh_key_type
    k_types = {
        "RSA": paramiko.RSAKey,
        "ECDSA": paramiko.ECDSAKey,
        "Ed25519": paramiko.Ed25519Key,
        "ed25519": paramiko.Ed25519Key,
    }

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    session = ws.cookies.get("session")
    if not session:
        await ws.close(code=1008, reason="No session cookie found")
        return
    
    session = await get_session_by_session_str(session)

    web_user_id = session.user_id
    group_id = await get_group_by_user_id(web_user_id)

    if not await is_group_linked(group_id, virtual_user_id):
        await ws.close(code=1008, reason="Access to this virtual user is not allowed")
        return

    if not session or session.expires_at < int(time()):
        await ws.close(code=1008, reason="Invalid or expired session")

    await ws.accept()

    try:
        kwargs = {
                'hostname': host,
                'port': port,
                'username': user,
                'timeout': 120,
                'passphrase': passphrase.encode() if passphrase else None,
                'pkey': None,
                'password': password,
        }

        if key:
            key_file = StringIO(key)
            kwargs['pkey'] = k_types[key_type](file_obj=key_file, password=passphrase.encode() if passphrase else None)

        await asyncio.to_thread(ssh.connect, **kwargs)
    except Exception as e:
        print(f"SSH connection failed: {type(e).__name__}: {e}")
        await ws.close(code=1011, reason=str(e))
        return

    termsize: dict = await ws.receive_json()
    print(f"Terminal size: {termsize}")

    chan = ssh.invoke_shell(term='xterm')
    chan.setblocking(False)
    chan.resize_pty(termsize['cols'], termsize['rows'])

    try:
        async def reader():
            while True:
                await asyncio.sleep(0.01)
                if chan.recv_ready():
                    data = await asyncio.to_thread(chan.recv, 1024)
                    if data:
                        await ws.send_bytes(data)

        asyncio.create_task(reader())

        while True:
            inp_mess = await ws.receive_bytes()
            await asyncio.to_thread(chan.send, inp_mess)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
        chan.close()
        ssh.close()
    except Exception as e:
        print(f"Session error: {type(e).__name__}: {e}")
        chan.close()
        ssh.close()

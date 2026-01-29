from time import time
from fastapi import WebSocket, APIRouter
from starlette.websockets import WebSocketDisconnect
from db.db import get_session_by_session_str, decrypt_string, get_virtual_user_by_id, get_group_by_user_id, is_group_linked
from ssh import SSHSession

import paramiko
import asyncio

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/ssh/{virtual_user_id}")
async def websocket_endpoint(ws: WebSocket, virtual_user_id: int):
    try:
        virt_usr = await get_virtual_user_by_id(virtual_user_id)
    except Exception:
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

    session_cookie = ws.cookies.get("session")
    if not session_cookie:
        await ws.close(code=1008, reason="No session cookie found")
        return

    session = await get_session_by_session_str(session_cookie)
    if not session or session.expires_at < int(time()):
        await ws.close(code=1008, reason="Invalid or expired session")
        return

    web_user_id = session.user_id
    group_id = await get_group_by_user_id(web_user_id)
    if not await is_group_linked(group_id, virtual_user_id):
        await ws.close(code=1008, reason="Access denied")
        return

    await ws.accept()

    try:
        termsize = await ws.receive_json()
    except Exception:
        await ws.close(code=1008, reason="No term size")
        return

    ssh_session = SSHSession(
        ws=ws,
        host=host,
        port=port,
        username=user,
        password=password,
        pkey=key,
        key_type=key_type,
        passphrase=passphrase,
        termsize=termsize,
    )

    ok = await ssh_session.connect()
    
    if not ok:
        return

    ssh_reader_task = asyncio.create_task(asyncio.to_thread(ssh_session.ssh_reader))
    ws_writer_task = asyncio.create_task(ssh_session.ws_writer())

    try:
        while True:
            data = await ws.receive_bytes()
            await asyncio.to_thread(ssh_session.chan.send, data)

    except WebSocketDisconnect:
        pass

    finally:
        if ssh_session.stop_event:
            ssh_session.stop_event.set()

        try:
            ssh_session.chan.close()
        except Exception:
            pass

        try:
            await ssh_reader_task
        except Exception:
            pass

        ws_writer_task.cancel()
        try:
            await ws_writer_task
        except asyncio.CancelledError:
            pass

        await ssh_session.close()

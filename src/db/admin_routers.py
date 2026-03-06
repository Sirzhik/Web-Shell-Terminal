from fastapi import APIRouter, FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from utils.template import templates
from db.schemas import (
    AddUserSchema,
    AddVirtualUserSchema,
    AddGroupSchema,
    SetGroupForUserSchema,
    RemoveLinkGroupToServerSchema,
    LinkGroupToServerSchema,
    ValidateCredentialsSchema,
    IsAccountLinkedSchema,
    useUserId,
)
# from db.db import (
#     add_user as db_add_user, 
#     remove_admin_session,
#     remove_user, 
#     add_virtual_user, 
#     link_group_to_server,
#     add_group,
#     remove_group,
#     remove_virtual_user,
#     remove_link_group_to_server,
#     set_group_for_user,
#     get_session_by_session_str,
#     get_user_by_username,
#     get_user_by_id,
#     validate_credentials,
#     # is_account_linked,
#     get_server_by_id,
#     validate_admin_credentials,
#     get_admin_session_by_field,
#     get_full_table,
#     create_admin_session,
#     remove_admin_session,
#     VirtualUsers,
#     Sessions,
#     WebUsers,
#     Groups,
#     GroupToServer,
#     AdminSessions,
# )
from db.db import db_operator, VirtualUsers, Sessions, WebUsers, Groups, GroupToServer, AdminSessions
from time import time


app = FastAPI()
# router = APIRouter(prefix='/admin', tags=['admin'])

@app.middleware("http")
async def admin_auth_middleware(request, call_next):
    current_session = request.cookies.get("admin_session")
    if not current_session:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "No admin session cookie found"}
        )
    
    session = await db_operator.get_admin_session_by_field('session', current_session)
    if not session or session.expires_at < int(time()):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or expired admin session"}
        )

    response = await call_next(request)
    return response

# Admin views
@app.get('/panel', name='Admin panel', tags=['Views'])
def admin_panel(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name='admin_panel.html'
    )

# Admin API
@app.get('/view-tables')
async def view_tables():
    return {
        "virtual_users": await db_operator.get_full_table(VirtualUsers),
        "sessions": await db_operator.get_full_table(Sessions),
        "web_users": await db_operator.get_full_table(WebUsers),
        "groups": await db_operator.get_full_table(Groups),
        "group_to_server": await db_operator.get_full_table(GroupToServer),
        "admin_sessions": await db_operator.get_full_table(AdminSessions)
    }

@app.post('/add_user')
async def add_user_endpoint(user: AddUserSchema):
    # try:
        user = await db_operator.add_user(username=user.username, password=user.password)
        return {"user": user.username, "id": user.id}
    
    # except IntegrityError:
    #     raise HTTPException(status_code=409, detail="Username already exists")

@app.delete('/remove_user/{id}')
async def delete_user(id: int):
    try:
        await db_operator.remove_user(id=id)
        return {"detail": "User removed successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/add_ssh_account')
async def add_ssh_account_endpoint(v_user: AddVirtualUserSchema):
    try:
        v_user_result = await db_operator.add_virtual_user(username=v_user.username, password=v_user.password, ssh_key=v_user.ssh_key, passphrase=v_user.passphrase, ssh_key_type=v_user.ssh_key_type, domain=v_user.domain, port=v_user.port)
        return {"ssh_account": v_user_result.username, "id": v_user_result.id}

    except IntegrityError:
        raise HTTPException(status_code=409, detail="SSH account exception")

@app.post('/link_group_to_server')
async def link_group_to_server_endpoint(link_data: LinkGroupToServerSchema):
    try:
        link = await db_operator.link_group_to_server(group_id=link_data.group_id, server_id=link_data.server_id)
        return {"detail": f"Group {link.group_id} linked to server {link.server_id}"}
    
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Link already exists")

@app.post('/add_group')
async def add_group_endpoint(group: AddGroupSchema):
    try:
        group_result = await db_operator.add_group(name=group.name)
        return {"group": group_result.name, "id": group_result.id}
    
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Group name already exists")

@app.post('/set_group_for_user')
async def set_group_for_user_endpoint(data: SetGroupForUserSchema):
    try:
        user = await db_operator.set_group_for_user(user_id=data.user_id, group_id=data.group_id)
        return {"user": user.username, "id": user.id, "group_id": user.group_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete('/remove_group/{id}')
async def delete_group(id: int):
    # try:
        await db_operator.remove_group(id=id)
        return {"detail": "Group removed successfully"}
    
    # except Exception as e:
    #     print(e)
    #     raise HTTPException(status_code=500, detail=str(e))

@app.delete('/remove_ssh_account/{id}')
async def delete_ssh_account(id: int):
    try:
        await db_operator.remove_virtual_user(id=id)
        return {"detail": "SSH account removed successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete('/remove_link_group_to_server')
async def delete_link_group_to_server(link_data: RemoveLinkGroupToServerSchema):
    try:
        await db_operator.remove_link_group_to_server(group_id=link_data.group_id, server_id=link_data.server_id)
        return {"detail": "Link removed successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete('/logout')
async def logout(request: Request):
    content = {"message": "Logout successful"}
    response = JSONResponse(content=content)
    response.delete_cookie(key="admin_session")
    
    current_session = request.cookies.get("admin_session")
    
    if current_session:
        await db_operator.remove_admin_session(current_session)
    
    return response

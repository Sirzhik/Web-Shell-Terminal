import pydantic


class AddUserSchema(pydantic.BaseModel):
    username: str
    password: str

class AddVirtualUserSchema(pydantic.BaseModel):
    username: str
    password: str = None
    ssh_key: str = None
    ssh_key_type: str = None
    passphrase: str = None
    domain: str
    port: int = 22

class AddGroupSchema(pydantic.BaseModel):
    name: str

class SetGroupForUserSchema(pydantic.BaseModel):
    user_id: int
    group_id: int

class PasswordSchema(pydantic.BaseModel):
    password: str

class RemoveLinkUserToServerSchema(pydantic.BaseModel):
    group_id: int
    server_id: int

class LinkUserToServerSchema(pydantic.BaseModel):
    group_id: int
    server_id: int

class ValidateCredentialsSchema(pydantic.BaseModel):
    username: str
    password: str

class IsAccountLinkedSchema(pydantic.BaseModel):
    user_id: int
    server_id: int

class useUserId(pydantic.BaseModel):
    id: int

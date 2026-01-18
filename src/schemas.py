from pydantic import BaseModel
from time import time


class UserCredentials(BaseModel):
    username: str
    password: str

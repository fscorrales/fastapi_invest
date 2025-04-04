"""
This script requires the file ADMIN_USER_CONF to be in the same directory as the 
script. Or you can set the username, email and password environment variables.
"""

import os

from src.auth.models import CreateUser
from src.auth.services import UsersService

try:
    with open("scripts/ADMIN_USER_CONF", "r") as f:
        print("Reading the config file...")
        lines = f.read().splitlines()
        data = dict(line.split("=") for line in lines)
except FileNotFoundError:
    data = dict(
        email=os.environ.get("ADMIN_EMAIL"),
        password=os.environ.get("ADMIN_PASSWORD"),
    )

# Assign role admin to user data
data["role"] = "admin"

insertion_user = CreateUser.model_validate(data)

print("Creating super user...")
result = UsersService.create_one(insertion_user)

print(f"Super user: {data["username"]} created with id: {result}")
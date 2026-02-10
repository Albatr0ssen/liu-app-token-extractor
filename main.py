import os
from pprint import pprint
from sys import exit
import httpx

from pydantic import BaseModel, EmailStr
from argparse import ArgumentParser

from dotenv import load_dotenv

#
#
# url = "https://jsonplaceholder.typicode.com/users/1"
#
# response = httpx.get(url)
# response.raise_for_status()
#
# user = User.model_validate(response.json())
# print(repr(user))
#
#


class FormsAuthentication(BaseModel):
    UserName: str
    Password: str
    Kmsi: str = "false"
    AuthMethod: str = "FormsAuthentication"


username = "samak519@ad.liu.se"

_ = load_dotenv()

# password = getpass.getpass(echo_char="*")
password = os.getenv("pass")
if password is None:
    exit(1)


headers = httpx.Headers({"Content-Type": "application/x-www-form-urlencoded"})

params = httpx.QueryParams(
    {
        "client_id": "Liuapp_student_oauth_client",
        "redirect_uri": "http%3A%2F%2Flocalhost%2FauthCallback",
        "response_type": "code",
        "resource": "https%3A%2F%2Fwww.student.liu.se%2Fliuapp",
        "client-request-id": "da4d0618-8cae-41a0-3750-0080030000fc",
    }
)

data = FormsAuthentication(UserName=username, Password=password)


res = httpx.post(
    url="https://fs.liu.se/adfs/oauth2/authorize",
    headers=headers,
    data=data.model_dump(),
    params=params,
    follow_redirects=False,
)

print(res.url, res.status_code)
print(res.headers)
# print(res.text)

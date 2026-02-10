from rich.pretty import pprint
import httpx
import os
from contextlib import asynccontextmanager
import signal
from typing import NamedTuple
from urllib.parse import urlunparse, urlencode
from fastapi import FastAPI
import uvicorn

LIU_APP_VERSION = "4.3.2"
USER_AGENT = "FxVersion/9.0.325.11113 OSVersion/Linux.6.1.124.android14.11.g8d713f9e8e7b.ab13202960.1.SMP.PREEMPT.Wed.Mar.12.13.40.07.UTC.2025 Liuapp.MobileAuth.MobileAuthApiClient.Generated.MobileAuth/1.0.0.0"


class UriComponents(NamedTuple):
    scheme: str
    netloc: str
    url: str
    path: str
    query: str
    fragment: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    query_params = {
        "client_id": "Liuapp_student_oauth_client",
        "redirect_uri": "http://localhost/authCallback",
        "response_type": "code",
        "resource": "https://www.student.liu.se/liuapp",
    }

    url_string = urlunparse(
        UriComponents(
            scheme="https",
            netloc="fs.liu.se",
            query=urlencode(query_params),
            path="",
            url="/adfs/oauth2/authorize",
            fragment="",
        )
    )
    print(url_string)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/authCallback")
async def auth(
    code: str,
):
    print(code)
    access_token = get_access_token_from_fs_liu(code)
    user_token = get_user_token_from_mobile_auth(access_token)
    print(user_token)
    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="127.0.0.1", port=80, reload=False, log_level="warning"
    )


def get_access_token_from_fs_liu(code: str) -> str:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost/authCallback",
        "client_id": "Liuapp_student_oauth_client",
        "User-Agent": USER_AGENT,
    }

    res = httpx.post("https://fs.liu.se/adfs/oauth2/token/adfs/oauth2/token", data=data)
    tokens = res.json()

    return tokens["access_token"]


def get_user_token_from_mobile_auth(access_token: str) -> str:
    res = httpx.get(
        "https://mobileauth.it.liu.se/OAuth/authorize",
        # verify=False,
        # proxy="http://localhost:8080",
        params={
            "deviceOsName": "Android",
            "deviceModelName": "Pixel 7 Pro",
            "deviceOsVersion": "16",
            "clientVersion": LIU_APP_VERSION,
        },
        headers={
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {access_token}",
        },
    )

    tokens = res.json()
    pprint(tokens)
    return tokens["UserToken"]

import base64
import json
import os
import urllib.request

from fastapi import FastAPI, Request
from fastapi.responses import Response

CACHE_DIR = "./cache"
FIREBASE_BASE_URL = "firebasestorage.googleapis.com"

app = FastAPI()

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


def save(file: str, download_url: str) -> None:
    if os.path.exists(file):
        return

    with urllib.request.urlopen(download_url) as response:
        content_type = response.getheader("Content-Type")

        file_data = json.dumps({
            "content_type": content_type,
            "content": base64.encodebytes(response.read()).decode("utf-8")
        }).encode("utf-8")

        with open(file, "wb") as f:
            f.write(file_data)


@app.get("/")
def root(url: str, request: Request):
    no_query_url = url.split("?")[0]
    path = no_query_url.split(FIREBASE_BASE_URL)[1]
    path = path.split("/o/")[1]

    download_url = "=".join(str(request.url).split("=")[1:])

    directory = os.path.join(CACHE_DIR, os.path.dirname(path))

    file = os.path.join(CACHE_DIR, path + ".cache")

    if not os.path.exists(directory):
        os.makedirs(directory)

    if not os.path.exists(file):
        save(file, download_url)

    with open(file, "rb") as f:
        content = json.loads(f.read().decode("utf-8"))
        image_content = base64.b64decode(content["content"])
        return Response(content=image_content, media_type=content["content_type"])

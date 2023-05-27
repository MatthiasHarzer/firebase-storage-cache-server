import os
import urllib.request

from fastapi import FastAPI, Request
from fastapi.responses import Response

CACHE_DIR = "./cache"
FIREBASE_BASE_URL = "firebasestorage.googleapis.com"
IMAGE_RESPONSES = {200: {"content": {"image/png": {}}}}

app = FastAPI()

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


@app.get("/", responses=IMAGE_RESPONSES, response_class=Response)
def root(url: str, request: Request):
    remaining_query_params = str(request.url).split("?")[2] if len(str(request.url).split("?")) > 2 else ""

    no_query_url = url.split("?")[0]
    path = no_query_url.split(FIREBASE_BASE_URL)[1]
    storage_base_url = no_query_url.split("/o/")[0] + "/o/"
    path = path.split("/o/")[1]

    path_encoded = path.replace("/", "%2F")

    download_url = storage_base_url + path_encoded + "?" + remaining_query_params

    directory = os.path.join(CACHE_DIR, os.path.dirname(path))
    file = os.path.join(CACHE_DIR, path + ".cache")

    if not os.path.exists(directory):
        os.makedirs(directory)

    if not os.path.exists(file):
        with urllib.request.urlopen(download_url) as response:
            with open(file, "wb") as f:
                f.write(response.read())

    with open(file, "rb") as f:
        return Response(content=f.read(), media_type="image/png")

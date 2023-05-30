import base64
import io
import json
import os
import urllib.request
from dataclasses import dataclass

import PIL
from PIL import Image

from fastapi import FastAPI, Request
from fastapi.responses import Response

CACHE_DIR = "./cache"
FIREBASE_BASE_URL = "firebasestorage.googleapis.com"

app = FastAPI()

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


@dataclass
class CachedImage:
    content_type: str
    content: bytes

    @property
    def response(self) -> Response:
        return Response(content=self.content, media_type=self.content_type)


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


def cache_and_get_image(url: str, request: Request) -> CachedImage:
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
        return CachedImage(content=image_content, content_type=content["content_type"])


def scale_image(cached_image: CachedImage, width: int, height: int) -> CachedImage:
    image_from_bytes = Image.open(io.BytesIO(cached_image.content))
    image_from_bytes.thumbnail((width, height), Image.LANCZOS)

    buffered = io.BytesIO()
    image_from_bytes.save(buffered, format="PNG")

    return CachedImage(content_type=cached_image.content_type, content=buffered.getvalue())


@app.get("/scale/{size}")
def scale(url: str, size: str, request: Request):
    width, height = size.split("x") if "x" in size else (size, size)
    image = cache_and_get_image(url, request)
    try:
        scaled_image = scale_image(image, int(width), int(height))
    except PIL.UnidentifiedImageError:
        return image.response
    return scaled_image.response


@app.get("/")
def root(url: str, request: Request):
    image = cache_and_get_image(url, request)
    return image.response

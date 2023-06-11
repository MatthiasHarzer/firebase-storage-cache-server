import base64
import io
import json
import os
from dataclasses import dataclass

import PIL
import requests
from PIL import Image
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

CACHE_DIR = "./cache"
"""
The directory to cache the assets in.
"""

FIREBASE_BASE_URL = "firebasestorage.googleapis.com"
"""
The base url of the firebase storage.
"""

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@dataclass
class CachedAsset:
    """
    A cached asset with the content and content type.
    """

    content_type: str
    """
    The content type of the asset. This is used to set the content type of the response. E.g. image/png, image/jpeg, ...
    """

    content: bytes
    """
    The raw bytes of the asset.
    """

    @property
    def response(self) -> Response:
        """
        Returns a response object with the content and content type.
        :return:  The response object
        """
        return Response(content=self.content, media_type=self.content_type)


def save(file: str, download_url: str) -> None:
    """
    Saves the file at the given url to the given path.
    :param file: The path to save the file to
    :param download_url:  The url to download the file from
    """

    # If the file is already present, do nothing
    if os.path.exists(file):
        return

    # Download the file
    request = requests.get(download_url)

    # If the request was not successful, raise an exception
    if request.status_code != 200:
        raise HTTPException(status_code=request.status_code, detail=request.reason)

    content_type = request.headers.get("Content-Type")

    # Build the file data
    file_data = json.dumps({
        "content_type": content_type,
        "content": base64.encodebytes(request.content).decode("utf-8")
    }).encode("utf-8")

    directory = os.path.dirname(file)

    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write the file
    with open(file, "wb") as f:
        f.write(file_data)


def check_access_right(url: str) -> None:
    """
    Check if the url is accessible. Private files are protected with a token.
    Check that this request has access to the file.
    :param url: The url to the asset
    :raises HTTPException: If the url is not accessible
    """
    request = requests.head(url)
    if request.status_code != 200:
        raise HTTPException(status_code=request.status_code, detail=request.reason)


def cache_and_get_asset(url: str, request: Request) -> CachedAsset:
    """
    If not present, downloads the asset from the url and saves it to the cache.
    If the asset is already present, checks if the url is still accessible (valid token).
    :param url: The url to the asses
    :param request: The request object
    :return: The cached asset with the content and content type
    """

    # Extract the path from the url
    no_query_url = url.split("?")[0]
    path = no_query_url.split(FIREBASE_BASE_URL)[1]
    path = path.split("/o/")[1]

    download_url = "=".join(str(request.url).split("=")[1:])

    file = os.path.join(CACHE_DIR, path + ".cache")

    # If the file is not present, download it
    if not os.path.exists(file):
        save(file, download_url)

    # If the file is present, check if the url is still accessible
    else:
        check_access_right(download_url)

    # Read the file from the cache
    with open(file, "rb") as f:
        content = json.loads(f.read().decode("utf-8"))
        image_content = base64.b64decode(content["content"])
        return CachedAsset(content=image_content, content_type=content["content_type"])


def scale_image(cached_image: CachedAsset, width: int, height: int) -> CachedAsset:
    """
    Scales the image to the given width and height, while maintaining the aspect ratio.
    :param cached_image:  The cached image
    :param width:  The width to scale to
    :param height:  The height to scale to
    :return:  The scaled image
    """

    image_from_bytes = Image.open(io.BytesIO(cached_image.content))
    image_from_bytes.thumbnail((width, height), Image.LANCZOS)

    buffered = io.BytesIO()
    image_from_bytes.save(buffered, format="PNG")

    return CachedAsset(content_type="image/png", content=buffered.getvalue())


@app.get("/scale/{size}")
def scale(url: str, size: str, request: Request):
    """
    Scales the image to the given size, while maintaining the aspect ratio.
    :param url: The firebase storage url
    :param size:  The size to scale to. This can be a single number (width and height) or <width>x<height>
    :param request:  The request object
    :return: The scaled image or the original asset if the url does not point to an image
    """
    width, height = size.split("x") if "x" in size else (size, size)
    image = cache_and_get_asset(url, request)
    try:
        scaled_image = scale_image(image, int(width), int(height))
    except PIL.UnidentifiedImageError:
        return image.response
    return scaled_image.response


@app.get("/")
def cache(url: str, request: Request):
    """
    Caches the asset at the given url and returns it.
    :param url:  The firebase storage url
    :param request:  The request object
    :return:  The cached asset
    """
    asset = cache_and_get_asset(url, request)
    return asset.response

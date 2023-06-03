# A Simple File Cache Server For [Firebase Cloud Storage](https://firebase.google.com/docs/storage)

Caches files and sclaes images from the Firebase Cloud Storage. This project aims to reduce the traffic of the Firebase Cloud Storage, which is limited to 1GB per day for free, thus cutting costs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Note, that the access rights to the assets will be preserved. The `token` passed with the `url` will be validated by firebase, even when the file is cached on the server.

### Installation
- Copy the [`docker-compose.yml`](./docker-compose.yml) file into your local directory.
- Run `docker compose up -d --build` to start the container.
- The server should now run on `0.0.0.0:9998` (you can change the port in the `docker-compose.yml` file)

### Update
- Run `docker compose down` to stop the running container
- Rebuild and start the container with `docker compose up -d --build`

### How To Use
#### Cache any asset
Instead of using `https://firebasestorage.googleapis.com/v0/b/<PROJECT>/o/...`, make the request to `https://<YOUR-ENDPOINT>/` and provide the query-parameter `url`.

e.g.: `https://<YOUR-ENDPOINT>/?url=https://firebasestorage.googleapis.com/v0/b/<PROJECT>/o/...`

#### Scale images
To scale an image from the cloud storage, use the `/scale/<size>` endpoint. `size` can be `<max-width>x<max-height>` or `<max-height / max-width>` (single parameter). Note, that the aspect ratio of the image will be preserved. The image will be cached as seen above and gets downscaled on the fly. If the requested url does not lead to an image file, the original asset will be returned.

e.g.: 
- `/scale/500x700?url=https://firebasestorage...` Scales the image to `500 x 700` while keeping the aspect ratio.
- `/scale/300?url=https://firebasestorage...` Scales the image to `300 x 300`

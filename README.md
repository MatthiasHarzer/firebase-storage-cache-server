# A Simple File Cache Server For [Firebase Cloud Storage](https://firebase.google.com/docs/storage)

Caches files from the Firebase Cloud Storage. This project aims to reduce the traffic of the Firebase Cloud Storage, which is limited to 1GB per day for free, thus cutting costs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### Warning:
The server caches all requests made to `firebasestorage.googleapis.com` and saves them localy. If the initial request was made with an access-token, any following requests won't check the access-token, thus rendering the content of the requested file public.

### Installation
- Copy the [`docker-compose.yml`](./docker-compose.yml) file into your local directory.
- Run `docker compose up -d --build` to start the container.
- The server should now run on `0.0.0.0:9998` (you can change the port in the `docker-compose.yml` file)

### Update
- Run `docker compose down` to stop the running container
- Rebuild and start the container with `docker compose up -d --build`

### How To Use
Instead of using `https://firebasestorage.googleapis.com/v0/b/<PROJECT>/o/...`, make the request to `https://<YOUR-ENDPOINT>/` and provide the query-parameter `url`.

e.g.: `https://<YOUR-ENDPOINT>/?url=https://firebasestorage.googleapis.com/v0/b/<PROJECT>/o/...`

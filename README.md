# Simple Nginx File Upload App

This example shows a Flask upload app behind Nginx with shared upload storage.

## Features

- File upload form (`/upload`) for allowed extensions
- Lists uploaded files
- Serves uploaded files via `/uploads/<filename>`
- Nginx reverse proxy in front of Flask

## Quick start

```bash
cd /home/fotis/gitea-repo/upload-files
docker compose up --build
```

Access:

- App UI: `http://localhost:9999`
- Uploaded files path: `http://localhost:9999/uploads/<filename>`

## Upload folder

`./uploads` is used by both containers. Nginx serves static files directly from `/var/www/uploads`.

## Extend

- Add auth in Flask
- Limit file size and types (already 100MB + safe types)
- Use HTTPS with certbot + proxy


Run command
with Gunicorn: gunicorn -w 2 wsgi:app
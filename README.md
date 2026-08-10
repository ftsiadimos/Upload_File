# File Upload Application

A robust file upload system built with Flask and Nginx, designed for secure and efficient file handling with shared storage.

## Overview

This application provides a user-friendly interface for uploading files with the following key features:

- File upload form with extension validation
- File listing and management interface
- Direct file serving via `/uploads/<filename>`
- Nginx reverse proxy for production-grade performance
- Shared upload storage between containers

<img src="mis/image.png" alt="UploadFile screenshot" style="border: 4px solid #444; padding: 4px;" />

## Features

| Feature                     | Description                                                                                     |
|-----------------------------|---------------------------------------------------------------------------------------------|
| File Upload Form           | Web interface for uploading files with allowed extensions validation                     |
| File Listing                | View all uploaded files with metadata (name, size, upload date)                           |
| Direct File Access          | Serve uploaded files directly via `/uploads/<filename>` endpoint                           |
| Nginx Reverse Proxy         | Production-ready setup with Nginx in front of Flask application                          |
| Shared Storage              | Persistent upload storage shared between containers                                         |
| Docker Support              | Complete containerized deployment with Docker Compose                                      |
| Gunicorn Support            | Production-ready WSGI server for handling requests                                          |

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Python 3.8+ (for local development)
- Git

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/upload-file.git
   cd upload-file
   ```

2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

## Docker Image

A pre-built Docker image is available on GitHub Container Registry (GHCR):

```bash
docker pull ghcr.io/ftsiadimos/upload_file:latest
```

## Configuration

### Settings File (`app/settings.json`)

The application uses a JSON settings file for runtime configuration. All available settings:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `UPLOAD_FOLDER` | string | `./uploads` | Directory path where uploaded files are stored |
| `MAX_CONTENT_LENGTH` | int | `524288000` (500 MB) | Maximum upload file size in bytes |
| `ALLOWED_EXTENSIONS` | array | See list below | Allowed file extensions for upload |
| `CATEGORIES` | array | See list below | File categories for organization |
| `PAGINATION_PER_CATEGORY` | int | `3` | Number of files displayed per category page |

#### Default Allowed Extensions

```
7z, apk, avi, bz2, c, cpp, css, csv, dmg, docx, exe, flac, gif, gz, h,
hpp, html, ipa, iso, java, jex, jpeg, jpg, js, json, kdbx, log, md, mkv,
mp3, mp4, msi, pdf, png, pptx, py, sql, tar, txt, wav, xlsx, xml, xz,
yaml, yml, zip
```

#### Default Categories

```
Documents, Images, Audio, Video, Archives, Others
```

### Environment Variables

Configure the application using environment variables in your `.env` file:

```env
# Flask Configuration
FLASK_APP=main.py
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key-here

# Upload settings
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=524288000
```

> **Note:** Environment variables take precedence over `settings.json` values where applicable. The `ALLOWED_EXTENSIONS`, `CATEGORIES`, and `PAGINATION_PER_CATEGORY` settings are managed exclusively through `app/settings.json`.

The application uses Docker Compose for container management. Key components:

- **Flask App**: Runs on port 5000
- **Nginx**: Acts as reverse proxy on port 9999
- **Shared Storage**: Files are stored in both `./uploads` (local) and `/var/www/uploads` (container)

## Usage

### Accessing the Application

After starting the containers:

- **Application UI**: `http://localhost:9999`
- **File Upload**: Navigate to `/upload` in the browser
- **File Listing**: View all uploaded files at `/uploads`
- **Direct File Access**: Access files via `http://localhost:9999/uploads/<filename>`

### Running Locally (Without Docker)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   export FLASK_APP=main.py
   flask run
   ```

3. For production, use Gunicorn:
   ```bash
   gunicorn -w 2 main:app
   ```

## Allowed File Extensions

The application restricts uploads to specific file types for security. Extensions are configured in `app/settings.json` under `ALLOWED_EXTENSIONS`.

To change allowed extensions, edit `app/settings.json` and update the `ALLOWED_EXTENSIONS` array.

## File Size Limits

The application enforces a maximum file size of 16MB. To change this limit:

1. Modify the `MAX_CONTENT_LENGTH` environment variable
2. Update the Nginx configuration for client_max_body_size

## Troubleshooting

### Common Issues

**Issue: Application not starting**
- Check Docker containers: `docker-compose ps`
- View logs: `docker-compose logs`
- Ensure ports are not in use

**Issue: Files not appearing**
- Verify the upload folder permissions: `chmod -R 755 uploads`
- Check Nginx configuration for proper file serving
- Ensure Docker volumes are correctly mounted

**Issue: 403 Forbidden errors**
- Verify file permissions in the upload directory
- Check Nginx error logs: `docker-compose logs nginx`
- Ensure the upload folder is accessible by both containers

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`) 
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please contact:

- GitHub Issues: [Open an issue](https://github.com/your-repo/upload-file/issues)

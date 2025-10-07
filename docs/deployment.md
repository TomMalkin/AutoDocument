
# Deployment

Autodocument deploys with three required components.

### Autodocument Components

Autodocument relies on:

*   **Web Application:** The user-facing interface for interacting with Autodocument.
*   **Redis Cache:** A high-performance in-memory data store used to relay messages from the web application to the worker.
*   **Worker Application:** Handles the asynchronous generation of documents, offloading intensive tasks from the web application.

### Deployment Options

To customize your Autodocument deployment, consider the following configuration options available in the `docker-compose.yaml` template:

*   **Admin Password:** Change the default administrator password if you intend on sharing workflows with other users.
*   **Bind Volumes:**
    *   **Purpose:** Mount local directories into the Autodocument containers.
    *   **Benefit:** Allows Autodocument to directly read from and write to your host filesystem, useful for storing generated documents or accessing source files.
*   **Database Persistence:**
    *   **Purpose:** Configure a persistent volume for Autodocument's internal database.
    *   **Benefit:** Safeguards your data across redeployments and upgrades, ensuring you don't lose information when updating your application.
*   **Custom Redis Deployment:**
    *   **Purpose:** Integrate an existing Redis instance instead of using the one provided in the `docker-compose.yaml`.
    *   **Benefit:** Useful if you already have a managed Redis service or prefer to manage Redis separately.

### Get Started

For a comprehensive `docker-compose.yaml` template with detailed explanations for each option, refer to the official source:

[https://github.com/TomMalkin/AutoDocument/blob/main/docker-compose.yaml](https://github.com/TomMalkin/AutoDocument/blob/main/docker-compose.yaml)

### Simplest Docker Compose deployment:

Simply run this docker-compose config to try out Autodocument.

```yaml
services:
  app:
    image: tommalkin/autodocument:latest
    ports:
      - "4605:4605"
    volumes:
      - download_dir:/download_dir
      - upload_dir:/upload_dir
      - db_data:/db_data
    depends_on:
      - redis

  worker:
    image: tommalkin/autodocument-worker:latest
    volumes:
      - download_dir:/download_dir
      - upload_dir:/upload_dir
      - db_data:/db_data
    depends_on:
      - redis
    command: ["dramatiq", "autodoc.tasks", "--processes", "1"]

  redis:
    image: "docker.io/redis:6-alpine"

volumes:
  download_dir: {}
  upload_dir: {}
  db_data: {}
```

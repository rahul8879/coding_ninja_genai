
# Commands Cheat Sheet

| Command                      | Purpose                   |
| ---------------------------- | ------------------------- |
| `docker --version`           | Check Docker installation |
| `docker run hello-world`     | Test Docker               |
| `docker build -t name:tag .` | Build an image            |
| `docker images`              | List images               |
| `docker image ls`            | List images               |
| `docker run`                 | Create + start container  |
| `docker run -d`              | Run in background         |
| `--name`                     | Give container a name     |
| `-p 8000:8000`               | Map host → container port |
| `-e VARIABLE`                | Pass environment variable |
| `docker ps`                  | Running containers        |
| `docker ps -a`               | All containers            |
| `docker logs NAME`           | View logs                 |
| `docker logs -f NAME`        | Follow logs               |
| `docker stop NAME`           | Stop container            |
| `docker start NAME`          | Start stopped container   |
| `docker restart NAME`        | Restart container         |
| `docker rm NAME`             | Remove container          |
| `docker rm -f NAME`          | Force-remove container    |
| `docker rmi IMAGE`           | Remove image              |
| `docker login`               | Login to Docker Hub       |
| `docker push IMAGE`          | Upload image              |
| `docker pull IMAGE`          | Download image            |

---



Don't just memorize commands.

Understand these four:

```text
docker build
     │
     ▼
Creates IMAGE


docker run
     │
     ▼
Creates + Starts CONTAINER


docker push
     │
     ▼
Local Image → Registry


docker pull
     │
     ▼
Registry → Local Image
```

---

# 33. Docker Lifecycle

```text
                    Dockerfile
                        │
                        │ docker build
                        ▼
                      IMAGE
                        │
                        │ docker run
                        ▼
                RUNNING CONTAINER
                        │
                        │ docker stop
                        ▼
                STOPPED CONTAINER
                        │
                        │ docker start
                        ▼
                RUNNING CONTAINER
                        │
                        │ docker rm
                        ▼
                      REMOVED
```

Image remains until:

```bash
docker rmi <image>
```

---


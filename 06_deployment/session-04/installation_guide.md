# Docker Installation Guide

This guide prepares your machine for the Docker demos in Session 4. Follow the section for your operating system, and then complete the verification steps.

## What will be installed

- **Docker Engine** runs containers.
- **Docker CLI** provides the `docker` command.
- **Docker Compose** runs applications made of multiple containers.
- **Docker Desktop** bundles all three in a graphical application for Windows and macOS.

> Docker Desktop is free for personal use, education, non-commercial open-source work, and qualifying small businesses. Review the [Docker subscription terms](https://www.docker.com/legal/docker-subscription-service-agreement/) before commercial use.

## Before you begin

You need:

- A 64-bit machine with hardware virtualization enabled
- At least 4 GB RAM (8 GB or more is recommended)
- Administrator access during installation
- A stable internet connection
- Roughly 10 GB of free disk space for Docker and the course images

Do not install Docker separately inside a WSL distribution when using Docker Desktop for Windows; the two installations can conflict.

---

## Windows 10 or Windows 11 (recommended: WSL 2)

### 1. Check virtualization

Open **Task Manager → Performance → CPU** and confirm that **Virtualization** says **Enabled**. If it is disabled, enable Intel VT-x or AMD-V/SVM in the computer's BIOS/UEFI settings.

### 2. Install or update WSL 2

Open **PowerShell as Administrator** and run:

```powershell
wsl --install
wsl --update
```

Restart Windows if requested. After restarting, check the installation:

```powershell
wsl --version
wsl --status
```

Docker recommends WSL 2.1.5 or later. If `wsl --version` is not recognized, install all pending Windows updates and retry. Microsoft's WSL instructions are available at <https://learn.microsoft.com/windows/wsl/install>.

### 3. Download Docker Desktop

Download the official installer:

<https://www.docker.com/products/docker-desktop/>

Choose the Windows build matching your processor (normally **AMD64**; use **Arm64** only for an ARM-based Windows device).

### 4. Install Docker Desktop

1. Run `Docker Desktop Installer.exe`.
2. Select **Use WSL 2 instead of Hyper-V** when offered.
3. Complete the wizard and restart or sign out if prompted.
4. Open **Docker Desktop** from the Start menu.
5. Accept the subscription agreement.
6. Wait until Docker Desktop reports that the engine is running.

In Docker Desktop, open **Settings → General** and confirm **Use the WSL 2 based engine** is enabled. If you use Ubuntu or another WSL distribution, enable it under **Settings → Resources → WSL Integration**.

Official Windows instructions: <https://docs.docker.com/desktop/setup/install/windows-install/>

---

## macOS

### 1. Identify the Mac processor

Open **Apple menu → About This Mac**:

- **Chip: Apple M-series** → download the Apple silicon installer.
- **Processor: Intel** → download the Intel installer.

### 2. Download and install Docker Desktop

1. Download the correct installer from <https://www.docker.com/products/docker-desktop/>.
2. Open `Docker.dmg`.
3. Drag **Docker** into **Applications**.
4. Open **Applications → Docker**.
5. Accept the subscription agreement and choose the recommended settings.
6. Wait until Docker Desktop reports that the engine is running.

Docker supports the current and two previous major macOS releases and requires at least 4 GB RAM. On Apple silicon, Rosetta 2 is recommended for some AMD64 command-line tools and images:

```bash
softwareupdate --install-rosetta
```

Official macOS instructions: <https://docs.docker.com/desktop/setup/install/mac-install/>

---

## Ubuntu Linux (Docker Engine)

The commands below configure Docker's official `apt` repository. They are intended for supported 64-bit Ubuntu releases. For Debian, Fedora, RHEL, CentOS, or Raspberry Pi OS, use the matching guide at <https://docs.docker.com/engine/install/>.

### 1. Remove conflicting packages

It is safe if this command reports that none are installed:

```bash
sudo apt remove docker.io docker-compose docker-compose-v2 docker-doc \
  docker-buildx podman-docker containerd runc
```

### 2. Add Docker's official repository

```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

```bash
echo "Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: ${UBUNTU_CODENAME:-$(. /etc/os-release && echo "$VERSION_CODENAME")}
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc" | \
  sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null

sudo apt update
```

### 3. Install Docker

```bash
sudo apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
```

Confirm that the service is running:

```bash
sudo systemctl status docker
```

Press `q` to leave the status screen. If the service is stopped, run:

```bash
sudo systemctl enable --now docker
```

### 4. Optional: run Docker without `sudo`

```bash
sudo usermod -aG docker "$USER"
```

Sign out and sign back in for the new group membership to apply. In a temporary terminal session, `newgrp docker` can apply it immediately.

> **Security note:** Membership in the `docker` group grants root-level privileges. Only add trusted users. See <https://docs.docker.com/engine/install/linux-postinstall/>.

Official Ubuntu instructions: <https://docs.docker.com/engine/install/ubuntu/>

---

## Verify the installation

Open a **new** terminal (PowerShell, Terminal, or a Linux shell) and run:

```bash
docker --version
docker compose version
docker info
```

Then run Docker's test container:

```bash
docker run --rm hello-world
```

Docker should download the small image and print **Hello from Docker!**. The `--rm` option automatically removes the stopped test container.

Run one more test to check port mapping:

```bash
docker run --rm -d --name session3-test -p 8080:80 nginx:alpine
```

Open <http://localhost:8080> in a browser. You should see the Nginx welcome page. View the container and stop it:

```bash
docker ps
docker stop session3-test
```

You are ready for Session 3 when all of these checks pass:

- `docker --version` prints a version
- `docker compose version` prints a version
- `docker info` connects to the Docker engine without an error
- `docker run --rm hello-world` succeeds
- <http://localhost:8080> opens during the Nginx test

## Optional Docker Hub sign-in

You do not need an account to run the course demos. An account is required if you later push images to Docker Hub.

Create an account at <https://hub.docker.com/signup>, then sign in through Docker Desktop or run:

```bash
docker login
```

Use a personal access token instead of your password when possible.

## Common problems

### `docker: command not found` or `docker is not recognized`

- Close and reopen the terminal after installation.
- Start Docker Desktop on Windows or macOS.
- On Windows, try the command in PowerShell first and confirm Docker Desktop completed startup.
- On Linux, confirm the packages installed successfully.

### Cannot connect to the Docker daemon

- **Windows/macOS:** Start or restart Docker Desktop and wait for the engine to become ready.
- **Linux:** Run `sudo systemctl start docker` and retry. If the command works only with `sudo`, complete the Linux group setup above.

### WSL or virtualization error on Windows

1. Confirm virtualization is enabled in Task Manager.
2. Run `wsl --update` in an Administrator PowerShell window.
3. Restart Windows.
4. Confirm Docker Desktop uses the WSL 2 engine.

### Port is already allocated

Another application is using the host port. Find the container and stop it:

```bash
docker ps
docker stop <container-id-or-name>
```

Alternatively, map a different host port. For example, use `-p 8081:80` and open <http://localhost:8081>.

### Image pull fails or times out

- Check the internet connection, VPN, proxy, and firewall.
- Restart Docker Desktop.
- If your organization uses a proxy, configure it in **Docker Desktop → Settings → Resources → Proxies**.
- Retry `docker pull hello-world`.

### Apple silicon image warning

Some older images are available only for AMD64. Prefer a multi-platform or ARM64 image. For a one-off compatibility test, use:

```bash
docker run --platform linux/amd64 <image-name>
```

Emulation can be slower than running a native ARM64 image.

## Updating Docker

- **Docker Desktop:** Use **Docker Desktop → Check for updates**, or download the current installer again.
- **Ubuntu:** Run:

  ```bash
  sudo apt update
  sudo apt upgrade
  ```

## Quick command reference

```bash
# Show local images and running containers
docker images
docker ps

# Include stopped containers
docker ps -a

# Download an image
docker pull nginx:alpine

# Stop and remove a container
docker stop <container-name>
docker rm <container-name>

# Remove an unused image
docker rmi <image-name>

# Show disk usage
docker system df
```

## Additional learning resources

- Video walkthrough: <https://www.youtube.com/watch?v=5Mfe54238xE>
- Docker getting started guide: <https://docs.docker.com/get-started/>

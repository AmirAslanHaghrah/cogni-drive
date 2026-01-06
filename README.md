# Cogni-Drive SysMon

**Cogni-Drive SysMon** is a lightweight system monitoring service for **Raspberry Pi OS (Headless)** designed for embedded, robotic, and autonomous driving platforms.

It continuously monitors:
- CPU usage
- RAM usage
- CPU temperature

and provides a **hardware status indicator (blinking LED)** to represent normal system operation.

The project follows a **production-grade Python structure**, supports **DEBUG / RELEASE** modes, and is suitable for long-running services in autonomous systems.

---

## Features

- CPU, RAM, and temperature monitoring  
- GPIO status LED (heartbeat indicator)  
- DEBUG / RELEASE build modes  
- Performance-aware (reduced overhead in RELEASE mode)  
- Clean `src/`-based Python package layout  
- Ready for systemd (auto-start, auto-restart)  
- Testable and extensible architecture  

## Install & Enable Cogni-Drive as a systemd Service

Follow these steps to deploy **Cogni-Drive** as a persistent background service on your system.

---

### 1. Copy the project to `/opt/cogni-drive`

You can either clone the repository directly into `/opt` or copy an existing local copy.

```bash
sudo mkdir -p /opt
sudo cp -r /path/to/your/cogni-drive /opt/cogni-drive
sudo chown -R pi:pi /opt/cogni-drive
```

> Replace `/path/to/your/cogni-drive` with the actual path to your project directory.

---

### 2. Create and prepare the virtual environment

Make sure the Python virtual environment exists inside the project directory and install the project along with its dependencies.

```bash
cd /opt/cogni-drive
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

All required dependencies are installed automatically from `pyproject.toml`.

---

### 3. Install the systemd service

Copy the service file to the systemd directory and enable it.

```bash
sudo cp /opt/cogni-drive/systemd/cogni-drive.service /etc/systemd/system/cogni-drive.service
sudo systemctl daemon-reload
sudo systemctl enable --now cogni-drive
```

This will:
- Register the service
- Start it immediately
- Enable it to start automatically on boot

---

### 4. Check service status and logs

Verify that the service is running correctly and inspect logs if needed.

```bash
sudo systemctl status cogni-drive
journalctl -u cogni-drive -f
```

The `journalctl` command will follow live logs from the Cogni-Drive service.

## Clone Cogni-Drive from GitHub on Raspberry Pi (SSH Method)

This guide explains how to securely clone the **Cogni-Drive** repository on a Raspberry Pi using **SSH keys**.  
Using SSH is recommended for long-term development and deployment on autonomous systems.

---

### 1. Install required tools

Ensure Git and OpenSSH are installed on your Raspberry Pi.

```bash
sudo apt update
sudo apt install -y git openssh-client
```

Verify installation:

```bash
git --version
ssh -V
```

---

### 2. Check for existing SSH keys

Before generating a new key, check if one already exists:

```bash
ls ~/.ssh
```

If you see files like `id_ed25519` and `id_ed25519.pub`, you can reuse them.

---

### 3. Generate a new SSH key (recommended)

Generate a modern and secure SSH key:

```bash
ssh-keygen -t ed25519 -C "cogni-drive@raspberrypi"
```

When prompted:
- Press **Enter** to accept the default file location
- Optionally set a passphrase (recommended for security)

This creates:
- Private key: `~/.ssh/id_ed25519`
- Public key: `~/.ssh/id_ed25519.pub`

---

### 4. Start the SSH agent and add the key

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

---

### 5. Add the SSH key to GitHub

Display your public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

1. Copy the entire output
2. Go to **GitHub → Settings → SSH and GPG keys**
3. Click **New SSH key**
4. Paste the key and give it a recognizable name (e.g., `RaspberryPi-CogniDrive`)
5. Save the key

---

### 6. Test the SSH connection to GitHub

```bash
ssh -T git@github.com
```

You should see a message similar to:

```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

---

### 7. Clone the Cogni-Drive repository

Navigate to your preferred directory (commonly `/opt`):

```bash
cd /opt
git clone git@github.com:your-org/cogni-drive.git
```

Replace `your-org` with your actual GitHub organization or username.

---

### 8. Set correct permissions (recommended)

```bash
sudo chown -R pi:pi /opt/cogni-drive
```

---

### 9. Verify the clone

```bash
cd /opt/cogni-drive
ls
```

You should see files such as:

- `pyproject.toml`
- `config/`
- `src/`
- `systemd/`

---

### Notes

- SSH authentication avoids repeated username/password prompts
- Recommended for headless Raspberry Pi deployments
- Ideal for autonomous vehicle development and field testing

---

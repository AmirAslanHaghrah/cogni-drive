# Cogni-Drive

**Cogni-Drive** is a modular software foundation for an **autonomous vehicle driving system**, designed to run on embedded Linux platforms such as **Raspberry Pi** in headless mode.

The project focuses on **reliability, determinism, and resource awareness**, which are critical requirements in autonomous driving applications. It provides core infrastructure for monitoring system health, managing hardware signals, and serving as a stable base for higher-level autonomy stacks such as perception, localization, planning, and control.

---

## Project Vision

Autonomous driving systems operate under strict real-time and safety constraints.  
Cogni-Drive is designed with the following goals:

- Ensure **continuous awareness of system health**
- Detect abnormal CPU, memory, or thermal conditions early
- Provide a **hardware-level heartbeat indicator** for system liveness
- Support long-running, unattended operation in embedded environments
- Act as a **base layer** beneath perception (vision), decision-making, and control modules

This makes Cogni-Drive suitable for **research prototypes, academic projects, and early industrial deployments** of autonomous vehicles and mobile robots.

---

## Core Capabilities

- Real-time monitoring of:
  - CPU utilization
  - RAM usage
  - CPU temperature
- Hardware heartbeat LED indicating normal system operation
- Dual build modes:
  - **DEBUG** – for development, diagnostics, and experimentation
  - **RELEASE** – optimized for deployment and long-term operation
- Performance-aware design (optional metrics disabled in RELEASE)
- Designed to run as a persistent Linux service (systemd)
- Clean, scalable, production-grade Python project structure

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

📄 README.md
Markdown
# Chockablock: Single-Node Talos Cluster

This project manages a single-node Talos Linux cluster running on a Dell Precision laptop, orchestrated via a Docker-based Matchbox instance.

## 🏗 Architecture
- **Orchestrator:** Docker host (192.168.30.2) running Matchbox.
- **Node:** Dell Precision (192.168.30.185).
- **Provisioning:** PXE Boot -> iPXE -> Matchbox (Assets/Configs).
- **Storage:** Hybrid (RAM-booted with persistence on USB/Internal Disk).

## 🚀 Quick Start (Fresh Deployment)

1. **Prepare the Orchestrator:**
```bash
make all
docker compose up -d
```

2. **Boot the Node:**
Power on the Dell node and ensure it is set to PXE boot. It will pull the kernel and config from Matchbox.

3. **Initialize Kubernetes:**
Once the dashboard on the node shows it is in `Maintenance` or `Running` stage:
```bash
make bootstrap
```

4. **Access the Cluster:**
```bash
talosctl kubeconfig .
export KUBECONFIG=$(pwd)/kubeconfig
make untaint
kubectl get nodes
```

## 🛠 Makefile Commands

| Command | Description |
| :--- | :--- |
| `make install-talosctl` | Installs/Updates the Talos CLI tool. |
| `make download-assets` | Downloads the Talos Kernel and Initrd. |
| `make gen-config` | Generates YAML configs and moves them to Matchbox assets. |
| `make move-config` | Syncs local `talosconfig` to `~/.talos/config`. |
| `make verify` | Checks if Matchbox is correctly serving the config. |
| `make bootstrap` | Triggers the creation of the Etcd cluster. |
| `make untaint` | Allows pods to run on the single control-plane node. |
| `make reset` | Clears Kubernetes state (Soft Reset). |
| `make wipe` | Force-wipes the node's disk (Nuclear Reset). |
| `make clean` | Deletes local YAMLs and secrets. |

## 📁 Directory Structure
- `matchbox-data/assets/`: Stores `vmlinuz`, `initramfs`, and `controlplane.yaml`.
- `matchbox-data/profiles/`: Matchbox profile JSON.
- `matchbox-data/groups/`: Matchbox selector groups.

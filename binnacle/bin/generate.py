import yaml
import os
import json
import subprocess

# 1. Load Talconfig
try:
    with open("talconfig.yaml", 'r') as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"❌ Error loading talconfig.yaml: {e}")
    exit(1)

if not os.path.exists("talsecret.yaml"):
    print("🔐 Generating new talsecret.yaml...")
    # Using talhelper to generate secrets instead of talosctl
    subprocess.run(["talhelper", "gensecret", ">", "talsecret.yaml"], shell=True)

nodes = config.get('nodes', [])
cluster_name = config.get('clusterName', 'myk8s')
# pxe_server must be the IP of your host machine running the containers
pxe_server = "192.168.30.2" 

print(f"📡 Found {len(nodes)} nodes in talconfig.yaml")

# 2. Run Talhelper
print("⚙️ Generating Talos configs via Talhelper...")
subprocess.run(["talhelper", "genconfig", "-o", "./talosconfig"], check=True)

# 3. Process Nodes for dnsmasq & Matchbox
dnsmasq_nodes = []

for node in nodes:
    hostname = node.get('hostname')
    ip = node.get('ipAddress')
    mac = node.get('mac')

    if not mac:
        print(f"⚠️ Warning: No MAC found for {hostname}. Skipping PXE setup for this node.")
        continue

    # dnsmasq entry [cite: 2]
    dnsmasq_nodes.append(f"dhcp-host={mac.lower()},{ip},{hostname},infinite")

    # Matchbox Profile [cite: 2]
    profile_name = f"profile-{hostname}"
    profile_data = {
        "id": profile_name,
        "name": f"Talos {hostname}",
        "boot": {
            "kernel": "/assets/vmlinuz",
            "initrd": ["/assets/initramfs.xz"],
            "args": [
                "initrd=initramfs.xz",
                f"talos.config=http://{pxe_server}:8081/assets/{cluster_name}-{hostname}.yaml",
                "talos.platform=metal"
            ]
        }
    }
    with open(f"matchbox-data/profiles/{profile_name}.json", 'w') as f:
        json.dump(profile_data, f, indent=2)

    # Matchbox Group [cite: 2]
    group_data = {
        "id": hostname,
        "name": f"Group for {hostname}",
        "profile": profile_name,
        "selector": { "mac": mac.lower() }
    }
    with open(f"matchbox-data/groups/{hostname}.json", 'w') as f:
        json.dump(group_data, f, indent=2)

# Write out the dnsmasq/nodes.conf [cite: 13]
with open("dnsmasq/nodes.conf", 'w') as f:
    f.write("\n".join(dnsmasq_nodes))

# 4. Final step: Copy all generated assets to Matchbox [cite: 13]
subprocess.run(f"cp talosconfig/{cluster_name}-*.yaml matchbox-data/assets/", shell=True)

print(f"✅ Successfully updated PXE configs for {len(dnsmasq_nodes)} nodes.")
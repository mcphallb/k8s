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

nodes = config.get('nodes', [])
cluster_name = config.get('clusterName', 'myk8s')
pxe_server = "192.168.30.2" 

# 2. Ensure directories exist 
os.makedirs("dnsmasq", exist_ok=True)
os.makedirs("talosconfig", exist_ok=True)
os.makedirs("matchbox-data/assets", exist_ok=True)

# 3. Handle Secrets (Switching to talsecret.yaml)
if not os.path.exists("talsecret.yaml"):
    print("🔐 Generating new talsecret.yaml...")
    subprocess.run("talhelper gensecret > talsecret.yaml", shell=True, check=True)

# 4. Run Talhelper
print("⚙️ Generating Talos configs via Talhelper...")
subprocess.run(["talhelper", "genconfig", "-o", "./talosconfig"], check=True)

# 5. Generate dnsmasq.conf (Ensures it is a FILE, not a directory) [cite: 11]
dnsmasq_content = f"""interface=eth0
bind-interfaces
dhcp-range=192.168.30.50,192.168.30.250,24h
dhcp-option=option:router,192.168.30.1
dhcp-boot=tag:!ipxe,ipxe.efi,,{pxe_server}
dhcp-boot=tag:ipxe,http://{pxe_server}:8081/boot.ipxe
conf-file=/etc/dnsmasq.d/nodes.conf
"""
with open("dnsmasq/dnsmasq.conf", 'w') as f:
    f.write(dnsmasq_content)

# 6. Process Nodes (dnsmasq/nodes.conf and Matchbox)
dnsmasq_nodes = []
for node in nodes:
    mac = node.get('mac')
    if mac:
        dnsmasq_nodes.append(f"dhcp-host={mac.lower()},{node['ipAddress']},{node['hostname']},infinite")
        # Profile/Group logic here...

with open("dnsmasq/nodes.conf", 'w') as f:
    f.write("\n".join(dnsmasq_nodes))

# 7. Copy assets for Matchbox
subprocess.run(f"cp talosconfig/{cluster_name}-*.yaml matchbox-data/assets/", shell=True)
print("✅ Config generation complete.")
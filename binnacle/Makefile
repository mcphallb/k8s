# --- Dynamic Variables (Extract from Inventory) ---
# Pulls the first controlplane IP for talosctl context setting
# Revised for Python yq (jq-based)
#NODE_IP := $(shell yq -r '.nodes[] | select(.type == "controlplane") | .ip' inventory.yaml | head -n 1)
#CLUSTER_NAME := $(shell yq -r '.cluster_name' inventory.yaml)
NODE_IP := $(shell yq -r '.nodes[] | select(.controlPlane == true) | .ipAddress' talconfig.yaml | head -n 1)
CLUSTER_NAME := $(shell yq -r '.clusterName' talconfig.yaml)
TALOS_VERSION := $(strip v1.6.1) # Change this as needed
ASSETS_DIR := matchbox-data/assets
MATCHBOX_PORT := 8081

# --- 1. THE "GOD MODE" COMMANDS ---

# First time setup: installs tools, gets images, generates configs, restarts infra
init: prereqs download-assets update verify-all
	@echo "🚀 SYSTEM INITIALIZED. Power on nodes and run 'make bootstrap' when ready."

# Standard update: run this when you edit inventory.yaml
update: 
	@echo "⚙️ Regenerating via Talhelper..."
	python3 bin/generate.py
	@mkdir -p ~/.talos
	# Note: talhelper names files as cluster-hostname.yaml
	@cp talosconfig/talosconfig ~/.talos/config
	@echo "♻️ Restarting Network Stack..."
	docker compose restart dnsmasq matchbox

# --- 2. PREREQUISITES & ASSETS ---

prereqs:
	@echo "--- Checking Tools ---"
	@which yq > /dev/null || (echo "❌ yq missing. Install via 'pip install yq'"; exit 1)
	@which python3 > /dev/null || (echo "❌ python3 missing"; exit 1)
	@which talosctl > /dev/null || (echo "--- Installing talosctl ---" && curl -sL https://talos.dev/install | sh)
	@mkdir -p $(ASSETS_DIR) dnsmasq matchbox-data/groups matchbox-data/profiles talosconfig
	@which talhelper > /dev/null || (echo "❌ talhelper missing. Install via 'curl https://i.jpillora.com/budimanjojo/talhelper! | sudo bash
'"; exit 1)

download-assets:
	@echo "--- Checking for Talos $(TALOS_VERSION) PXE Assets ---"
	@mkdir -p $(ASSETS_DIR)
	# Check if file is missing or empty, then download
	@[ -s $(ASSETS_DIR)/vmlinuz ] || curl -fL "https://github.com/siderolabs/talos/releases/download/$(strip $(TALOS_VERSION))/vmlinuz-amd64" -o $(ASSETS_DIR)/vmlinuz
	@[ -s $(ASSETS_DIR)/initramfs.xz ] || curl -fL "https://github.com/siderolabs/talos/releases/download/$(strip $(TALOS_VERSION))/initramfs-amd64.xz" -o $(ASSETS_DIR)/initramfs.xz
	@echo "📥 Downloading iPXE bootloaders..."
	@[ -s $(ASSETS_DIR)/ipxe.efi ] || curl -fL "https://boot.ipxe.org/x86_64-efi-sb/ipxe.efi" -o $(ASSETS_DIR)/ipxe.efi
	@[ -s $(ASSETS_DIR)/undionly.kpxe ] || curl -fL "https://boot.ipxe.org/x86_64-pcbios/undionly.kpxe" -o $(ASSETS_DIR)/undionly.kpxe
	@echo "✅ Assets verified in $(ASSETS_DIR)"

# --- 3. VERIFICATION ---

verify-all:
	@echo "--- Verifying Infrastructure ---"
	@curl -I -s -f http://127.0.0.1:$(MATCHBOX_PORT)/assets/vmlinuz > /dev/null || (echo "❌ Matchbox not serving vmlinuz"; exit 1)
	@docker compose ps dnsmasq | grep -q "Up" || (echo "❌ Dnsmasq container is down"; exit 1)
	@echo "✅ Everything looks good at $(NODE_IP)"

# --- 4. CLUSTER OPS ---

bootstrap:
	talosctl bootstrap --talosconfig talosconfig/talosconfig -n $(NODE_IP) -e $(NODE_IP)

kubeconfig:
	talosctl kubeconfig .
	@echo "✅ Kubeconfig generated. Run: export KUBECONFIG=$(shell pwd)/kubeconfig"

deploy-argocd:
	@echo "Installing ArgoCD using Server-Side Apply..."
	@kubectl create namespace argocd || true
	@kubectl apply -n argocd --server-side -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# --- 5. CLEANUP ---

# Safe clean: keeps secrets.yaml so you don't break TLS authority
clean:
	@echo "Deleting configs! "
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@rm -f talosconfig/controlplane.yaml talosconfig/worker.yaml talosconfig/talosconfig kubeconfig
	@rm -f $(ASSETS_DIR)/*.yaml $(ASSETS_DIR)/*.json
	@rm -f matchbox-data/groups/*.json
	@rm -f matchbox-data/profiles/*.json
	@rm -f matchbox-data/configs/*.yaml
	@rm -f dnsmasq/*.conf
	@echo "🧹 Cleaned local and asset configs."

# Only use this if you want to wipe the CA and start totally fresh
nuclear-reset: clean
	@echo "Deleting secrets.yaml!"
	@echo -n "Are you sure? This will make cluster unusable! [y/N] " && read ans && [ $${ans:-N} = y ]
	@rm -f talosconfig/secrets.yaml
	@rm -f matchbox-data/assets/*
	@echo "☢️  Root Secrets DELETED. Run 'make init' to start over."

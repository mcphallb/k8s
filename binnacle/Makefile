# Variables
TALOS_VERSION  := v1.12.3
MATCHBOX_IP    := 192.168.30.2
MATCHBOX_URL   := http://$(MATCHBOX_IP):8080

MB_ASSET_DIR   := ./matchbox/assets
MB_PROFILE_DIR := ./matchbox/profile
MB_GROUP_DIR   := ./matchbox/groups

.PHONY: all clean fetch gen-all up

all: fetch gen-all up

fetch:
	@echo "==> Fetching iPXE bootloaders..."
	mkdir -p ./tftpboot
	curl -fL "https://boot.ipxe.org/x86_64-efi-sb/ipxe.efi" -o ./tftpboot/ipxe.efi
	curl -fL "https://boot.ipxe.org/x86_64-pcbios/undionly.kpxe" -o ./tftpboot/undionly.kpxe
	#curl -L https://github.com/poseidon/matchbox/raw/main/tftp/ipxe.efi -o ./tftpboot/ipxe.efi
	#curl -L https://github.com/poseidon/matchbox/raw/main/tftp/undionly.kpxe -o ./tftpboot/undionly.kpxe
	@echo "==> Fetching Talos $(TALOS_VERSION) assets..."
	mkdir -p ${MB_ASSET_DIR}/talos/$(TALOS_VERSION)
	curl -L https://github.com/siderolabs/talos/releases/download/$(TALOS_VERSION)/vmlinuz-amd64 -o ${MB_ASSET_DIR}/talos/$(TALOS_VERSION)/vmlinuz
	curl -L https://github.com/siderolabs/talos/releases/download/$(TALOS_VERSION)/initramfs-amd64.xz -o ${MB_ASSET_DIR}/talos/$(TALOS_VERSION)/initramfs.xz

# 1. Generate secrets once so they persist
gen-secrets:
	@if [ ! -f talsecret.yaml ]; then \
		talhelper gensecret > talsecret.yaml; \
	fi

gen-configs: gen-secrets
	@echo "==> Generating Talos configs via talhelper..."
	talhelper genconfig --config-file talconfig.yaml --secret-file talsecret.yaml --out-dir ./clusterconfig
	@echo "==> Generating specific Matchbox Groups and Profiles..."
	@mkdir -p ${MB_GROUP_DIR} ${MB_PROFILE_DIR} ${MB_ASSET_DIR}/talos/$(TALOS_VERSION)
	@rm -f ./dnsmasq/static-leases.conf
	@grep -v '^#' nodes.txt | grep '[^[:space:]]' | while read -r host mac ip type; do \
		printf 'dhcp-host=%s,%s,%s,infinite\n' "$$mac" "$$ip" "$$host" >> ./dnsmasq/static-leases.conf; \
		# Create a Group that points to a specific profile for THIS host \
		printf '{"id":"%s","name":"%s","profile":"profile-%s","selector":{"mac":"%s"}}' "$$host" "$$host" "$$host" "$$mac" > ${MB_GROUP_DIR}/$$host.json; \
		# Create a Hardcoded Profile for THIS host \
		printf '{"id":"profile-%s","name":"Talos %s","boot":{"kernel":"/assets/talos/$(TALOS_VERSION)/vmlinuz","initrd":["/assets/talos/$(TALOS_VERSION)/initramfs.xz"],"args":["initrd=initramfs.xz","talos.config=http://$(MATCHBOX_IP):8080/assets/metal-cluster-%s.yaml","talos.platform=metal","slab_nomerge","pti=on"]}}' "$$host" "$$host" "$$host" > ${MB_PROFILE_DIR}/profile-$$host.json; \
		cp ./clusterconfig/metal-cluster-$$host.yaml ${MB_ASSET_DIR}/metal-cluster-$$host.yaml; \
	done

up:
	docker compose up -d

clean:
	@echo "==> Cleaning up generated configurations and assets..."
	@# Remove generated Talos machine configs
	rm -rf ./clusterconfig
	@# Remove Matchbox dynamic configs (keep the directory structure)
	rm -f ${MB_GROUP_DIR}/*.json
	rm -f ${MB_PROFILE_DIR}/*.json
	@# Remove staged assets in Matchbox (YAMLs and Binaries)
	rm -rf ${MB_ASSET_DIR}/*
	@# Remove generated dnsmasq leases
	rm -f ./dnsmasq/static-leases.conf
	@# Remove iPXE bootloaders
	rm -rf ./tftpboot
	@echo "==> Clean complete."

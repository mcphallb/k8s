# Create the directory structure
mkdir -p ./matchbox-data/assets

# Set the Talos version
export TALOS_VERSION=$(curl -s https://api.github.com/repos/siderolabs/talos/releases/latest | grep tag_name | cut -d '"' -f 4)

# Download Kernel and Initramfs
wget -O ./matchbox-data/assets/vmlinuz https://github.com/siderolabs/talos/releases/download/${TALOS_VERSION}/vmlinuz-amd64
wget -O ./matchbox-data/assets/initramfs.xz https://github.com/siderolabs/talos/releases/download/${TALOS_VERSION}/initramfs.xz

# Makefile for installing development environment
# Supports Debian/Ubuntu and Rocky Linux/RHEL/CentOS

.PHONY: all install-all install-python install-uv install-docker install-gnmic install-containerlab detect-os help

# Main entry point - always detects OS first
all: detect-os

# This should be the internal target that requires OS to be set
install-all: install-python install-uv install-docker install-gnmic install-containerlab
	@echo "✅ All tools installed successfully!"

# Detect operating system
detect-os:
	@echo "🔍 Detecting operating system..."
	@if [ -f /etc/debian_version ]; then \
		echo "📋 Detected: Debian/Ubuntu"; \
		$(MAKE) OS=debian install-all; \
	elif [ -f /etc/rocky-release ] || [ -f /etc/redhat-release ]; then \
		echo "📋 Detected: Rocky Linux/RHEL"; \
		$(MAKE) OS=rocky install-all; \
	else \
		echo "❌ Unsupported OS. This Makefile supports Debian/Ubuntu and Rocky Linux/RHEL only."; \
		exit 1; \
	fi

# Install Python
install-python:
	@echo "🐍 Installing Python..."
ifeq ($(OS),debian)
	sudo apt update
	sudo apt install -y python3 python3-pip python3-venv
else ifeq ($(OS),rocky)
	sudo dnf install -y python3 python3-pip python3-venv
endif
	@echo "✅ Python installed"

# Install uv
install-uv:
	@echo "⚡ Installing uv..."
	curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo "✅ uv installed (restart shell or run: source ~/.bashrc)"

# Install Docker
install-docker:
	@echo "🐳 Installing Docker..."
	curl -sL https://containerlab.dev/setup | sudo -E bash -s "install-docker"

	# Start and enable Docker
	sudo systemctl start docker
	sudo systemctl enable docker
	# Add current user to docker group
	sudo usermod -aG docker $$USER
	@echo "✅ Docker installed (logout/login required for group changes)"

# Install gnmic
install-gnmic:
	@echo "📊 Installing gnmic..."
	# Download latest release
	curl -sL https://get-gnmic.openconfig.net | sudo -E bash
	@echo "✅ gnmic installed"

# Install Containerlab
install-containerlab:
	@echo "🧪 Installing Containerlab..."
	# Download and install latest release
	curl -sL https://containerlab.dev/setup | sudo -E bash -s "install-containerlab"
	@echo "✅ Containerlab installed"

# Setup Python project environment
setup-project:
	@echo "🔧 Setting up Python project environment..."
	@if [ -f pyproject.toml ]; then \
		echo "📦 Found pyproject.toml, installing dependencies..."; \
		~/.cargo/bin/uv sync; \
		echo "✅ Project environment ready!"; \
		echo "💡 Use 'uv run <script>' to run Python scripts"; \
	else \
		echo "⚠️  No pyproject.toml found in current directory"; \
	fi
	@if [ -f gnmi/shell_gnmic.sh ]; then \
		echo "🔧 Making gnmi/shell_gnmic.sh executable..."; \
		chmod +x gnmi/shell_gnmic.sh; \
		echo "✅ gnmi/shell_gnmic.sh is now executable"; \
	else \
		echo "⚠️  gnmi/shell_gnmic.sh not found, skipping chmod"; \
	fi

# Verify installations
verify:
	@echo "🔍 Verifying installations..."
	@python3 --version || echo "❌ Python not found"
	@~/.local/bin/uv --version || echo "❌ uv not found"
	@docker --version || echo "❌ Docker not found"
	@gnmic version || echo "❌ gnmic not found"
	@containerlab version || echo "❌ Containerlab not found"

# Clean up downloaded files
clean:
	@echo "🧹 Cleaning up..."
	rm -f gnmic

# Help target
help:
	@echo "Available targets:"
	@echo "  all              - Install all tools (auto-detects OS)"
	@echo "  install-python   - Install Python 3"
	@echo "  install-uv       - Install uv package manager"
	@echo "  install-docker   - Install Docker"
	@echo "  install-gnmic    - Install gnmic"
	@echo "  install-containerlab - Install Containerlab"
	@echo "  setup-project    - Setup Python project with uv"
	@echo "  verify           - Verify all installations"
	@echo "  clean            - Clean up downloaded files"
	@echo "  help             - Show this help"
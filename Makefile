.PHONY: build clean install dev-frontend dev-backend deploy-local translate-videos process-azure help

FRONTEND_DIR = frontend
BACKEND_DIR = backend
BUILD_DIR = $(FRONTEND_DIR)/dist
STATIC_DIR = $(BACKEND_DIR)/static
TRANSLATIONS_DIR = translations
ORIGINAL_VIDEOS_DIR = $(TRANSLATIONS_DIR)/original
AZURE_VIDEOS_DIR = $(TRANSLATIONS_DIR)/azure
TRANSLATED_VIDEOS_DIR = $(TRANSLATIONS_DIR)/translated
BACKEND_VIDEOS_DIR = $(BACKEND_DIR)/videos


help:
	@echo "Available commands:"
	@echo "  make install             - Install all dependencies (frontend & backend)"
	@echo "  make build               - Build React app and copy to backend/static"
	@echo "  make clean               - Remove build artifacts"
	@echo "  make dev-frontend        - Run frontend dev server"
	@echo "  make dev-backend         - Run backend dev server"
	@echo "  make deploy-local        - Full build and run production server"
	@echo "  make process-azure       - Create modality videos from Azure translations"

install:
	@echo "Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && npm install
	@echo "Installing backend dependencies..."
	cd $(BACKEND_DIR) && pip install -r requirements.txt
	@echo "Installing translation dependencies..."
	cd $(TRANSLATIONS_DIR) && pip install -r requirements.txt
	@echo "All dependencies installed"

build:
	@echo "Building React app..."
	cd $(FRONTEND_DIR) && npm run build
	@echo "Cleaning old static files..."
	rm -rf $(STATIC_DIR)
	@echo "Copying build to backend/static..."
	cp -r $(BUILD_DIR) $(STATIC_DIR)
	@echo "Build complete! Static files are in $(STATIC_DIR)"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR)
	rm -rf $(STATIC_DIR)
	rm -rf $(FRONTEND_DIR)/node_modules/.vite
	@echo "Clean complete"

dev-frontend:
	@echo "Starting frontend dev server..."
	cd $(FRONTEND_DIR) && npm run dev

dev-backend:
	@echo "Starting backend dev server on port 3000..."
	cd $(BACKEND_DIR) && source venv/bin/activate && python app.py

deploy-local: clean build
	@echo "Starting production server on port 3000..."
	cd $(BACKEND_DIR) && source venv/bin/activate && gunicorn -w 4 -b 0.0.0.0:3000 app:app

process-azure:
	@echo "Processing Azure-translated videos..."
	@mkdir -p $(ORIGINAL_VIDEOS_DIR)
	@mkdir -p $(AZURE_VIDEOS_DIR)
	@mkdir -p $(TRANSLATED_VIDEOS_DIR)
	@echo ""
	@echo "Checking for videos..."
	@if [ ! "$$(ls -A $(ORIGINAL_VIDEOS_DIR)/*.{mp4,mov,avi,mkv} 2>/dev/null)" ]; then \
		echo "ERROR: No videos found in $(ORIGINAL_VIDEOS_DIR)"; \
		exit 1; \
	fi
	@if [ ! "$$(ls -A $(AZURE_VIDEOS_DIR)/*.{mp4,mov,avi,mkv} 2>/dev/null)" ]; then \
		echo "ERROR: No videos found in $(AZURE_VIDEOS_DIR)"; \
		exit 1; \
	fi
	@echo ""
	cd $(TRANSLATIONS_DIR) && python process_azure_videos.py --original-dir original --azure-dir azure --translated-dir translated
	@echo ""
	@echo "Processing complete!"
	@echo "Output: $(TRANSLATED_VIDEOS_DIR)/"
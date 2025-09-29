.PHONY: build clean install dev-frontend dev-backend deploy-local help

FRONTEND_DIR = frontend
BACKEND_DIR = backend
BUILD_DIR = $(FRONTEND_DIR)/dist
STATIC_DIR = $(BACKEND_DIR)/static

help:
	@echo "Available commands:"
	@echo "  make install        - Install all dependencies (frontend & backend)"
	@echo "  make build          - Build React app and copy to backend/static"
	@echo "  make clean          - Remove build artifacts"
	@echo "  make dev-frontend   - Run frontend dev server"
	@echo "  make dev-backend    - Run backend dev server"
	@echo "  make deploy-local   - Full build and run production server"

# install dependencies
install:
	@echo "Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && npm install
	@echo "Installing backend dependencies..."
	cd $(BACKEND_DIR) && pip install -r requirements.txt
	@echo "✓ All dependencies installed"

# build frontend React app and copy to backend folder so Flask serves
build:
	@echo "Building React app..."
	cd $(FRONTEND_DIR) && npm run build
	@echo "Cleaning old static files..."
	rm -rf $(STATIC_DIR)
	@echo "Copying build to backend/static..."
	cp -r $(BUILD_DIR) $(STATIC_DIR)
	@echo "✓ Build complete! Static files are in $(STATIC_DIR)"

# clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR)
	rm -rf $(STATIC_DIR)
	rm -rf $(FRONTEND_DIR)/node_modules/.vite
	@echo "✓ Clean complete"

# run frontend dev server
dev-frontend:
	@echo "Starting frontend dev server..."
	cd $(FRONTEND_DIR) && npm run dev

# run backend dev server
dev-backend:
	@echo "Starting backend dev server..."
	cd $(BACKEND_DIR) && source venv/bin/activate && python app.py

# full deployment build for Render
deploy-local: clean build
	@echo "Starting production server..."
	cd $(BACKEND_DIR) && source venv/bin/activate && gunicorn -w 4 -b 0.0.0.0:3000 app:app
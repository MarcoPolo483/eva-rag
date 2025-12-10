"""Test script to verify FastAPI app loads and show available routes."""
import sys
sys.path.insert(0, "src")

from eva_rag.main import app

print("✅ FastAPI app loaded successfully")
print("\n📍 Available routes:")
for route in app.routes:
    if hasattr(route, "path"):
        methods = getattr(route, "methods", {"GET"})
        print(f"  {', '.join(methods):8} {route.path}")

print("\n🔍 Space API endpoints:")
space_routes = [r for r in app.routes if hasattr(r, "path") and "/spaces" in r.path]
for route in space_routes:
    methods = getattr(route, "methods", {"GET"})
    print(f"  {', '.join(methods):8} {route.path}")

print("\n✅ All imports successful - server ready to start!")

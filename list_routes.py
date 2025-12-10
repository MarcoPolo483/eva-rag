"""List all registered API routes."""
import sys
sys.path.insert(0, 'src')

from eva_rag.main import app

print('✅ FastAPI app loaded with all routers')
print('')
print('REGISTERED ROUTES:')

routes = [r for r in app.routes if hasattr(r, 'path') and r.path.startswith('/api/v1')]
for r in sorted(routes, key=lambda x: x.path):
    methods = ', '.join(r.methods) if hasattr(r, 'methods') else ''
    print(f'  [{methods:20s}] {r.path}')

print('')
print(f'Total API routes: {len(routes)}')

# Mintly Frontend Guide

## Overview

Mintly now has **two frontend options**:

1. **Python/Jinja2 Frontend** (Original) - Server-side rendered HTML
2. **Node.js/React Frontend** (New) - Modern single-page application

Both frontends use the **same Python FastAPI backend** and **DuckDB database**.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│                                             │
│  React Frontend (Port 3000)                 │
│  - Modern SPA                               │
│  - Recharts visualizations                  │
│  - Component-based                          │
│                                             │
└──────────────────┬──────────────────────────┘
                   │
                   │ HTTP/REST API
                   │
┌──────────────────▼──────────────────────────┐
│                                             │
│  Python Backend (Port 8000)                 │
│  - FastAPI                                  │
│  - CSV Parsers                              │
│  - Auto-categorization                      │
│  - DuckDB integration                       │
│                                             │
└──────────────────┬──────────────────────────┘
                   │
                   │
┌──────────────────▼──────────────────────────┐
│                                             │
│  DuckDB Database                            │
│  - Local storage                            │
│  - Efficient queries                        │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Quick Start

### Option 1: React Frontend + Python Backend (Docker)

```bash
docker-compose up --build
```

- **React Frontend**: http://localhost:3000
- **Python Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Python Frontend Only (Original)

```bash
docker-compose up backend
```

- Access at: http://localhost:8000

### Option 3: Local Development

**Terminal 1 - Backend:**
```bash
pip install -r requirements.txt
python app/main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Comparison

| Feature | Python/Jinja2 | React/Node.js |
|---------|---------------|---------------|
| **Technology** | Server-side rendering | Single-page app |
| **Port** | 8000 | 3000 |
| **Charts** | Plotly (server-rendered) | Recharts (client-side) |
| **Interactivity** | Page reloads | Real-time updates |
| **Build Time** | None | ~30 seconds |
| **Bundle Size** | N/A | ~200KB (gzipped) |
| **SEO** | Better | Good with SSR |
| **Deployment** | Simple | Requires build step |

---

## When to Use Which?

### Use Python/Jinja2 Frontend If:
- ✅ You want simplicity
- ✅ You don't need a build process
- ✅ You prefer server-side rendering
- ✅ You want to minimize dependencies

### Use React/Node.js Frontend If:
- ✅ You want modern UX
- ✅ You need real-time updates
- ✅ You want component reusability
- ✅ You prefer client-side rendering
- ✅ You're building a larger app

---

## Development Workflow

### Backend Changes

Both frontends automatically use updated APIs:

```bash
# Edit app/database.py, app/models.py, etc.
# Backend hot-reloads automatically
```

### React Frontend Changes

```bash
cd frontend
npm run dev
# Edit src/components/*.jsx
# Vite hot-reloads instantly
```

### Python Frontend Changes

```bash
# Edit app/templates/*.html
# Refresh browser to see changes
```

---

## API Communication

Both frontends call the same REST APIs:

### Example: Upload Transactions

**React:**
```javascript
import { uploadTransactions } from './services/api'

const result = await uploadTransactions(file)
```

**Python/Jinja2:**
```javascript
const formData = new FormData()
formData.append('file', file)

fetch('/api/transactions/upload', {
  method: 'POST',
  body: formData
})
```

---

## Deployment Options

### Option 1: Both Frontends (Recommended for Development)

```yaml
# docker-compose.yml
services:
  backend:
    ports:
      - "8000:8000"
  frontend:
    ports:
      - "3000:3000"
```

### Option 2: React Frontend Only

```yaml
services:
  backend:
    ports:
      - "8000:8000"
  frontend:
    ports:
      - "80:3000"  # Expose on port 80
```

### Option 3: Python Frontend Only

```yaml
services:
  backend:
    ports:
      - "80:8000"  # Expose on port 80
```

---

## Environment Variables

### Backend (.env or docker-compose.yml)
```
PYTHONUNBUFFERED=1
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api  # Local dev
VITE_API_URL=http://backend:8000/api    # Docker
```

---

## Adding New Features

### 1. Add Backend Endpoint

`app/api/transactions.py`:
```python
@router.get("/new-endpoint")
async def new_feature():
    return {"data": "value"}
```

### 2. Add to API Client

`frontend/src/services/api.js`:
```javascript
export const getNewData = async () => {
  const response = await api.get('/transactions/new-endpoint')
  return response.data
}
```

### 3. Use in Component

`frontend/src/components/MyComponent.jsx`:
```javascript
import { getNewData } from '../services/api'

const data = await getNewData()
```

### 4. Update Python Template (Optional)

`app/templates/page.html`:
```javascript
fetch('/api/transactions/new-endpoint')
  .then(res => res.json())
  .then(data => console.log(data))
```

---

## Testing

### Test Backend
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/transactions/categories
```

### Test React Frontend
```bash
# Visit http://localhost:3000
# Open browser console
# Check network tab for API calls
```

### Test Python Frontend
```bash
# Visit http://localhost:8000
# Use browser dev tools
```

---

## Troubleshooting

### React Can't Connect to Backend

**Problem:** `Network Error` in console

**Solution:**
```javascript
// Check vite.config.js proxy settings
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

### CORS Errors

**Problem:** `CORS policy` errors

**Solution:** Backend should have CORS enabled:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Docker Containers Can't Communicate

**Problem:** Frontend can't reach backend

**Solution:** Use service names:
```yaml
# In docker-compose.yml
environment:
  - VITE_API_URL=http://backend:8000/api
```

---

## Performance

### React Frontend
- First load: ~1s
- Subsequent navigation: Instant
- Chart rendering: Fast (client-side)

### Python Frontend
- First load: ~500ms
- Subsequent pages: ~300ms
- Chart rendering: Fast (Plotly)

---

## Security

Both frontends:
- ✅ No sensitive data in frontend code
- ✅ API authentication handled by backend
- ✅ HTTPS recommended for production
- ✅ Input validation on backend
- ✅ CORS properly configured

---

## Production Deployment

### Nginx Reverse Proxy

```nginx
# Serve React frontend
location / {
    proxy_pass http://frontend:3000;
}

# Proxy API requests to backend
location /api {
    proxy_pass http://backend:8000;
}
```

### Alternative: Static Build

```bash
cd frontend
npm run build

# Serve dist/ folder with nginx
# Point API to backend URL
```

---

## Future Enhancements

- [ ] Add authentication
- [ ] Real-time WebSocket updates
- [ ] Progressive Web App (PWA)
- [ ] Mobile app (React Native)
- [ ] Server-side rendering (Next.js)
- [ ] GraphQL API

---

## Support

- **React Issues**: Check `frontend/README.md`
- **API Issues**: Check API docs at `/docs`
- **General**: Check main `README.md`


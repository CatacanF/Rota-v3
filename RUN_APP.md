# 🚀 How to Run Rota-v1

Since we have upgraded to a robust **Clean Architecture**, the app now consists of multiple services (API, Database, Redis, Worker).

## 1. Start the Backend (Docker)

Open a terminal in the project root (`sonic-granule`) and run:

```bash
docker-compose up --build
```

This will start:
- 🟢 **API**: http://localhost:8000
- 🟢 **Database**: TimescaleDB (Port 5432)
- 🟢 **Redis**: Port 6379
- 🟢 **Worker**: Background tasks

## 2. Start the Frontend

Open a new terminal in `sonic-granule/frontend` and run:

```bash
npm run dev
```

This will start:
- 🔵 **Web App**: http://localhost:5173

## 3. Access the App

- **Dashboard**: [http://localhost:5173](http://localhost:5173)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### ⚠️ Troubleshooting

**"Docker not found"**
- Ensure Docker Desktop is installed and running.

**"Port already in use"**
- Stop any running python scripts or containers.
- `docker-compose down` to clean up old containers.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import nav_router, nodes_router, edges_router
app = FastAPI(title="KuMap API")

# Настройка CORS для фронтенда (Next.js обычно на 3000 порту)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры KuMap
app.include_router(nodes_router, prefix="/api/v1/nodes", tags=["Nodes"])
app.include_router(edges_router, prefix="/api/v1/edges", tags=["Edges"])
app.include_router(nav_router, prefix="/api/v1/navigation", tags=["Navigation"])

@app.get("/health")
def health_check():
    return {"status": "online", "system": "KuMap Engine", "db": "PostGIS"}
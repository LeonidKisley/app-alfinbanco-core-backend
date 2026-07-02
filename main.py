import os  # <-- Librería del sistema agregada
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Importamos únicamente los routers operacionales activos
from app.routes import (
    rtr_auth, rtr_cartera, rtr_preeval, rtr_campanas, rtr_cliente
)

# Inicializamos FastAPI configurando las Docs nativas de forma segura y personalizada
app = FastAPI(
    title="ALFIN Banco",
    description="API Backend para los servicios móviles y operaciones principales de Alfin Banco",
    version="1.0.0",
    docs_url="/docs",  # Permitimos que FastAPI sirva la ruta nativamente
    swagger_ui_favicon_url="/static/alfinbancologo.png",  # Cambia el favicon por tu logo corporativo
    swagger_ui_parameters={"deepLinking": True, "defaultModelsExpandDepth": -1} 
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Montaje de la carpeta static para los logos/imágenes locales
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Configuración de CORS habilitada para desarrollo y apps móviles (Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTRO DE ROUTERS ACTIVOS DE ALFIN BANCO ---
app.include_router(rtr_auth.router,    prefix="/auth",         tags=["Auth - Fuerza de Ventas"])
app.include_router(rtr_cartera.router, prefix="/cartera",      tags=["Cartera - Agenda Diaria"])
app.include_router(rtr_preeval.router, prefix="/pre-evaluar",  tags=["PreEvaluacion - Créditos"])
app.include_router(rtr_campanas.router, prefix="/campanas",     tags=["Campanas - Productos Comerciales"])
app.include_router(rtr_cliente.router, prefix="/cliente",      tags=["Cliente - Canales Digitales"])

@app.get("/")
def root():
    return {"sistema": "Core Mobile ALFIN Banco", "version": "1.0.0", "status": "ok"}
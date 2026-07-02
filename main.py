import os  # <-- Librería del sistema agregada
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.routes import (
    rtr_auth, rtr_cartera, rtr_ficha, rtr_cobranza, rtr_preeval, rtr_buro,
    rtr_solicitudes, rtr_reportes, rtr_alertas, rtr_campanas, rtr_sync,
    rtr_cliente,
)

# Inicializamos FastAPI desactivando las docs por defecto (docs_url=None) 
app = FastAPI(
    title="ALFIN Banco",
    description="API Backend para los servicios móviles y operaciones principales de Alfin Banco",
    version="1.0.0",
    docs_url=None, 
    swagger_ui_parameters={"deepLinking": True, "defaultModelsExpandDepth": -1} 
)

# 🛠️ TRUCO DE RUTA ABSOLUTA: Calcula la ubicación exacta real de tu carpeta static
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Montamos la carpeta usando la ruta absoluta calculada por Python
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # apps moviles (Flutter / Android) — ajustar en produccion
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rtr_auth.router,    prefix="/auth",     tags=["Auth"])
app.include_router(rtr_cartera.router, prefix="/cartera",  tags=["Cartera"])
app.include_router(rtr_ficha.router,   prefix="/clientes", tags=["Ficha"])
app.include_router(rtr_cobranza.router, prefix="/cobranza", tags=["Cobranza"])
app.include_router(rtr_preeval.router, prefix="/pre-evaluar", tags=["PreEvaluacion"])
app.include_router(rtr_buro.router,    prefix="/buro",      tags=["Buro"])
app.include_router(rtr_solicitudes.router, prefix="/solicitudes", tags=["Solicitudes"])
app.include_router(rtr_reportes.router, prefix="/reportes", tags=["Reportes"])
app.include_router(rtr_alertas.router, prefix="/alertas", tags=["Alertas"])
app.include_router(rtr_campanas.router, prefix="/campanas", tags=["Campanas"])
app.include_router(rtr_sync.router, prefix="/sync", tags=["Sync (Puente al Core)"])

# App de clientes (appbanco / Flutter clientes) — login DNI + productos
app.include_router(rtr_cliente.router, prefix="/cliente", tags=["Cliente (App)"])


# --- SOBREESCRITURA DE LA RUTA /DOCS CON TU ICONO LOCAL ---
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Documentación",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="/static/alfinbancologo.png",  
    )
    
    custom_css = """
    <style>
        .swagger-ui .info .title { color: #FF6B00 !important; font-family: sans-serif; }
        .swagger-ui .btn.authorize { border-color: #FF6B00 !important; color: #FF6B00 !important; }
        .swagger-ui .btn.authorize svg { fill: #FF6B00 !important; }
        .swagger-ui .btn.authorize.locked { background-color: #FF6B00 !important; color: white !important; }
        .swagger-ui .btn.authorize.locked svg { fill: white !important; }
        .swagger-ui .opblock-tag { border-bottom: 1px solid #FF6B00 !important; }
    </style>
    """
    
    body_content = response.body.decode("utf-8").replace("</body>", f"{custom_css}</body>")
    return HTMLResponse(content=body_content)

@app.get("/")
def root():
    return {"sistema": "Core Mobile ALFIN Banco", "version": "1.0.0", "status": "ok"}
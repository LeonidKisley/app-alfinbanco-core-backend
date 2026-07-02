# Core Mobile — ALFIN Banco (FastAPI)

Capa operacional de canales móviles corporativos. La consumen la **app Flutter de fuerza de ventas** (para asesores de negocios) y la **app de clientes (appbanco_s8)**. Alimenta al núcleo `bd_core_financiero` vía servicio de promoción (tabla `sync_outbox`).

- DB: **Supabase PostgreSQL** (Cloud / AWS) · Puerto API: **8003**
- Stack: FastAPI · SQLAlchemy 2 · JWT (python-jose) · bcrypt (passlib)

## Puesta en marcha

```powershell
# 1) Entorno virtual
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2) Configuración de variables de entorno
# Asegúrate de configurar tu archivo .env en la raíz con la cadena de Supabase:
# DATABASE_URL="postgresql://postgres.ktzqtgtbpzimlmosksws:Celestesana1214%40%40%40@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

# 3) Levantar la API de ALFIN Banco (escuchando en toda la red para que el teléfono lo alcance)
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8003
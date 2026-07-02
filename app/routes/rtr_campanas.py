from datetime import date
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.cfg_database import get_db
from app.core.cfg_auth import get_current_asesor

router = APIRouter()


class CampanaOut(BaseModel):
    id: str
    cliente_id: str
    cliente_nombre: str
    tipo: Optional[str] = None
    monto_ofertado: float
    fecha_vencimiento: Optional[str] = None
    dias_restantes: int


@router.get("", response_model=list[CampanaOut])
def listar(
    db: Session = Depends(get_db),
    asesor: dict = Depends(get_current_asesor),
):
    """Campañas activas asignadas al asesor en ALFIN Banco, ordenadas por vencimiento."""
    rows = db.execute(
        text(
            """
            SELECT ca.id, ca.cliente_id, ca.tipo, ca.monto_ofertado,
                   ca.fecha_vencimiento, c.nombres, c.apellidos
            FROM campanas_activas ca
            JOIN clientes c ON c.id = ca.cliente_id
            WHERE ca.asesor_id = :asesor AND ca.activa = TRUE
              AND (ca.fecha_vencimiento IS NULL OR ca.fecha_vencimiento >= :hoy)
            ORDER BY ca.fecha_vencimiento ASC NULLS LAST
            """
        ),
        {"asesor": asesor["asesor_id"], "hoy": date.today()},
    ).mappings().all()
    
    hoy = date.today()
    resultado = []
    
    for r in rows:
        # --- ESTRATEGIA DE ADAPTACIÓN COMERCIAL ALFIN BANCO ---
        # Si la base de datos tiene nombres genéricos o vacíos, los homologamos a los productos del banco
        tipo_original = r["tipo"]
        tipo_alfin = "Crédito Al Toque ALFIN"  # Valor por defecto corporativo
        
        if tipo_original:
            tipo_lower = tipo_original.lower()
            if "consumo" in tipo_lower or "personal" in tipo_lower:
                tipo_alfin = "Crédito Al Toque ALFIN"
            elif "pyme" in tipo_lower or "comercial" in tipo_lower or "negocio" in tipo_lower:
                tipo_alfin = "Capital de Trabajo Emprendedor ALFIN"
            elif "ahorro" in tipo_lower or "pasivo" in tipo_lower:
                tipo_alfin = "Campaña Multiplica Tus Ahorros"
            else:
                # Si viene otro valor, lo decoramos con la marca
                tipo_alfin = f"{tipo_original} ALFIN"

        resultado.append(
            CampanaOut(
                id=str(r["id"]),
                cliente_id=str(r["cliente_id"]),
                cliente_nombre=f"{r['nombres']} {r['apellidos']}",
                tipo=tipo_alfin,
                monto_ofertado=float(r["monto_ofertado"] or 0),
                fecha_vencimiento=r["fecha_vencimiento"].isoformat() if r["fecha_vencimiento"] else None,
                dias_restantes=(r["fecha_vencimiento"] - hoy).days if r["fecha_vencimiento"] else 0,
            )
        )
        
    return resultado
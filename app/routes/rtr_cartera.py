from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.cfg_database import get_db
from app.core.cfg_auth import get_current_asesor
from app.schemas.sch_cartera import CarteraItemOut, MarcarVisitaIn
from app.repositories import rep_cartera

router = APIRouter()

@router.get("", response_model=list[CarteraItemOut])
def listar_cartera(
    fecha: date | None = None,
    db: Session = Depends(get_db),
     asesor: dict = Depends(get_current_asesor),
):
    """
    Recupera la cartera diaria de clientes asignada al asesor de negocios autenticado en ALFIN Banco.
    
    Permite filtrar por una fecha específica o por defecto toma el día actual para organizar las visitas 
    de campo enfocadas en prospección, evaluación comercial o cobranza preventiva.
    """
    f = fecha or date.today()
    return rep_cartera.listar_por_asesor(db, asesor["asesor_id"], f)

@router.post("/{cartera_id}/visita")
def marcar_visita(
    cartera_id: str,
    data: MarcarVisitaIn,
    db: Session = Depends(get_db),
    asesor: dict = Depends(get_current_asesor),
):
    """
    Registra formalmente el resultado de una visita de campo efectuada por el asesor.
    
    Actualiza el estado de la gestión (ej. Contactado, Promesa de Pago, Cliente Interesado en Crédito) 
    dentro del flujo operacional de ALFIN Banco.
    """
    ok = rep_cartera.marcar_visita(db, asesor["asesor_id"], cartera_id, data.model_dump())
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="El ítem de cartera o cliente especificado no pertenece al asesor o no se encuentra registrado en el core de ALFIN Banco."
        )
    return {
        "status": "ok", 
        "mensaje": "Gestión de campo registrada exitosamente en el sistema de ALFIN Banco.",
        "cartera_id": cartera_id, 
        "estado_visita": data.resultado
    }
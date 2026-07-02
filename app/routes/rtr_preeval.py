from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from app.core.cfg_auth import get_current_asesor

router = APIRouter()


class PreEvalIn(BaseModel):
    # Forzamos a que el documento sea un DNI válido de 8 dígitos para el mercado peruano
    numero_documento: str = Field(..., min_length=8, max_length=8, description="DNI del cliente (8 dígitos)")
    nombres: str = ""
    tipo_negocio: str = "" 
    ingresos_estimados: float = 0
    monto_solicitado: float = 0
    destino_credito: str = ""  


class PreEvalOut(BaseModel):
    calificacion: str   
    motivo: str
    puntaje: int
    campana_sugerida: Optional[str] = None  # Añadimos valor comercial de ALFIN Banco


@router.post("", response_model=PreEvalOut)
def pre_evaluar(data: PreEvalIn, asesor: dict = Depends(get_current_asesor)):
    """
    Pre-evaluación crediticia adaptada al motor de scoring de ALFIN Banco.

    Regla basada en capacidad de pago microfinanciera y relación monto vs. ingresos.
    En producción esto conectaría con el Core Bancario y Buró (Experian/Equifax).
    """
    # Validación inicial de negocio en Perú: El DNI debe ser puramente numérico
    if not data.numero_documento.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El número de documento debe ser un DNI válido de 8 dígitos numéricos."
        )

    ingresos_anuales = max(data.ingresos_estimados, 1) * 12
    ratio = data.monto_solicitado / ingresos_anuales if ingresos_anuales else 99

    # Escenario 1: Sin ingresos declarados
    if data.ingresos_estimados <= 0:
        return PreEvalOut(
            calificacion="REVISAR",
            motivo="Ingresos no declarados. Requiere evaluación en campo por el asesor de ALFIN Banco.",
            puntaje=50,
            campana_sugerida="Evaluación Tradicional Pyme"
        )
        
    # Escenario 2: Excelente capacidad de pago (Filtro verde para Crédito rápido)
    if ratio <= 0.6:
        return PreEvalOut(
            calificacion="APTO",
            motivo="Capacidad de pago suficiente. Califica para desembolso inmediato en canales digitales ALFIN.",
            puntaje=85,
            campana_sugerida="Crédito al Toque ALFIN"
        )
        
    # Escenario 3: Ratio intermedio (Requiere sustento o aval)
    if ratio <= 1.2:
        return PreEvalOut(
            calificacion="REVISAR",
            motivo="El monto solicitado es elevado para su rango de ingresos. Sujeto a evaluación de comité.",
            puntaje=60,
            campana_sugerida="Crédito Emprendedor / Capital de Trabajo"
        )
        
    # Escenario 4: Sobreendeudamiento
    return PreEvalOut(
        calificacion="NO_PROCEDE",
        motivo="El monto solicitado supera las políticas de endeudamiento y capacidad de pago vigentes de ALFIN Banco.",
        puntaje=25,
        campana_sugerida=None
    )
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.cfg_database import get_db
from app.schemas.sch_auth import LoginIn, TokenOut
from app.controllers import ctl_auth

router = APIRouter()

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    """
    Autenticación institucional para la Fuerza de Ventas de ALFIN Banco.
    
    Permite el ingreso de asesores de negocios mediante su código de empleado y contraseña corporativa.
    Retorna un JSON Web Token (JWT) válido para consumir la cartera y realizar pre-evaluaciones.
    """
    
    # Validación básica de estructura para el código de empleado corporativo
    if not data.codigo_empleado or len(data.codigo_empleado.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El formato del código de empleado ingresado no es válido para el sistema ALFIN."
        )

    result = ctl_auth.login(db, data.codigo_empleado, data.password)
    
    if result and result.get("_bloqueado"):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Cuenta corporativa bloqueada temporalmente por exceso de intentos fallidos. Restricción activa hasta las {result['hasta']}. Contactar con Soporte TI ALFIN.",
        )
        
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Las credenciales ingresadas no corresponden a un asesor activo en ALFIN Banco."
        )
        
    return result
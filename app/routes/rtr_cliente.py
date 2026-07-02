"""
Rutas de la app de clientes (appbanco / Flutter clientes) para ALFIN Banco.

Login con DNI (usuarios_cliente) y consulta de productos del cliente
autenticado: cuentas de ahorro, créditos + cronograma, movimientos,
tarjetas y notificaciones. Todas (excepto login) requieren Bearer token.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.cfg_database import get_db
from app.core.cfg_auth import get_current_cliente
from app.schemas.sch_cliente import (
    LoginClienteIn, TokenClienteOut, ClienteOut, CuentaAhorroOut, CreditoOut,
    CuotaOut, MovimientoOut, TarjetaOut, NotificacionOut, OperacionIn, OperacionOut,
)
from app.controllers import ctl_auth_cliente
from app.repositories import rep_cliente

router = APIRouter()


@router.post("/login", response_model=TokenClienteOut)
def login(data: LoginClienteIn, db: Session = Depends(get_db)):
    """Login institucional del cliente ALFIN Banco (numero_documento + password) -> JWT."""
    
    # Validación estricta para el mercado peruano: DNI debe tener 8 caracteres y ser numérico
    if len(data.numero_documento) != 8 or not data.numero_documento.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El número de documento ingresado debe ser un DNI válido de 8 dígitos."
        )

    result = ctl_auth_cliente.login(db, data.numero_documento, data.password)
    
    if result and result.get("_bloqueado"):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED, 
            detail="Por seguridad, tu Banca Móvil ALFIN ha sido bloqueada temporalmente por exceso de intentos fallidos. Por favor, comunícate con atención al cliente."
        )
        
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Las credenciales ingresadas no son válidas en el sistema de ALFIN Banco."
        )
        
    return result


@router.get("/perfil", response_model=ClienteOut)
def perfil(db: Session = Depends(get_db), cli: dict = Depends(get_current_cliente)):
    """Recupera el perfil del cliente autenticado en la plataforma ALFIN."""
    cliente = rep_cliente.get_cliente(db, cli["cliente_id"])
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Registro de cliente no localizado en el core de ALFIN Banco."
        )
    return cliente


@router.get("/cuentas", response_model=list[CuentaAhorroOut])
def cuentas(db: Session = Depends(get_db), cli: dict = Depends(get_current_cliente)):
    """Lista las cuentas de ahorros activas del cliente (ej. Cuenta Ahorro ALFIN, Cuenta Conectada)."""
    return rep_cliente.cuentas_ahorro(db, cli["cliente_id"])


@router.get("/creditos", response_model=list[CreditoOut])
def creditos(db: Session = Depends(get_db), cli: dict = Depends(get_current_cliente)):
    """Muestra los créditos vigentes del cliente (Crédito al Toque, Capital de Trabajo, etc.)."""
    return rep_cliente.creditos(db, cli["cliente_id"])


@router.get("/creditos/{cod_cuenta_credito}/cronograma", response_model=list[CuotaOut])
def cronograma(
    cod_cuenta_credito: str,
    db: Session = Depends(get_db),
    cli: dict = Depends(get_current_cliente),
):
    """Consulta el cronograma oficial de pagos y cuotas pendientes del crédito ALFIN."""
    return rep_cliente.cronograma(db, cod_cuenta_credito)


@router.get("/movimientos", response_model=list[MovimientoOut])
def movimientos(
    limit: int = 20,
    db: Session = Depends(get_db),
    cli: dict = Depends(get_current_cliente),
):
    """Historial reciente de transacciones y movimientos financieros del cliente."""
    return rep_cliente.movimientos(db, cli["cliente_id"], limit)


@router.get("/tarjetas", response_model=list[TarjetaOut])
def tarjetas(db: Session = Depends(get_db), cli: dict = Depends(get_current_cliente)):
    """Lista las tarjetas de débito o crédito asociadas al cliente ALFIN."""
    return rep_cliente.tarjetas(db, cli["cliente_id"])


@router.get("/notificaciones", response_model=list[NotificacionOut])
def notificaciones(db: Session = Depends(get_db), cli: dict = Depends(get_current_cliente)):
    """Alertas de seguridad, transferencias recibidas y avisos de cobranza de ALFIN Banco."""
    return rep_cliente.notificaciones(db, cli["cliente_id"])


@router.post("/operaciones", response_model=OperacionOut)
def crear_operacion(
    data: OperacionIn,
    db: Session = Depends(get_db),
    cli: dict = Depends(get_current_cliente),
):
    """
    Registra una operación financiera iniciada desde la App Móvil Flutter.
    Soporta pagos de servicios, transferencias internas e interbancarias de ALFIN.
    """
    return rep_cliente.crear_operacion(db, cli["cliente_id"], data.model_dump())
# =============================================================================
# Módulo: reserva.py
# Responsable: Integrante 4
# Descripción: Clase Reserva que integra cliente, servicio, duración y estado.
#              Implementa confirmar, cancelar y procesar con try/except/else/
#              finally y ENCADENAMIENTO de excepciones (raise ... from ...).
# =============================================================================

from cliente import Cliente  # Para verificar el tipo de cliente
from entidades import EntidadBase  # Clase abstracta padre
from excepciones import (  # Excepciones que se usan aquí
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ReservaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)
from logger import obtener_logger  # Logger del sistema
from servicios import Servicio  # Para verificar el tipo de servicio

log = obtener_logger()  # Logger compartido


class Reserva(EntidadBase):  # HEREDA de EntidadBase
    """Reserva de un servicio por parte de un cliente."""

    PENDIENTE = "PENDIENTE"  # Recién creada
    CONFIRMADA = "CONFIRMADA"  # Validada y aceptada
    CANCELADA = "CANCELADA"  # Anulada
    PROCESADA = "PROCESADA"  # Cobrada / finalizada

    def __init__(self, cliente, servicio, horas, **detalles):  # Datos de la reserva
        super().__init__("RES")  # Id con prefijo RES
        if cliente is None:  # Cliente obligatorio
            raise ParametroFaltanteError("cliente")  # Error
        if servicio is None:  # Servicio obligatorio
            raise ParametroFaltanteError("servicio")  # Error
        if not isinstance(cliente, Cliente):  # Debe ser un objeto Cliente
            raise ReservaError("El cliente de la reserva no es válido")  # Error
        if not isinstance(servicio, Servicio):  # Debe ser un objeto Servicio
            raise ReservaError("El servicio de la reserva no es válido")  # Error
        self.__cliente = cliente  # Atributo privado
        self.__servicio = servicio  # Atributo privado
        self.__horas = horas  # Duración en horas
        self.__detalles = detalles  # Datos extra (personas, cantidad...)
        self.__estado = Reserva.PENDIENTE  # Toda reserva inicia pendiente
        self.__costo_final = None  # Se calcula al procesar

    # ---------------- Getters (encapsulación) ----------------
    @property
    def cliente(self):  # Lee el cliente
        return self.__cliente

    @property
    def servicio(self):  # Lee el servicio
        return self.__servicio

    @property
    def estado(self):  # Lee el estado
        return self.__estado

    @property
    def costo_final(self):  # Lee el costo final
        return self.__costo_final

    # ---------------- Confirmar ----------------
    def confirmar(self):  # Pasa de PENDIENTE a CONFIRMADA
        if self.__estado != Reserva.PENDIENTE:  # Solo se confirman reservas pendientes
            raise OperacionNoPermitidaError(  # Error de operación
                f"No se puede confirmar {self.id}: estado actual {self.__estado}"
            )
        if not self.__servicio.disponible:  # El servicio debe estar disponible
            raise ServicioNoDisponibleError(self.__servicio.nombre)  # Error
        try:  # Validamos los parámetros con las reglas del servicio
            self.__servicio.validar_parametros(self.__horas, **self.__detalles)  # Polimorfismo
        except (ServicioInvalidoError, ParametroFaltanteError) as error:  # Si los parámetros fallan
            raise ReservaError(f"Reserva {self.id} rechazada: {error.mensaje}") from error  # ENCADENAMIENTO
        else:  # Solo se ejecuta si NO hubo error
            self.__estado = Reserva.CONFIRMADA  # Cambia el estado
            log.info(f"Reserva {self.id} confirmada ({self.__cliente.nombre} -> {self.__servicio.nombre})")  # Log

    # ---------------- Cancelar ----------------
    def cancelar(self, motivo="Sin motivo"):  # Anula la reserva
        if self.__estado in (Reserva.CANCELADA, Reserva.PROCESADA):  # No se cancela lo ya cerrado
            raise OperacionNoPermitidaError(  # Error
                f"No se puede cancelar {self.id}: ya está {self.__estado}"
            )
        self.__estado = Reserva.CANCELADA  # Cambia el estado
        log.info(f"Reserva {self.id} cancelada. Motivo: {motivo}")  # Log

    # ---------------- Procesar ----------------
    def procesar(self, impuesto=Servicio.IMPUESTO_IVA, descuento=None):  # Calcula el cobro final
        if self.__estado != Reserva.CONFIRMADA:  # Solo se procesan reservas confirmadas
            raise OperacionNoPermitidaError(  # Error
                f"No se puede procesar {self.id}: estado actual {self.__estado}"
            )
        try:  # Intentamos calcular el costo
            costo = self.__servicio.calcular_costo(  # Método sobrecargado
                self.__horas, impuesto=impuesto, descuento=descuento, **self.__detalles
            )
        except CalculoInconsistenteError as error:  # Error en el cálculo
            raise ReservaError(f"Error al procesar {self.id}: {error.mensaje}") from error  # ENCADENAMIENTO
        else:  # Si el cálculo fue correcto
            self.__costo_final = costo  # Guarda el costo
            self.__estado = Reserva.PROCESADA  # Cambia el estado
            log.info(f"Reserva {self.id} procesada. Total: ${costo:,.2f}")  # Log
            return costo  # Devuelve el total
        finally:  # Se ejecuta SIEMPRE, con o sin error
            log.debug(f"Intento de procesamiento de {self.id} finalizado (estado: {self.__estado})")  # Log de auditoría

    # ---------------- Métodos abstractos implementados ----------------
    def validar(self):  # Valida la reserva completa
        self.__cliente.validar()  # Valida el cliente
        self.__servicio.validar_parametros(self.__horas, **self.__detalles)  # Valida el servicio
        return True  # Válida

    def describir(self):  # Descripción de la reserva (polimorfismo)
        costo = f"${self.__costo_final:,.2f}" if self.__costo_final else "por calcular"  # Texto del costo
        return (f"{self.id} | {self.__cliente.nombre} | {self.__servicio.nombre} | "
                f"{self.__horas} h | {self.__estado} | {costo}")

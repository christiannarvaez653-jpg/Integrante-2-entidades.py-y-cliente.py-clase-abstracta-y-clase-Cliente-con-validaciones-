# =============================================================================
# Módulo: servicios.py
# Responsable: Integrante 3
# Descripción: Clase abstracta Servicio y tres servicios especializados:
#              ReservaSala, AlquilerEquipo y Asesoria. Aplica HERENCIA,
#              POLIMORFISMO (métodos sobrescritos) y SOBRECARGA de cálculo.
# =============================================================================

import math  # Para verificar que los números sean finitos
from abc import abstractmethod  # Para declarar métodos abstractos

from entidades import EntidadBase  # Clase abstracta padre
from excepciones import (  # Excepciones personalizadas que usaremos
    CalculoInconsistenteError,
    ParametroFaltanteError,
    ServicioInvalidoError,
)


class Servicio(EntidadBase):  # Clase ABSTRACTA (sigue siendo abstracta porque no implementa todo)
    """Servicio general ofrecido por Software FJ."""

    IMPUESTO_IVA = 0.19  # IVA por defecto en Colombia (19 %)

    def __init__(self, nombre, tarifa_hora, disponible=True):  # Datos comunes a todo servicio
        super().__init__("SRV")  # Id con prefijo SRV
        if not nombre or not str(nombre).strip():  # Nombre obligatorio
            raise ParametroFaltanteError("nombre del servicio")  # Error si falta
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:  # Tarifa numérica y positiva
            raise ServicioInvalidoError(f"Tarifa inválida para '{nombre}': {tarifa_hora}")  # Error
        self._nombre = str(nombre).strip()  # Atributo protegido (accesible a hijas)
        self._tarifa_hora = float(tarifa_hora)  # Tarifa por hora
        self._disponible = bool(disponible)  # Estado de disponibilidad

    @property  # Getter
    def nombre(self):  # Lee el nombre
        return self._nombre  # Devuelve el nombre

    @property  # Getter
    def disponible(self):  # Lee si está disponible
        return self._disponible  # True o False

    def cambiar_disponibilidad(self, estado):  # Activa o desactiva el servicio
        self._disponible = bool(estado)  # Cambia el estado

    # ---------- Métodos abstractos: cada hija los SOBRESCRIBE ----------
    @abstractmethod  # Obligatorio en las hijas
    def validar_parametros(self, horas, **detalles):  # Reglas propias de cada servicio
        """Valida las horas y detalles; lanza ServicioInvalidoError si algo falla."""

    @abstractmethod  # Obligatorio en las hijas
    def costo_base(self, horas, **detalles):  # Fórmula de costo propia de cada servicio
        """Calcula el costo sin impuestos ni descuentos."""

    # ---------- Validación común de horas ----------
    def _validar_horas(self, horas, minimo, maximo):  # Reutilizable por todas las hijas
        if horas is None:  # Si no se enviaron horas
            raise ParametroFaltanteError("horas")  # Error de parámetro faltante
        if not isinstance(horas, (int, float)) or not (minimo <= horas <= maximo):  # Fuera de rango
            raise ServicioInvalidoError(  # Error de servicio
                f"'{self.nombre}': las horas deben estar entre {minimo} y {maximo} (recibido: {horas})"
            )

    # ---------- SOBRECARGA del cálculo de costos ----------
    # Python no admite varios métodos con el mismo nombre, así que la sobrecarga
    # se implementa con parámetros opcionales. Se puede llamar de 4 formas:
    #   calcular_costo(horas)                          -> costo base
    #   calcular_costo(horas, impuesto=0.19)           -> con impuesto
    #   calcular_costo(horas, descuento=0.10)          -> con descuento
    #   calcular_costo(horas, impuesto=0.19, descuento=0.10, **detalles) -> completo
    def calcular_costo(self, horas, impuesto=None, descuento=None, **detalles):
        """Calcula el costo final con impuesto y/o descuento opcionales."""
        self.validar_parametros(horas, **detalles)  # Primero valida (polimórfico)
        total = self.costo_base(horas, **detalles)  # Costo base (polimórfico)
        if descuento is not None:  # Variante con descuento
            if not 0 <= descuento < 1:  # El descuento debe ser entre 0 % y 99 %
                raise CalculoInconsistenteError(f"Descuento inválido: {descuento}")  # Error de cálculo
            total *= (1 - descuento)  # Aplica el descuento
        if impuesto is not None:  # Variante con impuesto
            if not 0 <= impuesto <= 1:  # El impuesto debe estar entre 0 % y 100 %
                raise CalculoInconsistenteError(f"Impuesto inválido: {impuesto}")  # Error de cálculo
            total *= (1 + impuesto)  # Aplica el impuesto
        if not math.isfinite(total) or total <= 0:  # Resultado imposible (negativo, infinito, NaN)
            raise CalculoInconsistenteError(f"Costo inconsistente calculado: {total}")  # Error de cálculo
        return round(total, 2)  # Devuelve con 2 decimales

    def validar(self):  # Implementa el método abstracto de EntidadBase
        if self._tarifa_hora <= 0:  # Revisión de seguridad
            raise ServicioInvalidoError("Tarifa no válida")  # Error
        return True  # Válido


# =============================================================================
# Servicio 1: Reserva de salas
# =============================================================================
class ReservaSala(Servicio):  # HEREDA de Servicio
    """Alquiler de salas de reuniones por horas."""

    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):  # Agrega capacidad
        super().__init__(nombre, tarifa_hora, disponible)  # Inicializa la parte común
        if not isinstance(capacidad, int) or capacidad <= 0:  # Capacidad entera positiva
            raise ServicioInvalidoError(f"Capacidad inválida para sala '{nombre}': {capacidad}")  # Error
        self._capacidad = capacidad  # Guarda la capacidad máxima

    def validar_parametros(self, horas, **detalles):  # SOBRESCRIBE la validación
        self._validar_horas(horas, 1, 12)  # Una sala se reserva de 1 a 12 horas
        personas = detalles.get("personas")  # Número de asistentes
        if personas is None:  # Es obligatorio para salas
            raise ParametroFaltanteError("personas")  # Error
        if personas > self._capacidad:  # Supera la capacidad
            raise ServicioInvalidoError(  # Error
                f"La sala '{self.nombre}' admite {self._capacidad} personas (solicitadas: {personas})"
            )

    def costo_base(self, horas, **detalles):  # SOBRESCRIBE el costo
        return self._tarifa_hora * horas  # Tarifa × horas

    def describir(self):  # SOBRESCRIBE la descripción
        return f"{self.id} | Sala '{self.nombre}' | Capacidad {self._capacidad} | ${self._tarifa_hora:,.0f}/h"


# =============================================================================
# Servicio 2: Alquiler de equipos
# =============================================================================
class AlquilerEquipo(Servicio):  # HEREDA de Servicio
    """Alquiler de equipos (portátiles, proyectores, etc.)."""

    def __init__(self, nombre, tarifa_hora, unidades, deposito, disponible=True):  # Agrega unidades y depósito
        super().__init__(nombre, tarifa_hora, disponible)  # Parte común
        if not isinstance(unidades, int) or unidades <= 0:  # Unidades enteras positivas
            raise ServicioInvalidoError(f"Unidades inválidas para '{nombre}': {unidades}")  # Error
        if deposito < 0:  # El depósito no puede ser negativo
            raise ServicioInvalidoError(f"Depósito negativo para '{nombre}': {deposito}")  # Error
        self._unidades = unidades  # Unidades disponibles
        self._deposito = float(deposito)  # Valor del depósito de garantía

    def validar_parametros(self, horas, **detalles):  # SOBRESCRIBE la validación
        self._validar_horas(horas, 1, 72)  # Se alquila de 1 a 72 horas
        cantidad = detalles.get("cantidad", 1)  # Por defecto 1 equipo
        if not isinstance(cantidad, int) or cantidad <= 0:  # Cantidad válida
            raise ServicioInvalidoError(f"Cantidad inválida: {cantidad}")  # Error
        if cantidad > self._unidades:  # No hay suficientes equipos
            raise ServicioInvalidoError(  # Error
                f"Solo hay {self._unidades} unidades de '{self.nombre}' (solicitadas: {cantidad})"
            )

    def costo_base(self, horas, **detalles):  # SOBRESCRIBE el costo
        cantidad = detalles.get("cantidad", 1)  # Número de equipos
        return self._tarifa_hora * horas * cantidad + self._deposito  # Tarifa × horas × cantidad + depósito

    def describir(self):  # SOBRESCRIBE la descripción
        return f"{self.id} | Equipo '{self.nombre}' | {self._unidades} und. | ${self._tarifa_hora:,.0f}/h"


# =============================================================================
# Servicio 3: Asesorías especializadas
# =============================================================================
class Asesoria(Servicio):  # HEREDA de Servicio
    """Asesorías especializadas por nivel de experticia."""

    NIVELES = {"basico": 1.0, "avanzado": 1.5, "experto": 2.0}  # Multiplicador de tarifa por nivel

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="basico", disponible=True):  # Agrega especialidad y nivel
        super().__init__(nombre, tarifa_hora, disponible)  # Parte común
        if not especialidad:  # Especialidad obligatoria
            raise ParametroFaltanteError("especialidad")  # Error
        if nivel not in self.NIVELES:  # Nivel debe existir
            raise ServicioInvalidoError(f"Nivel '{nivel}' no existe. Use: {list(self.NIVELES)}")  # Error
        self._especialidad = especialidad  # Guarda la especialidad
        self._nivel = nivel  # Guarda el nivel

    def validar_parametros(self, horas, **detalles):  # SOBRESCRIBE la validación
        self._validar_horas(horas, 1, 8)  # Asesorías de 1 a 8 horas

    def costo_base(self, horas, **detalles):  # SOBRESCRIBE el costo
        return self._tarifa_hora * horas * self.NIVELES[self._nivel]  # Tarifa × horas × multiplicador

    def describir(self):  # SOBRESCRIBE la descripción
        return f"{self.id} | Asesoría '{self.nombre}' ({self._especialidad}, {self._nivel}) | ${self._tarifa_hora:,.0f}/h"

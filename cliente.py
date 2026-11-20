# =============================================================================
# Módulo: cliente.py
# Responsable: Integrante 2
# Descripción: Clase Cliente con datos personales encapsulados (atributos
#              privados + propiedades) y validaciones estrictas.
# =============================================================================

import re  # Expresiones regulares para validar correo, documento y teléfono

from entidades import EntidadBase  # Clase abstracta padre
from excepciones import ClienteInvalidoError, ParametroFaltanteError  # Errores propios


class Cliente(EntidadBase):  # Cliente HEREDA de EntidadBase
    """Cliente de Software FJ."""

    PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")  # Formato usuario@dominio.ext
    PATRON_DOCUMENTO = re.compile(r"^\d{6,12}$")  # Solo números, entre 6 y 12 dígitos
    PATRON_TELEFONO = re.compile(r"^3\d{9}$")  # Celular colombiano: 10 dígitos que empiezan por 3

    def __init__(self, nombre, documento, correo, telefono):  # Datos del cliente
        super().__init__("CLI")  # Crea el id con prefijo CLI
        self.nombre = nombre  # Usa el setter (valida automáticamente)
        self.documento = documento  # Usa el setter (valida automáticamente)
        self.correo = correo  # Usa el setter (valida automáticamente)
        self.telefono = telefono  # Usa el setter (valida automáticamente)

    # ---------------- Método auxiliar privado ----------------
    @staticmethod  # No necesita acceder al objeto
    def _requerido(valor, campo):  # Verifica que el dato exista
        if valor is None or str(valor).strip() == "":  # Vacío o None
            raise ParametroFaltanteError(campo)  # Lanza error de parámetro faltante
        return str(valor).strip()  # Devuelve el valor limpio

    # ---------------- Nombre ----------------
    @property  # Getter
    def nombre(self):  # Lee el nombre
        return self.__nombre  # Atributo privado

    @nombre.setter  # Setter con validación
    def nombre(self, valor):  # Asigna el nombre
        valor = self._requerido(valor, "nombre")  # No puede estar vacío
        if len(valor) < 3 or not all(c.isalpha() or c.isspace() for c in valor):  # Mín. 3 letras, sin números
            raise ClienteInvalidoError(f"Nombre inválido: '{valor}' (solo letras, mínimo 3)")  # Error
        self.__nombre = valor.title()  # Guarda con mayúscula inicial

    # ---------------- Documento ----------------
    @property  # Getter
    def documento(self):  # Lee el documento
        return self.__documento  # Atributo privado

    @documento.setter  # Setter con validación
    def documento(self, valor):  # Asigna el documento
        valor = self._requerido(valor, "documento")  # Obligatorio
        if not self.PATRON_DOCUMENTO.match(valor):  # Debe cumplir el patrón
            raise ClienteInvalidoError(f"Documento inválido: '{valor}' (6 a 12 dígitos)")  # Error
        self.__documento = valor  # Guarda el documento

    # ---------------- Correo ----------------
    @property  # Getter
    def correo(self):  # Lee el correo
        return self.__correo  # Atributo privado

    @correo.setter  # Setter con validación
    def correo(self, valor):  # Asigna el correo
        valor = self._requerido(valor, "correo")  # Obligatorio
        if not self.PATRON_CORREO.match(valor):  # Debe tener formato de correo
            raise ClienteInvalidoError(f"Correo inválido: '{valor}'")  # Error
        self.__correo = valor.lower()  # Guarda en minúsculas

    # ---------------- Teléfono ----------------
    @property  # Getter
    def telefono(self):  # Lee el teléfono
        return self.__telefono  # Atributo privado

    @telefono.setter  # Setter con validación
    def telefono(self, valor):  # Asigna el teléfono
        valor = self._requerido(valor, "telefono")  # Obligatorio
        if not self.PATRON_TELEFONO.match(valor):  # Debe ser celular válido
            raise ClienteInvalidoError(f"Teléfono inválido: '{valor}' (10 dígitos, inicia en 3)")  # Error
        self.__telefono = valor  # Guarda el teléfono

    # ---------------- Métodos abstractos implementados ----------------
    def validar(self):  # Revalida todos los datos del cliente
        self.nombre = self.nombre  # Pasa de nuevo por el setter
        self.documento = self.documento  # Pasa de nuevo por el setter
        self.correo = self.correo  # Pasa de nuevo por el setter
        self.telefono = self.telefono  # Pasa de nuevo por el setter
        return True  # Si no hubo excepción, es válido

    def describir(self):  # Descripción del cliente (polimorfismo)
        doc_oculto = "****" + self.documento[-4:]  # Oculta parte del documento (protección de datos)
        return f"{self.id} | {self.nombre} | Doc: {doc_oculto} | {self.correo}"  # Texto final

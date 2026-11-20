# =============================================================================
# Módulo: entidades.py
# Responsable: Integrante 2
# Descripción: Clase abstracta EntidadBase, de la que heredan Cliente,
#              Servicio y Reserva. Aplica ABSTRACCIÓN y ENCAPSULACIÓN.
# =============================================================================

from abc import ABC, abstractmethod  # ABC permite crear clases abstractas
from datetime import datetime  # Para guardar la fecha de creación


class EntidadBase(ABC):  # Clase abstracta: no se puede instanciar directamente
    """Representa cualquier entidad general del sistema."""

    _contadores = {}  # Diccionario compartido: un contador por prefijo (CLI, SRV, RES)

    def __init__(self, prefijo):  # El prefijo identifica el tipo de entidad
        EntidadBase._contadores[prefijo] = EntidadBase._contadores.get(prefijo, 0) + 1  # Aumenta el contador del prefijo
        self.__id = f"{prefijo}-{EntidadBase._contadores[prefijo]:03d}"  # Atributo privado: ej. CLI-001
        self.__fecha_creacion = datetime.now()  # Atributo privado: momento de creación

    @property  # Getter de solo lectura (encapsulación)
    def id(self):  # Permite leer el id pero no modificarlo
        return self.__id  # Devuelve el identificador

    @property  # Getter de solo lectura
    def fecha_creacion(self):  # Permite leer la fecha de creación
        return self.__fecha_creacion  # Devuelve la fecha

    @abstractmethod  # Obliga a las clases hijas a implementarlo
    def describir(self):  # Cada entidad se describe a su manera (polimorfismo)
        """Devuelve una descripción en texto de la entidad."""

    @abstractmethod  # Obliga a las clases hijas a implementarlo
    def validar(self):  # Cada entidad define sus propias reglas
        """Valida el estado interno de la entidad; lanza excepción si es inválido."""

    def __str__(self):  # Al imprimir el objeto
        return self.describir()  # Se usa la descripción polimórfica

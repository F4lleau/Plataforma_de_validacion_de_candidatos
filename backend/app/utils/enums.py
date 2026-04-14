from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    APODERADO = "apoderado"


class UserModuleType(str, Enum):
    DIPUTADOS_PROVINCIALES = "diputados_provinciales"
    CONSEJOS_LOCALES = "consejos_locales"


class CandidateStatus(str, Enum):
    BORRADOR = "borrador"
    PENDIENTE_VALIDACION = "pendiente_validacion"
    APROBADO_AUTOMATICAMENTE = "aprobado_automaticamente"
    RECHAZADO_AFILIACION = "rechazado_afiliacion"
    RECHAZADO_REQUISITOS = "rechazado_requisitos"
    RECHAZADO_RENAPER = "rechazado_renaper"
    ERROR_INTEGRACION = "error_integracion"


class ListStatus(str, Enum):
    BORRADOR = "borrador"
    INCOMPLETA = "incompleta"
    EN_VALIDACION = "en_validacion"
    RECHAZADA_COMPOSICION = "rechazada_composicion"
    APROBADA_SISTEMA = "aprobada_sistema"
    ENVIADA_ADMIN = "enviada_admin"


class ValidationType(str, Enum):
    AFILIACION = "afiliacion"
    RENAPER = "renaper"
    REQUISITOS_CARGO = "requisitos_cargo"
    COMPOSICION_LISTA = "composicion_lista"


class ValidationResult(str, Enum):
    OK = "ok"
    ERROR = "error"
    PENDIENTE = "pendiente"
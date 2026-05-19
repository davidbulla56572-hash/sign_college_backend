from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.db.models.convocatoria import Convocatoria  # noqa: E402,F401
from app.db.models.hoja_vida import ItemHojaVida, SoporteItem, TipoItemHojaVida  # noqa: E402,F401
from app.db.models.postulacion import Postulacion, PostulacionEstado  # noqa: E402,F401
from app.db.models.regla_evaluacion import ReglaEvaluacion  # noqa: E402,F401
from app.db.models.user import UserRole, Usuario  # noqa: E402,F401

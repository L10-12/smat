from pydantic import BaseModel
#--------------Clase para Estaciones--------------
class EstacionCreate(BaseModel):
    id: int
    nombre: str
    ubicacion: str

#--------------Clase para Lecturas--------------
class LecturaCreate(BaseModel):
    estacion_id: int
    valor: float
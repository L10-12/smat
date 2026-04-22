from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel


import models as models 
from database import engine, get_db


models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="SMAT Persistente")


#--------------Clase para Estaciones--------------
class EstacionCreate(BaseModel):
    id: int
    nombre: str
    ubicacion: str


#--------------Endpoints para estaciones--------------
@app.post("/estaciones/", status_code=201)
def crear_estacion(estacion: EstacionCreate, db: Session = Depends(get_db)):
    # Convertimos el esquema de Pydantic a Modelo de SQLAlchemy
    nueva_estacion = models.EstacionDB(id=estacion.id, nombre=estacion.nombre,ubicacion=estacion.ubicacion)
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    return {"msj": "Estación guardada en DB", "data": nueva_estacion}


@app.get("/estaciones/", response_model=list[EstacionCreate])
def mostrar_estaciones(db: Session = Depends(get_db)):
    return db.query(models.EstacionDB).all()


#--------------Clase para Lecturas--------------
class LecturaCreate(BaseModel):
    estacion_id: int
    valor: float
    


#--------------Endpoints para lecturas--------------
@app.post("/lecturas/", status_code=201)
def registrar_lectura(lectura: LecturaCreate, db: Session = Depends(get_db)):
    # Validar si la estación existe en la DB
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == lectura.estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no existe")
    nueva_lectura = models.LecturaDB(valor=lectura.valor,estacion_id=lectura.estacion_id)
    db.add(nueva_lectura)
    db.commit()
    return {"status": "Lectura guardada en DB"}


@app.get("/estaciones/{id}/historial", response_model=list[LecturaCreate])
def mostrar_lecturas_de_estacion(id: int, db: Session = Depends(get_db)):
    return db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == id).all()


'''
@app.get("/estaciones/{id}/riesgo")
async def obtener_riesgo(id: int):
    # 1. Validar existencia de la estación (Requisito 404)
    estacion_existe = any(e.id == id for e in db_estaciones)
    if not estacion_existe:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    # 2. Filtrar lecturas de la estación
    lecturas = [l for l in db_lecturas if l.estacion_id == id]
    if not lecturas:
        return {"id": id, "nivel": "SIN DATOS", "valor": 0}
    
    # 3. Evaluar última lectura (Motor de Reglas)
    ultima_lectura = lecturas[-1].valor
    if ultima_lectura > 20.0:
        nivel = "PELIGRO"
    elif ultima_lectura > 10.0:
        nivel = "ALERTA"
    else:
        nivel = "NORMAL"
    
    return {"id": id, "valor": ultima_lectura, "nivel": nivel}
'''


'''
@app.get("/estaciones/{id}/historial")
async def obtener_historial(id: int):
# PASO 1: Verificar si la estación existe en db_estaciones
    # (Si no existe, lanzar HTTPException 404)
    estacion_existe = any(e.id == id for e in db_estaciones)
    if not estacion_existe:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
# PASO 2: Filtrar las lecturas de db_lecturas que coincidan con el id
    lecturas_filtradas = [l.valor for l in db_lecturas if l.estacion_id == id]


# PASO 3: Calcular el promedio (usando la validación del punto 2)
    if len(lecturas_filtradas) > 0:
        promedio = sum(lecturas_filtradas) / len(lecturas_filtradas)
    else:
        promedio = 0.0


# PASO 4: Retornar el JSON con la estructura solicitada
    return {
    "estacion_id": id,
    "lecturas": lecturas_filtradas,
    "conteo": len(lecturas_filtradas),
    "promedio": round(promedio, 2) # round para solo 2 decimales
    }
'''

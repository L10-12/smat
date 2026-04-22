from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import models as models 
from database import engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
title="SMAT - Sistema de Monitoreo de Alerta Temprana",
description="""
API robusta para la gestión y monitoreo de desastres naturales.
Permite la telemetría de sensores en tiempo real y el cálculo de niveles de riesgo.
**Entidades principales:**
* **Estaciones:** Puntos de monitoreo físico.
* **Lecturas:** Datos capturados por sensores.
* **Riesgos:** Análisis de criticidad basado en umbrales.
""",
version="1.0.0",
terms_of_service="http://unmsm.edu.pe/terms/",
contact={
"name": "Soporte Técnico SMAT - FISI",
"url": "http://fisi.unmsm.edu.pe",
"email": "desarrollo.smat@unmsm.edu.pe",
},
license_info={
"name": "Apache 2.0",
"url": "https://www.apache.org/licenses/LICENSE-2.0.html",
},
)

'''
# Configuración de orígenes permitidos
origins = ["*"] # En producción, especificar dominios reales
app.add_middleware(
CORSMiddleware,
allow_origins=origins,
allow_credentials=True,
allow_methods=["*"],
allow_w_headers=["*"],
)
'''
#--------------Clase para Estaciones--------------
class EstacionCreate(BaseModel):
    id: int
    nombre: str
    ubicacion: str


#--------------Endpoints para estaciones--------------
# Endpoint para registrar una nueva estación de monitoreo
@app.post(
"/estaciones/",
status_code=201,
tags=["Gestión de Infraestructura"],
summary="Registrar una nueva estación de monitoreo",
description="Inserta una estación física (ej. río, volcán, zona sísmica) en la base de datos relacional."
)
def crear_estacion(estacion: EstacionCreate, db: Session = Depends(get_db)):
    # Convertimos el esquema de Pydantic a Modelo de SQLAlchemy
    nueva_estacion = models.EstacionDB(id=estacion.id, nombre=estacion.nombre,ubicacion=estacion.ubicacion)
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    return {"msj": "Estación guardada en DB", "data": nueva_estacion}

# Endpoint para mostrar todas las estaciones registradas
@app.get("/estaciones/", response_model=list[EstacionCreate])
def mostrar_estaciones(db: Session = Depends(get_db)):
    return db.query(models.EstacionDB).all()


#--------------Clase para Lecturas--------------
class LecturaCreate(BaseModel):
    estacion_id: int
    valor: float
    


#--------------Endpoints para lecturas--------------
# Endpoint para registrar una lectura de sensor vinculada a una estación
@app.post(
"/lecturas/",
status_code=201,
tags=["Telemetría de Sensores"],
summary="Recibir datos de telemetría",description="Recibe el valor capturado por un sensor y lo vincula a una estación existente mediante suID."
)
def registrar_lectura(lectura: LecturaCreate, db: Session = Depends(get_db)):
    # Validar si la estación existe en la DB
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == lectura.estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no existe")
    nueva_lectura = models.LecturaDB(valor=lectura.valor,estacion_id=lectura.estacion_id)
    db.add(nueva_lectura)
    db.commit()
    return {"status": "Lectura guardada en DB"}

# Endpoint para mostrar el historial de lecturas de una estación específica
@app.get("/estaciones/{id}/historial", response_model=list[LecturaCreate])
def mostrar_lecturas_de_estacion(id: int, db: Session = Depends(get_db)):
    return db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == id).all()

#Endpoint para mostrar un reporte histórico de todas las estaciones con conteo y promedio de lecturas
@app.get("/reporte/{id}/historial",
         tags=["Reporte Históricos"],
         summary="Reporte histórico de estaciones",
         description="Muestra el conteo total de lecturas y el valor promedio para cada estación registrada en la base de datos.",
         response_model=list[dict])

def mostrar_reporte_historico_por_estacion(db: Session = Depends(get_db)):
    estaciones = db.query(models.EstacionDB).all()
    reporte = []
    for estacion in estaciones:
        lecturas = db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == estacion.id).all()
        conteo = len(lecturas)
        promedio = sum(l.valor for l in lecturas) / conteo if conteo > 0 else 0.0
        reporte.append({
            "estacion_id": estacion.id,
            "nombre": estacion.nombre,
            "ubicacion": estacion.ubicacion,
            "conteo_lecturas": conteo,
            "promedio_lecturas": round(promedio, 2)
        })
    return reporte

#--------------Endpoint para análisis de riesgo--------------
# Endpoint para evaluar el nivel de riesgo actual basado en la última lectura de una estación
@app.get(
"/estaciones/{id}/riesgo",
tags=["Análisis de Riesgo"],
summary="Evaluar nivel de peligro actual",
description="Analiza la última lectura recibida de una estación y determina si el estado es NORMAL,ALERTA o PELIGRO."
)
# El nivel de riesgo se determina por los siguientes umbrales:
def obtener_riesgo(id: int, db: Session = Depends(get_db)):
    # Validar existencia de la estación
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    # Obtener la última lectura de la estación
    ultima_lectura = db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == id).order_by(models.LecturaDB.id.desc()).first()
    
    if not ultima_lectura:
        return {"id": id, "nivel": "SIN DATOS", "valor": 0}
    
    valor = ultima_lectura.valor
    if valor > 20.0:
        nivel = "PELIGRO"
    elif valor > 10.0:
        nivel = "ALERTA"
    else:
        nivel = "NORMAL"
    
    return {"id": id, "valor": valor, "nivel": nivel}


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
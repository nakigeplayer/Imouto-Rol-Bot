# -*- coding: utf-8 -*-
import json
import os
import asyncio
from modelo import estado_hermana

ARCHIVO_DATOS = "estado_hermana.json"

async def guardar_datos():
    """Guarda el estado de todos los usuarios a un archivo JSON."""
    datos = {}
    for uid, estado in estado_hermana.items():
        nuevo_estado = estado.copy()
        nuevo_estado["hora"] = nuevo_estado["hora"].isoformat()
        datos[str(uid)] = nuevo_estado

    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def cargar_datos():
    """Carga los estados desde un archivo JSON si existe."""
    if not os.path.exists(ARCHIVO_DATOS):
        return

    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            datos = json.load(f)

        for uid_str, estado in datos.items():
            estado["hora"] = __parsear_iso(estado["hora"])
            estado_hermana[int(uid_str)] = estado

    except Exception as e:
        print(f"[Error] Al cargar datos: {e}")

def __parsear_iso(texto_fecha):
    """Convierte texto ISO a datetime."""
    from datetime import datetime
    return datetime.fromisoformat(texto_fecha)

def setup_autoguardado(funcion_guardar):
    """Ejecuta autoguardado cada hora real usando asyncio."""
    async def ciclo():
        while True:
            await asyncio.sleep(3600)  # 1 hora real (en segundos)
            funcion_guardar()
            print("[AutoSave] Datos guardados correctamente.")

    asyncio.get_event_loop().create_task(ciclo())
    

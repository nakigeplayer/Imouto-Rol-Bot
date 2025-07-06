import os
import re
import json
from pyrogram import filters
from pyrogram.types import Message, Document
from persistencia import cargar_datos

ARCHIVO_DATOS = "estado_hermana.json"
ARCHIVO_ANNOTATED = "estado_hermana_annotated.json"

def es_admin(uid: int) -> bool:
    admin_ids = os.getenv("ADMIN", "")
    return str(uid) in admin_ids.split(",")

def limpiar_comentarios(origen: str, destino: str):
    with open(origen, "r", encoding="utf-8") as f:
        lineas_limpias = []
        for linea in f:
            # Elimina comentario en línea después de una llave
            if re.search(r"\{\s*#.*", linea):
                linea = re.sub(r"\{\s*#.*", "{", linea)

            # Asegura comillas dobles en claves numéricas
            match = re.match(r"\s*(\d+)\s*:\s*{", linea)
            if match:
                uid = match.group(1)
                linea = linea.replace(uid, f'"{uid}"', 1)

            lineas_limpias.append(linea)

    with open(destino, "w", encoding="utf-8") as f:
        f.writelines(lineas_limpias)
        

def registrar_handlers_load(app):

    @app.on_message(filters.command("load") & filters.private)
    async def comando_recibir(_, mensaje: Message):
        if not es_admin(mensaje.from_user.id):
            await mensaje.reply("No tienes permiso para usar este comando.")
            return
        await mensaje.reply("Por favor, envíame el archivo `estado_hermana.json` o `estado_hermana_annotated.json` como documento.")

    @app.on_message(filters.document & filters.private)
    async def recibir_archivo(_, mensaje: Message):
        if not es_admin(mensaje.from_user.id):
            return

        documento: Document = mensaje.document
        nombre_archivo = documento.file_name

        if nombre_archivo not in [ARCHIVO_DATOS, ARCHIVO_ANNOTATED]:
            await mensaje.reply("⚠️ El archivo debe llamarse `estado_hermana.json` o `estado_hermana_annotated.json`.")
            return

        try:
            ruta_descarga = os.path.join(".", nombre_archivo)

            await mensaje.download(file_name=ruta_descarga)

            if nombre_archivo == ARCHIVO_ANNOTATED:
                limpiar_comentarios(ruta_descarga, ARCHIVO_DATOS)
            else:
                # Si es el archivo limpio, lo dejamos como está
                os.rename(ruta_descarga, ARCHIVO_DATOS)

            cargar_datos()
            await mensaje.reply("✅ Datos cargados correctamente desde el archivo.")
        except Exception as e:
            await mensaje.reply(f"[Error al cargar archivo] {e}")

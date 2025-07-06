import os
import json
from pyrogram import filters
from pyrogram.types import Message, Document
from persistencia import cargar_datos

ARCHIVO_DATOS = "estado_hermana.json"

def es_admin(uid: int) -> bool:
    admin_ids = os.getenv("ADMIN", "")
    return str(uid) in admin_ids.split(",")

def registrar_handlers_load(app):

    @app.on_message(filters.command("load") & filters.private)
    async def comando_recibir(_, mensaje: Message):
        if not es_admin(mensaje.from_user.id):
            await mensaje.reply("No tienes permiso para usar este comando.")
            return
        await mensaje.reply("Por favor, envíame el archivo `estado_hermana.json` como documento.")

    @app.on_message(filters.document & filters.private)
    async def recibir_archivo(_, mensaje: Message):
        if not es_admin(mensaje.from_user.id):
            return

        documento: Document = mensaje.document
        if documento.file_name != ARCHIVO_DATOS:
            await mensaje.reply("⚠️ El archivo debe llamarse exactamente `estado_hermana.json`.")
            return

        try:
            ruta = os.path.join(".", ARCHIVO_DATOS)
            await mensaje.download(file_name=ruta)
            cargar_datos()
            await mensaje.reply("✅ Datos cargados correctamente desde el archivo.")
        except Exception as e:
            await mensaje.reply(f"[Error al cargar archivo] {e}")

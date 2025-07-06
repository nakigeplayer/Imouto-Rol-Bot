import os
from pyrogram import filters
from pyrogram.types import Message
from persistencia import guardar_datos

ARCHIVO_DATOS = "estado_hermana.json"

def es_admin(uid: int) -> bool:
    admin_ids = os.getenv("ADMIN", "")
    return str(uid) in admin_ids.split(",")

def registrar_handlers_save(app):

    @app.on_message(filters.command("save") & filters.private)
    async def comando_guardar(_, mensaje: Message):
        if not es_admin(mensaje.from_user.id):
            await mensaje.reply("No tienes permiso para usar este comando.")
            return

        try:
            guardar_datos()
            await mensaje.reply_document(ARCHIVO_DATOS, caption="📤 Datos guardados correctamente.")
        except Exception as e:
            await mensaje.reply(f"[Error al guardar datos] {e}")
          

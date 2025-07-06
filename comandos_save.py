import os
import json
from pyrogram import filters
from pyrogram.types import Message
from persistencia import guardar_datos

ARCHIVO_DATOS = "estado_hermana.json"
ARCHIVO_MODIFICADO = "estado_hermana_annotated.json"

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

            # Leer archivo JSON
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                datos = json.load(f)

            # Construir texto con comentarios
            resultado = "{\n"
            for uid, contenido in datos.items():
                try:
                    user = await app.get_users(int(uid))
                    nombre = user.first_name.replace("\n", " ")
                except Exception:
                    nombre = "Desconocido"

                json_formateado = json.dumps(contenido, indent=4, ensure_ascii=False)
                json_formateado = "\n".join("    " + linea for linea in json_formateado.splitlines())
                resultado += f'    "{uid}": {{  # {nombre}\n{json_formateado[1:]},\n'
            resultado = resultado.rstrip(",\n") + "\n}\n"

            # Escribir archivo modificado
            with open(ARCHIVO_MODIFICADO, "w", encoding="utf-8") as f:
                f.write(resultado)

            await mensaje.reply_document(ARCHIVO_MODIFICADO, caption="📤 Datos anotados con nombres.")

        except Exception as e:
            await mensaje.reply(f"[Error al guardar datos] {e}")

# -*- coding: utf-8 -*-
# coding: utf-8

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from modelo import inicializar_usuario, estado_hermana, consumir_item
from tienda import productos, comprar_producto
from tiempo import avanzar_tiempo, formato_tiempo, avanzar_tiempo_noche
from persistencia import guardar_datos, cargar_datos, setup_autoguardado
from datetime import datetime
import os
import json
import random
from dotenv import load_dotenv
import asyncio
import nest_asyncio
nest_asyncio.apply()
from menu_query import manejar_callback, generar_menu_principal, actualizar_aburrimiento
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("hermanita_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

aburrimiento = {}

def actualizar_aburrimiento(uid, accion):
    if uid not in aburrimiento:
        aburrimiento[uid] = {"jugar": 0, "conversar": 0}
    aburrimiento[uid][accion] += 20
    if random.randint(1, 100) <= aburrimiento[uid][accion]:
        aburrimiento[uid][accion] = 100

@app.on_message(filters.command("start"))
def start(_, message):
    user = message.from_user
    inicializar_usuario(user.id)
    reply_markup = generar_menu_principal()
    message.reply_text(f"¡Hola, {user.first_name}! Comienza tu día cuidando a tu hermanita", reply_markup=reply_markup)

@app.on_message(filters.command("load") & filters.reply)
def cargar_json(_, message: Message):
    if not message.reply_to_message.document:
        message.reply_text("Responde a un archivo .json válido.")
        return
    archivo = message.reply_to_message.document
    if not archivo.file_name.endswith(".json"):
        message.reply_text("El archivo debe ser formato .json.")
        return

    ruta = f"carga_{message.from_user.id}.json"
    archivo.download(ruta)

    try:
        with open(ruta, "r") as f:
            datos = json.load(f)
        for uid, estado in datos.items():
            estado["hora"] = datetime.fromisoformat(estado["hora"])
            estado_hermana[int(uid)] = estado
        message.reply_text("Datos cargados correctamente.")
    except Exception as e:
        message.reply_text(f"Error al cargar: {e}")
    finally:
        os.remove(ruta)

@app.on_callback_query()
def responder(app, query):
    manejar_callback(app, query)
    
async def main():
    cargar_datos()
    await app.start()
    setup_autoguardado(guardar_datos)
    print("Bot iniciado y operativo.")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Detención forzada realizada")

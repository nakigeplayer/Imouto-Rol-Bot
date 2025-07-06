# -*- coding: utf-8 -*-
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
from comandos_save import registrar_handlers_save
from comandos_load import registrar_handlers_load
from sexo import manejar_acto, generar_menu, iniciar_acto, actualizar_progresos, detener_actualizacion

# Variables de entorno
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Cliente del bot
app = Client("hermanita_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Registro de aburrimiento y actos activos
aburrimiento = {}
actos_en_progreso = set()

def actualizar_aburrimiento(uid, accion):
    if uid not in aburrimiento:
        aburrimiento[uid] = {"jugar": 0, "conversar": 0}
    aburrimiento[uid][accion] += 20
    if random.randint(1, 100) <= aburrimiento[uid][accion]:
        aburrimiento[uid][accion] = 100

# Comando /start
@app.on_message(filters.command("start"))
def start(_, message):
    user = message.from_user
    uid = user.id
    inicializar_usuario(uid)

    if uid in actos_en_progreso:
        message.reply_text("Tu hermanita está ocupada en algo especial ahora. Espera a que termine…")
    else:
        reply_markup = generar_menu_principal()
        message.reply_text(
            f"¡Hola, {user.first_name}! Comienza tu día cuidando a tu hermanita",
            reply_markup=reply_markup
        )

# Registro de funciones externas
registrar_handlers_save(app)
registrar_handlers_load(app)

# Acciones del menú principal
ACCIONES_MENU = {
    "jugar", "conversar", "comer_menu", "comprar_menu", "estado", "volver", "ir_escuela"
}

def es_callback_menu(data):
    return (
        data in ACCIONES_MENU
        or data.startswith("comer_")
        or data.startswith("buy_")
        or data.startswith("dormir")
    )

@app.on_callback_query()
async def responder(app, query):
    uid = user.id
    accion = query.data
    if es_callback_menu(accion):
        await manejar_callback(app, query)
        marcar_acto_terminado(uid)
    else:
        await manejar_acto(app, query)
        marcar_acto_activo(uid)

# Para marcar inicio y fin de actos
def marcar_acto_activo(user_id):
    actos_en_progreso.add(user_id)

def marcar_acto_terminado(user_id):
    actos_en_progreso.discard(user_id)

# Lógica principal del bot
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

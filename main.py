# -*- coding: utf-8 -*-
# coding: utf-8


from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from modelo import inicializar_usuario, estado_hermana, consumir_item, agregar_item
from tienda import productos, comprar_producto
from tiempo import avanzar_tiempo, formato_tiempo
from persistencia import guardar_datos, cargar_datos, setup_autoguardado
from datetime import datetime
import os
import json
from dotenv import load_dotenv
import asyncio
import nest_asyncio
nest_asyncio.apply()
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("hermanita_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start(_, message):
    user = message.from_user
    estado = inicializar_usuario(user.id)
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
        message.reply_text(f" Error al cargar: {e}")
    finally:
        os.remove(ruta)

@app.on_callback_query()
def responder(_, query):
    uid = query.from_user.id
    estado = estado_hermana[uid]
    accion = query.data
    respuesta = ""

    if accion == "volver":
        query.message.edit_text("Elige una acción:", reply_markup=generar_menu_principal())
        return

    if accion == "estado":
        respuesta = (
            f"Estado de tu hermanita:\n"
            f"Hambre: {estado['hambre']}\n"
            f"Ánimo: {estado['animo']}\n"
            f"Felicidad: {estado['felicidad']}\n"
            f"Energía: {estado['energia']}\n"
            f"Dinero: ${estado['dinero']}\n"
            + formato_tiempo(uid)
        )

    elif accion == "dormir":
        if estado["energia"] >= 100:
            respuesta = "La hermanita no tiene sueño aún"
        else:
            estado["energia"] += 100
            estado["hambre"] += 10
            respuesta = "Tu hermanita durmió profundamente y recuperó energía."

    elif accion == "jugar":
        if estado["energia"] < 15 and estado["hora"].hour >= 22:
            respuesta = "La hermana está muy cansada. Solo quiere dormir."
        else:
            estado["animo"] += 15
            estado["energia"] -= 10
            respuesta = "Jugaron juntas  y se divirtieron bastante."

    elif accion == "comer_menu":
        botones = [
            [InlineKeyboardButton(f"{item} x{cantidad}", callback_data=f"comer_{item}")]
            for item, cantidad in estado["inventario"].items() if cantidad > 0
        ]
        if not botones:
            botones = [[InlineKeyboardButton("Inventario vacío", callback_data="volver")]]
        botones.append([InlineKeyboardButton(" Volver", callback_data="volver")])
        query.message.edit_text(" ¿Qué deseas darle de comer?", reply_markup=InlineKeyboardMarkup(botones))
        return

    elif accion.startswith("comer_"):
        item = accion.replace("comer_", "")
        resultado = consumir_item(uid, item)
        if not resultado:
            respuesta = "No tienes esa comida ︄"
        else:
            efecto = productos.get(item)
            if not efecto:
                respuesta = f"{item} fue consumido, pero no causó efecto."
            else:
                texto_efecto = ""
                for atributo, delta in efecto["efecto"].items():
                    estado[atributo] = max(0, min(100, estado[atributo] + delta))
                    texto_efecto += f" {atributo.capitalize()} {delta:+d}"
                respuesta = f"Tu hermanita comió {item} 🍴.{texto_efecto}"

    elif accion == "comprar_menu":
        botones = [
            [InlineKeyboardButton(f"{item} - ${info['precio']}", callback_data=f"buy_{item}")]
            for item, info in productos.items()
        ]
        botones.append([InlineKeyboardButton("Volver", callback_data="volver")])
        query.message.edit_text(" ¿Qué quieres comprar?", reply_markup=InlineKeyboardMarkup(botones))
        return

    elif accion.startswith("buy_"):
        nombre = accion.replace("buy_", "")
        respuesta = comprar_producto(uid, nombre, estado)

    else:
        respuesta = "Comando no reconocido."

    avanzar_tiempo(uid)
    guardar_datos()
    query.answer()
    query.message.edit_text(respuesta + "\n" + formato_tiempo(uid), reply_markup=generar_menu_principal())

def generar_menu_principal():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Jugar", callback_data="jugar")],
        [InlineKeyboardButton("Comer", callback_data="comer_menu")],
        [InlineKeyboardButton("Compra Online", callback_data="comprar_menu")],
        [InlineKeyboardButton("Dormir", callback_data="dormir")],
        [InlineKeyboardButton("Ver Estado", callback_data="estado")]
    ])

async def main():
    await cargar_datos()
    await app.start()
    await setup_autoguardado(guardar_datos)
    print("Bot iniciado y operativo.")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Detención forzada realizada")

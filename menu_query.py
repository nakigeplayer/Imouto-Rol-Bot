from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from modelo import estado_hermana, consumir_item
from tienda import productos, comprar_producto
from tiempo import avanzar_tiempo, formato_tiempo, avanzar_tiempo_noche
from persistencia import guardar_datos
from textos import (
    JUGO_EXITOSO, NO_QUIERE_JUGAR, CONVERSACION, COMIO, NO_HAY_HAMBRE, aleatorio
)
from datetime import datetime
import random

aburrimiento = {}

def actualizar_aburrimiento(uid, accion):
    if uid not in aburrimiento:
        aburrimiento[uid] = {"jugar": 0, "conversar": 0}
    aburrimiento[uid][accion] += 20
    if random.randint(1, 100) <= aburrimiento[uid][accion]:
        aburrimiento[uid][accion] = 100

def generar_menu_principal():
    botones = [
        [InlineKeyboardButton("Jugar", callback_data="jugar"),
         InlineKeyboardButton("Conversar", callback_data="conversar")],
        [InlineKeyboardButton("Comer", callback_data="comer_menu"),
         InlineKeyboardButton("Compra Online", callback_data="comprar_menu")],
        [InlineKeyboardButton("Dormir", callback_data="dormir"),
         InlineKeyboardButton("Ver Estado", callback_data="estado")]
    ]
    return InlineKeyboardMarkup(botones)

def manejar_callback(app, query):
    uid = query.from_user.id
    if uid not in estado_hermana:
        query.answer("Primero usa /start para comenzar.")
        return

    estado = estado_hermana[uid]
    accion = query.data
    hambre = estado["hambre"]
    respuesta = ""

    if accion == "volver":
        query.message.edit_text("Elige una acción:", reply_markup=generar_menu_principal())
        return

    elif accion == "estado":
        respuesta = (
            f"Estado de tu hermanita:\n"
            f"Hambre: {estado['hambre']}\n"
            f"Ánimo: {estado['animo']}\n"
            f"Felicidad: {estado['felicidad']}\n"
            f"Energía: {estado['energia']}\n"
            f"Dinero: ${estado['dinero']}\n" + formato_tiempo(uid)
        )

    elif accion == "dormir":
        if hambre >= 80:
            respuesta = "Tu hermana no puede dormir por el hambre"
        elif estado["energia"] >= 100:
            respuesta = "La hermanita no tiene sueño aún"
        else:
            estado["energia"] += 100
            estado["hambre"] += 10
            aburrimiento.pop(uid, None)
            avanzar_tiempo_noche(uid)
            respuesta = "Tu hermanita durmió profundamente y recuperó energía."

    elif accion == "jugar":
        if hambre >= 60:
            respuesta = "Tu hermana tiene mucha hambre para eso"
        elif aburrimiento.get(uid, {}).get("jugar", 0) >= 100:
            respuesta = aleatorio(NO_QUIERE_JUGAR)
        elif estado["energia"] < 15 or estado["hora"].hour >= 22:
            respuesta = "La hermana está muy cansada. Solo quiere dormir."
        else:
            estado["animo"] += 15
            estado["energia"] -= 10
            avanzar_tiempo(uid)
            actualizar_aburrimiento(uid, "jugar")
            respuesta = aleatorio(JUGO_EXITOSO)

    elif accion == "conversar":
        if hambre >= 60:
            respuesta = "Tu hermana tiene mucha hambre para eso"
        elif aburrimiento.get(uid, {}).get("conversar", 0) >= 100:
            respuesta = aleatorio(NO_QUIERE_JUGAR)
        elif estado["energia"] < 10 or estado["hora"].hour >= 22:
            respuesta = "Tu hermana está muy cansada para hablar."
        else:
            estado["animo"] += 10
            estado["felicidad"] += 5
            estado["energia"] -= 8
            avanzar_tiempo(uid)
            actualizar_aburrimiento(uid, "conversar")
            respuesta = aleatorio(CONVERSACION)

    elif accion == "comer_menu":
        botones = [
            [InlineKeyboardButton(f"{item} x{cantidad}", callback_data=f"comer_{item}")]
            for item, cantidad in estado["inventario"].items() if cantidad > 0
        ]
        if estado["hambre"] == 0 or estado["hora"].hour >= 22:
            respuesta = aleatorio(NO_HAY_HAMBRE)
        if not botones:
            botones = [[InlineKeyboardButton("Inventario vacío", callback_data="volver")]]
        botones.append([InlineKeyboardButton("Volver", callback_data="volver")])
        query.message.edit_text("¿Qué deseas darle de comer?", reply_markup=InlineKeyboardMarkup(botones))
        return

    elif accion.startswith("comer_"):
        item = accion.replace("comer_", "")
        resultado = consumir_item(uid, item)
        if not resultado:
            respuesta = "No tienes esa comida ︄"
        else:
            efecto = productos.get(item)
            texto_efecto = ""
            if efecto:
                for atributo, delta in efecto["efecto"].items():
                    estado[atributo] = max(0, min(100, estado[atributo] + delta))
                    texto_efecto += f" {atributo.capitalize()} {delta:+d}"
            avanzar_tiempo(uid)
            respuesta = aleatorio(COMIO) + texto_efecto

    elif accion == "comprar_menu":
        if hambre >= 60:
            respuesta = "Tu hermana tiene mucha hambre para eso"
        else:
            botones = [
                [InlineKeyboardButton(f"{item} - ${info['precio']}", callback_data=f"buy_{item}")]
                for item, info in productos.items()
            ]
            botones.append([InlineKeyboardButton("Volver", callback_data="volver")])
            query.message.edit_text("¿Qué quieres comprar?", reply_markup=InlineKeyboardMarkup(botones))
            return

    elif accion.startswith("buy_"):
        nombre = accion.replace("buy_", "")
        respuesta = comprar_producto(uid, nombre, estado)
        avanzar_tiempo(uid)

    else:
        respuesta = "Comando no reconocido."

    guardar_datos()
    query.answer()
    query.message.edit_text(respuesta + "\n" + formato_tiempo(uid), reply_markup=generar_menu_principal())
            

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified

from datetime import datetime, timedelta
import random
import asyncio
from modelo import inicializar_usuario, estado_hermana, consumir_item

# --- Estados del Juego ---
usuarios = {}  # Guarda ánimo, felicidad, energía
usuarios_acto = {}  # Guarda progresos durante el acto
tarea_actualizacion = None

def estado_inicial():
    return {
        "animo": 70,
        "felicidad": 60,
        "energia": 80
    }

def iniciar_acto(uid):
    estado = estado_hermana[uid]
    return {
        "exitacion_jugador": 0,
        "eyaculaciones": 0,
        "exitacion_chica": 0,
        "molestia_chica": 0,
        "mult_jugador": 1.0,
        "mult_chica": 1.0,
        "mult_chica2": 0.0,
        "mult_molestia": 1.0,
        "mult_molestia2": 2.0,
        "sueño": 100 - estado["energia"],
        "despierta": False,
        "ropa": {
            "blusa": True,
            "falda": True,
            "pantis": True
        },
        "piernas_abiertas": False,
        "penetracion": False,
        "last_update": datetime.now()
    }

# --- Actualización Automática (Cada 5 segundos) ---
async def actualizar_progresos():
    while True:
        await asyncio.sleep(5)
        now = datetime.now()
        for uid, acto in usuarios_acto.items():
            # Calcular tiempo transcurrido
            elapsed = (now - acto["last_update"]).total_seconds()
            if elapsed < 5:
                continue

            # estado del usuario
            estado = estado_hermana[uid]

            # Actualizar valores
            acto["exitacion_jugador"] = min(100, acto["exitacion_jugador"] + acto["mult_jugador"])
            
            if acto["despierta"]:
                acto["exitacion_chica"] = min(100, acto["exitacion_chica"] + acto["mult_chica"] * (1 + estado["animo"]/100 + estado["felicidad"]/100))
            
            acto["molestia_chica"] = min(100, acto["molestia_chica"] + acto["mult_molestia"] * (1 - estado["animo"]/200 - estado["felicidad"]/200))

            # Probabilidad de despertar (inversa a energía)
            if not acto["despierta"] and random.random() < (100 - acto["sueño"]) / 200:
                acto["despierta"] = True
                acto["sueño"] = acto["sueño"] - random.randint(0, 4)
            acto["last_update"] = now

# --- Iniciar tarea de actualización ---
def iniciar_tarea_actualizacion():
    global tarea_actualizacion
    if tarea_actualizacion is None or tarea_actualizacion.done():
        tarea_actualizacion = asyncio.create_task(actualizar_progresos())
        
# --- Generar Menú ---
def generar_menu(uid):
    acto = usuarios_acto.get(uid, iniciar_acto(uid))
    botones = []

    # Opciones siempre disponibles
    if not acto["penetracion"]:
        botones.append([InlineKeyboardButton("Masturbarse", callback_data="masturbar_jugador")])

    # Opciones de desvestir
    if acto["ropa"]["blusa"] or acto["ropa"]["falda"] or acto["ropa"]["pantis"]:
        botones.append([InlineKeyboardButton("Desvestir", callback_data="desvestir_menu")])

    # Tocar pechos (solo sin blusa)
    if not acto["ropa"]["blusa"]:
        botones.append([InlineKeyboardButton("Tocar pechos", callback_data="tocar_pechos")])

    # Masturbación (solo sin falda)
    if not acto["ropa"]["falda"]:
        botones.append([InlineKeyboardButton("Masturbarla", callback_data="masturbar_chica")])

    # Abrir piernas (solo si están cerradas)
    if not (acto["ropa"]["falda"] or acto["piernas_abiertas"]):
        botones.append([InlineKeyboardButton("Abrir piernas", callback_data="abrir_piernas")])
    elif not acto["ropa"]["pantis"]:
        if not acto["penetracion"]:
            botones.append([InlineKeyboardButton("Rozar vagina", callback_data="rozar_vagina")])
            botones.append([InlineKeyboardButton("Penetrar", callback_data="penetrar")])
        if acto["penetracion"]:
            botones.append([InlineKeyboardButton("Moverse", callback_data="moverse")])

    botones.append([InlineKeyboardButton("Ir a dormir", callback_data="dormir_confirm")])

    return InlineKeyboardMarkup(botones)

def generar_menu_2(uid):
    acto = usuarios_acto.get(uid)
    estado = estado_hermana[uid]
    botones = []
    botones.append([InlineKeyboardButton("Continuar", callback_data="acto_continue")])
    if acto["exitacion_chica"] >= 100:
        acto["exitacion_chica"] = acto["exitacion_chica"] - random.randint(80, 100)
        acto["mult_chica"] = 0
        estado["felicidad"] = estado["felicidad"] + random.randint(10, 50)
        estado["animo"] = estado["felicidad"] + random.randint(10, 50)
        acto["molestia_chica"] = max(
            0,
            acto["molestia_chica"] - random.randint(
                int(acto["molestia_chica"] * 0.6),
                int(acto["molestia_chica"])
            )
        )
        estado["energia"] = estado["energia"] - random.randint(20, 30)

    if acto["exitacion_jugador"] >= 100:
        acto["exitacion_jugador"] = 0
        acto["mult_jugador"] = 0
    return InlineKeyboardMarkup(botones)
    
# --- Manejador de Callbacks ---
async def manejar_acto(app, query):
    # Iniciar tarea de actualización si no está corriendo
    iniciar_tarea_actualizacion()
    
    uid = query.from_user.id
    if uid not in estado_hermana: 
        await query.answer("Primero usa /start para comenzar.")
        return

    estado = estado_hermana[uid]
    if uid not in usuarios_acto:
        usuarios_acto[uid] = iniciar_acto(uid)
        
    acto = usuarios_acto[uid]
    callback_query = query
    data = query.data
    
    if data == "acto_start" or data == "acto_continue":
        generar_menu(uid)

    # Procesar acciones
    if data == "masturbar_jugador":
        acto["mult_jugador"] += 0.2
        await query.answer("Te masturbaste mirando a tu hermana", show_alert=True)
        
    elif data == "tocar_pechos":
        if acto["ropa"]["blusa"]:
            acto["mult_molestia"] += 0.3
        else:
            acto["mult_chica"] += 0.2
        await query.answer("Tocaste los pechos tu hermana", show_alert=True)

    elif data == "masturbar_chica":
        if acto["ropa"]["pantis"]:
            random.choices([
                lambda: acto.update({"mult_chica": acto["mult_chica"] + 0.3}),
                lambda: acto.update({"mult_molestia": acto["mult_molestia"] + 0.4}),
                lambda: acto.update({
                    "mult_chica": acto["mult_chica"] + 0.3,
                    "mult_molestia": acto["mult_molestia"] + 0.1
                }),
            ], weights=[70, 20, 10])[0]()  # ← Escoge la función y la ejecuta
        else:
            acto["mult_chica"] += 0.5 if acto["piernas_abiertas"] else 0.3
        await query.answer("Masturbaste a tu hermana", show_alert=True)

    elif data == "abrir_piernas":
        acto["piernas_abiertas"] = True
        acto["mult_molestia"] += 0.2
        await query.answer("Abriste las piernas de tu hermana", show_alert=True)

    elif data == "rozar_vagina":
        acto["mult_jugador"] += 0.4
        acto["mult_chica"] += 0.3
        await query.answer("Frotas tu pene con la vagina tu hermana", show_alert=True)

    elif data == "penetrar":
        acto["mult_jugador"] += 0.8
        acto["mult_chica"] += 0.6
        acto["penetracion"] = True
        await query.answer("Tienes sexo con tu hermana", show_alert=True)
        
    elif data == "moverse":
        acto["mult_jugador"] += 1.0
        acto["mult_chica"] += 0.8
        await query.answer("Tienes sexo con tu hermana", show_alert=True)
        
    elif data == "desvestir_menu":
        # Submenú de desvestir
        submenu = []
        if acto["ropa"]["blusa"]:
            submenu.append([InlineKeyboardButton("Quitar blusa", callback_data="quitar_blusa")])
        if acto["ropa"]["falda"]:
            submenu.append([InlineKeyboardButton("Quitar falda", callback_data="quitar_falda")])
        elif acto["ropa"]["pantis"]:
            submenu.append([InlineKeyboardButton("Quitar pantis", callback_data="quitar_pantis")])
        
        await callback_query.edit_message_text(
            "Elige qué quitar:",
            reply_markup=InlineKeyboardMarkup(submenu)
        )
        return

    elif data.startswith("quitar_"):
        item = data.split("_")[1]
        acto["ropa"][item] = False
        await query.answer(f"Le quitaste la {item} a tu hermana", show_alert=True)
        acto["mult_molestia"] += 0.1

    # Verificar condiciones de fin
    mensaje = None
    if acto["exitacion_jugador"] >= 100:
        mensaje = "Tu semen se desborda sobre el cuerpo de tu hermana"
        acto["eyaculaciones"] = acto["eyaculaciones"] + 1
        
    elif acto["exitacion_chica"] >= 100:
        mensaje = "Tu hermana tuvo un orgasmo"

    elif acto["molestia_chica"] >= 100:
        mensaje = "Tu hermana se enojo contigo"
        estado["felicidad"] = estado["felicidad"] - random.randint(80, 100)
        estado["animo"] = estado["animo"] - random.randint(80, 100)
        await callback_query.edit_message_text(mensaje)
        usuarios_acto.pop(uid, None)
        marcar_acto_terminado_2(uid)

    if mensaje:
        await callback_query.edit_message_text(mensaje, reply_markup=generar_menu_2(uid))
        #usuarios_acto.pop(uid, None)
    else:
        # Actualizar mensaje
        texto = (
            f"Exitación Jugador: {acto['exitacion_jugador']:.1f}%\n"
            f"Exitación Chica: {acto['exitacion_chica']:.1f}%\n"
            f"Molestia Chica: {acto['molestia_chica']:.1f}%\n"
            f"Estado: {'Despierta' if acto['despierta'] else 'Dormida'}"
        )
        try:
            await callback_query.edit_message_text(
                texto,
                reply_markup=generar_menu(uid)
            )
        except MessageNotModified:
            texto_modificado = texto + "." if not texto.endswith(".") else texto + " "
            await callback_query.edit_message_text(
                texto_modificado,
                reply_markup=generar_menu(uid)
            )
            

# Función para limpiar al detener el bot
async def detener_actualizacion():
    global tarea_actualizacion
    if tarea_actualizacion:
        tarea_actualizacion.cancel()
        try:
            await tarea_actualizacion
        except asyncio.CancelledError:
            pass
        tarea_actualizacion = None

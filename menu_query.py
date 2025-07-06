from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from modelo import estado_hermana, consumir_item
from tienda import productos, comprar_producto
from tiempo import avanzar_tiempo, formato_tiempo, avanzar_tiempo_noche
from persistencia import guardar_datos
from datetime import datetime
import random
from textos import (
    JUGO_EXITOSO, NO_QUIERE_JUGAR, CONVERSACION,
    COMIO, NO_HAY_HAMBRE, aleatorio
)

aburrimiento = {}
teclado_volver = InlineKeyboardMarkup([[InlineKeyboardButton("Volver", callback_data="volver")]])

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

    # 🏫 Restricción de opciones a las 07:30 de lunes a viernes
    if estado["dia_num"] <= 4 and estado["hora"].hour == 7 and estado["hora"].minute == 30:
        if accion == "ir_escuela":
            estado["energia"] -= 25
            estado["animo"] -= 10
            estado["felicidad"] += 15
            avanzar_tiempo(uid)
            respuesta = "Tu hermanita fue a clases y aprendió mucho 📚"
        elif accion == "estado":
            respuesta = (
                f"Estado de tu hermanita:\n"
                f"Hambre: {estado['hambre']}\n"
                f"Ánimo: {estado['animo']}\n"
                f"Felicidad: {estado['felicidad']}\n"
                f"Energía: {estado['energia']}\n"
                f"Dinero: ${estado['dinero']}\n" + formato_tiempo(uid)
            )
        else:
            query.answer()
            query.message.edit_text(
                "A esta hora solo puedes ir a la escuela 🏫 o revisar el estado 📋.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏫 Ir a la escuela", callback_data="ir_escuela")],
                    [InlineKeyboardButton("📋 Ver Estado", callback_data="estado")]
                ])
            )
            return

        guardar_datos()
        query.answer()
        query.message.edit_text(respuesta + "\n" + formato_tiempo(uid), reply_markup=teclado_volver)
        return

    # --- resto de acciones normales abajo ---
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

    elif accion.startswith("dormir"):
        if accion == "dormir":
            if hambre >= 80:
                respuesta = "Tu hermana no puede dormir por el hambre"
            elif estado["energia"] >= 100:
            respuesta = "La hermanita no tiene sueño aún"
                else:
            
                query.message.edit_text(
              
                    "Tu hermanita se acuesta en la cama.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Dormir también", callback_data="dormir_confirm")],
                        [InlineKeyboardButton("Invadir su cama", callback_data="acto_start")]
                    ])
        if accion == "dormir_cofirm":
                    estado["energia"] += 100
                    estado["hambre"] += 10
                    estado["animo"] -= random.randint(50, 100)
                    estado["felicidad"] -= random.randint(50, 100)
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
            delta_animo = -random.randint(2, 5) if random.random() < 0.05 else random.randint(10, 20)
            estado["animo"] += delta_animo
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
            if random.random() < 0.05:
                delta_animo = -random.randint(2, 4)
                delta_felicidad = -random.randint(1, 3)
            else:
                delta_animo = random.randint(5, 10)
                delta_felicidad = random.randint(4, 8)
            estado["animo"] += delta_animo
            estado["felicidad"] += delta_felicidad
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
                    estado[atributo] += delta
                    texto_efecto += f" {atributo.capitalize()} {delta:+d}"
            avanzar_tiempo(uid)
            respuesta = aleatorio(COMIO).format(item=item) + (texto_efecto or "")

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
    query.message.edit_text(respuesta + "\n" + formato_tiempo(uid), reply_markup=teclado_volver)

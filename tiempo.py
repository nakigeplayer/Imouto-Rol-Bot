# -*- coding: utf-8 -*-
from datetime import timedelta
from modelo import estado_hermana
import asyncio  # porque si vamos async, vamos con todo

DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

async def avanzar_tiempo_noche(user_id):
    """Avanza al día siguiente y establece la hora a las 06:30."""
    estado = estado_hermana[user_id]
    estado["dia_num"] = (estado["dia_num"] + 1) % 7
    estado["hora"] = estado["hora"].replace(hour=6, minute=30)
    await asyncio.sleep(0)  # puro arte decorativo

async def avanzar_tiempo(user_id):
    """Avanza 30 minutos en el tiempo del jugador."""
    estado = estado_hermana[user_id]
    estado["hora"] += timedelta(minutes=30)

    if estado["hora"].hour == 8 and estado["dia_num"] <= 4:
        estado["hora"] = estado["hora"].replace(hour=16, minute=0)

    if estado["hora"].hour >= 24:
        estado["hora"] = estado["hora"].replace(hour=7, minute=30)
        estado["dia_num"] = (estado["dia_num"] + 1) % 7

    if estado["hora"].hour == 8 and estado["dia_num"] == 5:
        monto = await __mesada_aleatoria()
        estado["dinero"] += monto

    await asyncio.sleep(0)

async def formato_tiempo(user_id):
    """Devuelve una cadena amigable con el tiempo y día actual."""
    estado = estado_hermana[user_id]
    hora_str = estado["hora"].strftime("%H:%M")
    dia_str = DAYS[estado["dia_num"]]
    await asyncio.sleep(0)  # para mantener el flow "asíncrono"
    return f"🕒 {hora_str} | 📅 {dia_str}"

async def __mesada_aleatoria():
    """Genera entre 10,000 y 15,000 monedas (múltiplos de 500)."""
    return 500 * await __numero_par(rand_min=20, rand_max=30)

async def __numero_par(rand_min=20, rand_max=30):
    """Devuelve un número aleatorio par en el rango dado."""
    from random import randint
    n = randint(rand_min, rand_max)
    await asyncio.sleep(0)
    return n if n % 2 == 0 else n - 1

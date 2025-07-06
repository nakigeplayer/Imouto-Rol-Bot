# -*- coding: utf-8 -*-
from datetime import timedelta
from modelo import estado_hermana

DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
def avanzar_tiempo_noche(user_id):
    """Avanza al día siguiente y establece la hora a las 06:30."""
    estado = estado_hermana[user_id]
    estado["dia_num"] = (estado["dia_num"] + 1) % 7
    estado["hora"] = estado["hora"].replace(hour=6, minute=30)
    
def avanzar_tiempo(user_id):
    """Avanza 30 minutos en el tiempo del jugador."""
    estado = estado_hermana[user_id]
    estado["hora"] += timedelta(minutes=30)

    # 📚 Salto escolar entre semana
    if estado["hora"].hour == 8 and estado["dia_num"] <= 4:
        estado["hora"] = estado["hora"].replace(hour=16, minute=0)

    # 🌙 Cambio de día si pasa medianoche
    if estado["hora"].hour >= 24:
        estado["hora"] = estado["hora"].replace(hour=7, minute=30)
        estado["dia_num"] = (estado["dia_num"] + 1) % 7

    # 💸 Mesada semanal cada sábado a las 8:00 AM
    if estado["hora"].hour == 8 and estado["dia_num"] == 5:
        monto = __mesada_aleatoria()
        estado["dinero"] += monto

def formato_tiempo(user_id):
    """Devuelve una cadena amigable con el tiempo y día actual."""
    estado = estado_hermana[user_id]
    hora_str = estado["hora"].strftime("%H:%M")
    dia_str = DAYS[estado["dia_num"]]
    return f"🕒 {hora_str} | 📅 {dia_str}"

def __mesada_aleatoria():
    """Genera entre 10,000 y 15,000 monedas (múltiplos de 500)."""
    return 500 * __numero_par(rand_min=20, rand_max=30)

def __numero_par(rand_min=20, rand_max=30):
    """Devuelve un número aleatorio par en el rango dado."""
    from random import randint
    n = randint(rand_min, rand_max)
    return n if n % 2 == 0 else n - 1
    

# -*- coding: utf-8 -*-
from datetime import datetime
from collections import defaultdict

# Estado global compartido entre módulos
estado_hermana = defaultdict(dict)

def estado_inicial():
    return {
        "hambre": 50,
        "animo": 70,
        "felicidad": 60,
        "energia": 80,
        "hora": datetime(2025, 7, 7, 7, 30),  # Día 1, lunes, 7:30 AM
        "dia_num": 0,
        "inventario": {
            "sopa instantánea": 1,
            "caramelo": 1
        },
        "dinero": 1000
    }

def inicializar_usuario(user_id):
    """Crea el estado inicial si no existe."""
    if user_id not in estado_hermana:
        estado_hermana[user_id] = estado_inicial()
    return estado_hermana[user_id]

def get_estado(user_id):
    """Devuelve el estado completo del usuario."""
    return estado_hermana.get(user_id, estado_inicial())

def actualizar_estado(user_id, clave, valor):
    """Cambia un valor del estado del usuario."""
    if user_id in estado_hermana:
        estado_hermana[user_id][clave] = valor

def modificar_valor(user_id, clave, delta, minimo=0, maximo=100):
    """Modifica un valor (como ánimo o hambre) de forma segura."""
    if user_id in estado_hermana:
        actual = estado_hermana[user_id].get(clave, 0)
        nuevo_valor = max(minimo, min(actual + delta, maximo))
        estado_hermana[user_id][clave] = nuevo_valor
        return nuevo_valor
    return None

def inventario_usuario(user_id):
    return estado_hermana[user_id].get("inventario", {})

def agregar_item(user_id, item, cantidad=1):
    inv = estado_hermana[user_id].setdefault("inventario", {})
    inv[item] = inv.get(item, 0) + cantidad

def consumir_item(user_id, item):
    inv = inventario_usuario(user_id)
    if inv.get(item, 0) > 0:
        inv[item] -= 1
        return True
    return False

def tiene_item(user_id, item):
    return inventario_usuario(user_id).get(item, 0) > 0
    
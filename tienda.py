# -*- coding: utf-8 -*-
from modelo import agregar_item

# 📦 Diccionario de productos disponibles para comprar
productos = {
    "sopa instantánea": {
        "precio": 500,
        "efecto": {"hambre": -25}
    },
    "huevo cocido": {
        "precio": 800,
        "efecto": {"hambre": -30}
    },
    "sándwich de jamón": {
        "precio": 1000,
        "efecto": {"hambre": -35, "felicidad": 5}
    },
    "queso fundido": {
        "precio": 700,
        "efecto": {"hambre": -15, "animo": 10}
    },
    "arroz blanco": {
        "precio": 600,
        "efecto": {"hambre": -20}
    },
    "puré de patatas": {
        "precio": 900,
        "efecto": {"hambre": -30, "animo": 5}
    },
    "caramelo": {
        "precio": 300,
        "efecto": {"felicidad": 15},  # efecto probable se gestiona en main
        "probabilidad": 0.7,
        "rebote": -10  # si falla
    },
    "chocolate negro": {
        "precio": 600,
        "efecto": {"felicidad": 20},
        "probabilidad": 0.7,
        "rebote": -15
    },
    "pizza mini": {
        "precio": 1300,
        "efecto": {"hambre": -40, "felicidad": 5}
    },
    "helado": {
        "precio": 1000,
        "efecto": {"felicidad": 20},
        "probabilidad": 0.7,
        "rebote": -5
    },
    "te relajante": {
        "precio": 200,
        "efecto": {"energia": -20}
        
    }
}

# 🛒 Función para procesar la compra de un producto
def comprar_producto(uid, nombre, estado):
    prod = productos.get(nombre)
    if not prod:
        return f"❌ El producto '{nombre}' no existe."

    precio = prod["precio"]
    dinero = estado.get("dinero", 0)

    if dinero < precio:
        return "💸 No tienes suficiente dinero para comprar eso."

    estado["dinero"] -= precio
    agregar_item(uid, nombre)
    return f"✅ Compraste {nombre} por ${precio} monedas."
    

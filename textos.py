import random

def aleatorio(lista):
    return random.choice(lista)

JUGO_EXITOSO = [
    "Jugaron juntos y se divirtieron mucho.",
    "La hermanita no podía parar de reír mientras jugaban.",
    "Se divirtieron lanzando juguetes por toda la casa.",
    "Hicieron una competencia de baile y fue épico.",
    "Tu hermanita aprendió a hacer malabares contigo."
]

NO_QUIERE_JUGAR = [
    "Tu hermanita está aburrida de jugar ahora.",
    "No tiene ganas de moverse.",
    "Parece que necesita otra cosa distinta al juego.",
    "Dice que quiere descansar mejor.",
    "Te mira y dice: 'Otra vez no...'."
]

CONVERSACION = [
    "Hablaron sobre sus dulces favoritos.",
    "Tu hermanita te contó un secreto de mentira.",
    "Tuvieron una charla tierna sobre estrellas.",
    "Imitaron voces de caricaturas por un rato.",
    "Se contaron chistes hasta llorar de risa."
]

COMIO = [
    "Tu hermanita comió {item} y quedó satisfecha 🍴.",
    "Dijo que el {item} estaba delicioso.",
    "Comió el {item} sin dejar ni las migas.",
    "Saboreó el {item} con alegría.",
    "¡Le encantó el {item} y hasta pidió más!"
]

NO_HAY_HAMBRE = [
    "No quiere comer {item} ahora mismo.",
    "Te dice que no tiene hambre para {item}.",
    "Rechaza el {item} y se cruza de brazos.",
    "No tiene ganas de comer {item} por ahora.",
    "Te mira y dice: '¿Otra vez {item}? No, gracias.'"
]

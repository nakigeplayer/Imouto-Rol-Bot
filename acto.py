# estado_actos.py
actos_en_progreso = set()

def marcar_acto_terminado(user_id):
    actos_en_progreso.discard(user_id)

def marcar_acto_activo(user_id):
    actos_en_progreso.add(user_id)
  

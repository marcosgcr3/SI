import random
import time
from operator import itemgetter
import collections

class BaseAgent:

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.ultima_posicion = None  # Última posición conocida
        self.contador_estancado = 0  # Contador de intentos atascados
        self.ultimo_movimiento_exitoso = None  # Último movimiento válido

        self.historial_posiciones = collections.deque(maxlen=4)  # Guardamos las últimas 4 posiciones
    def Name(self):
        return self.name

    def Id(self):
        return self.id

    def Start(self):
        print("Inicio del agente ")

    def movimiento_opuesto(self, movimiento):

        return {1: 3, 2: 4, 3: 1, 4: 2}.get(movimiento, None)

    def Update(self, perception):
        print("Toma de decisiones del agente")
        print(perception)

        # Convertir movimientos en un conjunto
        movimientos = {1, 2, 3, 4}
        disparar = False
        action = None

        # Bloquear movimientos según obstáculos
        if perception[0] in [1, 2] and perception[4] < 1:
            movimientos.discard(1)
        if perception[1] in [1, 2] and perception[5] < 1:
            movimientos.discard(2)
        if perception[2] in [1, 2] and perception[6] < 1:
            movimientos.discard(3)
        if perception[3] in [1, 2] and perception[7] < 1:
            movimientos.discard(4)

        # Verificar si puede disparar
        can_fire = perception[14] == 1

        # Priorizar disparar a amenazas
        directions = [
            (0, 4, 1),  # Up
            (1, 5, 2),  # Down
            (2, 6, 3),  # Right
            (3, 7, 4)  # Left
        ]
        """
        # Orden de prioridad: SHELL (cercana), PLAYER, COMMAND_CENTER, BRICK
        for dir_idx, dist_idx, move in directions:
            obj = perception[dir_idx]
            dist = perception[dist_idx]
            if can_fire:
                if obj == 5 and dist <= 2:  # SHELL cercana
                    return move, True
                elif obj == 4:  # PLAYER
                    return move, True
                elif obj == 3:  # COMMAND_CENTER
                    return move, True
                elif obj == 2 and self._is_brick_blocking(perception, move):  # BRICK útil
                    return move, True


        """
        if perception[0] == 3 or perception[0] == 4 or perception[0] == 5 or perception[0] == 6:
            return 1, True
        if perception[1] == 3 or perception[1] == 4 or perception[1] == 5 or perception[1] == 6:
            return 2, True
        if perception[2] == 3 or perception[2] == 4 or perception[2] == 5 or perception[2] == 6:
            return 3, True
        if perception[3] == 3 or perception[3] == 4 or perception[3] == 5 or perception[3] == 6:
            return 4, True
        # Si no hay movimientos, quedarse quieto
        if not movimientos:
            return None, disparar

        # Calcular mejor movimiento hacia el Command Center
        x_actual, y_actual = perception[12], perception[13]
        x_objetivo, y_objetivo = perception[10], perception[11]

        aux = []
        for movimiento in movimientos:
            if movimiento == 1:
                nueva_x, nueva_y = x_actual, y_actual + 1
            elif movimiento == 2:
                nueva_x, nueva_y = x_actual + 1, y_actual
            elif movimiento == 3:
                nueva_x, nueva_y = x_actual, y_actual - 1
            elif movimiento == 4:
                nueva_x, nueva_y = x_actual - 1, y_actual

            distancia = abs(x_objetivo - nueva_x) + abs(y_objetivo - nueva_y)
            aux.append((distancia, movimiento, (nueva_x, nueva_y)))


        aux.sort(key=lambda x: x[0])
        self.historial_posiciones.append((x_actual, y_actual))
        # Manejar estancamiento
        if self.ultima_posicion == (x_actual, y_actual):
            self.contador_estancado += 1
        else:
            self.contador_estancado = 0
        self.ultima_posicion = (x_actual, y_actual)

        # Elegir acción evitando peligros
        if self.contador_estancado >= 3 and len(aux) > 1:
            action = aux[1][1]
        else:
            action = aux[0][1]


        if len(self.historial_posiciones) == 4:
            p1, p2, p3, p4 = self.historial_posiciones
            if p1 == p3 and p2 == p4:
                print(f"🔄 Detectado bucle entre {p1} y {p2}, cambiando estrategia.")
                if len(aux) > 1:
                    action = aux[1][1]  # Elegir el segundo mejor movimiento
                else:
                    action = aux[0][1]  # Si solo hay una opción, tomarla

        print(aux)
        print(f"Movimiento elegido: {action}, Disparar: {disparar}")
        return action, False

    def _is_brick_blocking(self, perception, move):

        x_agent, y_agent = perception[12], perception[13]
        x_target, y_target = perception[10], perception[11]

        # Determinar dirección del movimiento
        if move == 1 and y_agent < y_target:
            return True  # BRICK arriba en ruta
        elif move == 3 and y_agent > y_target:
            return True  # BRICK abajo en ruta
        elif move == 2 and x_agent < x_target:
            return True  # BRICK derecha en ruta
        elif move == 4 and x_agent > x_target:
            return True  # BRICK izquierda en ruta
        return False

    def End(self, win):
        print("Agente finalizado")
        print("Victoria ", win)


"""   
class BaseAgent:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.ultima_posicion = None  # Última posición conocida
        self.contador_estancado = 0  # Contador de intentos atascados
        self.ultimo_movimiento_exitoso = None  # Último movimiento válido

    def Name(self):
        return self.name

    def Id(self):
        return self.id

    def Start(self):
        print("Inicio del agente ")

    def movimiento_opuesto(self, movimiento):
        
        return {1: 3, 2: 4, 3: 1, 4: 2}.get(movimiento, None)

    def Update(self, perception):
        print("Toma de decisiones del agente")
        print(perception)

        movimientos = [1, 2, 3, 4]
        disparar = False

        # Bloquear movimientos según la percepción
        if (perception[0] == 1 and perception[4] < 1) or (perception[0] == 2 and perception[4] < 1):
            movimientos.remove(1)
        if (perception[1] == 1 and perception[5] < 1) or (perception[1] == 2 and perception[5] < 1):
            movimientos.remove(2)
        if (perception[2] == 1 and perception[6] < 1) or (perception[2] == 2 and perception[6] < 1):
            movimientos.remove(3)
        if (perception[3] == 1 and perception[7] < 1) or (perception[3] == 2 and perception[7] < 1):
            movimientos.remove(4)

        if not movimientos:  # Si no hay movimientos válidos, quedarse quieto
            return None, disparar

        if perception[0] == 3 or perception[0] == 4 or perception[0] == 5 or perception[0] == 6:
            return 1, True
        if perception[1] == 3 or perception[1] == 4 or perception[1] == 5 or perception[1] == 6:
            return 2, True
        if perception[2] == 3 or perception[2] == 4 or perception[2] == 5 or perception[2] == 6:
            return 3, True
        if perception[3] == 3 or perception[3] == 4 or perception[3] == 5 or perception[3] == 6:
            return 4, True
        # Coordenadas actuales del agente
        x_actual = perception[12]
        y_actual = perception[13]

        # Coordenadas objetivo
        x_objetivo = perception[10]
        y_objetivo = perception[11]

        # Evaluar los movimientos posibles
        aux = []
        for movimiento in movimientos:
            if movimiento == 1:
                nueva_x, nueva_y = x_actual, y_actual + 1
            elif movimiento == 2:
                nueva_x, nueva_y = x_actual + 1, y_actual
            elif movimiento == 3:
                nueva_x, nueva_y = x_actual, y_actual - 1
            elif movimiento == 4:
                nueva_x, nueva_y = x_actual - 1, y_actual

            distancia = abs(x_objetivo - nueva_x) + abs(y_objetivo - nueva_y)

            # distancia = ((x_objetivo - nueva_x) ** 2 + (y_objetivo - nueva_y) ** 2) ** 0.5
            aux.append((distancia, movimiento, (nueva_x, nueva_y)))

        # Ordenar movimientos por la menor distancia
        aux.sort(key=lambda x: x[0])  # Ordena por distancia

        # Verificar si el agente se ha quedado en la misma posición
        if self.ultima_posicion == (x_actual, y_actual):
            self.contador_estancado += 1
        else:
            self.contador_estancado = 0  # Reiniciar si se movió

        self.ultima_posicion = (x_actual, y_actual)  # Guardar la última posición

        # Si el agente ha estado estancado más de 3 veces, elegir el segundo mejor movimiento

        if self.contador_estancado >= 3 and len(aux) > 1:

            action = aux[1][1]  # Elegir el segundo mejor movimiento
        else:
            action = aux[0][1]  # Elegir el mejor movimiento

        print("Movimiento elegido:", action)
        print("Historial de movimientos evaluados:", aux)
        print("Intentos atascado:", self.contador_estancado)

        return action, disparar

    def End(self, win):
        print("Agente finalizado")
        print("Victoria ", win)
"""
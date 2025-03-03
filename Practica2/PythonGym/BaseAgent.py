
import collections

UP = 1
DOWN = 2
RIGHT = 3
LEFT = 4

EMPTY = 0
OBSTACLE = 1
WALL = 2
COMMAND_CENTER = 3
PLAYER = 4
SHELL = 5
OTHER = 6


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
        return {UP: RIGHT, DOWN: LEFT, RIGHT: UP, LEFT: DOWN}.get(movimiento, None)

    def objetoPorMov(self, mov):
        return {UP: 0, DOWN: 1, RIGHT: 2, LEFT: 3}.get(mov, None)
    def mejores_movimiento(self, perception, movimientos):
        x_actual, y_actual = perception[12], perception[13]
        x_objetivo, y_objetivo = perception[10], perception[11]

        aux = []
        for movimiento in movimientos:
            if movimiento == UP:
                nueva_x, nueva_y = x_actual, y_actual + 1
            elif movimiento == DOWN:
                nueva_x, nueva_y = x_actual, y_actual - 1
            elif movimiento == RIGHT:
                nueva_x, nueva_y = x_actual + 1, y_actual
            elif movimiento == LEFT:
                nueva_x, nueva_y = x_actual - 1, y_actual

            distancia = abs(x_objetivo - nueva_x) + abs(y_objetivo - nueva_y)
            aux.append((distancia, movimiento, (nueva_x, nueva_y)))
        aux.sort(key=lambda x: x[0])
        return aux
    def manejar_estancamientos(self, mejores_mov, x_actual, y_actual):
        self.historial_posiciones.append((x_actual, y_actual))
        # Manejar estancamiento
        if self.ultima_posicion == (x_actual, y_actual):
            self.contador_estancado += 1
        else:
            self.contador_estancado = 0
        self.ultima_posicion = (x_actual, y_actual)

        # Elegir acción evitando peligros
        if self.contador_estancado >= 3 and len(mejores_mov) > 1:
            action = mejores_mov[1][1]
        else:
            action = mejores_mov[0][1]

        if len(self.historial_posiciones) == 4:
            p1, p2, p3, p4 = self.historial_posiciones
            if p1 == p3 and p2 == p4:
                print(f"Detectado bucle entre {p1} y {p2}, cambiando estrategia.")
                if len(mejores_mov) > 1:
                    action = mejores_mov[1][1]  # Elegir el segundo mejor movimiento
                else:
                    action = mejores_mov[0][1]  # Si solo hay una opción, tomarla
        return action
    def Update(self, perception):
       
        print("Toma de decisiones del agente")
        print(perception)

        # Convertir movimientos en un conjunto
        movimientos = {1, 2, 3, 4}
        disparar = False
        action = None
        x_actual, y_actual = perception[12], perception[13]
        x_objetivo, y_objetivo = perception[10], perception[11]
        distancia_actual = abs(x_objetivo - x_actual) + abs(y_objetivo - y_actual)

        # Bloquear movimientos según obstáculos

        if distancia_actual > 6:
            if perception[0] in [OBSTACLE, WALL] and perception[4] < 1.0:
                movimientos.discard(UP)
            if perception[1] in [OBSTACLE, WALL] and perception[5] < 1.0:
                movimientos.discard(DOWN)
            if perception[2] in [OBSTACLE, WALL] and perception[6] < 1.0:
                movimientos.discard(RIGHT)
            if perception[3] in [OBSTACLE, WALL] and perception[7] < 1.0:
                movimientos.discard(LEFT)
        else:
            if perception[0] == OBSTACLE:
                movimientos.discard(UP)
            if perception[1] == OBSTACLE:
                movimientos.discard(DOWN)
            if perception[2] == OBSTACLE:
                movimientos.discard(RIGHT)
            if perception[3] == OBSTACLE:
                movimientos.discard(LEFT)

        
        # Verificar si puede disparar
        can_fire = perception[14] == 1

        directions = [
            (0, 4, UP),    # Up
            (1, 5, DOWN),  # Down
            (2, 6, RIGHT), # Right
            (3, 7, LEFT)   # Left
        ]

        if not movimientos:
            return None, disparar

        # Llamar a mejor_movimiento
        mejores_mov = self.mejores_movimiento(perception, movimientos)
     

         # Llamar a decidir_disparo
        accion_disparo, disparar = self.decidir_disparo(perception, directions, can_fire, mejores_mov, distancia_actual)       
        if accion_disparo is not None:
            return accion_disparo, disparar  # Ejecuta el disparo a la amenaza


        action = self.manejar_estancamientos(mejores_mov, x_actual, y_actual)
       
        print(mejores_mov)
        print(f"Movimiento elegido: {action}, Disparar: {disparar}")
        return action, False

    
    def decidir_disparo(self,perception, directions, can_fire, mejores_mov, distancia_actual):
      
       
        if perception[self.objetoPorMov(mejores_mov[0][1])] == WALL and distancia_actual < 6:
            return mejores_mov[0][1], True
        # Lista para almacenar posibles acciones de disparo: (prioridad, movimiento)
        acciones_disparo = []

        # Examinar cada dirección
        for dir_idx, dist_idx, move in directions:
            obj = perception[dir_idx]
            dist = perception[dist_idx]
            if can_fire:
                if obj == SHELL:  # SHELL cercana
                    acciones_disparo.append((1, move))  # Prioridad alta
                elif obj == PLAYER:  # PLAYER
                    acciones_disparo.append((2, move))  # Prioridad media
                elif obj == COMMAND_CENTER:  # COMMAND_CENTER
                    acciones_disparo.append((3, move))  # Prioridad baja
                elif obj == OTHER:  # COMMAND_CENTER
                    acciones_disparo.append((4, move))  # Prioridad baja
                #elif obj == 2 and distancia_actual < 6:  # BRICK útil
                #    acciones_disparo.append((4, move))  # Prioridad más baja

        # Si hay acciones de disparo, elegir la de mayor prioridad
        if acciones_disparo:
            acciones_disparo.sort(key=lambda x: x[0])  # Ordenar por prioridad (menor número = mayor prioridad)
            return acciones_disparo[0][1], True  # Devolver el movimiento de la acción prioritaria

       
        return None, False
    



    def End(self, win):
        print("Agente finalizado")
        print("Victoria ", win)
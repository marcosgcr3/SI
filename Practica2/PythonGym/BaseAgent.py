
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

EXPLORAR = 0
ATAQUE = 1
HUIDA=2


directions = [
    (0, 4, UP),  # Up
    (1, 5, DOWN),  # Down
    (2, 6, RIGHT),  # Right
    (3, 7, LEFT)  # Left
]


class BaseAgent:

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.ultima_posicion = None  # Última posición conocida
        self.contador_estancado = 0  # Contador de intentos atascados
        self.ultimo_movimiento_exitoso = None  # Último movimiento válido
        self.estado = EXPLORAR
        self.ESCAPAR = None
        self.historial_posiciones = collections.deque(maxlen=4)  # Guardamos las últimas 4 posiciones
        self.atascado = False

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
    def cambio_estado(self, perception, distance):
        for i in range(4):
            if perception[i] in [SHELL, PLAYER, COMMAND_CENTER, OTHER] or self.atascado or (perception[i] == WALL and distance <6 ):
                if perception[14]==1:
                    self.estado = ATAQUE
                    break
                else:
                    if perception[i] in [SHELL, PLAYER, OTHER]:
                        self.estado = HUIDA
                        self.ESCAPAR = i
                    else:
                        self.estado = ATAQUE

            else:
                self.estado = EXPLORAR
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
    def bloquear_mov(self, distancia_actual , movimientos, perception):
        j=0
        for i in range(4):
            if perception[i] in [OBSTACLE, WALL] and perception[i+4] < 1:
                j=j+1

        if j >= 3:
            self.atascado = True
            if perception[0] == OBSTACLE:
                movimientos.discard(UP)
            if perception[1] == OBSTACLE:
                movimientos.discard(DOWN)
            if perception[2] == OBSTACLE:
                movimientos.discard(RIGHT)
            if perception[3] == OBSTACLE:
                movimientos.discard(LEFT)



        else:

            self.atascado = False


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
    def decidir_disparo(self, perception, mejores_mov, distancia_actual):


        # Lista para almacenar posibles acciones de disparo: (prioridad, movimiento)
        acciones_disparo = []

        # Examinar cada dirección
        for dir_idx, dist_idx, move in directions:
            obj = perception[dir_idx]

            if obj == SHELL:  # SHELL cercana
                acciones_disparo.append((1, move))  # Prioridad alta
            elif obj == PLAYER:  # PLAYER
                acciones_disparo.append((2, move))  # Prioridad media
            elif obj == COMMAND_CENTER:  # COMMAND_CENTER
                acciones_disparo.append((3, move))  # Prioridad baja
            elif obj == OTHER:  # COMMAND_CENTER
                acciones_disparo.append((4, move))  # Prioridad baja
            elif obj == 2 and perception[dist_idx] <6 and move == mejores_mov[0][1]:  # BRICK útil
                acciones_disparo.append((5, move))  # Prioridad más baja

        # Si hay acciones de disparo, elegir la de mayor prioridad
        if acciones_disparo:
            acciones_disparo.sort(key=lambda x: x[0])  # Ordenar por prioridad (menor número = mayor prioridad)
            return acciones_disparo[0][1], True  # Devolver el movimiento de la acción prioritaria


        return mejores_mov[0][1], False

    def huir(self, perception):
        # Si no hay dirección de peligro definida, no hay nada de qué huir
        if self.ESCAPAR is None:
            return None


        idx_huida = self.movimiento_opuesto(self.ESCAPAR)

        # Si la dirección del peligro es inválida, no huir
        if idx_huida is None:
            return None

        # Mapeo de índices a direcciones reales: 0 -> UP (1), 1 -> DOWN (2), 2 -> RIGHT (3), 3 -> LEFT (4)
        dir_from_idx = [UP, DOWN, RIGHT, LEFT]
        direccion_huida = dir_from_idx[idx_huida]

        # Verificar si la dirección opuesta está libre
        if perception[idx_huida] == EMPTY:
            return direccion_huida

        # Si la dirección opuesta no está libre, buscar direcciones perpendiculares
        perpendiculares_indices = {
            0: [2, 3],  # UP: RIGHT, LEFT
            1: [2, 3],  # DOWN: RIGHT, LEFT
            2: [0, 1],  # RIGHT: UP, DOWN
            3: [0, 1]  # LEFT: UP, DOWN
        }

        # Revisar las direcciones perpendiculares al peligro
        for idx_alt in perpendiculares_indices.get(self.ESCAPAR, []):
            if perception[idx_alt] == EMPTY:
                return dir_from_idx[idx_alt]

        # Si no hay perpendiculares libres, elegir cualquier dirección libre
        for idx in range(4):
            if perception[idx] == EMPTY:
                return dir_from_idx[idx]


        return None






    def Update(self, perception):

        print("Toma de decisiones del agente")
        print(perception)
        movimientos = {1, 2, 3, 4}
        disparar = False
        action = None
        x_actual, y_actual = perception[12], perception[13]
        x_objetivo, y_objetivo = perception[10], perception[11]
        distancia_actual = abs(x_objetivo - x_actual) + abs(y_objetivo - y_actual)
        self.cambio_estado(perception, distancia_actual)
        self.bloquear_mov(distancia_actual, movimientos, perception)

        if not movimientos:
            return None, disparar

        # Llamar a mejor_movimiento

        mejores_mov = self.mejores_movimiento(perception, movimientos)
        if self.estado == ATAQUE:

            accion_disparo, disparar = self.decidir_disparo(perception,  mejores_mov, distancia_actual)
            if accion_disparo is not None:
                return accion_disparo, disparar  # Ejecuta el disparo a la amenaza
        elif self.estado == EXPLORAR:

            action = self.manejar_estancamientos(mejores_mov, x_actual, y_actual)
        else:

            action = self.huir(perception)

        print(mejores_mov)
        print(f"Estado: {self.estado}")
        print(f"Movimiento elegido: {action}, Disparar: {disparar}")
        return action, False







    def End(self, win):
        print("Agente finalizado")
        print("Victoria ", win)
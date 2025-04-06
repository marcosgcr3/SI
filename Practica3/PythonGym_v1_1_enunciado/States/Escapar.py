from StateMachine.State import State
from States.AgentConsts import AgentConsts
import random


class Escapar(State):

    def __init__(self, id):
        super().__init__(id)
        self.lastAction = AgentConsts.NO_MOVE
        self.dangerDirection = -1
        self.EscaparTime = 0

    def Start(self, agent):
        super().Start(agent)
        self.EscaparTime = 0
        self.lastAction = AgentConsts.NO_MOVE

    def Update(self, perception, map, agent):
        # Determinar la dirección de la amenaza
        self.dangerDirection = self.DetectDangerDirection(perception)

        # Elegir dirección opuesta a la amenaza o una dirección segura aleatoria
        action = self.ChooseSafeDirection(perception, self.dangerDirection)

        # Si no encontramos una dirección segura, quedarnos quietos
        if action == AgentConsts.NO_MOVE:
            # Intentar otra dirección aleatoria que no sea la dirección de peligro
            possible_directions = [AgentConsts.MOVE_UP, AgentConsts.MOVE_DOWN,
                                   AgentConsts.MOVE_LEFT, AgentConsts.MOVE_RIGHT]
            if self.dangerDirection >= 0 and self.dangerDirection < 4:
                danger_move = self.dangerDirection + 1  # Convertir índice de percepción a movimiento
                if danger_move in possible_directions:
                    possible_directions.remove(danger_move)

            action = random.choice(possible_directions) if possible_directions else AgentConsts.NO_MOVE

        self.lastAction = action
        # No disparamos mientras huimos
        return action, False

    def Transit(self, perception, map):
        # Incrementar el tiempo de huida
        self.EscaparTime += 1

        # Si ya no hay amenaza y ha pasado suficiente tiempo, volver a ejecutar el plan
        if not self.IsInDanger(perception) and self.EscaparTime > 5:
            return "ExecutePlan"

        # Si seguimos en peligro, mantenernos en estado de huida
        return self.id

    def DetectDangerDirection(self, perception):
        # Verificar las 4 direcciones principales para la amenaza (jugador o proyectil)
        for i in range(4):  # UP, DOWN, RIGHT, LEFT
            if perception[i] == AgentConsts.SHELL or perception[i] == AgentConsts.PLAYER:
                return i

        # Si no hay amenaza inmediata pero podemos ver al jugador, considerar su dirección
        playerX = perception[AgentConsts.PLAYER_X]
        playerY = perception[AgentConsts.PLAYER_Y]
        agentX = perception[AgentConsts.AGENT_X]
        agentY = perception[AgentConsts.AGENT_Y]

        if playerX >= 0 and playerY >= 0:  # Si el jugador está visible
            # Calcular la dirección aproximada del jugador
            dx = playerX - agentX
            dy = playerY - agentY

            if abs(dx) > abs(dy):
                return AgentConsts.NEIGHBORHOOD_RIGHT if dx > 0 else AgentConsts.NEIGHBORHOOD_LEFT
            else:
                return AgentConsts.NEIGHBORHOOD_DOWN if dy > 0 else AgentConsts.NEIGHBORHOOD_UP

        return -1  # No se detectó peligro

    def ChooseSafeDirection(self, perception, dangerDirection):
        # Si no hay peligro inmediato, mantener la dirección actual
        if dangerDirection == -1:
            return self.lastAction if self.lastAction != AgentConsts.NO_MOVE else random.randint(1, 4)

        # Determinamos la dirección opuesta al peligro
        opposite_direction = -1
        if dangerDirection == AgentConsts.NEIGHBORHOOD_UP:
            opposite_direction = AgentConsts.MOVE_DOWN
        elif dangerDirection == AgentConsts.NEIGHBORHOOD_DOWN:
            opposite_direction = AgentConsts.MOVE_UP
        elif dangerDirection == AgentConsts.NEIGHBORHOOD_RIGHT:
            opposite_direction = AgentConsts.MOVE_LEFT
        elif dangerDirection == AgentConsts.NEIGHBORHOOD_LEFT:
            opposite_direction = AgentConsts.MOVE_RIGHT

        # Verificar si la dirección opuesta es segura (no hay obstáculos)
        index_to_check = opposite_direction - 1  # Convertir movimiento a índice de percepción
        if index_to_check >= 0 and index_to_check < 4:
            if perception[index_to_check] == AgentConsts.NOTHING:
                return opposite_direction

        # Si la dirección opuesta no es segura, buscar cualquier dirección segura
        safe_directions = []
        for i in range(4):  # Verificar las 4 direcciones
            if perception[i] == AgentConsts.NOTHING:
                safe_directions.append(i + 1)  # Convertir índice de percepción a movimiento

        if safe_directions:
            return random.choice(safe_directions)

        # Si no hay dirección segura, mantener la dirección actual o quedarse quieto
        return self.lastAction if self.lastAction != AgentConsts.NO_MOVE else AgentConsts.NO_MOVE

    def IsInDanger(self, perception):
        # Verificar si hay proyectiles o jugador cerca
        for i in range(4):  # UP, DOWN, RIGHT, LEFT
            if perception[i] == AgentConsts.SHELL or perception[i] == AgentConsts.PLAYER:
                return True

        # Verificar si el jugador está visible y no tenemos munición
        playerX = perception[AgentConsts.PLAYER_X]
        playerY = perception[AgentConsts.PLAYER_Y]
        canFire = perception[AgentConsts.CAN_FIRE]

        if playerX >= 0 and playerY >= 0 and canFire == 0:
            # Calcular distancia al jugador
            agentX = perception[AgentConsts.AGENT_X]
            agentY = perception[AgentConsts.AGENT_Y]
            playerDist = abs(playerX - agentX) + abs(playerY - agentY)

            # Si el jugador está cerca y no podemos disparar, estamos en peligro
            if playerDist < 8:
                return True

        return False
from StateMachine.State import State
from States.AgentConsts import AgentConsts


# Estado que nos permite atacar un objetivos desde la celda adyacente.
# se espera que el agente ay esté orientado
# agent.directionToLook es seteado por ExecutePlan para indicarnos cual es la dirección
# donde está el enemigo a atacar
class Attack(State):

    def __init__(self, id):
        super().__init__(id)
        self.directionToLook = -1

    def Update(self, perception, map, agent):
        # Verificar si necesitamos huir (no tenemos munición)
        if self.ShouldFlee(perception):
            return 0, False  # No nos movemos, pero no disparamos y cambiamos de estado

        self.directionToLook = agent.directionToLook
        return 0, True

    def Transit(self, perception, map):
        # Si no podemos disparar y hay una amenaza, huir
        if self.deberiaEscapar(perception):
            return "Escapar"

        target = perception[self.directionToLook]
        # si mi target ya no está vuelvo a ExecutePlan
        if target != AgentConsts.PLAYER and target != AgentConsts.COMMAND_CENTER:
            return "ExecutePlan"
        return self.id

    def deberiaEscapar(self, perception):
        # Si no podemos disparar y detectamos amenaza, huir
        if perception[AgentConsts.CAN_FIRE] == 0:
            # Verificar si hay proyectiles
            for i in range(4):  # UP, DOWN, RIGHT, LEFT
                if perception[i] == AgentConsts.SHELL:
                    return True

            # Verificar si hay jugador cerca
            for i in range(4):  # UP, DOWN, RIGHT, LEFT
                if perception[i] == AgentConsts.PLAYER:
                    return True

            # Verificar si el jugador está visible y cerca
            playerX = perception[AgentConsts.PLAYER_X]
            playerY = perception[AgentConsts.PLAYER_Y]

            if playerX >= 0 and playerY >= 0:
                # Calcular distancia al jugador
                agentX = perception[AgentConsts.AGENT_X]
                agentY = perception[AgentConsts.AGENT_Y]
                playerDist = abs(playerX - agentX) + abs(playerY - agentY)

                # Si el jugador está cerca y no podemos disparar, debemos huir
                if playerDist < 8:
                    return True

        return False
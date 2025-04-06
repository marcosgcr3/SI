import random



from States.AgentConsts import AgentConsts

class GoalMonitor:

    GOAL_COMMAND_CENTRER = 0
    GOAL_LIFE = 1
    GOAL_PLAYER = 2
    GOAL_SHELL = 3

    def __init__(self, problem, goals):
        self.goals = goals
        self.problem = problem
        self.lastTime = -1
        self.recalculate = False
        self.planA= False

    def ForceToRecalculate(self):
        self.recalculate = True

    def NeedReplaning(self, perception, map, agent):
        if self.recalculate:
            self.lastTime = perception[AgentConsts.TIME]
            self.recalculate = False
            return True

        # Replanificar en estas condiciones:




        playerX, playerY = perception[AgentConsts.PLAYER_X], perception[AgentConsts.PLAYER_Y]
        agentX, agentY = perception[AgentConsts.AGENT_X], perception[AgentConsts.AGENT_Y]
        commandX, commandY = perception[AgentConsts.COMMAND_CENTER_X], perception[AgentConsts.COMMAND_CENTER_Y]







        # 1. Si detencta un enemigo
        playerDist = abs(playerX - agentX) + abs(playerY - agentY)
        comandDist = abs(commandX - agentX) + abs(commandY - agentY)
        if playerDist < comandDist and playerDist < 10 and perception[AgentConsts.PLAYER_X] >= 0 and perception[AgentConsts.PLAYER_Y] >= 0:
            self.lastTime = perception[AgentConsts.TIME]

            return True



        #Si nuestro objetivo actual es el jugador pero estamos mas cerca de command center, vamos a por el.
        goal = agent.problem.GetGoal()
        if goal.value == AgentConsts.PLAYER and playerDist > comandDist or perception[AgentConsts.TIME] - self.lastTime > 4:
            self.lastTime = perception[AgentConsts.TIME]

            return True




        # 2. Si ha pasado más de 5 segundos desde la última planificación(por si se atasca)
        if perception[AgentConsts.TIME] - self.lastTime > 5:
            self.lastTime = perception[AgentConsts.TIME]
            return True

        # 3. Si nuestra salud está baja (menos de 2)
        if perception[AgentConsts.HEALTH] < 2:
            self.lastTime = perception[AgentConsts.TIME]
            return True

        # 4. Si el plan actual está vacío
        if len(agent.GetPlan()) == 0:
            self.lastTime = perception[AgentConsts.TIME]
            return True

        return False

    def SelectGoal(self, perception, map, agent):

        playerX, playerY = perception[AgentConsts.PLAYER_X], perception[AgentConsts.PLAYER_Y]
        agentX, agentY = perception[AgentConsts.AGENT_X], perception[AgentConsts.AGENT_Y]
        commandX, commandY = perception[AgentConsts.COMMAND_CENTER_X], perception[AgentConsts.COMMAND_CENTER_Y]
        # 1. Si hay un power-up de vida y tenemos poca vida, priorizar ir por él
        if perception[AgentConsts.HEALTH] < 2 and perception[AgentConsts.LIFE_X] >= 0 and perception[
            AgentConsts.LIFE_Y] >= 0:
            return self.goals[self.GOAL_LIFE]



        # 2. Si el jugador está cerca, priorizar atacarlo
        playerDist = abs(playerX - agentX) + abs(playerY - agentY)
        comandDist = abs(commandX - agentX) + abs(commandY - agentY)
        if playerDist < comandDist and playerDist < 10 and perception[AgentConsts.PLAYER_X] >= 0 and perception[
            AgentConsts.PLAYER_Y] >= 0:
            self.lastTime = perception[AgentConsts.TIME]

            return self.goals[self.GOAL_PLAYER]




        # 3. Por defecto, ir al centro de comando
        return self.goals[self.GOAL_COMMAND_CENTRER]

    def UpdateGoals(self,goal, goalId):
        self.goals[goalId] = goal

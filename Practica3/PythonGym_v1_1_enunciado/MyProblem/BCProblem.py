#import sys
#sys.path.insert(1, '../AStar')
from AStar.Problem import Problem
from MyProblem.BCNode import BCNode
from States.AgentConsts import AgentConsts
import sys
import numpy as np

#Clase que implementa el problema especifico que queremos resolver y que hereda de la calse
#Problema genérico.
class BCProblem(Problem):
    

    def __init__(self, initial, goal, xSize, ySize):
        super().__init__(initial, goal)
        self.map = np.zeros((xSize,ySize),dtype=int)
        self.xSize = xSize
        self.ySize = ySize
    
    #inicializa un mapa con el mapa proveniente del entorno Vector => Matriz
    def InitMap(self,m):
        for i in range(len(m)):
            x,y = BCProblem.Vector2MatrixCoord(i,self.xSize,self.ySize)
            self.map[x][y] = m[i]

    #Muestra el mapa por consola
    def ShowMap(self):
        for j in range(self.ySize):
            s = ""
            for i in range(self.xSize):
                s += ("[" + str(i) + "," + str(j) + "," + str(self.map[i][j]) +"]")
            print(s)

    #Calcula la heuristica del nodo en base al problema planteado (Se necesita reimplementar)
    def Heuristic(self, node):
        # Distancia Manhattan entre el nodo y el objetivo
        return abs(node.x - self.goal.x) + abs(node.y - self.goal.y)

    def GetSucessors(self, node):
        successors = []
        # Verificar si podemos movernos en las 4 direcciones
        # Derecha
        if node.x + 1 < self.xSize and BCProblem.CanMove(self.map[node.x + 1][node.y]):
            self.CreateNode(successors, node, node.x + 1, node.y)
        # Izquierda
        if node.x - 1 >= 0 and BCProblem.CanMove(self.map[node.x - 1][node.y]):
            self.CreateNode(successors, node, node.x - 1, node.y)
        # Arriba
        if node.y - 1 >= 0 and BCProblem.CanMove(self.map[node.x][node.y - 1]):
            self.CreateNode(successors, node, node.x, node.y - 1)
        # Abajo
        if node.y + 1 < self.ySize and BCProblem.CanMove(self.map[node.x][node.y + 1]):
            self.CreateNode(successors, node, node.x, node.y + 1)
        return successors
    
    #métodos estáticos
    #nos dice si podemos movernos hacia una casilla, se debe poner el valor de la casilla como
    #parámetro
    @staticmethod
    def CanMove(value):
        return value != AgentConsts.UNBREAKABLE and value != AgentConsts.SEMI_UNBREKABLE and value != AgentConsts.SEMI_UNBREKABLE
    
    #convierte coordenadas mapa en formato vector a matriz
    @staticmethod
    def Vector2MatrixCoord(pos,xSize,ySize):
        x = pos % xSize
        y = pos // ySize #division entera
        return x,y

    #convierte coordenadas mapa en formato matriz a vector
    @staticmethod
    def Matrix2VectorCoord(x,y,xSize):
        return y * xSize + x
    
    #convierte coordenadas del mapa en coordenadas del entorno (World) (nótese que la Y está invertida)
    @staticmethod
    def MapToWorldCoord(x,y,ySize):
        xW = x * 2
        yW = (ySize - y - 1) * 2
        return xW, yW

    #convierte coordenadas del entorno (World) en coordenadas mapa (nótese que la Y está invertida)
    @staticmethod
    def WorldToMapCoord(xW,yW,ySize):
        x = xW // 2
        y = yW // 2
        y = ySize - y - 1
        return x, y
    
    #versión real del método anterior, que nos ayuda a buscar los centros de las celdas.
    #aqui nos dirá los decimales, es decir como de cerca estamos de la esquina superior derecha
    #un valor de 1.9,1.9 nos dice que estamos en la casilla 1,1 muy cerca de la 2,2
    #en realidad, lo que buscamos es el punto medio de la casilla, es decir la 1.5, 1.5 en el caso
    #de la casilla 1,1
    @staticmethod
    def WorldToMapCoordFloat(xW,yW,ySize):
        x = xW / 2
        invY = (ySize*2) - yW
        invY = invY / 2
        return x, invY

    #se utiliza para calcular el coste de cada elemento del mapa 
    @staticmethod
    def GetCost(value):
        # Asignar costos según el tipo de casilla
        if value == AgentConsts.NOTHING:
            return 1
        elif value == AgentConsts.BRICK:
            return 5  # Costo para romper un ladrillo
        elif value == AgentConsts.SEMI_BREKABLE:
            return 3  # Costo para romper un semi-rompible
        elif value == AgentConsts.COMMAND_CENTER:
            return 10  # Costo para el centro de comando (objetivo final)
        elif value == AgentConsts.LIFE:
            return 2  # Costo para vida (prioridad alta)
        elif value == AgentConsts.PLAYER:
            return 7  # Costo para el jugador (enemigo)
        else:  # Paredes no rompibles
            return sys.maxsize
    #crea un nodo y lo añade a successors (lista) con el padre indicado y la posición x,y en coordenadas mapa 
    def CreateNode(self,successors,parent,x,y):
        value=self.map[x][y]
        g=BCProblem.GetCost(value)
        rightNode = BCNode(parent,g,value,x,y)
        rightNode.SetH(self.Heuristic(rightNode))
        successors.append(rightNode)

    #Calcula el coste de ir del nodo from al nodo to (Se necesita reimplementar)
    def GetGCost(self, nodeTo):
        return BCProblem.GetCost(nodeTo.value)
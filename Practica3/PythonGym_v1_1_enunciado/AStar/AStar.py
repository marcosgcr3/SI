

#Algoritmo A* genérico que resuelve cualquier problema descrito usando la plantilla de la
#la calse Problem que tenga como nodos hijos de la clase Node
class AStar:

    def __init__(self, problem):
        self.open = [] # lista de abiertos o frontera de exploración
        self.precessed = set() # set, conjunto de cerrados (más eficiente que una lista)
        self.problem = problem #problema a resolver

    def GetPlan(self):
        findGoal = False
        self.open.clear()
        self.precessed.clear()
        self.open.append(self.problem.Initial())
        path = []

        # Mientras haya nodos en abiertos y no hayamos encontrado la meta
        while len(self.open) > 0 and not findGoal:
            # Ordenar los nodos por su F(n) = G(n) + H(n)
            self.open.sort(key=lambda node: node.F())

            # Extraer el nodo con menor F(n)
            current = self.open.pop(0)

            # Si es la meta, reconstruir el camino
            if self.problem.IsASolution(current):
                findGoal = True
                path = self.ReconstructPath(current)
                return path[::-1]  # Devolver el camino invertido

            # Añadir a cerrados
            self.precessed.add(current)

            # Expandir el nodo
            successors = self.problem.GetSucessors(current)

            # Si no hay sucesores, continuar con el siguiente nodo
            if len(successors) == 0:
                continue

            # Procesar cada sucesor
            for sucesor in successors:
                # Si ya está en cerrados, ignorar
                is_in_closed = False
                for closed_node in self.precessed:
                    if sucesor == closed_node:
                        is_in_closed = True
                        break
                if is_in_closed:
                    continue

                # Calcular nuevo G(n)
                new_g = current.G() + self.problem.GetGCost(sucesor)

                # Buscar si ya está en abiertos
                node_in_open = self.GetSucesorInOpen(sucesor)

                # Si no está en abiertos, añadirlo
                if node_in_open is None:
                    self._ConfigureNode(sucesor, current, new_g)
                    self.open.append(sucesor)
                # Si está en abiertos pero el nuevo camino es mejor
                elif new_g < node_in_open.G():
                    self._ConfigureNode(node_in_open, current, new_g)

        # Si no se encontró solución, devolver camino vacío
        return []

    #nos permite configurar un nodo (node) con el padre y la nueva G
    def _ConfigureNode(self, node, parent, newG):
        node.SetParent(parent)
        node.SetG(newG)
        node.SetH(self.problem.Heuristic(node))

    #nos dice si un sucesor está en abierta. Si esta es que ya ha sido expandido y tendrá un coste, comprobar que le nuevo camino no es más eficiente
    #En caso de serlos, _ConfigureNode para setearle el nuevo padre y el nuevo G, asi como su heurística
    def GetSucesorInOpen(self,sucesor):
        i = 0
        found = None
        while found == None and i < len(self.open):
            node = self.open[i]
            i += 1
            if node == sucesor:
                found = node
        return found


    #reconstruye el path desde la meta encontrada.
    def ReconstructPath(self, goal):
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = current.GetParent()
        return path


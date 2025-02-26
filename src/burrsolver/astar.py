"""Implementation of the A* pathfinding algorithm."""

from collections import namedtuple
from heapq import heappop, heappush


def reconstruct_path(came_from, current):
    """Reconstructs the path from the start to the goal."""
    total_path = [(current, None)]
    while current in came_from:
        if came_from[current] is None:
            break

        current, edge = came_from[current]
        total_path.append((current, edge))

    return total_path[::-1]


Step = namedtuple("Step", ["state", "edge"])


def astar(distance, heuristic, neighbors, is_goal, start):
    """A* pathfinding algorithm.

    Description:
        Note that this version is slightly different from what you have
        seen before in that it stores the edge on the graph that was taken
        to reach a state in addition to the state itself. For more complex
        problem spaces, this saves us the work of reconstructing what can
        sometimes be a complicated state transition, as it the case
        here.

    Args:
        distance: Function to calculate the distance between two states.
        heuristic: Function to estimate the cost from a state to the goal.
        neighbors: Function to get the neighboring states of a given state.
        is_goal: Function to check if a state is the goal.
        start: The starting state.
    """
    frontier = []
    heappush(frontier, (0, 0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, _, x = heappop(frontier)

        if is_goal(x):
            return reconstruct_path(came_from, x)

        for e, y in neighbors(x):
            new_cost = cost_so_far[x] + distance(x, y)
            if new_cost < cost_so_far.get(y, float("inf")):
                cost_so_far[y] = new_cost
                h = heuristic(y)
                priority = new_cost + h
                heappush(frontier, (priority, h, y))
                came_from[y] = Step(x, e)

    return None

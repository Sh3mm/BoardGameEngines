import numpy as np


def bfs(board: np.ndarray, ini_pos: int, goal: range, pid: int):
    fifo = [(ini_pos, [ini_pos])]
    visited = {-1}
    while len(fifo) > 0:
        pos, path = fifo.pop(0)

        if pos in goal:
            return path

        to_visit = set(board[:, pos]) - visited
        for p in to_visit:
            fifo.append((p, path + [p]))
            visited.add(p)


def dfs(board: np.ndarray, ini_pos: int, goal: range, pid: int):
    lifo = [(ini_pos, [ini_pos])]
    visited = {-1}
    while len(lifo) > 0:
        pos, path = lifo.pop()

        if pos in goal:
            return path

        to_visit = sorted(set(board[:, pos]) - visited, reverse=(pid == 1))
        for p in to_visit:
            lifo.append((p, path + [p]))
            visited.add(p)

def best_fs(board: np.ndarray, ini_pos: int, goal: range, pid: int):
    cache = [[] for _ in range(9)]
    cache[dist(ini_pos, pid)].append((ini_pos, [ini_pos]))
    csize = 1

    visited = {-1}
    while csize > 0:
        pos, path = None, None
        for i in range(9):
            if len(cache[i]) > 0:
                pos, path = cache[i].pop()
                csize -= 1
                break

        if pos in goal:
            return path

        to_visit = set(board[:, pos]) - visited
        csize += len(to_visit)
        for p in to_visit:
            cache[dist(p, pid)].append((p, path + [p]))
            visited.add(p)


def dist(pos: int, pid: int) -> int:
    if pid == 1:
        return pos // 9
    return 8 - (pos // 9)
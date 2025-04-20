import heapq
import collections

class Ghost:
    def __init__(self, id, start_pos, algorithm, cell_size):
        self.id = id
        self.start_pos = start_pos
        self.position = start_pos
        self.pixel_position = (
            start_pos[0] * cell_size + cell_size // 2,
            start_pos[1] * cell_size + cell_size // 2
        )
        self.algorithm = algorithm
        self.path = []
        self.speed = 0.05
        self.move_progress = 0.0
        self.cell_size = cell_size

    def find_path(self, maze, target_pos):
        if self.algorithm == 'BFS':
            self.path = self.bfs(maze, target_pos)
        elif self.algorithm == 'DFS':
            self.path = self.dfs(maze, target_pos)
        elif self.algorithm == 'UCS':
            self.path = self.ucs(maze, target_pos)
        elif self.algorithm == 'A*':
            self.path = self.a_star(maze, target_pos)

    def bfs(self, maze, target_pos):
        queue = collections.deque([(self.position, [self.position])])
        visited = set([self.position])

        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == target_pos:
                return path[1:] if len(path) > 1 else []

            for nx, ny in maze.get_valid_moves(x, y):
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
        return []

    def dfs(self, maze, target_pos):
        stack = [(self.position, [self.position])]
        visited = set([self.position])

        while stack:
            (x, y), path = stack.pop()
            if (x, y) == target_pos:
                return path[1:] if len(path) > 1 else []

            for nx, ny in maze.get_valid_moves(x, y):
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    stack.append(((nx, ny), path + [(nx, ny)]))
        return []

    def ucs(self, maze, target_pos):
        pq = [(0, self.position, [self.position])]
        visited = set()

        while pq:
            cost, (x, y), path = heapq.heappop(pq)
            if (x, y) == target_pos:
                return path[1:] if len(path) > 1 else []

            if (x, y) not in visited:
                visited.add((x, y))
                for nx, ny in maze.get_valid_moves(x, y):
                    new_cost = cost + 1
                    heapq.heappush(pq, (new_cost, (nx, ny), path + [(nx, ny)]))
        return []

    def a_star(self, maze, target_pos):
        def manhattan_distance(p1, p2):
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        pq = [(0, 0, self.position, [self.position])]
        visited = set()

        while pq:
            f, g, (x, y), path = heapq.heappop(pq)
            if (x, y) == target_pos:
                return path[1:] if len(path) > 1 else []

            if (x, y) not in visited:
                visited.add((x, y))
                for nx, ny in maze.get_valid_moves(x, y):
                    new_g = g + 1
                    new_h = manhattan_distance((nx, ny), target_pos)
                    new_f = new_g + new_h
                    heapq.heappush(pq, (new_f, new_g, (nx, ny), path + [(nx, ny)]))
        return []

    def move(self, maze):
        if not self.path:
            return

        self.move_progress += self.speed
        if self.move_progress < 1.0:
            next_pos = self.path[0]
            dx = next_pos[0] - self.position[0]
            dy = next_pos[1] - self.position[1]
            self.pixel_position = (
                self.position[0] * self.cell_size + self.cell_size // 2 + dx * self.move_progress * self.cell_size,
                self.position[1] * self.cell_size + self.cell_size // 2 + dy * self.move_progress * self.cell_size
            )
            return

        self.move_progress = 0.0
        self.position = self.path.pop(0)
        self.pixel_position = (
            self.position[0] * self.cell_size + self.cell_size // 2,
            self.position[1] * self.cell_size + self.cell_size // 2
        )

    def reset(self):
        self.position = self.start_pos
        self.pixel_position = (
            self.start_pos[0] * self.cell_size + self.cell_size // 2,
            self.start_pos[1] * self.cell_size + self.cell_size // 2
        )
        self.path = []
        self.move_progress = 0.0
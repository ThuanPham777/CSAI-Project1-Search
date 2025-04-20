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
        self.previous_position = None
        self.last_target = None

    def find_path(self, maze, target_pos):
        # Check if we can reuse the existing path
        if (self.path and 
            self.last_target == target_pos and 
            any((self.position[0] + dx, self.position[1] + dy) in self.path 
                for dx, dy in [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0)])):
            print(f"Ghost {self.id} reusing existing path to {target_pos}, current pos: {self.position}")
            return

        print(f"Computing new path for Ghost {self.id} from {self.position} to {target_pos}")
        self.last_target = target_pos
        if self.algorithm == 'BFS':
            self.path = self.bfs(maze, target_pos)
        elif self.algorithm == 'DFS':
            self.path = self.dfs(maze, target_pos)
        elif self.algorithm == 'UCS':
            self.path = self.ucs(maze, target_pos)
        elif self.algorithm == 'A*':
            self.path = self.a_star(maze, target_pos)
        print(f"Path computed: {self.path}")

    def bfs(self, maze, target_pos):
        queue = collections.deque([(self.position, [self.position])])
        visited = set([self.position])

        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == target_pos:
                return path[1:] if len(path) > 1 else []

            valid_moves = maze.get_valid_moves(x, y)
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in valid_moves and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
        print(f"BFS failed to find path for Ghost {self.id} to {target_pos}")
        return []

    def dfs(self, maze, target_pos):
        stack = [(self.position, [self.position])]
        visited = set([self.position])
        max_path_length = 30  # Increased to allow previous 24-step path

        while stack:
            current, path = stack.pop()
            if current == target_pos:
                print(f"DFS found path for Ghost {self.id}: {path[1:]}")
                return path[1:] if len(path) > 1 else []

            if len(path) >= max_path_length:
                continue

            valid_moves = maze.get_valid_moves(current[0], current[1])
            print(f"DFS at {current}, valid moves: {valid_moves}, path length: {len(path)}")
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor in valid_moves and neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, path + [neighbor]))

        print(f"DFS failed to find path for Ghost {self.id} to {target_pos}")
        return []

    def ucs(self, maze, target_pos):
        pq = [(0, self.position, [self.position])]
        visited = set()

        while pq:
            cost, (x, y), path = heapq.heappop(pq)
            if (x, y) == target_pos:
                return path[1:] if len(path) > 1 else []
                
            if (x, y) in visited:
                continue
                
            visited.add((x, y))
            
            valid_moves = maze.get_valid_moves(x, y)
            for nx, ny in valid_moves:
                if (nx, ny) not in visited:
                    new_cost = cost + 1
                    heapq.heappush(pq, (new_cost, (nx, ny), path + [(nx, ny)]))
        print(f"UCS failed to find path for Ghost {self.id} to {target_pos}")
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
                
            if (x, y) in visited:
                continue
                
            visited.add((x, y))
            
            valid_moves = maze.get_valid_moves(x, y)
            for nx, ny in valid_moves:
                if (nx, ny) not in visited:
                    new_g = g + 1
                    new_h = manhattan_distance((nx, ny), target_pos)
                    new_f = new_g + new_h
                    heapq.heappush(pq, (new_f, new_g, (nx, ny), path + [(nx, ny)]))
        print(f"A* failed to find path for Ghost {self.id} to {target_pos}")
        return []

    def move(self, maze):
        if not self.path:
            print(f"Ghost {self.id} has no path to follow at {self.position}")
            return

        self.move_progress += self.speed
        print(f"Ghost {self.id} move progress: {self.move_progress}, next pos: {self.path[0]}")
        if self.move_progress < 1.0:
            next_pos = self.path[0]
            dx = next_pos[0] - self.position[0]
            dy = next_pos[1] - self.position[1]
            self.pixel_position = (
                self.position[0] * self.cell_size + self.cell_size // 2 + dx * self.move_progress * self.cell_size,
                self.position[1] * self.cell_size + self.cell_size // 2 + dy * self.move_progress * self.cell_size
            )
            return

        self.previous_position = self.position
        self.move_progress = 0.0
        self.position = self.path.pop(0)
        self.pixel_position = (
            self.position[0] * self.cell_size + self.cell_size // 2,
            self.position[1] * self.cell_size + self.cell_size // 2
        )
        print(f"Ghost {self.id} moved to {self.position}, remaining path: {self.path}")

    def reset(self):
        self.position = self.start_pos
        self.pixel_position = (
            self.start_pos[0] * self.cell_size + self.cell_size // 2,
            self.start_pos[1] * self.cell_size + self.cell_size // 2
        )
        self.path = []
        self.move_progress = 0.0
        self.previous_position = None
        self.last_target = None
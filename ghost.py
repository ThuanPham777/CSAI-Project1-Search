import heapq
import collections
import tracemalloc
import time

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
        self.speed = 0.05  # Tăng tốc độ để di chuyển nhanh hơn
        self.move_progress = 0.0
        self.cell_size = cell_size
        self.previous_position = None
        self.last_target = None
        self.metrics_history = []  # Lưu trữ lịch sử metric

    def find_path(self, maze, target_pos):
        print(f"Computing path for Ghost {self.id} from {self.position} to {target_pos}")

        # Khởi tạo metrics cho mọi trường hợp
        tracemalloc.start()
        start_time = time.time()
        
        # Kiểm tra tính hợp lệ của target_pos
        valid_moves = maze.get_valid_moves(target_pos[0], target_pos[1])
        if not valid_moves and (target_pos[0], target_pos[1]) != self.position:
            print(f"Invalid target position {target_pos} for Ghost {self.id} (no valid moves)")
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            end_time = time.time()
            return {
                "path": [],
                "time": end_time - start_time,
                "memory": peak / 1024,
                "nodes": 0
            }

        # Tái sử dụng đường đi nếu có thể
        if (self.path and self.last_target == target_pos and
                any((self.position[0] + dx, self.position[1] + dy) in self.path
                    for dx, dy in [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0)])):
            print(f"Ghost {self.id} reusing existing path to {target_pos}")
            
            # Đo thời gian và bộ nhớ cho quá trình kiểm tra và tái sử dụng
            current, peak = tracemalloc.get_traced_memory()
            end_time = time.time()
            tracemalloc.stop()
            
            metrics = {
                "path": self.path,
                "time": end_time - start_time,
                "memory": peak / 1024,
                "nodes": 1,  # Tính 1 nút cho quá trình kiểm tra
                "reused": True
            }
            
            # Lưu metric vào lịch sử cho trường hợp tái sử dụng
            self.metrics_history.append({
                "ghost_id": self.id,
                "algorithm": self.algorithm,
                "time": metrics["time"],
                "memory": metrics["memory"],
                "nodes": metrics["nodes"],
                "path_length": len(self.path),
                "timestamp": time.time(),
                "reused": True
            })
            
            print(f"Reuse path metrics - Time: {metrics['time']:.6f}s, Memory: {metrics['memory']:.2f}KB, Nodes: {metrics['nodes']}")
            return metrics

        self.last_target = target_pos
        
        # Tiếp tục với thuật toán tìm đường như bình thường
        peak_memory = 0
        result = None

        try:
            if self.algorithm == 'BFS':
                result = self.bfs(maze, target_pos)
            elif self.algorithm == 'DFS':
                result = self.dfs(maze, target_pos)
            elif self.algorithm == 'UCS':
                result = self.ucs(maze, target_pos)
            elif self.algorithm == 'A*':
                result = self.a_star(maze, target_pos)
            else:
                raise ValueError(f"Unknown algorithm: {self.algorithm}")
        except Exception as e:
            print(f"Error in pathfinding for Ghost {self.id}: {e}")
        finally:
            # Ghi lại bộ nhớ
            current, peak = tracemalloc.get_traced_memory()
            peak_memory = peak / 1024  # Chuyển đổi sang KB
            tracemalloc.stop()

        # Ghi lại thời gian
        end_time = time.time()
        
        self.path = result["path"] if result else []
        metrics = {
            "path": self.path,
            "time": end_time - start_time,
            "memory": peak_memory,
            "nodes": result["nodes"] if result else 0
        }
        
        # Lưu metric vào lịch sử
        self.metrics_history.append({
            "ghost_id": self.id,
            "algorithm": self.algorithm,
            "time": metrics["time"],
            "memory": metrics["memory"],
            "nodes": metrics["nodes"],
            "path_length": len(self.path),
            "timestamp": time.time()
        })
        
        print(f"Path computed: {self.path}")
        print(f"Metrics for {self.algorithm} - Time: {metrics['time']:.6f}s, Memory: {metrics['memory']:.2f}KB, Nodes: {metrics['nodes']}")
        return metrics

    def bfs(self, maze, target_pos):
        queue = collections.deque([(self.position, [self.position])])
        visited = set([self.position])
        expanded_nodes = 0

        while queue:
            (x, y), path = queue.popleft()
            expanded_nodes += 1
            if (x, y) == target_pos:
                return {"path": path[1:] if len(path) > 1 else [], "nodes": expanded_nodes}

            valid_moves = maze.get_valid_moves(x, y)
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in valid_moves and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
        print(f"BFS failed to find path for Ghost {self.id} to {target_pos}")
        return {"path": [], "nodes": expanded_nodes}

    def dfs(self, maze, target_pos):
        stack = [(self.position, [self.position])]
        visited = set([self.position])
        max_path_length = 30
        expanded_nodes = 0

        while stack:
            current, path = stack.pop()
            expanded_nodes += 1
            if current == target_pos:
                print(f"DFS found path for Ghost {self.id}: {path[1:]}")
                return {"path": path[1:] if len(path) > 1 else [], "nodes": expanded_nodes}

            if len(path) >= max_path_length:
                continue

            valid_moves = maze.get_valid_moves(current[0], current[1])
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor in valid_moves and neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, path + [neighbor]))
        print(f"DFS failed to find path for Ghost {self.id} to {target_pos}")
        return {"path": [], "nodes": expanded_nodes}

    def ucs(self, maze, target_pos):
        pq = [(0, self.position, [self.position])]
        visited = set()
        expanded_nodes = 0

        while pq:
            cost, (x, y), path = heapq.heappop(pq)
            expanded_nodes += 1
            if (x, y) == target_pos:
                return {"path": path[1:] if len(path) > 1 else [], "nodes": expanded_nodes}
                
            if (x, y) in visited:
                continue
                
            visited.add((x, y))
            
            valid_moves = maze.get_valid_moves(x, y)
            for nx, ny in valid_moves:
                if (nx, ny) not in visited:  # Đã sửa: "not in" thay vì "in"
                    new_cost = cost + 1
                    heapq.heappush(pq, (new_cost, (nx, ny), path + [(nx, ny)]))
        print(f"UCS failed to find path for Ghost {self.id} to {target_pos}")
        return {"path": [], "nodes": expanded_nodes}

    def a_star(self, maze, target_pos):
        def manhattan_distance(p1, p2):
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        pq = [(0, 0, self.position, [self.position])]
        visited = set()
        expanded_nodes = 0

        while pq:
            f, g, (x, y), path = heapq.heappop(pq)
            expanded_nodes += 1
            if (x, y) == target_pos:
                return {"path": path[1:] if len(path) > 1 else [], "nodes": expanded_nodes}
                
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
        return {"path": [], "nodes": expanded_nodes}

    def move(self, maze, target_pos):
        print(f"Ghost {self.id} moving towards {target_pos}, current position: {self.position}")
        
        # Chỉ gọi find_path nếu cần
        if not self.path or self.last_target != target_pos:
            metrics = self.find_path(maze, target_pos)
        else:
            # Đường đi vẫn còn hiệu lực, không cần tìm lại
            # Sử dụng metrics từ lần cuối cùng
            if self.metrics_history:
                metrics = {
                    "path": self.path,
                    "time": self.metrics_history[-1]["time"],
                    "memory": self.metrics_history[-1]["memory"],
                    "nodes": self.metrics_history[-1]["nodes"],
                    "reused": True
                }
            else:
                metrics = {"path": self.path, "time": 0, "memory": 0, "nodes": 0, "reused": True}
            print(f"Ghost {self.id} using existing path: {self.path}")

        if not self.path:
            print(f"No path available for Ghost {self.id}")
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
        else:
            self.previous_position = self.position
            self.move_progress = 0.0
            self.position = self.path.pop(0)
            self.pixel_position = (
                self.position[0] * self.cell_size + self.cell_size // 2,
                self.position[1] * self.cell_size + self.cell_size // 2
            )
            print(f"Ghost {self.id} moved to new position: {self.position}")
        
        # In metric sau mỗi bước di chuyển
        print(f"Metrics after move - Time: {metrics['time']:.6f}s, Memory: {metrics['memory']:.2f}KB, Nodes: {metrics['nodes']}")
        if metrics.get("reused"):
            print(f"Path reused")
            if len(self.metrics_history) > 0:
                print(f"Latest metrics history: {self.metrics_history[-1]}")
        else:
            print(f"Latest metrics history: {self.metrics_history[-1]}")

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
        self.metrics_history = []
        print(f"Ghost {self.id} reset to start position: {self.start_pos}")
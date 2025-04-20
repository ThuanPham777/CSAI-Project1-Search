class PacMan:
    def __init__(self, start_pos, cell_size):
        """
        Initialize Pac-Man with starting position, score, lives, and direction.

        Args:
            start_pos (tuple): Initial (x, y) position on the maze grid.
            cell_size (int): Size of each cell in pixels.
        """
        self.position = start_pos  # Current (x, y) position
        self.pixel_position = (
            start_pos[0] * cell_size + cell_size // 2,
            start_pos[1] * cell_size + cell_size // 2
        )
        self.score = 0             # Player score
        self.lives = 3             # Remaining lives
        self.direction = (0, 0)    # Current movement direction (dx, dy)
        self.speed = 0.1           # Speed for smooth movement
        self.move_progress = 0.0   # Progress towards the next cell (0 to 1)
        self.cell_size = cell_size
        self.requested_direction = (0, 0)  # Hướng người chơi yêu cầu

    def move(self, maze, new_direction):
        """
        Move Pac-Man to a new position if the target cell is valid (not a wall or gate).

        Args:
            maze (Maze): The maze object from maze.py.
            new_direction (tuple): Direction vector (e.g., (1, 0) = right).
        """
        # Lưu hướng người chơi yêu cầu
        if new_direction != (0, 0):  # Chỉ cập nhật nếu có hướng mới
            self.requested_direction = new_direction

        # Kiểm tra hướng yêu cầu có hợp lệ không
        x, y = self.position
        dx, dy = self.requested_direction
        new_x, new_y = x + dx, y + dy

        # Nếu hướng yêu cầu không dẫn vào tường hoặc cửa, cập nhật hướng di chuyển
        if (0 <= new_x < maze.width and 0 <= new_y < maze.height and
                not maze.is_blocked_for_pacman(new_x, new_y)):
            self.direction = self.requested_direction
        else:
            # Nếu hướng yêu cầu không hợp lệ, thử tiếp tục hướng hiện tại
            dx, dy = self.direction
            new_x, new_y = x + dx, y + dy
            if not (0 <= new_x < maze.width and 0 <= new_y < maze.height and
                    not maze.is_blocked_for_pacman(new_x, new_y)):
                # Nếu hướng hiện tại cũng không hợp lệ (đang đối diện tường/cửa), dừng lại
                self.direction = (0, 0)

        # Cập nhật chuyển động
        self.move_progress += self.speed
        if self.move_progress < 1.0:
            # Nội suy pixel_position cho chuyển động mượt mà
            dx, dy = self.direction
            self.pixel_position = (
                self.position[0] * self.cell_size + self.cell_size // 2 + dx * self.move_progress * self.cell_size,
                self.position[1] * self.cell_size + self.cell_size // 2 + dy * self.move_progress * self.cell_size
            )
            return

        # Khi move_progress >= 1.0, di chuyển sang ô tiếp theo
        self.move_progress = 0.0
        dx, dy = self.direction
        new_x, new_y = x + dx, y + dy

        # Chỉ di chuyển nếu vị trí mới hợp lệ
        if (0 <= new_x < maze.width and 0 <= new_y < maze.height and
                not maze.is_blocked_for_pacman(new_x, new_y)):
            self.position = (new_x, new_y)
            self.pixel_position = (
                new_x * self.cell_size + self.cell_size // 2,
                new_y * self.cell_size + self.cell_size // 2
            )
            self._eat_dot(maze)  # Handle dot consumption

    def _eat_dot(self, maze):
        """Update score when Pac-Man eats a dot or power pellet."""
        x, y = self.position
        if maze.is_dot(x, y):
            self.score += 10
            maze.board[y][x] = 0  # Remove dot from the maze
        elif maze.is_power_pellet(x, y):
            self.score += 50
            maze.board[y][x] = 0  # Remove power pellet
            # TODO: Trigger ghost "frightened" mode (add logic in ghost.py)

    def reset(self, start_pos):
        """Reset Pac-Man's position and direction after losing a life."""
        self.position = start_pos
        self.pixel_position = (
            start_pos[0] * self.cell_size + self.cell_size // 2,
            start_pos[1] * self.cell_size + self.cell_size // 2
        )
        self.direction = (0, 0)
        self.requested_direction = (0, 0)
        self.move_progress = 0.0
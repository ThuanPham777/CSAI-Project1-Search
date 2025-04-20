import pygame
import sys
from maze import Maze
from ghost import Ghost
from pacman import PacMan

# Initialize Pygame
pygame.init()
CELL_SIZE = 20
SCREEN_WIDTH = 30 * CELL_SIZE  # 30 cells wide
SCREEN_HEIGHT = 33 * CELL_SIZE  # 33 cells tall to match maze height
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man AI Project")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
PINK = (255, 192, 203)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Game:
    def __init__(self):
        self.maze = Maze()
        self.pacman = PacMan(self.maze.pacman_pos, CELL_SIZE)
        self.ghosts = []  # Sẽ được khởi tạo dựa trên cấp độ
        self.running = True
        self.game_over = False
        self.game_won = False
        self.player_moved = False
        self.level_selection = True  # Trạng thái chọn cấp độ
        self.quit_confirmation = False  # Trạng thái xác nhận thoát
        self.current_level = 0  # Cấp độ hiện tại (1-6)
        self.font = pygame.font.SysFont('Arial', 24)
        self.level_font = pygame.font.SysFont('Arial', 30)

    def initialize_level(self):
        """Khởi tạo cấp độ dựa trên current_level."""
        self.maze = Maze()
        self.pacman = PacMan(self.maze.pacman_pos, CELL_SIZE)
        self.ghosts = []
        self.player_moved = False
        self.game_over = False
        self.game_won = False
        self.quit_confirmation = False  # Đặt lại trạng thái xác nhận thoát

        if self.current_level == 1:
            self.ghosts = [Ghost('B', self.maze.ghosts['B'], 'BFS', CELL_SIZE)]
        elif self.current_level == 2:
            self.ghosts = [Ghost('P', self.maze.ghosts['P'], 'DFS', CELL_SIZE)]
        elif self.current_level == 3:
            self.ghosts = [Ghost('O', self.maze.ghosts['O'], 'UCS', CELL_SIZE)]
        elif self.current_level == 4:
            self.ghosts = [Ghost('R', self.maze.ghosts['R'], 'A*', CELL_SIZE)]
        elif self.current_level in [5, 6]:
            self.ghosts = [
                Ghost('B', self.maze.ghosts['B'], 'BFS', CELL_SIZE),
                Ghost('P', self.maze.ghosts['P'], 'DFS', CELL_SIZE),
                Ghost('O', self.maze.ghosts['O'], 'UCS', CELL_SIZE),
                Ghost('R', self.maze.ghosts['R'], 'A*', CELL_SIZE)
            ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                print(f"Key pressed: {event.key}")  # Log để gỡ lỗi
                if self.level_selection:
                    # Hỗ trợ cả phím số chính và numpad
                    if event.key in (pygame.K_1, pygame.K_KP1):
                        self.current_level = 1
                        self.level_selection = False
                        self.initialize_level()
                        print("Selected Level 1")
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        self.current_level = 2
                        self.level_selection = False
                        self.initialize_level()
                        print("Selected Level 2")
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        self.current_level = 3
                        self.level_selection = False
                        self.initialize_level()
                        print("Selected Level 3")
                    elif event.key in (pygame.K_4, pygame.K_KP4):
                        self.current_level = 4
                        self.level_selection = False
                        self.initialize_level()
                        print("Selected Level 4")
                    elif event.key in (pygame.K_5, pygame.K_KP5):
                        self.current_level = 5
                        self.level_selection = False
                        self.initialize_level()
                        print("Selected Level 5")
                    elif event.key in (pygame.K_6, pygame.K_KP6):
                        self.current_level = 6
                        self.level_selection = False
                        self.initialize_level()
                        print("Selected Level 6")

                elif self.quit_confirmation:
                    # Xử lý xác nhận thoát
                    if event.key == pygame.K_y:
                        self.running = False  # Thoát trò chơi
                    elif event.key == pygame.K_n:
                        self.quit_confirmation = False  # Tiếp tục chơi

                elif self.game_over or self.game_won:
                    if event.key == pygame.K_r:
                        self.level_selection = True  # Quay lại màn hình chọn cấp độ
                        self.current_level = 0
                    elif event.key == pygame.K_q:
                        self.running = False

                else:
                    # Khi đang chơi, nhấn Q để hiển thị màn hình xác nhận thoát
                    if event.key == pygame.K_q:
                        self.quit_confirmation = True

        # Điều khiển Pac-Man (chỉ ở Level 6, và không trong trạng thái xác nhận thoát)
        if not self.level_selection and not self.game_over and not self.game_won and not self.quit_confirmation:
            if self.current_level == 6:  # Chỉ Level 6 cho phép điều khiển Pac-Man
                keys = pygame.key.get_pressed()
                new_direction = (0, 0)
                if keys[pygame.K_RIGHT]:
                    new_direction = (1, 0)
                elif keys[pygame.K_LEFT]:
                    new_direction = (-1, 0)
                elif keys[pygame.K_UP]:
                    new_direction = (0, -1)
                elif keys[pygame.K_DOWN]:
                    new_direction = (0, 1)
                if new_direction != (0, 0):
                    self.player_moved = True
                self.pacman.move(self.maze, new_direction)

    def update(self):
        if self.level_selection or self.game_over or self.game_won or self.quit_confirmation:
            return

        # Update ghosts only if player has moved (hoặc ở level 1-5 thì ghost di chuyển ngay)
        if self.current_level in [1, 2, 3, 4, 5] or self.player_moved:
            for ghost in self.ghosts:
                ghost.find_path(self.maze, self.pacman.position)
                ghost.move(self.maze)

        # Check collisions with ghosts
        for ghost in self.ghosts:
            if ghost.position == self.pacman.position:
                self.pacman.lives -= 1
                if self.pacman.lives <= 0:
                    self.game_over = True
                else:
                    # Reset Pac-Man and ghosts
                    self.pacman.reset(self.maze.pacman_pos)
                    for ghost in self.ghosts:
                        ghost.reset()
                    self.player_moved = False
                break

        # Check win condition (no dots or power pellets left) - Chỉ áp dụng cho Level 6
        if self.current_level == 6:
            dots_remaining = any(
                cell in [1, 2]
                for row in self.maze.board
                for cell in row
            )
            if not dots_remaining:
                self.game_won = True

    def draw(self):
        screen.fill(BLACK)

        if self.level_selection:
            # Hiển thị màn hình chọn cấp độ
            title_text = self.level_font.render("Select Level", True, WHITE)
            screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 50))

            level_texts = [
                self.font.render("1 - Blue Ghost (BFS)", True, WHITE),
                self.font.render("2 - Pink Ghost (DFS)", True, WHITE),
                self.font.render("3 - Orange Ghost (UCS)", True, WHITE),
                self.font.render("4 - Red Ghost (A*)", True, WHITE),
                self.font.render("5 - All Ghosts (Parallel)", True, WHITE),
                self.font.render("6 - User-Controlled Pac-Man", True, WHITE)
            ]
            for i, text in enumerate(level_texts):
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 150 + i*50))
            pygame.display.flip()
            return

        # Draw maze
        for y in range(len(self.maze.board)):
            for x in range(len(self.maze.board[0])):
                rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cell = self.maze.board[y][x]

                if cell == 1:  # Dot
                    pygame.draw.circle(screen, WHITE, rect.center, 3)
                elif cell == 2:  # Big dot
                    pygame.draw.circle(screen, WHITE, rect.center, 6)
                elif cell in [3,4,5,6,7,8]:  # Walls
                    pygame.draw.rect(screen, BLUE, rect)
                elif cell == 9:  # Gate
                    pygame.draw.rect(screen, WHITE, rect)

        # Draw Pac-Man
        pygame.draw.circle(screen, YELLOW,
                           (int(self.pacman.pixel_position[0]),
                            int(self.pacman.pixel_position[1])),
                           CELL_SIZE//2)

        # Draw Ghosts
        ghost_colors = {'B': BLUE, 'P': PINK, 'O': ORANGE, 'R': RED}
        for ghost in self.ghosts:
            pygame.draw.circle(screen, ghost_colors[ghost.id],
                               (int(ghost.pixel_position[0]),
                                int(ghost.pixel_position[1])),
                               CELL_SIZE//2)

        # Draw UI
        score_text = self.font.render(f"Score: {self.pacman.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.pacman.lives}", True, WHITE)
        level_text = self.font.render(f"Level: {self.current_level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (SCREEN_WIDTH-150, 10))
        screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, 10))

        # Draw Quit Confirmation screen
        if self.quit_confirmation:
            quit_text = self.font.render("Are you sure you want to quit?", True, WHITE)
            confirm_text = self.font.render("Press Y to Quit, N to Resume", True, WHITE)
            screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
            screen.blit(confirm_text, (SCREEN_WIDTH//2 - confirm_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
            pygame.display.flip()
            return

        # Draw Game Over screen
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press R to Select Level, Q to Quit", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH//2-80, SCREEN_HEIGHT//2))
            screen.blit(restart_text, (SCREEN_WIDTH//2-140, SCREEN_HEIGHT//2+30))

        # Draw Win screen (chỉ ở Level 6)
        if self.game_won:
            win_text = self.font.render("YOU WIN!", True, GREEN)
            restart_text = self.font.render("Press R to Select Level, Q to Quit", True, WHITE)
            screen.blit(win_text, (SCREEN_WIDTH//2-60, SCREEN_HEIGHT//2))
            screen.blit(restart_text, (SCREEN_WIDTH//2-140, SCREEN_HEIGHT//2+30))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)  # 60 FPS
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
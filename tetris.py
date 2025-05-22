import pygame
import random

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
COLUMNS = SCREEN_WIDTH // BLOCK_SIZE
ROWS = SCREEN_HEIGHT // BLOCK_SIZE

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # I
    (0, 0, 255),    # J
    (255, 127, 0),  # L
    (255, 255, 0),  # O
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 0, 0),    # Z
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],                      # I
    [[1, 0, 0], [1, 1, 1]],              # J
    [[0, 0, 1], [1, 1, 1]],              # L
    [[1, 1], [1, 1]],                    # O
    [[0, 1, 1], [1, 1, 0]],              # S
    [[0, 1, 0], [1, 1, 1]],              # T
    [[1, 1, 0], [0, 1, 1]],              # Z
]

class Tetromino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = COLUMNS // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def get_cells(self):
        cells = []
        for dy, row in enumerate(self.shape):
            for dx, cell in enumerate(row):
                if cell:
                    cells.append((self.x + dx, self.y + dy))
        return cells

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLUMNS):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def check_collision(shape, offset_x, offset_y, grid):
    for dy, row in enumerate(shape):
        for dx, cell in enumerate(row):
            if cell:
                x = offset_x + dx
                y = offset_y + dy
                if x < 0 or x >= COLUMNS or y >= ROWS or (y >= 0 and grid[y][x] != BLACK):
                    return True
    return False

def clear_rows(grid, locked_positions):
    cleared = 0
    for y in range(ROWS-1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            # Remove the row
            for x in range(COLUMNS):
                del locked_positions[(x, y)]
            # Move every row above down
            for key in sorted(list(locked_positions), key=lambda k: k[1])[::-1]:
                x, y2 = key
                if y2 < y:
                    locked_positions[(x, y2 + 1)] = locked_positions.pop((x, y2))
    return cleared

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLUMNS):
            pygame.draw.rect(
                surface,
                grid[y][x],
                (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            )
    # Draw grid lines
    for x in range(COLUMNS + 1):
        pygame.draw.line(surface, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))
    for y in range(ROWS + 1):
        pygame.draw.line(surface, GRAY, (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont('Arial', size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (x, y))

def get_new_tetromino():
    idx = random.randint(0, len(SHAPES) - 1)
    return Tetromino(SHAPES[idx], COLORS[idx])

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5

    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = get_new_tetromino()
    next_piece = get_new_tetromino()

    running = True
    score = 0

    while running:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 > fall_speed:
            current_piece.y += 1
            if check_collision(current_piece.shape, current_piece.x, current_piece.y, grid):
                current_piece.y -= 1
                for x, y in current_piece.get_cells():
                    locked_positions[(x, y)] = current_piece.color
                current_piece = next_piece
                next_piece = get_new_tetromino()
                if check_collision(current_piece.shape, current_piece.x, current_piece.y, grid):
                    running = False  # Game over
            fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not check_collision(current_piece.shape, current_piece.x - 1, current_piece.y, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if not check_collision(current_piece.shape, current_piece.x + 1, current_piece.y, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_DOWN:
                    if not check_collision(current_piece.shape, current_piece.x, current_piece.y + 1, grid):
                        current_piece.y += 1
                elif event.key == pygame.K_UP:
                    original_shape = [row[:] for row in current_piece.shape]
                    current_piece.rotate()
                    if check_collision(current_piece.shape, current_piece.x, current_piece.y, grid):
                        current_piece.shape = original_shape

        # Draw current piece on grid
        for x, y in current_piece.get_cells():
            if y >= 0:
                grid[y][x] = current_piece.color

        # Clear rows and update score
        cleared = clear_rows(grid, locked_positions)
        score += cleared * 100

        screen.fill(BLACK)
        draw_grid(screen, grid)
        draw_text(screen, f"Score: {score}", 24, WHITE, 10, 10)
        pygame.display.update()

    screen.fill(BLACK)
    draw_text(screen, "GAME OVER", 48, WHITE, 40, SCREEN_HEIGHT//2 - 50)
    draw_text(screen, f"Score: {score}", 36, WHITE, 70, SCREEN_HEIGHT//2 + 10)
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    main()
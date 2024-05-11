import pygame
import sys
import random
# Constants
WIDTH, HEIGHT = 800,800
COLS, ROWS = 10,10
CELL_WIDTH = WIDTH // COLS
CELL_HEIGHT = HEIGHT // ROWS
FPS = 3

# Define Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
# Initialize Pygame
pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Solver")
clock = pygame.time.Clock()

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.walls = {'N': True, 'S': True, 'E': True, 'W': True}
        self.visited = False
        self.in_path = False
        self.current = False
        self.is_goal = False

    def draw(self, win):
        x = self.col * CELL_WIDTH
        y = self.row * CELL_HEIGHT
        wall_thickness = 4

        if self.current:
            pygame.draw.rect(win, BLUE, (x + 1, y + 1, CELL_WIDTH - 2, CELL_HEIGHT - 2))
        elif self.in_path:
            pygame.draw.rect(win, RED, (x + 1, y + 1, CELL_WIDTH - 2, CELL_HEIGHT - 2))
        elif self.is_goal:
            pygame.draw.rect(win, GREEN, (x + 1, y + 1, CELL_WIDTH - 2, CELL_HEIGHT - 2))
        
        if self.walls['N']:
            pygame.draw.line(win, WHITE, (x, y), (x + CELL_WIDTH, y), wall_thickness)
        if self.walls['S']:
            pygame.draw.line(win, WHITE, (x, y + CELL_HEIGHT), (x + CELL_WIDTH, y + CELL_HEIGHT), wall_thickness)
        if self.walls['E']:
            pygame.draw.line(win, WHITE, (x + CELL_WIDTH, y), (x + CELL_WIDTH, y + CELL_HEIGHT), wall_thickness)
        if self.walls['W']:
            pygame.draw.line(win, WHITE, (x, y), (x, y + CELL_HEIGHT), wall_thickness)



def solve_maze(grid, start_row, start_col):
    path = []
    moves = []
    current = grid[start_row][start_col]
    direction = 'S'  # Start facing downwards
    directions_dict = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1)}
    left_turns = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}
    right_turns = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}
    opposite_direction = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    while (current.row, current.col) != (ROWS - 1, COLS - 1):
        path.append((current.row, current.col))
        current.in_path = True
        current.current = True
        yield current  # Yield the current position to update the game display
        current.current = False

        # Attempt to turn left first
        next_dir = left_turns[direction]
        dx, dy = directions_dict[next_dir]
        if 0 <= current.row + dx < ROWS and 0 <= current.col + dy < COLS and not current.walls[next_dir]:
            direction = next_dir
            moves.append('L')
            current = grid[current.row + dx][current.col + dy]
        # Attempt to move forward if left turn is not available
        elif 0 <= current.row + directions_dict[direction][0] < ROWS and 0 <= current.col + directions_dict[direction][1] < COLS and not current.walls[direction]:
            moves.append('F')
            current = grid[current.row + directions_dict[direction][0]][current.col + directions_dict[direction][1]]
        # Attempt to turn right if forward move is not available
        else:
            next_dir = right_turns[direction]
            dx, dy = directions_dict[next_dir]
            if 0 <= current.row + dx < ROWS and 0 <= current.col + dy < COLS and not current.walls[next_dir]:
                direction = next_dir
                moves.append('R')
                current = grid[current.row + dx][current.col + dy]
            # Perform a U-turn if no other moves are possible
            else:
                direction = opposite_direction[direction]  # Change direction to the opposite
                moves.append('B')  # U-turn
                # Continue moving in the new direction after U-turn
                if 0 <= current.row + directions_dict[direction][0] < ROWS and 0 <= current.col + directions_dict[direction][1] < COLS and not current.walls[direction]:
                    current = grid[current.row + directions_dict[direction][0]][current.col + directions_dict[direction][1]]

    path.append((current.row, current.col))  # Append the goal position
    
    yield path, moves  # Yield the complete path and optimized moves after the goal is reached

def create_maze(rows, cols):
    grid = [[Cell(row, col) for col in range(cols)] for row in range(rows)]
    stack = []
    current = grid[0][0]
    current.visited = True
    total_cells = rows * cols
    visited_cells = 1

    while visited_cells < total_cells:
        neighbors = []
        if current.row > 0 and not grid[current.row - 1][current.col].visited:
            neighbors.append(('N', grid[current.row - 1][current.col]))
        if current.row < rows - 1 and not grid[current.row + 1][current.col].visited:
            neighbors.append(('S', grid[current.row + 1][current.col]))
        if current.col > 0 and not grid[current.row][current.col - 1].visited:
            neighbors.append(('W', grid[current.row][current.col - 1]))
        if current.col < cols - 1 and not grid[current.row][current.col + 1].visited:
            neighbors.append(('E', grid[current.row][current.col + 1]))

        if neighbors:
            direction, next_cell = random.choice(neighbors)
            if direction == 'N':
                current.walls['N'] = False
                next_cell.walls['S'] = False
            elif direction == 'S':
                current.walls['S'] = False
                next_cell.walls['N'] = False
            elif direction == 'W':
                current.walls['W'] = False
                next_cell.walls['E'] = False
            elif direction == 'E':
                current.walls['E'] = False
                next_cell.walls['W'] = False
            stack.append(current)
            current = next_cell
            current.visited = True
            visited_cells += 1
        else:
            current = stack.pop()

    grid[rows - 1][cols - 1].is_goal = True  # Mark the goal cell
    return grid

def simplify_path(commands):
    # Convert list of commands into a single string for easier manipulation
    command_str = ''.join(commands)
    
    # Mapping of patterns to their simplifications
    patterns = {
        'LBR': 'B',
        'LBF': 'R',
        'RBL': 'B',
        'FBL': 'R',
        'FBF': 'B',
        'LBL': 'F'
    }

    # Keep applying the rules until no more changes can be made
    while True:
        old_command_str = command_str
        for pattern, replacement in patterns.items():
            command_str = command_str.replace(pattern, replacement)
        
        # If no changes were made in this iteration, break out of the loop
        if command_str == old_command_str:
            break

    # Convert the string back to a list of moves for consistency with the input format
    return list(command_str)


def solve_maze_optimized(grid, start_row, start_col, moves):
    current = grid[start_row][start_col]
    direction = 'S'  # Start facing downwards
    directions_dict = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1)}
    left_turns = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}
    right_turns = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}

    for move in moves:
        if move == 'L':
            direction = left_turns[direction]
            dx, dy = directions_dict[direction]
            current = grid[current.row + dx][current.col + dy]
        elif move == 'R':
            direction = right_turns[direction]
            dx, dy = directions_dict[direction]
            current = grid[current.row + dx][current.col + dy]
        elif move == 'F':
            current = grid[current.row + directions_dict[direction][0]][current.col + directions_dict[direction][1]]
        elif move == 'B':
            direction = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}[direction]
            current = grid[current.row + directions_dict[direction][0]][current.col + directions_dict[direction][1]]

        current.in_path = True
        current.current = True
        yield current  # Yield the current position to update the game display
        current.current = False

    current.in_path = True
    current.current = True
    yield current  # Yield the goal position


def main():
    # Create the maze only once here
    maze = create_maze(ROWS, COLS)
    solver_gen = solve_maze(maze, 0, 0)
    running = True
    path = []
    moves = []
    optimized_solver_gen = None
    display_optimized_path = False  # Flag to control which path to display

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        win.fill(BLACK)
        for row in maze:
            for cell in row:
                cell.draw(win)

        if not display_optimized_path:
            try:
                current = next(solver_gen)
                if isinstance(current, tuple):
                    path, moves = current
                    print("Original moves:", moves)
                    optimized_moves = simplify_path(moves)
                    print("Optimized moves:", optimized_moves)
                    optimized_solver_gen = solve_maze_optimized(maze, 0, 0, optimized_moves)
                    display_optimized_path = True  # Change flag to start displaying optimized path
            except StopIteration:
                pass

        if display_optimized_path and optimized_solver_gen is not None:
            try:
                current = next(optimized_solver_gen)
                if isinstance(current, Cell):
                    # Highlight the cell in the optimized path
                    pygame.draw.rect(win, YELLOW, (current.col * CELL_WIDTH + 1, current.row * CELL_HEIGHT + 1, CELL_WIDTH - 2, CELL_HEIGHT - 2))
            except StopIteration:
                # Optionally reset the generator if needed
                optimized_solver_gen = solve_maze_optimized(maze, 0, 0, optimized_moves)

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()


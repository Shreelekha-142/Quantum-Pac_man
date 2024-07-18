import pygame
import random
import qiskit
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, plot_circuit_layout
import matplotlib.pyplot as plt

# Initialize Pygame
pygame.init()

# Screen dimensions and block size
BLOCK_SIZE = 20
MAZE_WIDTH = 20
MAZE_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * MAZE_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * MAZE_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Quantum Pac-Man with Power-Ups')

# Font for text
font = pygame.font.SysFont(None, 36)

# Clock
clock = pygame.time.Clock()

def draw_text(surface, text, color, position):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=position)
    surface.blit(textobj, textrect)

# Quantum Circuit Initialization
def initialize_quantum():
    # Create a Quantum Circuit with 2 qubits
    qc = QuantumCircuit(2)
    qc.h(0)  # Apply Hadamard gate to put qubit 0 in superposition
    qc.cx(0, 1)  # Entangle qubit 0 and qubit 1
    return qc

# Apply quantum gate based on Pac-Man's movement
def apply_quantum_gate(qc, gate):
    if gate == 'x':
        qc.x(0)
    elif gate == 'y':
        qc.y(0)
    elif gate == 'z':
        qc.z(0)
    return qc

# Measure the quantum circuit
def measure_quantum(qc):
    qc.measure_all()
    backend = AerSimulator()
    result = backend.run(qc).result()
    counts = result.get_counts()
    return counts

# Initialize game variables
def init_game():
    global walls, foods, powerups, pacman, ghosts, game_over, power_up_active, power_up_end_time, ghost_home_positions, ghost_rejuvenate_time, ghost_colors, win, qc, running

    # Initialize game state
    game_over = False
    win = False
    power_up_active = False
    power_up_end_time = 0
    ghost_rejuvenate_time = [0] * 2  # Assuming 2 ghosts
    ghost_colors = [RED] * 2  # Assuming 2 ghosts

    # Initialize quantum circuit
    qc = initialize_quantum()

    # Maze layout (0 = path, 1 = wall)
    maze = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1],
        [1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1],
        [1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    # Convert maze layout to pygame.Rect objects for collision detection
    walls = []
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            if maze[y][x] == 1:
                walls.append(pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    # Initialize foods
    foods = []
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            if maze[y][x] == 0:
                foods.append(pygame.Rect(x * BLOCK_SIZE + BLOCK_SIZE // 4, y * BLOCK_SIZE + BLOCK_SIZE // 4, BLOCK_SIZE // 2, BLOCK_SIZE // 2))

    # Initialize power-ups
    powerups = []
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            if maze[y][x] == 0 and random.random() < 0.05:
                powerups.append(pygame.Rect(x * BLOCK_SIZE + BLOCK_SIZE // 4, y * BLOCK_SIZE + BLOCK_SIZE // 4, BLOCK_SIZE // 2, BLOCK_SIZE // 2))

    # Initialize Pac-Man
    pacman = pygame.Rect(1 * BLOCK_SIZE, 1 * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)

    # Initialize ghosts
    ghosts = [pygame.Rect(18 * BLOCK_SIZE, 1 * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
              pygame.Rect(18 * BLOCK_SIZE, 18 * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)]
    ghost_home_positions = [ghost.topleft for ghost in ghosts]

# Initialize game variables
init_game()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Pac-Man movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        new_position = pacman.move(-BLOCK_SIZE, 0)
        if not any(wall.collidepoint(new_position.topleft) for wall in walls):
            pacman = new_position
            qc = apply_quantum_gate(qc, 'x')
    if keys[pygame.K_RIGHT]:
        new_position = pacman.move(BLOCK_SIZE, 0)
        if not any(wall.collidepoint(new_position.topleft) for wall in walls):
            pacman = new_position
            qc = apply_quantum_gate(qc, 'y')
    if keys[pygame.K_UP]:
        new_position = pacman.move(0, -BLOCK_SIZE)
        if not any(wall.collidepoint(new_position.topleft) for wall in walls):
            pacman = new_position
            qc = apply_quantum_gate(qc, 'z')
    if keys[pygame.K_DOWN]:
        new_position = pacman.move(0, BLOCK_SIZE)
        if not any(wall.collidepoint(new_position.topleft) for wall in walls):
            pacman = new_position
            qc = apply_quantum_gate(qc, 'x')

    # Check for food collisions
    for food in foods[:]:
        if pacman.colliderect(food):
            foods.remove(food)

    # Check for power-up collisions
    for powerup in powerups[:]:
        if pacman.colliderect(powerup):
            powerups.remove(powerup)
            power_up_active = True
            power_up_end_time = pygame.time.get_ticks() + 5000  # Power-up lasts for 5 seconds

    # Deactivate power-up if time is up
    if power_up_active and pygame.time.get_ticks() > power_up_end_time:
        power_up_active = False

    # Ghost movement
    for i, ghost in enumerate(ghosts):
        if pygame.time.get_ticks() < ghost_rejuvenate_time[i]:
            ghost_colors[i] = BLUE
            continue

        ghost_colors[i] = RED
        if random.random() < 0.5:
            if pacman.x > ghost.x:
                new_position = ghost.move(BLOCK_SIZE, 0)
            elif pacman.x < ghost.x:
                new_position = ghost.move(-BLOCK_SIZE, 0)
            elif pacman.y > ghost.y:
                new_position = ghost.move(0, BLOCK_SIZE)
            elif pacman.y < ghost.y:
                new_position = ghost.move(0, -BLOCK_SIZE)
        else:
            direction = random.choice([(BLOCK_SIZE, 0), (-BLOCK_SIZE, 0), (0, BLOCK_SIZE), (0, -BLOCK_SIZE)])
            new_position = ghost.move(*direction)

        # Check for wall collisions
        if not any(wall.collidepoint(new_position.topleft) for wall in walls):
            ghost.topleft = new_position.topleft

        # Check for collisions with Pac-Man
        if pacman.colliderect(ghost):
            if power_up_active:
                ghost_rejuvenate_time[i] = pygame.time.get_ticks() + 5000  # Ghost is out for 5 seconds
                ghost.topleft = ghost_home_positions[i]
                ghost_colors[i] = BLUE
            else:
                game_over = True

    # Check for win condition
    if not foods:
        win = True

    # Draw everything
    screen.fill(BLACK)
    for wall in walls:
        pygame.draw.rect(screen, WHITE, wall)
    for food in foods:
        pygame.draw.ellipse(screen, YELLOW, food)
    for powerup in powerups:
        pygame.draw.ellipse(screen, GREEN, powerup)
    pygame.draw.rect(screen, YELLOW, pacman)
    for i, ghost in enumerate(ghosts):
        pygame.draw.rect(screen, ghost_colors[i], ghost)
    if game_over:
        draw_text(screen, 'Game Over', RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    if win:
        draw_text(screen, 'You Win!', GREEN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(10)

    # Check for game over or win condition
    if game_over or win:
        draw_text(screen, 'Press R to Restart or Q to Quit', WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.display.flip()
        waiting_for_restart = True
        while waiting_for_restart:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting_for_restart = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        init_game()
                        waiting_for_restart = False
                    elif event.key == pygame.K_q:
                        running = False
                        waiting_for_restart = False

# Quit Pygame
pygame.quit()

# Measure and display quantum results
counts = measure_quantum(qc)

# Display the quantum circuit
print(qc.draw(output='text'))

# Plot the histogram of measurement results
plot_histogram(counts).show()

# Display the histogram for 15 seconds
plt.pause(15)



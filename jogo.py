
import pygame
import sys
import math

# ------------------------
# Configurações
# ------------------------
TILE = 35
ROWS = 15
COLS = 15
WIDTH, HEIGHT = COLS * TILE, (ROWS + 3) * TILE
FPS = 60
UI_BAR = 3 * TILE

# ------------------------
# Labirinto
# ------------------------
MAZE = [
    "##############",
    "#....p.....h.#",
    "#.##.##.##.#.#",
    "#p##.......#h#",
    "#.##.#####...#",
    "#....l.......#",
    "##.##.###.#..#",
    "#.....b......#",
    "##.##.###.##.#",
    "#............#",
    "#.##.####.##.#",
    "#b##......##p#",
    "#.##.##.#.##.#",
    "#......l.....#",
    "##############",
]

ROWS = len(MAZE)
COLS = len(MAZE[0])

# ------------------------
# Helpers
# ------------------------
def grid_to_px(c, r):
    return c * TILE, UI_BAR + r * TILE

def px_to_grid(x, y):
    return int(x // TILE), int((y - UI_BAR) // TILE)

def is_wall(c, r):
    if r < 0 or r >= ROWS or c < 0 or c >= COLS:
        return True
    return MAZE[r][c] == '#'

# ------------------------
# Classes
# ------------------------
class PelletField:
    def __init__(self, food_images):
        self.pellets = set()
        self.power = set()
        self.foods = []
        self.food_images = food_images
        for r, row in enumerate(MAZE):
            for c, ch in enumerate(row):
                if ch == '.':
                    self.pellets.add((c, r))
                elif ch == 'o':
                    self.power.add((c, r))
                elif ch in ['h', 'f', 'p', 'l']:
                    self.foods.append((c, r, ch))

    def draw(self, surf):
        for (c, r) in self.pellets:
            x, y = grid_to_px(c, r)
            pygame.draw.circle(surf, (255, 255, 255), (x + TILE // 2, y + TILE // 2), 4)
        for (c, r) in self.power:
            x, y = grid_to_px(c, r)
            pygame.draw.circle(surf, (255, 255, 255), (x + TILE // 2, y + TILE // 2), 9, width=2)
        for (c, r, ch) in self.foods:
            x, y = grid_to_px(c, r)
            surf.blit(self.food_images[ch], (x, y))

class Pacman:
    def __init__(self, c, r):
        self.x, self.y = grid_to_px(c, r)
        self.x += TILE // 2
        self.y += TILE // 2
        self.speed = 3.0
        self.dir = pygame.Vector2(0,0)   # começa parado
        self.next_dir = pygame.Vector2(0,0)
        self.anim_frame = 0

    def set_direction(self, direction):
        self.next_dir = direction

    def update(self):
        gx, gy = px_to_grid(self.x, self.y)

        # centralização no tile
        centered_x = abs((self.x - TILE//2) % TILE) < self.speed
        centered_y = abs((self.y - UI_BAR - TILE//2) % TILE) < self.speed

        if centered_x and centered_y:
            nx, ny = int(gx + self.next_dir.x), int(gy + self.next_dir.y)
            if not is_wall(nx, ny):
                self.dir = self.next_dir
                self.x = gx * TILE + TILE//2
                self.y = gy * TILE + UI_BAR + TILE//2

        # movimento
        next_x = self.x + self.dir.x * self.speed
        next_y = self.y + self.dir.y * self.speed
        tile_c = int(next_x // TILE)
        tile_r = int((next_y - UI_BAR) // TILE)

        if not is_wall(tile_c, tile_r):
            self.x = next_x
            self.y = next_y
        else:
            # centraliza ao bater
            self.x = gx * TILE + TILE//2
            self.y = gy * TILE + UI_BAR + TILE//2

        self.anim_frame = (self.anim_frame + 1) % 30

    def draw(self, surf):
        center = (int(self.x), int(self.y))
        radius = TILE//2 - 2
        mouth_angle = 30 if self.anim_frame < 15 else 5
        start_angle = 0
        if self.dir.x == 1: start_angle = 0
        elif self.dir.x == -1: start_angle = 180
        elif self.dir.y == -1: start_angle = 90
        elif self.dir.y == 1: start_angle = 270

        pygame.draw.circle(surf, (255,255,0), center, radius)
        mouth = [
            center,
            (center[0] + radius * math.cos(math.radians(start_angle + mouth_angle)),
             center[1] - radius * math.sin(math.radians(start_angle + mouth_angle))),
            (center[0] + radius * math.cos(math.radians(start_angle - mouth_angle)),
             center[1] - radius * math.sin(math.radians(start_angle - mouth_angle))),
        ]
        pygame.draw.polygon(surf, (0,0,0), mouth)

# ------------------------
# Jogo
# ------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pac-Man Comida Saudável vs Gordurosa")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22, bold=True)

        self.food_images = {
            'h': pygame.transform.scale(pygame.image.load("hamburguer.png"), (TILE, TILE)),
            'f': pygame.transform.scale(pygame.image.load("batata.png"), (TILE, TILE)),
            'p': pygame.transform.scale(pygame.image.load("pizza.png"), (TILE, TILE)),
            'l': pygame.transform.scale(pygame.image.load("legume.png"), (TILE, TILE))
        }

        self.reset()

    def reset(self):
        self.score = 0
        self.pac = Pacman(1, 1)
        self.pellets = PelletField(self.food_images)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.pac.set_direction(pygame.Vector2(-1,0))
        elif keys[pygame.K_RIGHT]:
            self.pac.set_direction(pygame.Vector2(1,0))
        elif keys[pygame.K_UP]:
            self.pac.set_direction(pygame.Vector2(0,-1))
        elif keys[pygame.K_DOWN]:
            self.pac.set_direction(pygame.Vector2(0,1))

    def pellet_collision(self):
        gx, gy = px_to_grid(self.pac.x, self.pac.y)

        if (gx, gy) in self.pellets.pellets:
            self.pellets.pellets.remove((gx, gy))
            self.score += 10

        if (gx, gy) in self.pellets.power:
            self.pellets.power.remove((gx, gy))
            self.score += 50

        for f in list(self.pellets.foods):
            c, r, ch = f
            if gx == c and gy == r:
                self.pellets.foods.remove(f)
                if ch in ['h','f','p']:
                    self.score += 100
                    self.pac.speed = max(1.5, self.pac.speed - 0.5)  # acumula lentidão
                elif ch == 'l':
                    self.score += 50
                    self.pac.speed = min(8.0, self.pac.speed + 0.5)  # acumula velocidade

    def draw_maze(self):
        self.screen.fill((0,0,0))
        for r, row in enumerate(MAZE):
            for c, ch in enumerate(row):
                if ch == '#':
                    x, y = grid_to_px(c, r)
                    pygame.draw.rect(self.screen, (33,33,222), (x, y, TILE, TILE), 2)
        self.pellets.draw(self.screen)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.handle_input()
            self.pac.update()
            self.pellet_collision()

            self.draw_maze()
            self.pac.draw(self.screen)

            score_s = self.font.render(f"SCORE: {self.score}", True, (255,255,255))
            speed_s = self.font.render(f"SPEED: {self.pac.speed:.1f}", True, (255,255,255))
            self.screen.blit(score_s, (10,8))
            self.screen.blit(speed_s, (200,8))

            pygame.display.flip()
            self.clock.tick(FPS)

# ------------------------
# Execução
# ------------------------
if __name__ == "__main__":
    Game().run()

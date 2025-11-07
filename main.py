import pygame
import sys
import random
from pygame.math import Vector2

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 300
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cubo Runner: Endless Survival")
clock = pygame.time.Clock()

# Colores (Mantengo los colores de fallback)
SKY = (135, 206, 235)
GROUND = (200, 200, 200)
CUBE_COLOR = (0, 200, 0)
CACTUS_COLOR = (0, 100, 0)
BIRD_COLOR = (100, 100, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# --- 🖼️ CARGA GLOBAL DE IMÁGENES / ASSETS 🖼️ ---
ASSETS_LOADED = False
CUBE_ASSET = None
CACTUS_ASSETS = []
BIRD_ASSET_STATIC = None

try:
    # 1. Carga del Cubo (usando tu circulo.png)
    CUBE_IMAGE_TEMP = pygame.image.load('assets/circulo.png').convert_alpha()
    CUBE_ASSET = pygame.transform.scale(CUBE_IMAGE_TEMP, (40, 40)) 
    
    # 2. Carga de Obstáculos (Placeholders: necesitas crear estos archivos)
    # Por ahora, usaré los mismos assets para mostrar la estructura:
    
    # Cactus (Ejemplo usando circulo.png como placeholder escalado)
    CACTUS_IMAGE_TEMP = pygame.image.load('assets/1141794.png').convert_alpha()
    CACTUS_ASSETS = [
        pygame.transform.scale(CACTUS_IMAGE_TEMP, (20, 40)), # Cactus pequeño
        pygame.transform.scale(CACTUS_IMAGE_TEMP, (30, 50)), # Cactus mediano
        pygame.transform.scale(CACTUS_IMAGE_TEMP, (40, 60)), # Cactus grande
    ]

    # Pájaro (Ejemplo usando circulo.png como placeholder escalado)
    BIRD_IMAGE_TEMP = pygame.image.load('assets/384.png').convert_alpha()
    BIRD_ASSET_STATIC = pygame.transform.scale(BIRD_IMAGE_TEMP, (50, 30))

    ASSETS_LOADED = True
    print("Assets cargados correctamente.")

except pygame.error as e:
    print(f"⚠️ Error al cargar assets. ¿Está 'assets/circulo.png' en su sitio? Se usará el dibujo simple. Error: {e}")
    ASSETS_LOADED = False
# ----------------------------------------------------------------------


class Cube:
    def __init__(self):
        self.size = 40
        # Posición inicial
        self.pos = Vector2(80, SCREEN_HEIGHT - 80 - self.size)
        self.vel = Vector2(0, 0)
        self.on_ground = True
        self.gravity = 1.2
        self.jump_power = -18
        
        # Asignamos el objeto Surface cargado globalmente (¡la clave para que funcione!)
        if ASSETS_LOADED:
            self.image = CUBE_ASSET
        else:
            self.image = None
        
        # Rect para colisiones
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)


    def jump(self):
        if self.on_ground:
            self.vel.y = self.jump_power
            self.on_ground = False

    def update(self):
        self.vel.y += self.gravity
        self.pos.y += self.vel.y
        if self.pos.y >= SCREEN_HEIGHT - 80 - self.size:
            self.pos.y = SCREEN_HEIGHT - 80 - self.size
            self.vel.y = 0
            self.on_ground = True
        
        # Actualizar la posición del rect
        self.rect.topleft = (self.pos.x, self.pos.y)

    def draw(self, screen):
        if self.image:
            # Dibujar la imagen (Surface)
            screen.blit(self.image, self.pos)
        else:
            # DIBUJO SIMPLE (Fallback si la imagen no carga)
            pygame.draw.rect(screen, CUBE_COLOR, (self.pos.x, self.pos.y, self.size, self.size))
            pygame.draw.rect(screen, BLACK, (self.pos.x, self.pos.y, self.size, self.size), 3)


class Obstacle:
    def __init__(self, type):
        self.type = type
        
        if self.type == 'cactus':
            if ASSETS_LOADED:
                self.image = random.choice(CACTUS_ASSETS)
            else:
                self.image = None

            self.width, self.height = self.image.get_size() if self.image else random.choice([(20, 40), (30, 50), (40, 60)])
            self.pos = Vector2(SCREEN_WIDTH, SCREEN_HEIGHT - 80 - self.height)
            
        else:  # bird
            if ASSETS_LOADED:
                self.image = BIRD_ASSET_STATIC
            else:
                self.image = None

            self.width, self.height = self.image.get_size() if self.image else (50, 30)
            self.pos = Vector2(SCREEN_WIDTH, random.randint(100, 200))
            
        # Rect para colisiones
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)

    def update(self, speed):
        self.pos.x -= speed
        self.rect.topleft = (self.pos.x, self.pos.y)

    def draw(self, screen):
        if self.image:
            # Dibujar la imagen (Surface)
            screen.blit(self.image, self.pos)
        else:
            # DIBUJO SIMPLE (Fallback)
            if self.type == 'cactus':
                pygame.draw.rect(screen, CACTUS_COLOR, (self.pos.x, self.pos.y, self.width, self.height))
                pygame.draw.rect(screen, BLACK, (self.pos.x, self.pos.y, self.width, self.height), 2)
            else:
                pygame.draw.ellipse(screen, BIRD_COLOR, (self.pos.x, self.pos.y, self.width, self.height))
                pygame.draw.ellipse(screen, BLACK, (self.pos.x, self.pos.y, self.width, self.height), 2)

    def collides_with(self, cube):
        # Usamos los rects actualizados para colisiones
        return cube.rect.colliderect(self.rect)

# ------------------------------------------------
# LÓGICA DEL JUEGO
# ------------------------------------------------

cube = Cube()
obstacles = []
score = 0
high_score = 0
game_speed = 8
spawn_timer = 0
font = pygame.font.SysFont('Courier', 24, bold=True)
game_over = False
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP):
                if not game_over:
                    cube.jump()
                else:
                    # Reiniciar
                    cube = Cube()
                    obstacles = []
                    score = 0
                    game_speed = 8
                    game_over = False

    if not game_over:
        spawn_timer += 1
        spawn_rate = max(30, 90 - int(score / 100))
        if spawn_timer > spawn_rate:
            spawn_timer = 0
            # Aumentar la probabilidad de ave con la dificultad (ejemplo)
            bird_chance = 0.3 + (score * 0.0001) 
            obstacles.append(Obstacle('cactus') if random.random() < (0.7 - bird_chance) else Obstacle('bird'))

        cube.update()
        
        # Actualización de obstáculos y colisión
        for obs in obstacles[:]:
            obs.update(game_speed)
            if obs.collides_with(cube):
                game_over = True
                if score > high_score:
                    high_score = score
            if obs.pos.x < -100:
                obstacles.remove(obs)
                score += 10 
        
        # Aumento de velocidad y dificultad
        if score % 100 == 0 and score > 0 and score // 100 != (score - 10) // 100:
            game_speed += 0.02
        game_speed += 0.0005 # Aumento lento y constante

    # Dibujar
    screen.fill(SKY)
    pygame.draw.rect(screen, GROUND, (0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80))
    pygame.draw.line(screen, BLACK, (0, SCREEN_HEIGHT - 80), (SCREEN_WIDTH, SCREEN_HEIGHT - 80), 3)

    for obs in obstacles:
        obs.draw(screen)
    cube.draw(screen)

    # Puntuación
    screen.blit(font.render(f"SCORE: {score}", True, BLACK), (SCREEN_WIDTH - 180, 20))
    screen.blit(font.render(f"HI: {high_score}", True, BLACK), (SCREEN_WIDTH - 180, 50))

    if game_over:
        screen.blit(font.render("ERI ENTERO MALO - ESPACIO PARA REINICIAR", True, (200, 0, 0)),
                     (100, SCREEN_HEIGHT // 2 - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
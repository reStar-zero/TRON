import pygame
import random
import math

WIDTH, HEIGHT = 1000, 800
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_COLOR = (0, 0, 0)
PLAYER_OUTLINE_COLOR = (0, 200, 255)
DISK_COLOR = (0, 0, 0)
DISK_OUTLINE_COLOR = (0, 200, 255)
SHIELD_COLOR = (0, 0, 0)
SHIELD_OUTLINE_COLOR = (255, 255, 0)
ENEMY_COLOR = (0, 0, 0)
ENEMY_OUTLINE_COLOR = (255, 0, 0)
DISK_DISTANCE = 400
DISK_SPEED = 10
DISK_RADIUS = 5
DISK_ON_BACK_RADIUS = 8  # Увеличенный радиус диска на спине
SHIELD_RADIUS = 8
OUTLINE_WIDTH = 2
GRID_SIZE = 50
RETURN_SPEED_MULTIPLIER = 1.5
TRAIL_LENGTH = 20
TRAIL_FADE = 0.7

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRON")
programIcon = pygame.image.load('images/icon.png')
pygame.display.set_icon(programIcon)

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y), 1)

def draw_dual_disk(x, y, radius, angle=0):
    pygame.draw.circle(screen, DISK_OUTLINE_COLOR, (int(x), int(y)), radius)
    
    inner_radius = radius - 2
    pygame.draw.circle(screen, DISK_COLOR, (int(x), int(y)), inner_radius)
    
    core_radius = radius - 4
    pygame.draw.circle(screen, DISK_OUTLINE_COLOR, (int(x), int(y)), core_radius)
    
    black_core_radius = radius - 6
    pygame.draw.circle(screen, DISK_COLOR, (int(x), int(y)), black_core_radius)

def draw_rotating_dual_disk(x, y, radius, angle):
    size = radius * 2 + 4  
    disk_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2
    
    pygame.draw.circle(disk_surface, DISK_OUTLINE_COLOR, (center, center), radius)
    
    inner_radius = radius - 2
    pygame.draw.circle(disk_surface, DISK_COLOR, (center, center), inner_radius)
    
    core_radius = radius - 4
    pygame.draw.circle(disk_surface, DISK_OUTLINE_COLOR, (center, center), core_radius)
    
    black_core_radius = radius - 6
    pygame.draw.circle(disk_surface, DISK_COLOR, (center, center), black_core_radius)
    
    rotated_disk = pygame.transform.rotate(disk_surface, math.degrees(angle))
    
    new_rect = rotated_disk.get_rect(center=(x, y))
    screen.blit(rotated_disk, new_rect)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 50, 50)
        self.speed = 6
        self.has_shield = False
        self.has_disk = True  

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

    def draw(self):
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect)
        pygame.draw.rect(screen, PLAYER_OUTLINE_COLOR, self.rect, OUTLINE_WIDTH)
        
        if self.has_disk:
            disk_x = self.rect.centerx
            disk_y = self.rect.centery
            
            draw_dual_disk(disk_x, disk_y, DISK_ON_BACK_RADIUS)

class Disk:
    def __init__(self, x, y, angle):
        self.initial_position = (x, y)
        self.x = x
        self.y = y
        self.speed = DISK_SPEED
        self.return_speed = DISK_SPEED * RETURN_SPEED_MULTIPLIER
        self.angle = angle
        self.rotation_angle = 0  # Угол поворота диска
        self.distance_traveled = 0
        self.flying = True
        self.radius = DISK_RADIUS
        self.returning = False
        self.target_position = None
        self.trail = []

    def move(self, player_position):
        if self.flying:
            self.x += self.speed * math.cos(self.angle)
            self.y += self.speed * math.sin(self.angle)
            self.distance_traveled += self.speed
            
            self.rotation_angle += 0.3
            
            self.trail.append((self.x, self.y))
            if len(self.trail) > TRAIL_LENGTH:
                self.trail.pop(0)
            
            if self.distance_traveled >= DISK_DISTANCE:
                self.flying = False
                self.returning = True
                self.target_position = player_position
        elif self.returning:
            target_x, target_y = player_position
            
            dx = target_x - self.x
            dy = target_y - self.y
            distance_to_target = math.sqrt(dx**2 + dy**2)
            
            if distance_to_target > self.return_speed:
                self.x += (dx / distance_to_target) * self.return_speed
                self.y += (dy / distance_to_target) * self.return_speed
                
                self.rotation_angle += 0.3
                
                self.trail.append((self.x, self.y))
                if len(self.trail) > TRAIL_LENGTH:
                    self.trail.pop(0)
            else:
                self.x = target_x
                self.y = target_y
                return True
        return False

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

    def draw(self):
        # Рисуем след
        for i, pos in enumerate(self.trail):
            alpha = (i + 1) / len(self.trail) * 255 * TRAIL_FADE
            trail_radius = self.radius * (0.5 + (i / len(self.trail)) * 0.5)
            
            trail_surface = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
            trail_color = (*DISK_OUTLINE_COLOR, int(alpha))
            pygame.draw.circle(trail_surface, trail_color, 
                             (trail_radius, trail_radius), trail_radius)
            screen.blit(trail_surface, (pos[0] - trail_radius, pos[1] - trail_radius))
        
        draw_rotating_dual_disk(self.x, self.y, self.radius, self.rotation_angle)

class Shield:
    def __init__(self, player):
        self.player = player
        self.distance_from_player = 40
        self.angle = 0
        self.radius = SHIELD_RADIUS
        
    def update(self, mouse_pos):
        player_center = self.player.rect.center
        dx = mouse_pos[0] - player_center[0]
        dy = mouse_pos[1] - player_center[1]
        self.angle = math.atan2(dy, dx)
        
    def get_position(self):
        player_center = self.player.rect.center
        x = player_center[0] + math.cos(self.angle) * self.distance_from_player
        y = player_center[1] + math.sin(self.angle) * self.distance_from_player
        return (x, y)
        
    def get_rect(self):
        x, y = self.get_position()
        return pygame.Rect(x - self.radius, y - self.radius, 
                          self.radius * 2, self.radius * 2)
        
    def draw(self):
        x, y = self.get_position()
        pygame.draw.circle(screen, SHIELD_COLOR, (int(x), int(y)), self.radius)
        pygame.draw.circle(screen, SHIELD_OUTLINE_COLOR, (int(x), int(y)), self.radius, OUTLINE_WIDTH)

class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - 50), random.randint(0, HEIGHT - 50), 50, 50)
        self.health = 50
        self.speed = 2
        self.move_timer = 0
        self.move_interval = 30
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    def move(self):
        self.move_timer += 1
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            
        dx, dy = self.direction
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

    def draw(self):
        pygame.draw.rect(screen, ENEMY_COLOR, self.rect)
        pygame.draw.rect(screen, ENEMY_OUTLINE_COLOR, self.rect, OUTLINE_WIDTH)

def main():
    clock = pygame.time.Clock()
    player = Player()
    disks = []
    enemies = [Enemy() for _ in range(5)]
    shield = Shield(player)
    running = True
    show_shield = False

    while running:
        screen.fill(BLACK)
        draw_grid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if player.has_disk and not any(d.flying or d.returning for d in disks):
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        angle = math.atan2(mouse_y - player.rect.centery, mouse_x - player.rect.centerx)
                        disks.append(Disk(player.rect.centerx, player.rect.centery, angle))
                        player.has_disk = False  # Убираем диск со спины
                
                elif event.button == 3:
                    show_shield = not show_shield

        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        player.move(dx, dy)

        shield.update(pygame.mouse.get_pos())

        player_position = (player.rect.centerx, player.rect.centery)

        for enemy in enemies:
            enemy.move()

        for disk in disks[:]:
            if disk.move(player_position):
                disks.remove(disk)
                player.has_disk = True 

            for enemy in enemies[:]:
                if disk.get_rect().colliderect(enemy.rect) and disk.flying:
                    enemy.health -= 50
                    disk.flying = False
                    disk.returning = True
                    disk.target_position = player_position
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                    break

        player.draw()
        for disk in disks:
            disk.draw()
        for enemy in enemies:
            enemy.draw()
        
        if show_shield:
            shield.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
import pygame
import random
import math
import time
import json
import os

WIDTH, HEIGHT = 1000, 800
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_COLOR = (0, 0, 0)
PLAYER_OUTLINE_COLOR = (0, 200, 255)
DISK_COLOR = (0, 0, 0)
DISK_OUTLINE_COLOR = (0, 200, 255)
DISK_ON_BACK_COLOR = (20, 20, 20)
DISK_ON_BACK_OUTLINE_COLOR = (0, 100, 150)
ENEMY_DISK_COLOR = (0, 0, 0)
ENEMY_DISK_OUTLINE_COLOR = (255, 0, 0)
ENEMY_DISK_ON_BACK_OUTLINE_COLOR = (150, 0, 0)
SHIELD_COLOR = (0, 0, 0)
SHIELD_OUTLINE_COLOR = (255, 255, 0)
ENEMY_COLOR = (0, 0, 0)
ENEMY_OUTLINE_COLOR = (255, 0, 0)
FORBIDDEN_COLOR = (0, 0, 0)
FORBIDDEN_OUTLINE_COLOR = (255, 255, 255)
MEDKIT_COLOR = (255, 255, 255)
MEDKIT_CROSS_COLOR = (0, 255, 0)
DISK_DISTANCE = 400
DISK_SPEED = 10
DISK_RADIUS = 10
SHIELD_RADIUS = 12
OUTLINE_WIDTH = 2
GRID_SIZE = 50
RETURN_SPEED_MULTIPLIER = 1.5
TRAIL_LENGTH = 20
TRAIL_FADE = 0.7
FORBIDDEN_SIZE = 200
MAX_HEALTH = 5
SHIELD_REFLECT_BUFF_TIME = 0.5
CHARGED_DISK_DISTANCE_MULTIPLIER = 2.0
CHARGED_DISK_SPEED_MULTIPLIER = 1.5
CHARGED_DISK_DAMAGE_MULTIPLIER = 2.0
MEDKIT_SPAWN_DELAY = 3000

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRON")

forbidden_rect = pygame.Rect(WIDTH // 2 - FORBIDDEN_SIZE // 2, HEIGHT // 2 - FORBIDDEN_SIZE // 2, FORBIDDEN_SIZE, FORBIDDEN_SIZE)

# ========== ЭТАП 1: ОКНО ВВОДА ИМЕНИ ==========
def get_player_name():
    """Простое окно ввода имени"""
    font = pygame.font.Font(None, 48)
    input_box = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 25, 300, 50)
    name = ""
    active = True
    clock = pygame.time.Clock()
    
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()[:20]
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 20 and event.unicode.isprintable():
                        name += event.unicode
        
        screen.fill(BLACK)
        title = font.render("ENTER YOUR NAME:", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
        screen.blit(title, title_rect)
        
        txt_surface = font.render(name + "_", True, WHITE)
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))
        pygame.draw.rect(screen, WHITE, input_box, 2)
        
        pygame.display.flip()
        clock.tick(30)
    
    return None

# ========== ОСТАЛЬНЫЕ ФУНКЦИИ ИГРЫ (БЕЗ СИСТЕМЫ УБИЙСТВ) ==========
def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y), 1)

def draw_forbidden_area():
    pygame.draw.rect(screen, FORBIDDEN_COLOR, forbidden_rect)
    pygame.draw.rect(screen, FORBIDDEN_OUTLINE_COLOR, forbidden_rect, OUTLINE_WIDTH)

def draw_health(health, x, y, is_player=True):
    HEART_RADIUS = 12
    HEART_SPACING = 28
    color = (0, 100, 255) if is_player else (255, 50, 50)
    
    for i in range(MAX_HEALTH):
        heart_x = x + i * HEART_SPACING
        if i < health:
            pygame.draw.circle(screen, color, (heart_x, y), HEART_RADIUS)
            pygame.draw.circle(screen, WHITE, (heart_x, y), HEART_RADIUS, 2)
        else:
            pygame.draw.circle(screen, (50, 50, 50), (heart_x, y), HEART_RADIUS)
            pygame.draw.circle(screen, (100, 100, 100), (heart_x, y), HEART_RADIUS, 2)

def draw_medkit(x, y):
    size = 20
    medkit_rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(screen, MEDKIT_COLOR, medkit_rect)
    pygame.draw.rect(screen, BLACK, medkit_rect, 2)
    pygame.draw.line(screen, MEDKIT_CROSS_COLOR, (x + size//2, y + 4), (x + size//2, y + size - 4), 4)
    pygame.draw.line(screen, MEDKIT_CROSS_COLOR, (x + 4, y + size//2), (x + size - 4, y + size//2), 4)

def draw_disk_on_back(x, y, radius, is_enemy=False, is_charged=False):
    if is_charged:
        outline_color = (255, 215, 0)
        pygame.draw.circle(screen, outline_color, (int(x), int(y)), radius + 2)
    else:
        outline_color = DISK_ON_BACK_OUTLINE_COLOR if not is_enemy else ENEMY_DISK_ON_BACK_OUTLINE_COLOR
    
    pygame.draw.circle(screen, outline_color, (int(x), int(y)), radius)
    inner_radius = radius - 2
    pygame.draw.circle(screen, DISK_ON_BACK_COLOR, (int(x), int(y)), inner_radius)
    core_radius = radius - 4
    pygame.draw.circle(screen, outline_color, (int(x), int(y)), core_radius)
    black_core_radius = radius - 6
    pygame.draw.circle(screen, DISK_ON_BACK_COLOR, (int(x), int(y)), black_core_radius)

def draw_rotating_disk(x, y, radius, angle, is_enemy=False, is_charged=False):
    size = radius * 2 + 8
    disk_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2
    
    color = DISK_COLOR if not is_enemy else ENEMY_DISK_COLOR
    if is_charged:
        outline_color = (255, 215, 0)
    else:
        outline_color = DISK_OUTLINE_COLOR if not is_enemy else ENEMY_DISK_OUTLINE_COLOR
    
    pygame.draw.circle(disk_surface, outline_color, (center, center), radius)
    inner_radius = radius - 2
    pygame.draw.circle(disk_surface, color, (center, center), inner_radius)
    core_radius = radius - 4
    pygame.draw.circle(disk_surface, outline_color, (center, center), core_radius)
    black_core_radius = radius - 6
    pygame.draw.circle(disk_surface, color, (center, center), black_core_radius)
    
    for i in range(2):
        particle_angle = angle + (i * math.pi)
        px = center + math.cos(particle_angle) * (radius - 1)
        py = center + math.sin(particle_angle) * (radius - 1)
        pygame.draw.circle(disk_surface, WHITE, (int(px), int(py)), 2)
    
    rotated_disk = pygame.transform.rotate(disk_surface, math.degrees(angle * 2))
    new_rect = rotated_disk.get_rect(center=(x, y))
    screen.blit(rotated_disk, new_rect)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 50, 50)
        while self.rect.colliderect(forbidden_rect):
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        self.speed = 6
        self.has_disk = True
        self.health = MAX_HEALTH
        self.disk_charged = False

    def move(self, dx, dy):
        new_x = self.rect.x + dx * self.speed
        new_y = self.rect.y + dy * self.speed
        new_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)
        
        if not new_rect.colliderect(forbidden_rect):
            self.rect.x = new_x
            self.rect.y = new_y
        
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

    def draw(self):
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect)
        pygame.draw.rect(screen, PLAYER_OUTLINE_COLOR, self.rect, OUTLINE_WIDTH)
        
        if self.has_disk:
            disk_x = self.rect.centerx
            disk_y = self.rect.centery
            draw_disk_on_back(disk_x, disk_y, DISK_RADIUS, is_enemy=False, is_charged=self.disk_charged)

class Disk:
    def __init__(self, x, y, angle, is_enemy=False, is_charged=False):
        self.x = x
        self.y = y
        self.is_charged = is_charged
        if is_charged:
            self.speed = DISK_SPEED * CHARGED_DISK_SPEED_MULTIPLIER
            self.max_distance = DISK_DISTANCE * CHARGED_DISK_DISTANCE_MULTIPLIER
            self.damage = 1
        else:
            self.speed = DISK_SPEED
            self.max_distance = DISK_DISTANCE
            self.damage = 1
        self.return_speed = self.speed * RETURN_SPEED_MULTIPLIER
        self.angle = angle
        self.rotation_angle = 0
        self.distance_traveled = 0
        self.flying = True
        self.radius = DISK_RADIUS
        self.returning = False
        self.target_position = None
        self.trail = []
        self.is_enemy = is_enemy

    def check_collision_with_forbidden(self):
        disk_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        
        if disk_rect.colliderect(forbidden_rect):
            overlap_left = disk_rect.right - forbidden_rect.left
            overlap_right = forbidden_rect.right - disk_rect.left
            overlap_top = disk_rect.bottom - forbidden_rect.top
            overlap_bottom = forbidden_rect.bottom - disk_rect.top
            
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            
            if min_overlap == overlap_left or min_overlap == overlap_right:
                self.angle = math.pi - self.angle
                if min_overlap == overlap_left:
                    self.x = forbidden_rect.left - self.radius - 1
                else:
                    self.x = forbidden_rect.right + self.radius + 1
            else:
                self.angle = -self.angle
                if min_overlap == overlap_top:
                    self.y = forbidden_rect.top - self.radius - 1
                else:
                    self.y = forbidden_rect.bottom + self.radius + 1

    def move(self, target_position):
        if self.flying:
            self.x += self.speed * math.cos(self.angle)
            self.y += self.speed * math.sin(self.angle)
            self.distance_traveled += self.speed
            
            self.check_collision_with_forbidden()
            
            if self.x - self.radius < 0 or self.x + self.radius > WIDTH:
                self.angle = math.pi - self.angle
                self.x = max(self.radius, min(WIDTH - self.radius, self.x))
            
            if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
                self.angle = -self.angle
                self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
            
            self.rotation_angle += 0.15
            
            self.trail.append((self.x, self.y))
            if len(self.trail) > TRAIL_LENGTH:
                self.trail.pop(0)
            
            if self.distance_traveled >= self.max_distance:
                self.flying = False
                self.returning = True
                self.target_position = target_position
        elif self.returning:
            target_x, target_y = target_position
            
            dx = target_x - self.x
            dy = target_y - self.y
            distance_to_target = math.sqrt(dx**2 + dy**2)
            
            if distance_to_target > self.return_speed:
                self.x += (dx / distance_to_target) * self.return_speed
                self.y += (dy / distance_to_target) * self.return_speed
                
                self.check_collision_with_forbidden()
                
                self.rotation_angle += 0.15
                
                self.trail.append((self.x, self.y))
                if len(self.trail) > TRAIL_LENGTH:
                    self.trail.pop(0)
            else:
                self.x = target_x
                self.y = target_y
                return True
        return False

    def start_returning(self, target_position):
        if self.flying or not self.returning:
            self.flying = False
            self.returning = True
            self.target_position = target_position

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

    def draw(self):
        for i, pos in enumerate(self.trail):
            alpha = (i + 1) / len(self.trail) * 255 * TRAIL_FADE
            trail_radius = self.radius * (0.5 + (i / len(self.trail)) * 0.5)
            
            trail_surface = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
            if self.is_charged:
                outline_color = (255, 215, 0)
            else:
                outline_color = DISK_OUTLINE_COLOR if not self.is_enemy else ENEMY_DISK_OUTLINE_COLOR
            trail_color = (*outline_color, int(alpha))
            pygame.draw.circle(trail_surface, trail_color, 
                             (trail_radius, trail_radius), trail_radius)
            screen.blit(trail_surface, (pos[0] - trail_radius, pos[1] - trail_radius))
        
        draw_rotating_disk(self.x, self.y, self.radius, self.rotation_angle, self.is_enemy, self.is_charged)

class Shield:
    def __init__(self, player):
        self.player = player
        self.distance_from_player = 40
        self.angle = 0
        self.radius = SHIELD_RADIUS
        self.active = False
        self.last_reflect_time = 0
        
    def update(self, mouse_pos):
        if self.active:
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
    
    def reflect(self):
        self.last_reflect_time = time.time()
        
    def is_charged(self):
        return time.time() - self.last_reflect_time <= SHIELD_REFLECT_BUFF_TIME
        
    def draw(self):
        if self.active:
            x, y = self.get_position()
            if self.is_charged():
                glow_radius = self.radius + 4
                for i in range(3):
                    alpha = 100 - i * 30
                    glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (255, 215, 0, alpha), 
                                     (glow_radius, glow_radius), glow_radius - i * 2)
                    screen.blit(glow_surface, (x - glow_radius + i * 2, y - glow_radius + i * 2))
            
            pygame.draw.circle(screen, SHIELD_COLOR, (int(x), int(y)), self.radius)
            pygame.draw.circle(screen, SHIELD_OUTLINE_COLOR, (int(x), int(y)), self.radius, OUTLINE_WIDTH)

class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - 50), random.randint(0, HEIGHT - 50), 50, 50)
        while self.rect.colliderect(forbidden_rect):
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        self.health = MAX_HEALTH
        self.speed = 3
        self.has_disk = True
        self.last_shot_time = 0
        self.shoot_delay = 2000
        self.active = False

    def respawn(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - 50), random.randint(0, HEIGHT - 50), 50, 50)
        while self.rect.colliderect(forbidden_rect):
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        self.health = MAX_HEALTH
        self.has_disk = True
        self.last_shot_time = 0
        self.active = True

    def update_ai(self, player_pos, current_time):
        if not self.active:
            return None
        
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.rect.x += (dx / distance) * self.speed
            self.rect.y += (dy / distance) * self.speed
        
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))
        
        if self.rect.colliderect(forbidden_rect):
            if self.rect.centerx < forbidden_rect.centerx:
                self.rect.x = forbidden_rect.left - self.rect.width
            else:
                self.rect.x = forbidden_rect.right
            if self.rect.centery < forbidden_rect.centery:
                self.rect.y = forbidden_rect.top - self.rect.height
            else:
                self.rect.y = forbidden_rect.bottom
        
        if self.has_disk and current_time - self.last_shot_time > self.shoot_delay:
            angle = math.atan2(player_pos[1] - self.rect.centery, player_pos[0] - self.rect.centerx)
            self.last_shot_time = current_time
            return angle
        return None

    def draw(self):
        pygame.draw.rect(screen, ENEMY_COLOR, self.rect)
        pygame.draw.rect(screen, ENEMY_OUTLINE_COLOR, self.rect, OUTLINE_WIDTH)
        
        if self.has_disk:
            disk_x = self.rect.centerx
            disk_y = self.rect.centery
            draw_disk_on_back(disk_x, disk_y, DISK_RADIUS, is_enemy=True)

class Medkit:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        
    def draw(self):
        draw_medkit(self.rect.x, self.rect.y)

def show_game_over_screen():
    font_big = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    game_over_text = font_big.render("GAME OVER", True, WHITE)
    text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
    screen.blit(game_over_text, text_rect)
    
    restart_text = font_small.render("Press Z to Restart or X to Quit", True, WHITE)
    restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(restart_text, restart_rect)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    return True
                if event.key == pygame.K_x:
                    return False
    return False

def handle_events():
    global running, player, shield, player_disks, right_mouse_pressed, enemy
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if player.has_disk and not any(d.flying or d.returning for d in player_disks):
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    angle = math.atan2(mouse_y - player.rect.centery, 
                                      mouse_x - player.rect.centerx)
                    player_disks.append(Disk(player.rect.centerx, player.rect.centery, angle, 
                                            is_enemy=False, is_charged=player.disk_charged))
                    player.has_disk = False
                    player.disk_charged = False
            
            elif event.button == 3:
                shield.active = True
                right_mouse_pressed = True
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            shield.active = False
            right_mouse_pressed = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and not enemy.active:
                enemy.respawn()

def update_player():
    global player, enemy
    
    keys = pygame.key.get_pressed()
    dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
    dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
    player.move(dx, dy)

def update_shield():
    global shield, right_mouse_pressed
    
    if right_mouse_pressed:
        mouse_pos = pygame.mouse.get_pos()
        shield.update(mouse_pos)

def update_health_packs():
    global health_packs, player, last_spawn_time
    
    current_time = pygame.time.get_ticks()
    missing_health = MAX_HEALTH - player.health
    
    while len(health_packs) > missing_health:
        health_packs.pop()
    
    if missing_health > 0 and len(health_packs) < missing_health and current_time - last_spawn_time > MEDKIT_SPAWN_DELAY:
        last_spawn_time = current_time
        
        while True:
            x = random.randint(50, WIDTH - 70)
            y = random.randint(50, HEIGHT - 70)
            medkit_rect = pygame.Rect(x, y, 20, 20)
            if not medkit_rect.colliderect(forbidden_rect):
                health_packs.append(Medkit(x, y))
                break
    
    for medkit in health_packs[:]:
        if player.rect.colliderect(medkit.rect) and player.health < MAX_HEALTH:
            player.health = min(MAX_HEALTH, player.health + 1)
            health_packs.remove(medkit)

def update_disks():
    global player_disks, enemy_disks, player, enemy, shield
    
    for disk in player_disks[:]:
        disk_returned = disk.move((player.rect.centerx, player.rect.centery))
        
        if disk.get_rect().colliderect(enemy.rect) and enemy.active:
            if shield.active and shield.get_rect().colliderect(disk.get_rect()):
                disk.start_returning((player.rect.centerx, player.rect.centery))
                shield.reflect()
                player.disk_charged = True
            else:
                enemy.health -= disk.damage
                disk.start_returning((player.rect.centerx, player.rect.centery))
        
        if disk_returned:
            player_disks.remove(disk)
            player.has_disk = True
    
    for disk in enemy_disks[:]:
        disk_returned = disk.move((enemy.rect.centerx, enemy.rect.centery))
        
        if disk.get_rect().colliderect(player.rect):
            if shield.active and shield.get_rect().colliderect(disk.get_rect()):
                disk.start_returning((enemy.rect.centerx, enemy.rect.centery))
                shield.reflect()
                player.disk_charged = True
            else:
                player.health -= disk.damage
                disk.start_returning((enemy.rect.centerx, enemy.rect.centery))
        
        if disk_returned:
            enemy_disks.remove(disk)
            enemy.has_disk = True

def draw_all():
    global player, enemy, player_disks, enemy_disks, shield, health_packs, player_name
    
    player.draw()
    if enemy.active:
        enemy.draw()
    
    for disk in player_disks + enemy_disks:
        disk.draw()
    
    if shield.active:
        shield.draw()
    
    for medkit in health_packs:
        medkit.draw()
    
    draw_health(player.health, 10, 10, is_player=True)
    
    if enemy.active:
        draw_health(enemy.health, 10, 50, is_player=False)
    
    small_font = pygame.font.Font(None, 24)
    q_text = small_font.render('Q - Activate Enemy', True, WHITE)
    q_rect = q_text.get_rect()
    q_rect.topright = (WIDTH - 10, 10)
    screen.blit(q_text, q_rect)
    
    # Отображаем имя игрока
    name_text = small_font.render(f'Player: {player_name}', True, WHITE)
    name_rect = name_text.get_rect(topleft=(10, 10))
    screen.blit(name_text, name_rect)
    
    if player.disk_charged:
        charge_text = small_font.render("DISK CHARGED!", True, (255, 215, 0))
        charge_rect = charge_text.get_rect(center=(WIDTH//2, 30))
        screen.blit(charge_text, charge_rect)

def main():
    global running, player, enemy, player_disks, enemy_disks, shield, health_packs
    global last_spawn_time, game_over, right_mouse_pressed, player_name
    
    # ЭТАП 1: запрашиваем имя
    player_name = get_player_name()
    if not player_name:
        pygame.quit()
        return
    
    running = True
    clock = pygame.time.Clock()
    
    player = Player()
    enemy = Enemy()
    player_disks = []
    enemy_disks = []
    shield = Shield(player)
    health_packs = []
    last_spawn_time = 0
    game_over = False
    right_mouse_pressed = False
    
    while running:
        if game_over:
            if show_game_over_screen():
                player = Player()
                enemy = Enemy()
                player_disks.clear()
                enemy_disks.clear()
                health_packs.clear()
                shield = Shield(player)
                game_over = False
                last_spawn_time = pygame.time.get_ticks()
            else:
                running = False
            continue
        
        screen.fill(BLACK)
        draw_grid()
        draw_forbidden_area()
        
        handle_events()
        update_player()
        update_health_packs()
        update_shield()
        
        if enemy.active:
            current_time = pygame.time.get_ticks()
            shoot_angle = enemy.update_ai((player.rect.centerx, player.rect.centery), current_time)
            if shoot_angle is not None:
                enemy_disks.append(Disk(enemy.rect.centerx, enemy.rect.centery, shoot_angle, is_enemy=True))
                enemy.has_disk = False
        
        update_disks()
        
        if player.health <= 0:
            game_over = True
        elif enemy.health <= 0:
            enemy.active = False
            enemy.health = MAX_HEALTH
            enemy.has_disk = True
        
        draw_all()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
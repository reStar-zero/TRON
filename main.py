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

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRON")
programIcon = pygame.image.load('images/icon.png')
pygame.display.set_icon(programIcon)

forbidden_rect = pygame.Rect(WIDTH // 2 - FORBIDDEN_SIZE // 2, HEIGHT // 2 - FORBIDDEN_SIZE // 2, FORBIDDEN_SIZE, FORBIDDEN_SIZE)

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y), 1)

def draw_forbidden_area():
    pygame.draw.rect(screen, FORBIDDEN_COLOR, forbidden_rect)
    pygame.draw.rect(screen, FORBIDDEN_OUTLINE_COLOR, forbidden_rect, OUTLINE_WIDTH)

def draw_disk_on_back(x, y, radius, is_enemy=False):
    outline_color = DISK_ON_BACK_OUTLINE_COLOR if not is_enemy else ENEMY_DISK_ON_BACK_OUTLINE_COLOR
    pygame.draw.circle(screen, outline_color, (int(x), int(y)), radius)
    inner_radius = radius - 2
    pygame.draw.circle(screen, DISK_ON_BACK_COLOR, (int(x), int(y)), inner_radius)
    core_radius = radius - 4
    pygame.draw.circle(screen, outline_color, (int(x), int(y)), core_radius)
    black_core_radius = radius - 6
    pygame.draw.circle(screen, DISK_ON_BACK_COLOR, (int(x), int(y)), black_core_radius)

def draw_rotating_disk(x, y, radius, angle, is_enemy=False):
    size = radius * 2 + 8
    disk_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2
    
    color = DISK_COLOR if not is_enemy else ENEMY_DISK_COLOR
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
        self.has_shield = False
        self.has_disk = True
        self.health = 100
        self.shield_active = False

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
            draw_disk_on_back(disk_x, disk_y, DISK_RADIUS, is_enemy=False)

class Disk:
    def __init__(self, x, y, angle, is_enemy=False):
        self.x = x
        self.y = y
        self.speed = DISK_SPEED
        self.return_speed = DISK_SPEED * RETURN_SPEED_MULTIPLIER
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
            
            if self.distance_traveled >= DISK_DISTANCE:
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
            outline_color = DISK_OUTLINE_COLOR if not self.is_enemy else ENEMY_DISK_OUTLINE_COLOR
            trail_color = (*outline_color, int(alpha))
            pygame.draw.circle(trail_surface, trail_color, 
                             (trail_radius, trail_radius), trail_radius)
            screen.blit(trail_surface, (pos[0] - trail_radius, pos[1] - trail_radius))
        
        draw_rotating_disk(self.x, self.y, self.radius, self.rotation_angle, self.is_enemy)

class Shield:
    def __init__(self, player):
        self.player = player
        self.distance_from_player = 40
        self.angle = 0
        self.radius = SHIELD_RADIUS
        self.active = False
        
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
        
    def draw(self):
        if self.active:
            x, y = self.get_position()
            pygame.draw.circle(screen, SHIELD_COLOR, (int(x), int(y)), self.radius)
            pygame.draw.circle(screen, SHIELD_OUTLINE_COLOR, (int(x), int(y)), self.radius, OUTLINE_WIDTH)

class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - 50), random.randint(0, HEIGHT - 50), 50, 50)
        while self.rect.colliderect(forbidden_rect):
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        self.health = 100
        self.speed = 3
        self.has_disk = True
        self.last_shot_time = 0
        self.shoot_delay = 2000
        self.active = False

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

def main():
    clock = pygame.time.Clock()
    player = Player()
    enemy = Enemy()
    player_disks = []
    enemy_disks = []
    shield = Shield(player)
    running = True
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    while running:
        screen.fill(BLACK)
        draw_grid()
        draw_forbidden_area()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if player.has_disk and not any(d.flying or d.returning for d in player_disks):
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        angle = math.atan2(mouse_y - player.rect.centery, mouse_x - player.rect.centerx)
                        player_disks.append(Disk(player.rect.centerx, player.rect.centery, angle, is_enemy=False))
                        player.has_disk = False
                
                elif event.button == 3:
                    shield.active = True
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    shield.active = False

        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        player.move(dx, dy)

        if keys[pygame.K_q]:
            enemy.active = True

        shield.update(pygame.mouse.get_pos())
        player_position = (player.rect.centerx, player.rect.centery)
        enemy_position = (enemy.rect.centerx, enemy.rect.centery)
        
        current_time = pygame.time.get_ticks()
        shoot_angle = enemy.update_ai(player_position, current_time)
        if shoot_angle is not None:
            enemy_disks.append(Disk(enemy.rect.centerx, enemy.rect.centery, shoot_angle, is_enemy=True))
            enemy.has_disk = False

        for disk in player_disks[:]:
            disk_returned = disk.move(player_position)
            
            if disk.get_rect().colliderect(enemy.rect) and not disk.is_enemy and enemy.active:
                if shield.active and shield.get_rect().colliderect(disk.get_rect()):
                    disk.start_returning(player_position)
                else:
                    enemy.health -= 25
                    disk.start_returning(player_position)
                    if enemy.health <= 0:
                        running = False
            
            if disk_returned:
                player_disks.remove(disk)
                player.has_disk = True

        for disk in enemy_disks[:]:
            disk_returned = disk.move(enemy_position)
            
            if disk.get_rect().colliderect(player.rect) and disk.is_enemy and enemy.active:
                if shield.active and shield.get_rect().colliderect(disk.get_rect()):
                    disk.start_returning(enemy_position)
                else:
                    player.health -= 25
                    disk.start_returning(enemy_position)
                    if player.health <= 0:
                        running = False
            
            if disk_returned:
                enemy_disks.remove(disk)
                enemy.has_disk = True

        player.draw()
        if enemy.active:
            enemy.draw()
        
        for disk in player_disks:
            disk.draw()
        for disk in enemy_disks:
            disk.draw()
        
        if shield.active:
            shield.draw()

        player_health_text = font.render(f'Health: {player.health}', True, WHITE)
        screen.blit(player_health_text, (10, 10))
        
        if enemy.active:
            enemy_health_text = font.render(f'Enemy Health: {enemy.health}', True, WHITE)
            screen.blit(enemy_health_text, (10, 50))
        
        q_text = small_font.render('Q - Activate Enemy', True, WHITE)
        q_rect = q_text.get_rect()
        q_rect.topright = (WIDTH - 10, 10)
        screen.blit(q_text, q_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
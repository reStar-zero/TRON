import pygame
import random
import math

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
PLAYER_COLOR = (0, 128, 255)
DISK_COLOR = (255, 0, 0)
ENEMY_COLOR = (0, 255, 0)
DISK_DISTANCE = 200  
DISK_SPEED = 5  

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRON")
icon = pygame.image.load('images\icon.png')
pygame.display.set_icon(icon)


class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 50, 50)
        self.speed = 5

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

class Disk:
    def __init__(self, x, y, angle):
        self.initial_position = (x, y)  
        self.rect = pygame.Rect(x, y, 10, 10)
        self.speed = DISK_SPEED
        self.angle = angle
        self.distance_traveled = 0
        self.flying = True

    def move(self):
        if self.flying:
            self.rect.x += self.speed * math.cos(self.angle)
            self.rect.y += self.speed * math.sin(self.angle)
            self.distance_traveled += self.speed
            
            if self.distance_traveled >= DISK_DISTANCE:
                self.flying = False
        else:
            if self.rect.x < self.initial_position[0]:
                self.rect.x += self.speed
            elif self.rect.x > self.initial_position[0]:
                self.rect.x -= self.speed
            if self.rect.y < self.initial_position[1]:
                self.rect.y += self.speed
            elif self.rect.y > self.initial_position[1]:
                self.rect.y -= self.speed

            if self.rect.topleft == self.initial_position:
                return True  
        return False  

class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - 50), random.randint(0, HEIGHT - 50), 50, 50)
        self.health = 100

def main():
    clock = pygame.time.Clock()
    player = Player()
    disks = []
    enemies = [Enemy() for _ in range(5)]
    running = True

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  
                if not any(d.flying for d in disks):  
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                
                    angle = math.atan2(mouse_y - player.rect.centery, mouse_x - player.rect.centerx)
                    disks.append(Disk(player.rect.centerx - 5, player.rect.centery - 5, angle))  

        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        player.move(dx, dy)

        for disk in disks[:]:
            if disk.move():  
                disks.remove(disk)

            for enemy in enemies[:]:
                if disk.rect.colliderect(enemy.rect):
                    enemy.health -= 50
                    disks.remove(disk)
                    if enemy.health <= 0:
                        enemies.remove(enemy)

        pygame.draw.rect(screen, PLAYER_COLOR, player.rect)

        for disk in disks:
            pygame.draw.rect(screen, DISK_COLOR, disk.rect)

        for enemy in enemies:
            pygame.draw.rect(screen, ENEMY_COLOR, enemy.rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

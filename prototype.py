import os
import sys
import random
import pygame

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED = 3
SPAWN_EVENT = pygame.USEREVENT + 1

# Weapon upgrade thresholds
UPGRADE_KILLS = [0, 5, 15]

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = (60, SCREEN_HEIGHT // 2)
        self.kill_count = 0
        self.weapon_level = 0

    def update(self, pressed):
        if pressed[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
        if pressed[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def shoot(self, bullets):
        if self.weapon_level == 0:
            bullets.add(Bullet(self.rect.midright))
        elif self.weapon_level == 1:
            bullets.add(Bullet((self.rect.right, self.rect.top)))
            bullets.add(Bullet((self.rect.right, self.rect.bottom)))
        else:
            bullets.add(Bullet((self.rect.right, self.rect.centery - 10), (-1, -0.2)))
            bullets.add(Bullet(self.rect.midright))
            bullets.add(Bullet((self.rect.right, self.rect.centery + 10), (-1, 0.2)))

    def add_kill(self):
        self.kill_count += 1
        if self.weapon_level < len(UPGRADE_KILLS) - 1:
            if self.kill_count >= UPGRADE_KILLS[self.weapon_level + 1]:
                self.weapon_level += 1

class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, direction=(1, 0)):
        super().__init__()
        self.image = pygame.Surface((10, 4))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=position)
        self.dx = direction[0] * BULLET_SPEED
        self.dy = direction[1] * BULLET_SPEED

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.randint(20, 40)
        self.image = pygame.Surface((size, size))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.left = SCREEN_WIDTH + random.randint(0, 100)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - size)

    def update(self):
        self.rect.x -= ENEMY_SPEED
        if self.rect.right < 0:
            self.kill()

def main(max_frames=None):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    player = Player()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)

    pygame.time.set_timer(SPAWN_EVENT, 1000)
    frame = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == SPAWN_EVENT:
                enemy = Enemy()
                enemies.add(enemy)
                all_sprites.add(enemy)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.shoot(bullets)
                all_sprites.add(*bullets)

        pressed = pygame.key.get_pressed()
        player.update(pressed)
        bullets.update()
        enemies.update()

        # Collisions
        for enemy in pygame.sprite.groupcollide(enemies, bullets, True, True):
            player.add_kill()
        if pygame.sprite.spritecollide(player, enemies, False):
            running = False

        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)

        frame += 1
        if max_frames is not None and frame >= max_frames:
            running = False

    pygame.quit()

if __name__ == "__main__":
    test_mode = "--test" in sys.argv
    max_frames = 10 if test_mode else None
    if os.environ.get("SDL_VIDEODRIVER") == "dummy" and not test_mode:
        max_frames = 10
    main(max_frames)

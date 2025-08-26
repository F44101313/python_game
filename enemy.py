import pygame
import json
from config import RED, GREEN, BOSS_HP
from enemy_bullet import EnemyBullet
import os

# 讀取路徑
def load_path(level):
    path_file = f"path{level}.json"
    if not os.path.exists(path_file):
        return []
    data = json.load(open(path_file, "r", encoding="utf-8"))
    pts = [pygame.Vector2(x, y) for x, y in data.get("points", [])]
    return pts

REACH_RADIUS = 16  # 接近路徑點的半徑

class Enemy(pygame.sprite.Sprite):
    def __init__(self, hp=20, speed=80, type_index=0, castle=None, path=[]):
        super().__init__()
        self.hp = hp
        self.max_hp = hp
        self.base_speed = float(speed)
        self.speed_factor = 1.0
        self._effect_end = 0
        self.type_index = type_index
        self.castle = castle
        self._last_swing = 0
        self._last_shot = 0
        self.siege_interval = 700
        self.contact_damage = 5

        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.path = path
        self.path_index = 0
        if path:
            self.pos = path[0].copy()
            self.rect.center = (int(self.pos.x), int(self.pos.y))
        else:
            self.pos = pygame.Vector2(0,0)

        self.phase = "path" if path else "to_castle"

    def current_speed(self):
        return self.base_speed * max(0.0, self.speed_factor)

    def update(self, castle, dt, enemy_bullets=None):
        now = pygame.time.get_ticks()
        if self._effect_end and now > self._effect_end:
            self.speed_factor = 1.0
            self._effect_end = 0

        if self.phase == "path":
            self._follow_path(dt)
        elif self.phase == "to_castle":
            self._move_towards_castle(castle, dt)
        else:
            self._do_siege(castle)

        # 遠程射擊小兵 3,6,9
        if self.type_index in [2,5,8] and enemy_bullets and castle:
            if now - self._last_shot >= 1200:
                self._last_shot = now
                dx, dy = castle.rect.centerx - self.pos.x, castle.rect.centery - self.pos.y
                bullet = EnemyBullet(self.pos.x, self.pos.y, (dx, dy), speed=4, damage=3)
                enemy_bullets.add(bullet)

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def _follow_path(self, dt):
        if self.path_index >= len(self.path):
            self.phase = "to_castle"
            return
        target = self.path[self.path_index]
        vec = target - self.pos
        dist = vec.length()
        if dist <= REACH_RADIUS:
            self.path_index += 1
            if self.path_index >= len(self.path):
                self.phase = "to_castle"
            return
        if dist != 0:
            self.pos += vec.normalize() * (self.current_speed() * dt)

    def _move_towards_castle(self, castle, dt):
        if not castle:
            return
        c = pygame.Vector2(castle.rect.centerx, castle.rect.centery)
        vec = c - self.pos
        if vec.length() != 0 and self.current_speed() > 0:
            self.pos += vec.normalize() * (self.current_speed() * dt)
        if self.rect.colliderect(castle.rect):
            self.phase = "siege"

    def _do_siege(self, castle):
        if not castle:
            return
        now = pygame.time.get_ticks()
        if now - self._last_swing >= self.siege_interval:
            self._last_swing = now
            castle.take_damage(self.contact_damage)

    def draw_hp(self, surface):
        pygame.draw.rect(surface, RED, (self.rect.left, self.rect.top-8, self.rect.width, 5))
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, GREEN, (self.rect.left, self.rect.top-8, self.rect.width*ratio, 5))


class Boss(Enemy):
    def __init__(self, hp=BOSS_HP, speed=55, path=[]):
        super().__init__(hp=hp, speed=speed, type_index=0, path=path)
        self.image = pygame.Surface((150,150), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.siege_interval = 500
        self.contact_damage = 10

    def draw_hp(self, surface):
        pygame.draw.rect(surface, RED, (self.rect.left, self.rect.top-20, self.rect.width, 12))
        ratio = max(0, self.hp/self.max_hp)
        pygame.draw.rect(surface, GREEN, (self.rect.left, self.rect.top-20, self.rect.width*ratio, 12))

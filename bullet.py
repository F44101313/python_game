# bullet.py
import pygame
from config import WHITE

BULLET_OUT_W = 600
BULLET_OUT_H = 800

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=10, damage=5, pierce=0):
        super().__init__()

        # 外觀：保留你原本的白色長方形
        self.image = pygame.Surface((6, 12))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))

        # 浮點座標（防止逐幀捨入誤差）
        self.fx = float(x)
        self.fy = float(y)

        # 方向 → 單位化 → 乘速度（與瞄準線一致）
        dx, dy = direction
        length2 = dx*dx + dy*dy
        if length2 != 0:
            inv = (length2) ** -0.5
            dx *= inv
            dy *= inv
        self.vx = dx * float(speed)
        self.vy = dy * float(speed)

        # 保留舊欄位（給 view.py 用）
        self.speedx = self.vx
        self.speedy = self.vy

        self.damage = int(damage)
        self.pierce_left = int(pierce)
        self._hit_ids = set()

    def update(self):
        # 用浮點移動，呈現時再 round 成整數
        self.fx += self.vx
        self.fy += self.vy
        self.rect.centerx = int(round(self.fx))
        self.rect.centery = int(round(self.fy))

        # 出界移除
        if (self.rect.right < 0 or self.rect.left > BULLET_OUT_W or
            self.rect.bottom < 0 or self.rect.top > BULLET_OUT_H):
            self.kill()

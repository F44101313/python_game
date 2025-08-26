import pygame #player.py
import math
from bullet import Bullet
from config import (
    GREEN,
    BULLET_BASE_SPEED, BULLET_BASE_DAMAGE,
    UPGRADE_COST, UPGRADE_SPEED_INC, UPGRADE_DAMAGE_INC
)

PLAYER_IMG = pygame.image.load("Image/tower/tower0.png")
PLAYER_IMG = pygame.transform.scale(PLAYER_IMG, (40, 40))

class Player(pygame.sprite.Sprite):
    """
    固定式炮塔
    controls: (left_key, right_key)
    angle：以「向上」為 90 度；限制在 [min_angle, max_angle]
    """
    shared_money = 0  # 全體共用金錢

    def __init__(self, x, y, controls, initial_angle, min_angle, max_angle):
        super().__init__()
        self.base_image = PLAYER_IMG.copy()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

        # 操作按鍵
        self.controls = controls
        self.angle = initial_angle
        self.min_angle = min_angle
        self.max_angle = max_angle

        # 射擊屬性
        self.shoot_delay = 400
        self.last_shot = pygame.time.get_ticks()
        self.bullet_speed = BULLET_BASE_SPEED
        self.bullet_damage = BULLET_BASE_DAMAGE

        self.turn_speed_deg = 180
        self.barrel_len = 46
        self.barrel_color = (80, 200, 120)

        self._flash_timer_ms = 0
        self._flash_max_ms = 60

        self.level = 1
        self.max_level = 5

        # 升級冷卻
        self._last_upgrade = 0
        self.upgrade_cooldown_ms = 1000  # 1 秒

        self.sfx_buy = pygame.mixer.Sound("sound/sound_effect/buy.ogg")
        self.sfx_power_volume = 0.02
        self.sfx_buy.set_volume(self.sfx_power_volume)

    def upgrade(self):
        now = pygame.time.get_ticks()
        if now - self._last_upgrade < self.upgrade_cooldown_ms:
            return  # 冷卻中，不升級

        if self.level >= self.max_level:
            print("已達最高等級")
            return

        if Player.shared_money >= UPGRADE_COST:
            Player.shared_money -= UPGRADE_COST
            self.bullet_speed += UPGRADE_SPEED_INC
            self.bullet_damage += UPGRADE_DAMAGE_INC
            self.sfx_buy.play()
            self.level += 1
            self._last_upgrade = now
        else:
            print("金錢不足，無法升級")

    def update(self, bullets, all_sprites, dt):
        keys = pygame.key.get_pressed()

        delta_deg = self.turn_speed_deg * dt * 0.2
        if keys[self.controls[0]]:
            self.angle += delta_deg
        if keys[self.controls[1]]:
            self.angle -= delta_deg

        self.angle = max(self.min_angle, min(self.max_angle, self.angle))

        # 自動射擊
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            pos, dirv = self.muzzle_pos()
            bullet = Bullet(pos.x, pos.y, (dirv.x, dirv.y),
                            speed=self.bullet_speed,
                            damage=self.bullet_damage)
            bullets.add(bullet)
            all_sprites.add(bullet)
            self._flash_timer_ms = self._flash_max_ms

        if self._flash_timer_ms > 0:
            self._flash_timer_ms = max(0, self._flash_timer_ms - int(dt * 1000))

    def muzzle_pos(self):
        base = pygame.Vector2(self.rect.centerx, self.rect.centery)
        rad = math.radians(self.angle)
        dirv = pygame.Vector2(math.cos(rad), -math.sin(rad))
        muzzle = base + dirv * self.barrel_len
        return muzzle, dirv

    def draw_overlay(self, surface):
        base = pygame.Vector2(self.rect.centerx, self.rect.centery)
        muzzle, dirv = self.muzzle_pos()
        tail = base + dirv * 12

        # 炮管
        pygame.draw.line(surface, self.barrel_color, tail, muzzle, 6)

        # 瞄準線
        aim_layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        end = muzzle + dirv * 420
        pygame.draw.line(aim_layer, (255, 255, 200, 120), muzzle, end, 1)
        pygame.draw.circle(aim_layer, (255, 255, 200, 160), (int(end.x), int(end.y)), 3)
        surface.blit(aim_layer, (0, 0))

        # 火光
        if self._flash_timer_ms > 0:
            p1 = muzzle
            p2 = muzzle + dirv.rotate(28) * 12
            p3 = muzzle + dirv.rotate(-28) * 12
            pygame.draw.polygon(surface, (255, 240, 120), (p1, p2, p3))

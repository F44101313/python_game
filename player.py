import pygame
import math
from bullet import Bullet
from config import (
    BULLET_BASE_SPEED, BULLET_BASE_DAMAGE,
    UPGRADE_DAMAGE_INC, UPGRADE_SPEED_INC
)

PLAYER_IMG = pygame.image.load("Image/tower/tower0.png")
PLAYER_IMG = pygame.transform.scale(PLAYER_IMG, (40, 40))

COST_DMG0, COST_RATE0, COST_PIERCE0 = 50, 60, 70
COST_INC = 20               # 每升一次、下一次加多少錢
FIRERATE_MIN_MS = 140       # 射速升級的最小間隔(避免0)

class Player(pygame.sprite.Sprite):
    shared_money = 0  # 共用金錢

    def __init__(self, x, y, controls, initial_angle, min_angle, max_angle):
        super().__init__()
        self.base_image = PLAYER_IMG.copy()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

        # 操作
        self.controls = controls
        self.angle = initial_angle
        self.min_angle = min_angle
        self.max_angle = max_angle

        # ======== 三路等級與費用 ========
        self.lv_damage   = 1
        self.lv_firerate = 1
        self.lv_pierce   = 1
        self.cost_damage   = COST_DMG0
        self.cost_firerate = COST_RATE0
        self.cost_pierce   = COST_PIERCE0

        # ======== 屬性 ========
        self.bullet_speed  = BULLET_BASE_SPEED
        self.bullet_damage = BULLET_BASE_DAMAGE
        self.pierce        = 0               # 會被升級「貫穿」設定
        self.shoot_delay   = 400             # 毫秒，會被升級「射速」下降
        self.last_shot     = pygame.time.get_ticks()

        self.turn_speed_deg = 180
        self.barrel_len     = 46
        self.barrel_color   = (80, 200, 120)

        self._flash_timer_ms = 0
        self._flash_max_ms   = 60

        # 原本的一般等級（不影響三路顯示，你保留用）
        self.level     = 1
        self.max_level = 5

        # 音效
        self.sfx_buy = pygame.mixer.Sound("sound/sound_effect/buy.ogg")
        self.sfx_buy.set_volume(0.02)

    # ---------- 計算總等級 ----------
    @property
    def total_level(self):
        return self.lv_damage + self.lv_firerate + self.lv_pierce -2

    # ---------- 三路升級 ----------
    def _can_pay(self, cost: int) -> bool:
        return Player.shared_money >= cost

    def upgrade_damage(self):
        cost = self.cost_damage
        if not self._can_pay(cost): return False
        Player.shared_money -= cost
        self.lv_damage += 1
        self.bullet_damage += UPGRADE_DAMAGE_INC
        self.cost_damage += COST_INC
        self.sfx_buy.play()
        return True

    def upgrade_firerate(self):
        cost = self.cost_firerate
        if not self._can_pay(cost): return False
        Player.shared_money -= cost
        self.lv_firerate += 1
        self.shoot_delay = max(FIRERATE_MIN_MS, self.shoot_delay - 60)  # 每級快一點
        self.cost_firerate += COST_INC
        self.sfx_buy.play()
        return True

    def upgrade_pierce(self):
        cost = self.cost_pierce
        if not self._can_pay(cost): return False
        Player.shared_money -= cost
        self.lv_pierce += 1
        self.pierce = max(self.pierce, self.lv_pierce - 1)   # Lv1=0, Lv2=1, Lv3=2...
        self.cost_pierce += COST_INC
        self.sfx_buy.play()
        return True

    # ---------- 舊的一鍵升級(保留) ----------
    def upgrade(self):
        if not self._can_pay(50): return
        Player.shared_money -= 50
        self.bullet_speed += UPGRADE_SPEED_INC
        self.bullet_damage += UPGRADE_DAMAGE_INC
        self.level = min(self.max_level, self.level + 1)
        self.sfx_buy.play()

    # ---------- 更新與開火 ----------
    def update(self, bullets, all_sprites, dt):
        keys = pygame.key.get_pressed()
        delta_deg = self.turn_speed_deg * dt * 0.2
        if keys[self.controls[0]]: self.angle += delta_deg
        if keys[self.controls[1]]: self.angle -= delta_deg
        self.angle = max(self.min_angle, min(self.max_angle, self.angle))

        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            pos, dirv = self.muzzle_pos()
            bullet = Bullet(
                pos.x, pos.y, (dirv.x, dirv.y),
                speed=self.bullet_speed,
                damage=self.bullet_damage,
                pierce=self.pierce
            )
            bullets.add(bullet); all_sprites.add(bullet)
            self._flash_timer_ms = self._flash_max_ms

        if self._flash_timer_ms > 0:
            self._flash_timer_ms = max(0, self._flash_timer_ms - int(dt * 1000))

    def muzzle_pos(self):
        base = pygame.Vector2(self.rect.centerx, self.rect.centery)
        rad = math.radians(self.angle)
        dirv = pygame.Vector2(math.cos(rad), -math.sin(rad))
        if dirv.length_squared() != 0:
            dirv = dirv.normalize()  # 單位化，避免任何微小誤差
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

import pygame
from config import WHITE, WIDTH

# 每關城堡圖片，請確保 Image/castle/ 下有 castle0.png, castle1.png, castle2.png
CASTLE_IMGS = [
    pygame.image.load("Image/castle/熱蘭遮城(荷蘭).png"),
    pygame.image.load("Image/castle/台南孔廟(明鄭).png"),
    pygame.image.load("Image/castle/台南州廳(日治).png"),
]
CASTLE_IMGS = [pygame.transform.scale(img, (200, 200)) for img in CASTLE_IMGS]

class Castle(pygame.sprite.Sprite):
    def __init__(self, level=1, hp=100):
        super().__init__()
        # 關卡對應圖片，level 從 1 開始
        self.image = CASTLE_IMGS[level-1].copy()
        self.rect = self.image.get_rect()
        self.max_hp = hp
        self.hp = hp

        # 預設位置置中頂端
        self.rect.topleft = (WIDTH // 2 - self.rect.width // 2, 0)

    def take_damage(self, dmg):
        """扣血並夾到 0 以上"""
        self.hp = max(0, self.hp - int(dmg))

    def is_destroyed(self):
        """判斷城堡是否被摧毀"""
        return self.hp <= 0

    def draw(self, surface, font):
        """畫城堡血條與數值"""
        # 血條尺寸與位置
        bar_width = 160
        bar_height = 15
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top + 20
        fill = int(bar_width * self.hp / self.max_hp)

        # 背景紅條
        pygame.draw.rect(surface, (255,0,0), (x, y, bar_width, bar_height))
        # 綠色血量條
        pygame.draw.rect(surface, (0,255,0), (x, y, fill, bar_height))

        # 顯示 HP 數字
        hp_text = font.render(f"{self.hp}/{self.max_hp}", True, BLACK)
        surface.blit(hp_text, (self.rect.centerx - hp_text.get_width()//2, y - 20))

    def is_destroyed(self):
        return self.hp <= 0

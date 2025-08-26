# upgrade_ui.py
import pygame
from config import WIDTH, HEIGHT, WHITE, YELLOW, ui_price_font, ui_lv_font, ui_name_font

CARD_NAMES = ["傷 害", "速 度", "貫 穿"]

class UpgradePanel:
    def __init__(self, *, side: str, key_left, key_right, key_buy, font=None, small_font=None):
        self.side = side
        self.key_left = key_left
        self.key_right = key_right
        self.key_buy = key_buy

        # 你調好的版面
        self.card_w, self.card_h = 50, 80
        self.gap = 12
        self.panel_bottom_gap = 45
        self.margin_side = 16

        self.name_y_in = 8
        self.price_y_in = -28
        self.lv_y_in = -17

        self.f_name  = ui_name_font
        self.f_price = ui_price_font
        self.f_lv    = ui_lv_font

        sheet = pygame.image.load("Image/ui/iconn.png").convert_alpha()
        W, H = sheet.get_size()
        raw_w, raw_h = W // 3, H
        self.cards = [pygame.transform.smoothscale(
            sheet.subsurface((raw_w * i, 0, raw_w, raw_h)), (self.card_w, self.card_h)
        ) for i in range(3)]

        self.total_w = self.card_w * 3 + self.gap * 2
        self.base_y = HEIGHT - self.card_h - self.panel_bottom_gap
        self.base_x = (self.margin_side if self.side == "left"
                       else WIDTH - self.total_w - self.margin_side)

        self.sel = 0
        self.levels = [1, 1, 1]
        self.costs  = [50, 60, 70]  # 會被 set_costs 覆蓋

        self.cooldown_ms = 160
        self._next_switch = 0

    def set_levels(self, lv_damage, lv_firerate, lv_pierce):
        self.levels = [lv_damage, lv_firerate, lv_pierce]

    def set_costs(self, cost_damage, cost_firerate, cost_pierce):
        self.costs = [cost_damage, cost_firerate, cost_pierce]

    def handle_key(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.key_left:  return "left"
            if event.key == self.key_right: return "right"
            if event.key == self.key_buy:   return "buy"
        return None

    def switch_sel(self, direction: int):
        now = pygame.time.get_ticks()
        if now < self._next_switch: return
        self.sel = (self.sel + direction) % 3
        self._next_switch = now + self.cooldown_ms

    # 是否購買在 Game 內呼叫 Player 的升級，這裡不再扣錢
    def try_buy(self, *args, **kwargs):
        return False  # 交給 Game / Player

    def draw(self, surface, money: int):
        x, y = self.base_x, self.base_y
        for i in range(3):
            surface.blit(self.cards[i], (x, y))

            # 名稱
            name_surf = self.f_name.render(CARD_NAMES[i], True, WHITE)
            surface.blit(name_surf, (x + (self.card_w - name_surf.get_width()) // 2, y + self.name_y_in))

            # 價格
            price_surf = self.f_price.render(f"${self.costs[i]}", True, YELLOW)
            surface.blit(price_surf, (x + (self.card_w - price_surf.get_width()) // 2, y + self.card_h + self.price_y_in))

            # 等級
            lv_surf = self.f_lv.render(f"Lv.{self.levels[i]}", True, WHITE)
            surface.blit(lv_surf, (x + (self.card_w - lv_surf.get_width()) // 2, y + self.card_h + self.lv_y_in))

            x += self.card_w + self.gap

        sel_x = self.base_x + self.sel * (self.card_w + self.gap)
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(sel_x - 2, y - 2, self.card_w + 4, self.card_h + 4), 2)

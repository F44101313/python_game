# view.py
import pygame
import json
import os
from config import WIDTH, HEIGHT, WHITE, font, title_font, YELLOW, title_font_small

# ================== 背景載入 ==================
def load_bg(path):
    img = pygame.image.load(path)  # 不要 convert()，避免 import 時還沒 set_mode
    return pygame.transform.scale(img, (WIDTH, HEIGHT))

# 主選單 / 劇情 / 教學背景
MENU_BG     = load_bg("Image/background/主畫面.png")
STORY_BG    = load_bg("Image/background/主畫面.png")
TUTORIAL_BG = load_bg("Image/background/主畫面.png")

# 關卡背景（依 level 使用）
LEVEL_BGS = [
    load_bg("Image/background/level1_bg.png"),
    load_bg("Image/background/level2_bg.png"),
    load_bg("Image/background/level3_bg.png"),
]

# ================== 城堡 / Boss / 敵人 ==================
CASTLE_IMGS = [
    pygame.image.load("Image/castle/熱蘭遮城(荷蘭).png"),
    pygame.image.load("Image/castle/台南孔廟(明鄭).png"),
    pygame.image.load("Image/castle/台南州廳(日治).png"),
]
CASTLE_IMGS = [pygame.transform.scale(img, (200, 200)) for img in CASTLE_IMGS]
CASTLE_POS = (WIDTH // 2 - 100, 50)

BOSS_IMGS = [
    pygame.image.load("Image/boss/BOSS(荷蘭).png"),
    pygame.image.load("Image/boss/BOSS(明鄭).png"),
    pygame.image.load("Image/boss/BOSS(日治).png"),
]
BOSS_IMGS = [pygame.transform.scale(img, (200, 200)) for img in BOSS_IMGS]

ENEMY_IMGS = [
    pygame.image.load(f"Image/enemy/enemys{i}-{j}.png") for i in range(1, 4) for j in range(1, 4)
]
ENEMY_IMGS = [pygame.transform.scale(img, (60, 70)) for img in ENEMY_IMGS]

# ================== 工具 ==================
def render_chinese_text_surface(text, font, color, spacing=0):
    chars = list(text)
    images = [font.render(ch, True, color) for ch in chars]
    total_width = sum(img.get_width() for img in images) + spacing * (len(images) - 1)
    height = max(img.get_height() for img in images)
    surface = pygame.Surface((total_width, height), pygame.SRCALPHA)
    x = 0
    for img in images:
        surface.blit(img, (x, 0))
        x += img.get_width() + spacing
    return surface

# ================== 路徑繪製 ==================
def draw_path_polyline(screen, level=1):
    path_file = os.path.join("path", f"path{level}.json")
    if not os.path.exists(path_file):
        return
    try:
        data = json.load(open(path_file,"r",encoding="utf-8"))
        pts = [pygame.Vector2(x, y) for x, y in data.get("points", [])]
    except Exception:
        return
    if len(pts) < 2:
        return

    import math
    road_width   = 26
    border_width = road_width + 6
    road_color   = (230, 210, 150)
    border_color = (205, 185, 130)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    def draw_capsule(surf, color, p0, p1, width):
        v = pygame.Vector2(p1) - pygame.Vector2(p0)
        L = v.length()
        if L == 0:
            pygame.draw.circle(surf, color, (int(p0.x), int(p0.y)), width//2)
            return
        ang = math.degrees(math.atan2(v.y, v.x))
        rect = pygame.Surface((L, width), pygame.SRCALPHA)
        pygame.draw.rect(rect, color, (0, 0, L, width))
        pygame.draw.circle(rect, color, (0, width//2), width//2)
        pygame.draw.circle(rect, color, (int(L), width//2), width//2)
        rect = pygame.transform.rotate(rect, -ang)
        surf.blit(rect, rect.get_rect(center=((p0.x+p1.x)/2, (p0.y+p1.y)/2)))

    for a, b in zip(pts[:-1], pts[1:]):
        draw_capsule(overlay, border_color, a, b, border_width)
    for a, b in zip(pts[:-1], pts[1:]):
        draw_capsule(overlay, road_color, a, b, road_width)

    try:
        pygame.draw.aalines(overlay, (240, 230, 180), False, pts, blend=1)
    except:
        pass

    overlay.set_alpha(200)
    screen.blit(overlay, (0, 0))

def draw_button(screen, rect, text, font, text_color=WHITE, hover_color=YELLOW, bg_color=(100, 100, 100)):
    mouse_pos = pygame.mouse.get_pos()
    render_color = hover_color if rect.collidepoint(mouse_pos) else text_color
    pygame.draw.rect(screen, bg_color, rect, border_radius=8)
    text_surface = font.render(text, True, render_color)
    screen.blit(text_surface, (rect.centerx - text_surface.get_width() // 2,
                               rect.centery - text_surface.get_height() // 2))

# ================== 畫面 ==================
def draw_menu(screen):
    screen.blit(MENU_BG, (0, 0))
    title = render_chinese_text_surface("《時空城防：台南異象》", title_font, WHITE, spacing=4)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))

    start_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 50)
    howto_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    draw_button(screen, start_rect, "START", font)
    draw_button(screen, howto_rect, "How to Play", font)

    return {"start": start_rect, "howto": howto_rect}

def draw_end_screen(screen, win=True, level=1, final_level=3):
    screen.blit(MENU_BG, (0, 0))
    if win:
        if level < final_level:
            msg = "VICTORY!"
            prompt = "Press SPACE to next level"
        else:
            msg = "THE WORLD IS SAVED !!!"
            prompt = "Press SPACE to title"
    else:
        msg = "LOSE!"
        prompt = "Press SPACE to continue."

    text = font.render(msg, True, WHITE)
    prompt_text = font.render(prompt, True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 10))

def draw_story(screen, top=160, side_margin=72, line_spacing=46, letter_spacing=2, align="center", nudge_x=0):
    screen.blit(STORY_BG, (0, 0))

    lines = [
        "在不久的未來，台南古城因為神秘的能量波動",
        "而陷入了時間的混亂。",
        "不同時期的時空裂縫逐一開啟，讓來自荷蘭時期、明鄭時期",
        "等各種歷史階段的敵人穿越而來，意圖佔領古城。",
        "玩家將化身為守護者，肩負起保衛古城的使命，",
        "利用手中的力量抵禦一波波入侵。",
        "隨著戰鬥推進，玩家不僅要擊退敵人，還能逐步解鎖",
        "不同時代的故事片段，體驗守護台南歷史文化的榮耀與挑戰。",
    ]

    # 做出每行 surface，好計寬高
    surfaces = [render_chinese_text_surface(line, font, WHITE, spacing=letter_spacing) for line in lines]
    text_w  = max(s.get_width() for s in surfaces)
    text_h  = sum(s.get_height() for s in surfaces) + (len(surfaces)-1) * (line_spacing - surfaces[0].get_height())

    # 文字區塊左上角：置中 or 靠左；可用 nudge_x 微調左右偏移
    x0 = (WIDTH - text_w)//2 if align == "center" else side_margin
    x0 += nudge_x
    y0 = top

    # 半透明底盒（讓字更清楚）
    pad = 10
    box = pygame.Surface((text_w + pad*2, text_h + pad*2), pygame.SRCALPHA)
    pygame.draw.rect(box, (0, 0, 0, 90), box.get_rect(), border_radius=10)
    screen.blit(box, (x0 - pad, y0 - pad))

    # 標題也置中（相對整個畫面居中，再加同樣 nudge_x）
    title = title_font_small.render("STORY", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2 + nudge_x, y0 - 62))

    # 每行都置中到同一塊（寬度 text_w），自然是一行一行的置中
    y = y0
    for s in surfaces:
        x = x0 + (text_w - s.get_width())//2 if align == "center" else x0
        screen.blit(s, (x, y))
        y += line_spacing

    # GO 按鈕放在文字塊正下方，也跟著 nudge_x
    go_rect = pygame.Rect(WIDTH//2 - 60 + nudge_x, y + 20, 120, 40)
    draw_button(screen, go_rect, "GO!!!", font)
    return {"go": go_rect}

def draw_tutorial(screen):
    screen.blit(TUTORIAL_BG, (0, 0))
    start_y = HEIGHT // 4
    line_spacing = 30
    side_margin = 40
    lines = [
        "P1：",
        "UP、DOWN：調整守護塔射擊方向",
        "M：升級武器(更高傷害 + 更快速度)",
        " ",
        "P2：",
        "W、S：調整守護塔射擊方向",
        "E：升級武器(更高傷害 + 更快速度)",
        " ",
        "射擊來襲擊古城的敵人",
        "並最後擊殺boss即獲勝"
    ]
    for i, line in enumerate(lines):
        text_surface = render_chinese_text_surface(line, font, WHITE, spacing=4)
        screen.blit(text_surface, (side_margin, start_y + i * line_spacing))

    ok_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 100, 120, 40)
    draw_button(screen, ok_rect, "OK", font)
    return {"ok": ok_rect}

def draw_game_screen(screen, all_sprites, enemies, castle, boss, money,
                     show_path=True, level=1, enemy_bullets=None):
    # 依關卡套背景
    bg = LEVEL_BGS[min(level-1,len(LEVEL_BGS)-1)]
    screen.blit(bg, (0,0))
    if show_path:
        draw_path_polyline(screen, level=level)
    # 城堡
    castle_img = CASTLE_IMGS[level - 1] if level - 1 < len(CASTLE_IMGS) else CASTLE_IMGS[0]
    screen.blit(castle_img, CASTLE_POS)
    castle.rect.topleft = CASTLE_POS
    castle.draw(screen, font)

    # 敵人
    for enemy in enemies:
        img = ENEMY_IMGS[getattr(enemy, "type_index", 0)]
        enemy_rect = img.get_rect(center=enemy.rect.center)
        screen.blit(img, enemy_rect)
        if hasattr(enemy, "draw_hp"):
            enemy.draw_hp(screen)

    # Boss
    if boss and boss.alive():
        boss_img = BOSS_IMGS[min(level - 1, len(BOSS_IMGS) - 1)]
        boss_rect = boss_img.get_rect(center=boss.rect.center)
        screen.blit(boss_img, boss_rect)
        if hasattr(boss, "draw_hp"):
            boss.draw_hp(screen)

    # 玩家
    all_sprites.draw(screen)
    for spr in all_sprites:
        if hasattr(spr, "draw_overlay"):
            spr.draw_overlay(screen)

    # 敵人子彈
    if enemy_bullets:
        for b in enemy_bullets:
            pygame.draw.rect(screen, (255, 0, 0), b.rect)
            pygame.draw.line(
                screen, (255, 100, 100),
                (b.rect.centerx, b.rect.centery),
                (b.rect.centerx - b.speedx * 2, b.rect.centery - b.speedy * 2), 2
            )

    # 金錢 / 關卡
    money_text = font.render(f"Money: {money}", True, WHITE)
    screen.blit(money_text, (10, 10))
    level_text = font.render(f"Level {level}", True, WHITE)
    screen.blit(level_text, (10, HEIGHT - 30))

    screen.blit(money_text, (10, 10))
    level_text = font.render(f"Level {level}", True, WHITE)
    screen.blit(level_text, (10, HEIGHT - 30))

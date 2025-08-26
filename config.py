import pygame #config.py

# --- 視窗設定 ---
WIDTH, HEIGHT = 600, 800

# --- 顏色 ---
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# --- 遊戲參數 ---
PLAYER_SPEED = 5
BULLET_SPEED = -10
ENEMY_SPEED = 2
BOSS_HP = 100
CASTLE_HP = 1000

# 字型
pygame.font.init()
font = pygame.font.Font("Font/BoutiqueBitmap9x9_Bold_1.9.ttf", 18)
# 新增大字體給標題
title_font = pygame.font.Font("Font/BoutiqueBitmap9x9_Bold_1.9.ttf", 48)  # 48 可依需求調整大小
title_font_small = pygame.font.Font("Font/BoutiqueBitmap9x9_Bold_1.9.ttf", 30)  # 48 可依需求調整大小
#
ui_price_font = pygame.font.Font("Font/BoutiqueBitmap9x9_Bold_1.9.ttf", 9)
ui_lv_font    = pygame.font.Font("Font/BoutiqueBitmap9x9_Bold_1.9.ttf", 9)
ui_name_font  = pygame.font.Font("Font/BoutiqueBitmap9x9_Bold_1.9.ttf", 10)

# --- 金錢與升級 ---
ENEMY_REWARD = {10:5, 20:10, 30:15, 40:20, 50:25, 60:30, 70:35, 80:40, 90:45, 100:50}
BULLET_BASE_SPEED = 7
BULLET_BASE_DAMAGE = 5
UPGRADE_COST = 50
UPGRADE_SPEED_INC = 2
UPGRADE_DAMAGE_INC = 2

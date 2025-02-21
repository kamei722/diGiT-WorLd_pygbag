# # enemy.py

# import pygame
# import math
# from game.game_utils import SCREEN_WIDTH, SCREEN_HEIGHT

# class Enemy:
#     def __init__(self, x, y, speed, color=(255, 0, 0), width=20, height=20):
#         self.x = x
#         self.y = y
#         self.width = width
#         self.height = height
#         self.speed = speed
#         self.direction = -1  # 左方向
#         self.active = True

#         # 単色の矩形を使用
#         self.color = color
#         self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
#         print(f"[DEBUG] Enemy created at ({self.x}, {self.y}) with color {self.color} and size ({self.width}, {self.height})")

#     def get_rect(self):
#         return self.rect

#     def update(self, dt):
#         self.x += self.speed * self.direction * dt
#         self.rect.x = int(self.x)
#         # 画面外に出たら非アクティブに設定
#         if self.x + self.width < 0 or self.x > SCREEN_WIDTH:
#             self.active = False
#             print(f"[DEBUG] Enemy at ({self.x}, {self.y}) moved out of screen and is now inactive.")

#     def draw(self, screen):
#         pygame.draw.rect(screen, self.color, self.rect)
#         # デバッグ用: 敵が描画されていることを確認
#         # print(f"[DEBUG] Enemy drawn at ({self.x}, {self.y}) with size ({self.width}, {self.height}) and color {self.color}")

# class BasicEnemy(Enemy):
#     def __init__(self, x, y, speed, direction="left", color=(255, 0, 0), width=20, height=20):
#         super().__init__(x, y, speed, color, width, height)
#         self.direction = -1 if direction == "left" else 1
#         print(f"[DEBUG] Initialized BasicEnemy at ({self.x}, {self.y}) with direction {self.direction} and size ({self.width}, {self.height})")

# class PatrolEnemy(Enemy):
#     def __init__(self, x, y, speed, patrol_range, color=(255, 0, 0), width=30, height=30):
#         super().__init__(x, y, speed, color, width, height)
#         self.start_x = x
#         self.patrol_range = patrol_range
#         self.direction = 1
#         print(f"[DEBUG] Initialized PatrolEnemy at ({self.x}, {self.y}) with patrol range {self.patrol_range} and size ({self.width}, {self.height})")

#     def update(self, dt):
#         self.x += self.speed * self.direction * dt
#         self.rect.x = int(self.x)
#         if self.x > self.start_x + self.patrol_range:
#             self.direction = -1
#             print(f"[DEBUG] PatrolEnemy at ({self.x}, {self.y}) changed direction to left")
#         elif self.x < self.start_x:
#             self.direction = 1
#             print(f"[DEBUG] PatrolEnemy at ({self.x}, {self.y}) changed direction to right")

# class SineWaveEnemy(Enemy):
#     def __init__(self, x, y, speed, amplitude, frequency, color=(255, 0, 0), width=25, height=25):
#         super().__init__(x, y, speed, color, width, height)
#         self.start_y = y
#         self.amplitude = amplitude
#         self.frequency = frequency
#         self.time = 0.0
#         print(f"[DEBUG] Initialized SineWaveEnemy at ({self.x}, {self.y}) with amplitude {self.amplitude}, frequency {self.frequency}, and size ({self.width}, {self.height})")

#     def update(self, dt):
#         count = 1
#         self.time += dt
#         self.x += self.speed * self.direction * dt
#         self.y = self.start_y + self.amplitude * math.sin(2 * math.pi * self.frequency * self.time)
#         self.rect.x = int(self.x)
#         self.rect.y = int(self.y)

#         if count % 100 == 0:
#             print(f"[DEBUG] SineWaveEnemy moved to ({self.x}, {self.y})")

#         count += 1

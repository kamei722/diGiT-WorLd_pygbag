# item.py

import pygame
import os
import time
from ..game_utils import KEY_SIZE,resource_path

class BaseItem:
    def __init__(self, x, y, duration=None):
        self.x = x
        self.y = y
        self.collected = False
        self.spawn_time = None
        self.duration = 2.0 if duration is None else duration

    def update(self, dt):
        pass

    def get_rect(self):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError

    def on_collect(self, player, stage_manager=None):
        self.collected = True

class Key(BaseItem):
    # BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "pics")
    # KEY_IMAGE = pygame.image.load(os.path.join(BASE_DIR, "key.png"))

    KEY_IMAGE = pygame.image.load(resource_path("assets/pics/key.png"))
    
    def __init__(self, x, y, duration=None, number=1):
        super().__init__(x, y, duration)
        self.number = number
        self.image = pygame.transform.scale(Key.KEY_IMAGE, (KEY_SIZE, KEY_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
    
    def get_rect(self):
        # この rect はワールド座標のまま返す
        return self.rect

    def draw(self, screen, cam_x=0, cam_y=0):
        if not self.collected:
            # オブジェクトの位置からカメラオフセットを引いた位置に描画
            screen.blit(self.image, (self.x - cam_x, self.y - cam_y))


    def update(self, dt):
        # アニメーション等があればここで実装
        pass

    def on_collect(self, player, stage_manager=None):
        super().on_collect(player, stage_manager)
        if stage_manager:
            stage_manager.increment_consecutive_keys()
        if stage_manager and stage_manager.sound_manager:
            stage_manager.sound_manager.play("pickup")
        #print(f"Key #{self.number} collected by player!")


class FinalKey(Key):
    """最終ステージ専用キー"""
    FIN_IMAGE = pygame.image.load(resource_path("assets/pics/fin.png"))
    #FIN_IMAGE = pygame.image.load(os.path.join(Key.BASE_DIR, "fin.png"))

    def __init__(self, x, y, duration=None, number=1):
        super().__init__(x, y, duration, number)
        self.image = pygame.transform.scale(FinalKey.FIN_IMAGE, (KEY_SIZE, KEY_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_collect(self, player, stage_manager=None):
        super().on_collect(player, stage_manager)
        if stage_manager:
            stage_manager.increment_consecutive_keys()
        # **音を鳴らさない**
        #print(f"Final Key #{self.number} collected by player!")


# class ClockItem:
#     def __init__(self, x, y, effect_type="speedup", duration=None):
#         super().__init__(x, y, duration)
#         self.width = 30
#         self.height = 30
#         self.color = (100, 200, 255)  # 水色
#         self.effect_type = effect_type

#     def get_rect(self):
#         return pygame.Rect(self.x, self.y, self.width, self.height)

#     def draw(self, screen):
#         if not self.collected:
#             pygame.draw.rect(
#                 screen,
#                 self.color,
#                 (self.x, self.y, self.width, self.height),
#                 border_radius=6
#             )

#     def update(self, dt):
#         pass  # StageManager が管理

#     def on_collect(self, player, stage_manager=None):
#         super().on_collect(player, stage_manager)
#         if stage_manager is not None:
#             if self.effect_type == "speedup":
#                 stage_manager.time_per_number *= 0.5
#             elif self.effect_type == "slowdown":
#                 stage_manager.time_per_number *= 1.5
#         print(f"ClockItem collected! Effect: {self.effect_type}")  # デバッグ用メッセージ

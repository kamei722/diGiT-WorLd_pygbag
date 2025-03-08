import pygame
import time
from ..game_utils import KEY_SIZE, resource_path

class BaseItem:
    def __init__(self, x, y, duration=None):
        self.x = x
        self.y = y
        self.collected = False
        self.spawn_time = None  # ブラウザ環境では pygame.time.get_ticks() で設定される
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
    # 静的画像の読み込みをクラス変数として一度だけ行う
    KEY_IMAGE = None
    
    def __init__(self, x, y, duration=None, number=1):
        super().__init__(x, y, duration)
        self.number = number
        
        # 画像の遅延読み込み（クラス変数として一度だけ読み込む）
        if Key.KEY_IMAGE is None:
            try:
                Key.KEY_IMAGE = pygame.image.load(resource_path("assets/pics/key.png"))
            except Exception as e:
                print(f"Failed to load key image: {e}")
                # 画像が読み込めない場合に備えたフォールバック
                Key.KEY_IMAGE = pygame.Surface((KEY_SIZE, KEY_SIZE))
                Key.KEY_IMAGE.fill((255, 255, 0))  # 黄色の四角形
        
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


class FinalKey(Key):
    """最終ステージ専用キー"""
    FIN_IMAGE = None

    def __init__(self, x, y, duration=None, number=1):
        super().__init__(x, y, duration, number)
        
        # 画像の遅延読み込み
        if FinalKey.FIN_IMAGE is None:
            try:
                FinalKey.FIN_IMAGE = pygame.image.load(resource_path("assets/pics/fin.png"))
            except Exception as e:
                print(f"Failed to load fin image: {e}")
                # 画像が読み込めない場合のフォールバック
                FinalKey.FIN_IMAGE = pygame.Surface((KEY_SIZE, KEY_SIZE))
                FinalKey.FIN_IMAGE.fill((0, 255, 255))  # シアン色の四角形
                
        self.image = pygame.transform.scale(FinalKey.FIN_IMAGE, (KEY_SIZE, KEY_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))

    def on_collect(self, player, stage_manager=None):
        super().on_collect(player, stage_manager)
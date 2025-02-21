# game/scenes/base_scene.py

import pygame
from ..game_utils import SCREEN_WIDTH, SCREEN_HEIGHT

class BaseScene:
    def __init__(self, screen, sound_manager):
        """
        シーンの初期化
        Args:
            screen: pygameのスクリーンオブジェクト
            sound_manager: サウンドマネージャーのインスタンス
        """
        self.screen = screen
        self.sound_manager = sound_manager
        self.next_scene = None
        self.is_running = True

    def update(self, dt):
        """
        シーンの状態を更新
        Args:
            dt: 前フレームからの経過時間
        """
        pass

    def draw(self):
        """
        シーンの描画処理
        """
        pass

    def handle_events(self, events):
        """
        イベント処理
        Args:
            events: pygameのイベントリスト
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.is_running = False
            self.process_event(event)

    def process_event(self, event):
        """
        個別のイベント処理（サブクラスでオーバーライド）
        Args:
            event: 処理するイベント
        """
        pass

    def cleanup(self):
        """
        シーン終了時のクリーンアップ処理
        """
        pass
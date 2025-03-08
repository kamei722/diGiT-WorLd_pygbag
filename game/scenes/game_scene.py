# game/scenes/game_scene.py
import pygame
import os
import re
import math
from game.game_utils import SCREEN_WIDTH, SCREEN_HEIGHT, FPS,FONT_PATH, STAGE_CLEAR_DISPLAY_TIME,resource_path
from .base_scene import BaseScene
from game.objects.player import Player
from game.managers.stagemanager import StageManager
from game.managers.progress_manager import ProgressManager

class KeyStreak:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = int(SCREEN_WIDTH * 0.025)
        self.gap = int(SCREEN_HEIGHT * 0.075)
        self.colors = {
            'active': (255, 255, 0),
            'inactive': (50, 50, 50)
        }
        
    def draw(self, screen, consecutive_keys,target_keys):
        for i in range(target_keys):
            color = self.colors['active'] if i < consecutive_keys else self.colors['inactive']
            pygame.draw.circle(screen, color, 
                            (self.x, self.y + i * self.gap), 
                            self.radius)

class SequenceProgress:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = int(SCREEN_WIDTH * 0.01)
        self.gap = int(SCREEN_WIDTH * 0.025)
        self.colors = {
            'active': (255, 140, 0),
            'inactive': (70, 70, 70)
        }
        
    def draw(self, screen, current_sequence, total_sequences):
        for i in range(total_sequences):
            color = self.colors['active'] if i < current_sequence else self.colors['inactive']
            pygame.draw.circle(screen, color, 
                            (self.x + i * self.gap, self.y), 
                            self.radius)

class GameScene(BaseScene):
    def __init__(self, screen, sound_manager, stage_file):
        super().__init__(screen, sound_manager)
        self.stage_file = stage_file
        self.game_state = "playing"
        self.clear_display_start = 0

        self.world = 1
        self.stage = 1
        
        # ステージ情報を早期に抽出
        match = re.search(r"stage(\d+)-(\d+)\.json", stage_file)
        if match:
            self.world = int(match.group(1))
            self.stage = int(match.group(2))

        # フォントの一括ロード
        self._load_fonts()
        
        # チュートリアル関連の初期化
        self.show_tutorial = False
        self.tutorial_text_surfs = []  # 事前レンダリング用
        
        # ステージ1-1のチュートリアル準備
        if self.world == 1 and self.stage == 1:
            self.show_tutorial = True
            self._prepare_tutorial()
        
        # ステージマネージャーの初期化
        self.stage_manager = StageManager(self.sound_manager)
        self.stage_manager.load_stage(self.stage_file)
        
        # プレイヤーと項目の初期化
        self.player = None
        self.items = []
        self.prev_space = False

        # UI要素の初期化
        self.key_streak = KeyStreak(
            int(SCREEN_WIDTH * 0.0625),
            int(SCREEN_HEIGHT * 0.1)
        )
        
        self.sequence_progress = SequenceProgress(
            int(SCREEN_WIDTH * 0.02),
            int(SCREEN_HEIGHT * 0.03)
        )
        
        # カメラの初期化
        self.use_scroll = False
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.initial_camera_set = False
        self.camera_accumulator = 0.0
        
        # 最終ステージの特別設定
        if self.world == 4 and self.stage == 3:
            self._setup_final_stage()
        
        # ゲームの初期化
        self._initialize_game()

    def _load_fonts(self):
        """すべてのフォントを初期化時にロード"""
        font_full_path = resource_path(FONT_PATH)
        
        try:
            # メインフォント
            self.font = pygame.font.Font(font_full_path, int(SCREEN_HEIGHT * 0.04))
            
            # 各目的別のフォントを一度に読み込み
            self.tutorial_font = pygame.font.Font(font_full_path, int(SCREEN_HEIGHT * 0.035))
            self.mission_font = pygame.font.Font(font_full_path, int(SCREEN_HEIGHT * 0.05))
            self.t_font = pygame.font.Font(font_full_path, int(SCREEN_HEIGHT * 0.03))
            self.clear_font = pygame.font.Font(font_full_path, int(SCREEN_HEIGHT * 0.15))
            self.peak_font = pygame.font.Font(font_full_path, int(SCREEN_HEIGHT * 0.1))
            self.game_clear_font = pygame.font.Font(font_full_path, int(SCREEN_HEIGHT * 0.2))
        except Exception as e:
            print(f"Failed to load font: {e}")
            # システムフォントへのフォールバック
            self.font = pygame.font.SysFont(None, int(SCREEN_HEIGHT * 0.04))
            self.tutorial_font = pygame.font.SysFont(None, int(SCREEN_HEIGHT * 0.035))
            self.mission_font = pygame.font.SysFont(None, int(SCREEN_HEIGHT * 0.05))
            self.t_font = pygame.font.SysFont(None, int(SCREEN_HEIGHT * 0.03))
            self.clear_font = pygame.font.SysFont(None, int(SCREEN_HEIGHT * 0.15))
            self.peak_font = pygame.font.SysFont(None, int(SCREEN_HEIGHT * 0.1))
            self.game_clear_font = pygame.font.SysFont(None, int(SCREEN_HEIGHT * 0.2))
        
    def _prepare_tutorial(self):
            """チュートリアルテキストを事前レンダリング"""
            # ミッションテキストを事前レンダリング
            self.mission_text = self.mission_font.render("カギをのがすな!!", True, (255, 255, 255))
            
            # チュートリアル行を事前レンダリング
            tutorial_lines = [
                "　　　　　　     W ↑ Space ",
                " A ← | S ↓ | D →",
                "Esc : 戻る"
            ]
            
            self.tutorial_text_surfs = []
            for line in tutorial_lines:
                surf = self.t_font.render(line, True, (255, 255, 255))
                self.tutorial_text_surfs.append(surf)
                
            # 鍵画像の読み込み
            try:
                self.key_image = pygame.image.load(resource_path("assets/pics/key.png")).convert_alpha()
            except Exception as e:
                print(f"Failed to load key image: {e}")
                self.key_image = None

                

    def _initialize_game(self):
        """ゲーム要素の初期化"""
        # プレイヤーの初期化
        player_start = self.stage_manager.stage_data.get("player_start", {"x": 400, "y": 50})
        self.player = Player(x=player_start["x"], y=player_start["y"], sound_manager=self.sound_manager)
        
        self.items = []
        
        # 初期ループのリセットとキーの出現
        self.stage_manager.reset()
        self.stage_manager.update(0, items=self.items, player=self.player)

    def _reset_game(self):
        """ゲームのリセット処理"""
        player_start = self.stage_manager.stage_data.get("player_start", {"x": 400, "y": 50})
        self.player.x = player_start["x"]
        self.player.y = player_start["y"]
        self.player.velocity_y = 0
        self.player.on_ground = False
        self.player.is_game_over = False
        self.player.coyote_timer = 0.0
        self.sound_manager.stop_music()

        if self.world == 4 and self.stage == 3:
            self.use_scroll = True
            #self.show_peak_message = True
            self.sound_manager.play_music("stage_4-3.ogg") 
            #self.peak_message_start_time = pygame.time.get_ticks()
            target_cam_x = self.player.x + self.player.width / 2 - SCREEN_WIDTH / 2
            target_cam_y = self.player.y + self.player.height / 2 - SCREEN_HEIGHT / 2
            self.camera_offset_x = target_cam_x
            self.camera_offset_y = target_cam_y
            self.initial_camera_set = True
        
        self.stage_manager.new_game_reset()
        self.items.clear()            
        self.stage_manager.update(0, self.items, self.player)


    def update(self, dt):
        """ゲームの状態更新"""

        # --- ステージクリア状態のチェック ---
        if self.stage_manager.is_stage_clear:
            if self.game_state != "stage_clear":
                self.game_state = "stage_clear"
                self.clear_display_start = pygame.time.get_ticks()
                self.sound_manager.play("stage_clear")

                if self.stage_manager.final_stage and self.world == 4 and self.stage == 3:
                    self.sound_manager.stop_music()
                    self.sound_manager.play("game_clear")
                else:
                    self.sound_manager.play("stage_clear")

                import re
                match = re.search(r'stage(\d+)-(\d+)\.json', self.stage_file)
                if match:
                    world = int(match.group(1))
                    stage = int(match.group(2))
                    progress_manager = ProgressManager()
                    progress_manager.clear_stage(world, stage)
            if pygame.time.get_ticks() - self.clear_display_start >= STAGE_CLEAR_DISPLAY_TIME:
                import re
                match = re.search(r'stage(\d+)-(\d+)\.json', self.stage_file)
                if match:
                    world = int(match.group(1))
                    stage = int(match.group(2))
                    from .stage_select_scene import StageSelectScene
                    self.next_scene = StageSelectScene(self.screen, self.sound_manager, world, stage)
            return

        # --- ゲームオーバーチェック ---
        if self.player.is_game_over:
            self._reset_game()
            self.sound_manager.play("hit")
            return

        # --- 入力処理 ---
        keys = pygame.key.get_pressed()
        current_space = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        space_pressed_this_frame = (current_space and not self.prev_space)
        self.prev_space = current_space

        # ステージ、Digit, プレイヤーの更新
        self.stage_manager.update(dt, self.items, self.player)
        for digit in self.stage_manager.digits:
            digit.update(dt)
        self.player.update(
            dt,
            keys,
            self.stage_manager.digits,
            space_pressed_this_frame,
            items=self.items,
            stage_manager=self.stage_manager
        )
        self.items = [item for item in self.items if not item.collected]

        # 最終ステージカメラオフセット更新
        if self.use_scroll:
            fixed_dt = 1.0 / 60.0  # 固定時間ステップ
            self.camera_accumulator += dt

            target_cam_x = self.player.x + self.player.width / 2 - SCREEN_WIDTH / 2
            target_cam_y = self.player.y + self.player.height / 2 - SCREEN_HEIGHT / 2
            
            # 初回のカメラセット
            while self.camera_accumulator >= fixed_dt:
                if not self.initial_camera_set:
                    self.camera_offset_x = target_cam_x
                    self.camera_offset_y = target_cam_y
                    self.initial_camera_set = True
                else:
                    smoothing = 0.1
                    self.camera_offset_x = (1 - smoothing) * self.camera_offset_x + smoothing * target_cam_x
                    self.camera_offset_y = (1 - smoothing) * self.camera_offset_y + smoothing * target_cam_y

                self.camera_accumulator -= fixed_dt

        
    def draw(self):
        """ゲーム画面の描画"""
        self.screen.fill((0, 0, 0))

        # ゲームオブジェクトの描画
        for digit in self.stage_manager.digits:
            digit.draw(self.screen, self.camera_offset_x, self.camera_offset_y)
        for item in self.items:
            item.draw(self.screen, self.camera_offset_x, self.camera_offset_y)
        self.player.draw(self.screen, self.camera_offset_x, self.camera_offset_y)
        for enemy in self.stage_manager.active_enemies:
            enemy.draw(self.screen, self.camera_offset_x, self.camera_offset_y)

        # 最終ステージのメッセージ表示または通常のUI表示
        if (self.world == 4 and self.stage == 3) and self.show_peak_message:
            self._draw_peak_message()
        else:
            # キーストリークとシーケンス進行状況の描画
            self.key_streak.draw(self.screen, self.stage_manager.consecutive_keys, self.stage_manager.target_keys)
            self.sequence_progress.draw(
                self.screen,
                self.stage_manager.current_sequence_index,
                self.stage_manager.total_sequences
            )

        # ステージクリア表示
        if self.game_state == "stage_clear":
            self._draw_stage_clear()

        # チュートリアル表示
        if self.show_tutorial:
            self._draw_tutorial()

    def _draw_tutorial(self):
        """事前レンダリングされたチュートリアルテキストを描画"""
        top_margin_x = int(SCREEN_WIDTH * 0.05)
        top_margin_y = int(SCREEN_HEIGHT * 0.05)

        # ミッションテキスト描画（右寄せ）
        mission_x = (SCREEN_WIDTH - top_margin_x) - self.mission_text.get_width()
        mission_y = top_margin_y
        self.screen.blit(self.mission_text, (mission_x, mission_y))

        # チュートリアル指示の描画
        bottom_margin_x = int(SCREEN_WIDTH * 0.05)
        bottom_margin_y = int(SCREEN_HEIGHT * 0.05)

        # 全テキストサーフェスの合計高さを計算
        total_height = sum(surf.get_height() for surf in self.tutorial_text_surfs) + 6 * (len(self.tutorial_text_surfs) - 1)
        start_y = SCREEN_HEIGHT - bottom_margin_y - total_height

        # 各事前レンダリング行を描画
        ty = start_y
        for surf in self.tutorial_text_surfs:
            # 右寄せテキスト
            tx = (SCREEN_WIDTH - bottom_margin_x) - surf.get_width()
            self.screen.blit(surf, (tx, ty))
            ty += surf.get_height() + 6


    def process_event(self, event):
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._reset_game()
            elif event.key == pygame.K_ESCAPE:
                # ステージ選択画面に戻る（現在のワールドとステージ情報を渡す）
                match = re.search(r'stage(\d+)-(\d+)\.json', self.stage_file)
                if match:
                    world = int(match.group(1))
                    stage = int(match.group(2))
                    from .stage_select_scene import StageSelectScene
                    self.next_scene = StageSelectScene(self.screen, self.sound_manager, world, stage)
            elif event.key == pygame.K_v:
                self.sound_manager.toggle_sound()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.player.set_debug_mode(not self.player.debug_mode)

    def cleanup(self):
        """シーン終了時の処理"""
        if self.stage_manager.final_stage:
            self.sound_manager.stop_music()

    def _draw_peak_message(self):
        """最終ステージのピークメッセージ描画"""
        if not self.show_peak_message:
            return

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.peak_message_start_time
        display_duration = 5000  # 5秒間表示

        if elapsed < display_duration:
            # 事前レンダリングされたピークメッセージを使用
            text_rect = self.peak_message.get_rect(
                center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.1))
            )
            self.screen.blit(self.peak_message, text_rect)
    
    def _setup_final_stage(self):
        """最終ステージ（4-3）の設定"""
        self.use_scroll = True
        self.show_peak_message = True
        self.sound_manager.play_music("stage_4-3.ogg") 
        self.peak_message_start_time = pygame.time.get_ticks()
        # ピークメッセージを事前レンダリング
        self.peak_message = self.peak_font.render("頂点を目指せ！！", True, (255, 255, 0))

    def _draw_stage_clear(self):
        """ステージクリアまたはゲームクリアメッセージの描画"""
        # ゲームクリア表示（最終ステージの場合）
        if self.stage_manager.final_stage and self.world == 4 and self.stage == 3:
            current_time = pygame.time.get_ticks()
            shake_offset = math.sin(current_time * 0.005) * 10

            # 事前にロードしたゲームクリアフォントを使用
            clear_text = self.game_clear_font.render("Game Cleared!", True, (255, 80, 80))
            clear_rect = clear_text.get_rect(center=(SCREEN_WIDTH // 2 + shake_offset, SCREEN_HEIGHT // 2 + shake_offset))
            shadow_text = self.game_clear_font.render("Game Cleared!", True, (100, 0, 0))
            shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 8 + shake_offset, SCREEN_HEIGHT // 2 + 8 + shake_offset))
            
            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(clear_text, clear_rect)
        else:
            # 通常のステージクリア表示
            clear_text = self.clear_font.render("Stage Cleared!", True, (200, 200, 0))
            
            offset = math.sin(pygame.time.get_ticks() * 0.005) * 10
            clear_rect = clear_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + offset))
            shadow_text = self.clear_font.render("Stage Cleared!", True, (100, 100, 0))
            shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 4, SCREEN_HEIGHT // 2 + 4 + offset))
            
            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(clear_text, clear_rect)      
        

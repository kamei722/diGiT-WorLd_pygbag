import pygame
import os
import re
import math
from game.game_utils import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH,resource_path
from .base_scene import BaseScene
from game.managers.progress_manager import ProgressManager
from config.keys import MOVE_LEFT_KEYS, MOVE_RIGHT_KEYS, MOVE_UP_KEYS, MOVE_DOWN_KEYS

class StageSelectScene(BaseScene):
    def __init__(self, screen, sound_manager, current_world=1, current_stage=1):
        super().__init__(screen, sound_manager)

        base_w = 1078.0
        base_h = 768.0
        scale_w = SCREEN_WIDTH / base_w
        scale_h = SCREEN_HEIGHT / base_h

        btn_x = int(20 * scale_w)
        btn_y = int(20 * scale_h)
        btn_w = int(140 * scale_w)
        btn_h = int( 50 * scale_h)
        self.sound_toggle_button = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        
        # キーリピート設定 (delay=200ms, interval=50ms)
        pygame.key.set_repeat(200, 50)
        
        # ProgressManager の初期化
        self.progress_manager = ProgressManager()
        
        # ステージ選択状態の管理
        self.worlds = 5
        self.stages_per_world = 3 
        
        # ステージレイアウトの計算
        total_stages = self.stages_per_world
        desired_padding_ratio = 0.15
        side_margin_ratio = 0.08 
        
        self.side_margin = int(SCREEN_WIDTH * side_margin_ratio)
        usable_width = SCREEN_WIDTH - 2 * self.side_margin
        base_unit = usable_width / (total_stages + (total_stages - 1) * desired_padding_ratio)
        self.stage_size = int(base_unit)
        self.stage_padding = int(base_unit * desired_padding_ratio)
        
        # UI領域の定義
        self.title_area_height = int(SCREEN_HEIGHT * 0.25)
        self.stage_area_margin = int(SCREEN_HEIGHT * 0.25)
        
        # フォント設定
        self.title_font = pygame.font.Font(FONT_PATH, int(SCREEN_HEIGHT * 0.13))
        self.stage_font = pygame.font.Font(FONT_PATH, int(self.stage_size * 0.45))
        self.guide_font = pygame.font.Font(FONT_PATH, int(SCREEN_HEIGHT * 0.05))
        self.sound_font = pygame.font.Font(FONT_PATH, int(SCREEN_HEIGHT * 0.03))
        
        # 選択状態の初期化
        self.selected_world = current_world
        self.selected_stage = current_stage
        self._adjust_selection()

        # ステージデータのパス生成
        # 例: "../stage/stage1-1.json"
        #self.stage_path = os.path.join(os.path.dirname(__file__), "..", "..", "stage", "stage{}-{}.json")
        self.stage_path = os.path.join(resource_path("stage"), "stage{}-{}.json")

        self.stage_titles = {
            (1, 1): "にこにこ",
            (1, 2): "カウントダウン",
            (1, 3): "円周率は体で覚える",
            (2, 1): "いざ! ２の段!!",
            (2, 2): "掛け算スクエア",
            (2, 3): "倍倍バイバイ",
            (3, 1): "数の素は丈夫",
            (3, 2): "ぎこちない笑顔",
            (3, 3): "インド式スクエア",
            (4, 1): "3・2・1 発射!",
            (4, 2): "リアルカウントダウン",
            (4, 3): "数の頂へ",
            (5, 1): "Thank You!!"
        }

        # ロックの表示
        lock_image_path = os.path.join(resource_path("assets/pics"), "lock.png")
        self.lock_image = pygame.image.load(lock_image_path).convert_alpha()

        original_size = self.lock_image.get_size()
        new_width = int(original_size[0] * scale_w)
        new_height = int(original_size[1] * scale_h)
        self.lock_image = pygame.transform.scale(self.lock_image, (new_width, new_height))

        # すりぬけの注意書き
        if (self.selected_world == 3 and self.selected_stage in [1, 2, 3]) \
            or (self.selected_world == 4 and self.selected_stage == 1):

            warning_font = pygame.font.Font(FONT_PATH, int(SCREEN_HEIGHT * 0.05))
            warning_surf = warning_font.render("すりぬけ禁止", True, (255, 100, 100))  # 薄めの赤
            warning_rect = warning_surf.get_rect(
                left=SCREEN_WIDTH * 0.1,
                top=self.title_area_height + 10
            )
            self.screen.blit(warning_surf, warning_rect)
        
        btn_x = int(20 * scale_w)
        btn_y = int(20 * scale_h)
        btn_w = int(140 * scale_w)
        btn_h = int( 50 * scale_h)
        self.sound_toggle_button = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        self.last_select_time = 0

        self.password_buffer = ""
        self.secret_code = "LOGIC"
        self.ex_world_unlocked = False 

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill((0, 0, 0))
        
        # タイトル
        title = self.stage_titles.get((self.selected_world, self.selected_stage), "No Title")
        selected_title_surf = self.title_font.render(title, True, (255, 255, 255))
        title_rect = selected_title_surf.get_rect(center=(SCREEN_WIDTH // 2, int(self.title_area_height * 0.7)))
        self.screen.blit(selected_title_surf, title_rect)

        if (self.selected_world == 3 and self.selected_stage in [1, 2, 3])\
            or (self.selected_world == 4 and self.selected_stage == 1):
            warning_font = pygame.font.Font(FONT_PATH, int(SCREEN_HEIGHT * 0.05))
            warning_surf = warning_font.render("すりぬけ禁止", True, (255, 100, 100))
            warning_rect = warning_surf.get_rect(
                left=SCREEN_WIDTH * 0.1,
                top=self.title_area_height + 10
            )
            self.screen.blit(warning_surf, warning_rect)

        if self.selected_world == 5:
            self._draw_world5()
        else:
            self._draw_normal_world()

        if self.sound_manager.sound_on:
            toggle_text = "Sound: ON"
            button_color = (50, 200, 50)
        else:
            toggle_text = "Sound: OFF"
            button_color = (200, 50, 50)
        pygame.draw.rect(self.screen, button_color, self.sound_toggle_button)
        toggle_surf = self.sound_font.render(toggle_text, True, (255, 255, 255))
        toggle_rect = toggle_surf.get_rect(center=self.sound_toggle_button.center)
        self.screen.blit(toggle_surf, toggle_rect)

        back_text = self.guide_font.render("← Esc", True, (200, 200, 200))
        back_rect = back_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        self.screen.blit(back_text, back_rect)

    def _draw_world5(self):
        """エンディング用のワールド5を1ステージだけステージだけ特殊な描画処理"""
        stage = 1
        is_unlocked = self.progress_manager.is_stage_unlocked(5, stage)

        stage_box_width = self.stage_size
        stage_box_height = self.stage_size
        x = (SCREEN_WIDTH // 2) - (stage_box_width // 2)
        y = (SCREEN_HEIGHT // 2) - (stage_box_height // 2) + 50

        if is_unlocked:
            color = (255, 255, 0) if self.selected_stage == stage else (255, 255, 255)
        else:
            color = (128, 128, 128)
        
        pygame.draw.rect(self.screen, color, (x, y, stage_box_width, stage_box_height), 2)

        stage_text = self.stage_font.render(f"5-{stage}", True, color)
        text_rect = stage_text.get_rect(center=(x + stage_box_width // 2, y + stage_box_height // 2))
        self.screen.blit(stage_text, text_rect)

        # ロックされているなら錠前を重ねる
        if not is_unlocked:
            lock_rect = self.lock_image.get_rect(center=(x + stage_box_width // 2, y + stage_box_height // 2))
            self.screen.blit(self.lock_image, lock_rect)


    def _draw_normal_world(self):
        """通常ワールドの描画"""
        stage_area_start_y = self.title_area_height + self.stage_area_margin
        for stage in range(1, self.stages_per_world + 1):
            x = self.side_margin + (self.stage_size + self.stage_padding) * (stage - 1)
            y = stage_area_start_y

            is_unlocked = self.progress_manager.is_stage_unlocked(self.selected_world, stage)

            if is_unlocked:
                color = (255, 255, 0) if stage == self.selected_stage else (255, 255, 255)
            else:
                color = (128, 128, 128)
            
            pygame.draw.rect(self.screen, color, (x, y, self.stage_size, self.stage_size), 2)
            stage_text = self.stage_font.render(f"{self.selected_world}-{stage}", True, color)
            text_rect = stage_text.get_rect(center=(x + self.stage_size // 2, y + self.stage_size // 2))
            self.screen.blit(stage_text, text_rect)

            if not is_unlocked:
                lock_rect = self.lock_image.get_rect(center=(x + self.stage_size // 2, y + self.stage_size // 2))
                lock_rect.y += 10
                self.screen.blit(self.lock_image, lock_rect)

        # ヒント矢印を描画(↑world n)
        if self.selected_world > 1 and self.progress_manager.progress["unlocked_stages"].get(str(self.selected_world - 1), []):
            hint_text_up = self.guide_font.render("↑ World " + str(self.selected_world - 1), True, (255, 255, 255))
            self.screen.blit(hint_text_up, (SCREEN_WIDTH - 200, self.title_area_height + 40))
        if self.selected_world < 4 and self.progress_manager.progress["unlocked_stages"].get(str(self.selected_world + 1), []):
            hint_text_down = self.guide_font.render("↓ World " + str(self.selected_world + 1), True, (255, 255, 255))
            self.screen.blit(hint_text_down, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80))

    def _start_stage(self, world, stage):
        stage_file = self.stage_path.format(world, stage)
        if os.path.exists(stage_file):
            from .game_scene import GameScene
            self.next_scene = GameScene(self.screen, self.sound_manager, stage_file)
        else:
            print(f"Stage file not found: {stage_file}")

    def _adjust_selection(self):
        """
        一番最初に解放されているステージへ移動する。
        """
        unlocked = self.progress_manager.progress["unlocked_stages"].get(str(self.selected_world), [])
        if unlocked:
            unlocked = sorted(int(s) for s in unlocked)
            if self.selected_stage not in unlocked:
                self.selected_stage = unlocked[0]
        else:
            self.selected_stage = 1

    def process_event(self, event):
        """
        ステージ選択を制御しつつ、5回のアルファベット/数字入力が行われるたびに判定し、
        失敗の場合は unmove を鳴らすサンプル。
        """
        #パスワード処理　(没)
        if event.type == pygame.KEYDOWN:
            # # 1) 入力された文字を取得 (大文字に統一)
            # char = event.unicode.upper()
        
            # # 英数字のみをバッファに追加
            # if char.isalnum():
            #     # 1) 追加
            #     self.password_buffer += char
                
            #     # 2) デバッグ出力: 現在のバッファを表示
            #     print(f"[DEBUG] Current buffer: {self.password_buffer}")
                
            #     # 3) 5文字に達したら判定
            #     if len(self.password_buffer) == 5:
            #         if self.password_buffer == self.secret_code:
            #             # 成功 → EXワールド解放
            #             if self.sound_manager:
            #                 self.sound_manager.play("ex_open")
            #             for stage_num in range(1, 5):
            #                 self.progress_manager.unlock_stage(4, stage_num)
            #             print("EX world unlocked by password LOGIC!")
            #         else:
            #             # 失敗 → unmove
            #             if self.sound_manager:
            #                 self.sound_manager.play("unmove")

            #         # 判定後バッファリセット
            #         self.password_buffer = ""
                
            # 左移動
            if event.key in MOVE_LEFT_KEYS:
                unlocked = sorted(self.progress_manager.progress["unlocked_stages"].get(str(self.selected_world), []))
                if self.selected_stage in unlocked:
                    idx = unlocked.index(self.selected_stage)
                else:
                    idx = 0
                if idx > 0:
                    self.selected_stage = unlocked[idx - 1]
                    if self.sound_manager:
                        self.sound_manager.play("select")
                else:
                    if self.sound_manager:
                        self.sound_manager.play("unmove")

            # 右移動
            elif event.key in MOVE_RIGHT_KEYS:
                unlocked = sorted(self.progress_manager.progress["unlocked_stages"].get(str(self.selected_world), []))
                if self.selected_stage in unlocked:
                    idx = unlocked.index(self.selected_stage)
                else:
                    idx = 0
                if idx < len(unlocked) - 1:
                    self.selected_stage = unlocked[idx + 1]
                    if self.sound_manager:
                        self.sound_manager.play("select")
                else:
                    if self.sound_manager:
                        self.sound_manager.play("unmove")

            # 上移動 (ワールド切替)
            elif event.key in MOVE_UP_KEYS:
                if self.selected_world == 1:
                    if self.sound_manager:
                        self.sound_manager.play("unmove")
                else:
                    new_world = max(1, self.selected_world - 1)
                    if self.progress_manager.progress["unlocked_stages"].get(str(new_world), []):
                        self.selected_world = new_world
                        unlocked = sorted(self.progress_manager.progress["unlocked_stages"].get(str(new_world), []))
                        self.selected_stage = unlocked[0] if unlocked else 1
                        if self.sound_manager:
                            self.sound_manager.play("select")
                    else:
                        if self.sound_manager:
                            self.sound_manager.play("unmove")

            # 下移動 (ワールド切替)
            elif event.key in MOVE_DOWN_KEYS:
                new_world = min(self.worlds, self.selected_world + 1)
                if self.progress_manager.progress["unlocked_stages"].get(str(new_world), []):
                    self.selected_world = new_world
                    unlocked = sorted(self.progress_manager.progress["unlocked_stages"].get(str(new_world), []))
                    self.selected_stage = unlocked[0] if unlocked else 1
                    if self.sound_manager:
                        self.sound_manager.play("select")
                else:
                    if self.sound_manager:
                        self.sound_manager.play("unmove")

            # タイトル画面へ戻る
            elif event.key == pygame.K_ESCAPE:
                from .title_scene import TitleScene
                self.next_scene = TitleScene(self.screen, self.sound_manager)

            elif event.key == pygame.K_v:
                self.sound_manager.toggle_sound()

            # ステージ開始
            elif event.key == pygame.K_RETURN:
                if self.progress_manager.is_stage_unlocked(self.selected_world, self.selected_stage):
                    if self.sound_manager:
                        self.sound_manager.play("stage_in")
                    self._start_stage(self.selected_world, self.selected_stage)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # サウンドトグルボタン
            if self.sound_toggle_button.collidepoint(event.pos):
                if self.sound_manager:
                    self.sound_manager.toggle_sound()


    # def _unlock_ex_world(self):
    #     # 例: world=4 が Exステージ
    #     # 4-1,4-2,4-3,4-4 を全解放する
    #     for stage_num in range(1, 5):
    #         self.progress_manager.unlock_stage(4, stage_num)

    #     # もしサウンドを流すなら
    #     if self.sound_manager:
    #         self.sound_manager.play("select")  # あるいは "stage_in" 等
            
        # print("[DEBUG] EX World (world=4) unlocked via password!")

# game/scenes/title_scene.py

import pygame
import os
import math
import random
from datetime import datetime
from game.game_utils import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH,resource_path
from .base_scene import BaseScene
from game.objects.digit import Digit
from game.objects.player import Player
from game.objects.item import Key

class TitleScene(BaseScene):
    def __init__(self, screen, sound_manager):
        super().__init__(screen, sound_manager)
        
        # 1078x768 を基準としたスケーリング
        base_w = 1078.0
        base_h = 768.0
        scale_w = SCREEN_WIDTH / base_w
        scale_h = SCREEN_HEIGHT / base_h

        # タイトルテキスト表示用 Digit
        self.title_line1 = "DIGIT"
        self.title_line2 = "WORLD"

        self.title_digit_width  = int(125 * scale_w)
        self.title_digit_height = int(250 * scale_h)
        self.title_spacing      = int( 30 * scale_w)
        self.title_line_gap     = int( 20 * scale_h)
        
        # 1行目: "DIGIT"
        total_width_line1 = len(self.title_line1) * self.title_digit_width \
                            + (len(self.title_line1) - 1) * self.title_spacing
        start_x_line1 = (SCREEN_WIDTH - total_width_line1) // 2
        line1_y = int(SCREEN_HEIGHT * 0.25)
        self.title1_digits = []
        for i, ch in enumerate(self.title_line1):
            x = start_x_line1 + i * (self.title_digit_width + self.title_spacing)
            y = line1_y
            d = Digit(x, y, self.title_digit_width, self.title_digit_height, number=ch)
            self.title1_digits.append(d)
        
        # 2行目: "WORLD"
        total_width_line2 = len(self.title_line2) * self.title_digit_width \
                            + (len(self.title_line2) - 1) * self.title_spacing
        start_x_line2 = (SCREEN_WIDTH - total_width_line2) // 2
        line2_y = line1_y + self.title_digit_height + self.title_line_gap
        self.title2_digits = []
        for i, ch in enumerate(self.title_line2):
            x = start_x_line2 + i * (self.title_digit_width + self.title_spacing)
            y = line2_y
            d = Digit(x, y, self.title_digit_width, self.title_digit_height, number=ch)
            self.title2_digits.append(d)
        
        # T,W用の調整
        t_x_offset = int(44 * scale_w)
        t_y_offset = int(-10 * scale_h)

        w_x_offset = int(44 * scale_w)
        w_y_offset = int(10 * scale_h)
        self.overlay_config_top = {
            'T': {
                'overlay_char': 'I',
                'x_offset': t_x_offset,
                'y_offset': t_y_offset
            }
        }
        self.overlay_config_bottom = {
            'W': {
                'overlay_char': 'I',
                'x_offset': w_x_offset,
                'y_offset': w_y_offset
            }
        }
        
        # 時計表示用 (右上): HH:MM
        clock_digit_width  = int( 90 * scale_w)
        clock_digit_height = int(150 * scale_h)
        clock_spacing      = int(  5 * scale_w)
        clock_time_gap     = int( 20 * scale_w)
        total_clock_width = 4 * clock_digit_width + 3 * clock_spacing + clock_time_gap

        clock_start_x = SCREEN_WIDTH - total_clock_width - int(20 * scale_w)
        clock_y = int(20 * scale_h)
        
        self.clock_digits = []
        for i in range(4):
            if i >= 2:
                x = clock_start_x + i * (clock_digit_width + clock_spacing) + clock_time_gap
            else:
                x = clock_start_x + i * (clock_digit_width + clock_spacing)
            d = Digit(x, clock_y, clock_digit_width, clock_digit_height, number=0)
            self.clock_digits.append(d)

        colon_x = clock_start_x + 2 * (clock_digit_width + clock_spacing) + clock_time_gap // 2
        self.colon_center = (colon_x, clock_y + clock_digit_height // 2)
        
        # Player配置
        player_start_x = SCREEN_WIDTH // 2 - int(20 * scale_w)
        player_start_y = int(SCREEN_HEIGHT * 0.2)
        self.player = Player(x=player_start_x, y=player_start_y, sound_manager=sound_manager)
        
        # ガイドテキスト ("Press ENTER to Start")
        try:
            font_full_path = resource_path(FONT_PATH)
            self.guide_font = pygame.font.Font(font_full_path, int(SCREEN_HEIGHT * 0.03))
        except Exception as e:
            print(f"Failed to load font: {e}")
            # フォントの読み込みに失敗した場合はデフォルトフォントを使用
            self.guide_font = pygame.font.SysFont(None, int(SCREEN_HEIGHT * 0.03))
            
        self.enter_blink_timer = 0.0
        
        # Sound Toggle Button (画面左上)
        button_x = int(20 * scale_w)
        button_y = int(20 * scale_h)
        button_w = int(140 * scale_w)
        button_h = int( 50 * scale_h)
        self.sound_toggle_button = pygame.Rect(button_x, button_y, button_w, button_h)
        self.sound_button_pressed = False

        # タイトル画面用のキー　　(3つのランダムパターン)
        pattern1 = [(0.22, 0.2), (0.48, 0.65), (0.9, 0.23)]
        pattern2 = [(0.33, 0.82), (0.77, 0.17), (0.58, 0.57)]
        pattern3 = [(0.18, 0.45), (0.48, 0.4), (0.65, 0.8)]
        patterns = [pattern1, pattern2, pattern3]
        chosen_pattern = random.choice(patterns)

        self.title_keys = []
        for (rx, ry) in chosen_pattern:
            x = int(SCREEN_WIDTH * rx)
            y = int(SCREEN_HEIGHT * ry)
            key_item = Key(x, y, duration=None)
            self.title_keys.append(key_item)

    def _reset_player(self):
        """プレイヤーが落下した場合に初期位置に戻す"""
        player_start_x = SCREEN_WIDTH // 2 - 20
        player_start_y = int(SCREEN_HEIGHT * 0.2)
        self.player.x = player_start_x
        self.player.y = player_start_y
        self.player.velocity_y = 0
        self.player.on_ground = False

    def update(self, dt):
        for d in self.title1_digits:
            d.update(dt)
        for d in self.title2_digits:
            d.update(dt)
        for d in self.clock_digits:
            d.update(dt)
        
        # 時計の更新
        try:
            now = datetime.now()
            hour = now.hour
            minute = now.minute
        except Exception:
            # ブラウザ環境ではdatetimeが使えない場合がある
            # 代替として固定値または現在のティックからの計算を使用
            ticks = pygame.time.get_ticks() / 1000
            minute = int((ticks / 60) % 60)
            hour = int((ticks / 3600) % 24)
            
        clock_vals = [hour // 10, hour % 10, minute // 10, minute % 10]
        for d, val in zip(self.clock_digits, clock_vals):
            d.set_number(val)
        
        # ガイドテキスト点滅
        self.enter_blink_timer += dt
        if self.enter_blink_timer > 1.0:
            self.enter_blink_timer = 0.0
        
        # 足場
        platforms = self.title1_digits + self.title2_digits + self.clock_digits

        # 調整用Digit
        for i, d in enumerate(self.title1_digits):
            ch = self.title_line1[i].upper()
            if ch in self.overlay_config_top:
                conf = self.overlay_config_top[ch]
                overlay = Digit(
                    x = d.x + conf.get('x_offset', 0),
                    y = d.y + conf.get('y_offset', 0),
                    width = d.width,
                    height = d.height,
                    number = conf.get('overlay_char')
                )
                platforms.append(overlay)
        for i, d in enumerate(self.title2_digits):
            ch = self.title_line2[i].upper()
            if ch in self.overlay_config_bottom:
                conf = self.overlay_config_bottom[ch]
                overlay = Digit(
                    x = d.x + conf.get('x_offset', 0),
                    y = d.y + conf.get('y_offset', 0),
                    width = d.width,
                    height = d.height,
                    number = conf.get('overlay_char')
                )
                platforms.append(overlay)
        
        # プレイヤー更新
        keys = pygame.key.get_pressed()
        current_space = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]

        # title_keys
        self.player.update(dt, keys, platforms, current_space, items=self.title_keys, stage_manager=None)
        
        for key_item in self.title_keys:
            key_item.update(dt)

        # プレイヤーの画面外リセット
        if self.player.y > SCREEN_HEIGHT:
            self.sound_manager.play("miss")
            self._reset_player()
        
        # プレイヤーと Sound Toggle Button の衝突判定
        if self.player.get_rect().colliderect(self.sound_toggle_button):
            if not self.sound_button_pressed:
                self.sound_manager.toggle_sound()
                self.sound_button_pressed = True
        else:
            self.sound_button_pressed = False

        # 3つのキーすべて取得したらステージ選択へ遷移
        collected_count = sum(key.collected for key in self.title_keys)
        if collected_count == 3:
            self.sound_manager.play("ex_open")
            from .stage_select_scene import StageSelectScene
            self.next_scene = StageSelectScene(self.screen, self.sound_manager)

    def draw(self):
        self.screen.fill((0, 0, 0))
        #digit描画
        for i, d in enumerate(self.title1_digits):
            d.draw(self.screen)
            ch = self.title_line1[i].upper()
            if ch in self.overlay_config_top:
                conf = self.overlay_config_top[ch]
                overlay = Digit(
                    x = d.x + conf.get('x_offset', 0),
                    y = d.y + conf.get('y_offset', 0),
                    width = d.width,
                    height = d.height,
                    number = conf.get('overlay_char')
                )
                overlay.draw(self.screen)

        for i, d in enumerate(self.title2_digits):
            d.draw(self.screen)
            ch = self.title_line2[i].upper()
            if ch in self.overlay_config_bottom:
                conf = self.overlay_config_bottom[ch]
                overlay = Digit(
                    x = d.x + conf.get('x_offset', 0),
                    y = d.y + conf.get('y_offset', 0),
                    width = d.width,
                    height = d.height,
                    number = conf.get('overlay_char')
                )
                overlay.draw(self.screen)

        # 時計の描画
        for d in self.clock_digits:
            d.draw(self.screen)
        colon_radius = 6
        pygame.draw.circle(self.screen, (255,255,255),
                        (self.colon_center[0], self.colon_center[1] - 15), colon_radius)
        pygame.draw.circle(self.screen, (255,255,255),
                        (self.colon_center[0], self.colon_center[1] + 15), colon_radius)
        
        # プレイヤーの描画
        self.player.draw(self.screen)
        # if self.player.debug_mode:
        #     self.player._draw_trail(self.screen)
        
        # キーを描画
        for key_item in self.title_keys:
            key_item.draw(self.screen)
        
        # ガイドテキスト
        if self.enter_blink_timer < 0.5:
            guide_text = self.guide_font.render("Press ENTER to Start", True, (255,255,255))
            guide_rect = guide_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 20))
            self.screen.blit(guide_text, guide_rect)
        
        # Sound Toggle Button の描画
        if self.sound_manager.sound_on:
            toggle_text = "Sound: ON"
            btn_color = (50, 200, 50)
        else:
            toggle_text = "Sound: OFF"
            btn_color = (200, 50, 50)
        pygame.draw.rect(self.screen, btn_color, self.sound_toggle_button)
        toggle_surf = self.guide_font.render(toggle_text, True, (255,255,255))
        toggle_rect = toggle_surf.get_rect(center=self.sound_toggle_button.center)
        self.screen.blit(toggle_surf, toggle_rect)

    def process_event(self, event):
        #print(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                print("[DEBUG] ENTER Pressed! Going to play sound...")
                self.sound_manager.play("title_in")
                from .stage_select_scene import StageSelectScene
                self.next_scene = StageSelectScene(self.screen, self.sound_manager)
            elif event.key == pygame.K_v:
                self.sound_manager.toggle_sound()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.sound_toggle_button.collidepoint(event.pos):
                self.sound_manager.toggle_sound()

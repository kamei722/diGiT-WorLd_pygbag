import pygame
import os
from game.game_utils import SCREEN_WIDTH, SCREEN_HEIGHT, resource_path
from config.keys import MOVE_LEFT_KEYS, MOVE_RIGHT_KEYS, JUMP_KEYS

BASE_DIR = resource_path("assets/pics")

class Player:
    def __init__(self, x, y, sound_manager):
        self.x = float(x)
        self.y = float(y)

        self.width = int(SCREEN_WIDTH * 0.0225)
        self.height = int(SCREEN_HEIGHT * 0.03)

        self.speed = SCREEN_WIDTH * 0.0075
        self.jump_power = SCREEN_HEIGHT * -0.0292
        self.gravity = SCREEN_HEIGHT * 0.00133

        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.on_ground = False
        self.is_game_over = False

        # 足場の待機時間
        self.coyote_time = 0.05
        self.coyote_timer = 0.0

        self.key_count = 0
        self.sound_manager = sound_manager
        self.max_fall_speed = SCREEN_HEIGHT * 0.026

        # 画像の読み込み
        self.image_right = pygame.image.load(os.path.join(BASE_DIR, "num_right.png")).convert_alpha()
        self.image_left = pygame.image.load(os.path.join(BASE_DIR, "num_left.png")).convert_alpha()
        self.image_right = pygame.transform.scale(self.image_right, (self.width, self.height))
        self.image_left = pygame.transform.scale(self.image_left, (self.width, self.height))

        self.facing_left = False

    def set_debug_mode(self, enabled: bool):
        self.debug_mode = enabled

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collect_key(self):
        self.key_count += 1
        if self.sound_manager:
            self.sound_manager.play("pickup")

    def update(self, dt, keys, digits, space_pressed_this_frame, items=None, stage_manager=None):
        """
        1) 入力による横方向速度の設定
        2) X軸移動 & 衝突解決
        3) コヨーテタイムとジャンプの処理
        4) Y軸移動 & 衝突解決
        5) その他判定
        """

        # ----- 1) 入力による速度の設定 -----
        moving_left = any(keys[k] for k in MOVE_LEFT_KEYS)
        moving_right = any(keys[k] for k in MOVE_RIGHT_KEYS)

        # 左右速度は毎フレーム更新 (定数速度モデル)
        if moving_left and not moving_right:
            self.velocity_x = -self.speed
            self.facing_left = True
        elif moving_right and not moving_left:
            self.velocity_x = self.speed
            self.facing_left = False
        else:
            self.velocity_x = 0.0

        # ----- 2) X軸移動 & 衝突解決 -----
        self.x += self.velocity_x

        # X軸方向の衝突解決
        self.handle_collision_x(digits, keys)

        # 画面 or ワールド左右端の処理
        if stage_manager is not None and hasattr(stage_manager, "world_left") and hasattr(stage_manager, "world_right"):
            if self.x < stage_manager.world_left:
                self.x = stage_manager.world_left
            elif self.x + self.width > stage_manager.world_right:
                self.x = stage_manager.world_right - self.width
        else:
            if self.x < 0:
                self.x = 0
            elif self.x + self.width > SCREEN_WIDTH:
                self.x = SCREEN_WIDTH - self.width

        # ----- 3) コヨーテタイムとジャンプ処理 -----
        if self.on_ground:
            self.coyote_timer = self.coyote_time
        else:
            self.coyote_timer -= dt
            if self.coyote_timer < 0:
                self.coyote_timer = 0

        if self.coyote_timer > 0 and space_pressed_this_frame:
            self.velocity_y = self.jump_power
            self.on_ground = False
            self.coyote_timer = 0
            if self.sound_manager:
                self.sound_manager.play("jump")

        # ----- 4) Y軸移動 & 衝突解決 -----
        # 重力
        self.velocity_y += self.gravity
        if self.velocity_y > self.max_fall_speed:
            self.velocity_y = self.max_fall_speed

        # 実際に Y を動かす
        self.y += self.velocity_y

        # Y軸の衝突解決
        self.handle_collision_y(digits, keys)

        # ----- 5) その他判定 (画面外, アイテム, etc) -----

        # 足場から落ちたかを確認 (world_bottom より下ならゲームオーバー)
        if stage_manager is not None and hasattr(stage_manager, "world_bottom"):
            bottom_threshold = stage_manager.world_bottom
        else:
            bottom_threshold = SCREEN_HEIGHT

        if self.y + self.height > bottom_threshold:
            self.is_game_over = True
            if stage_manager and stage_manager.sound_manager:
                stage_manager.sound_manager.play("miss")
            return  # このフレームはここで終了

        # アイテムとの衝突
        if items:
            player_rect = self.get_rect()
            for item in items:
                if not getattr(item, 'collected', False):
                    if player_rect.colliderect(item.get_rect()):
                        if hasattr(item, 'on_collect'):
                            item.on_collect(self, stage_manager)
                            # 鍵であれば collect_key() も実行
                            from game.objects.item import Key
                            if isinstance(item, Key):
                                self.collect_key()

        # 敵との衝突(もしあれば)
        # if stage_manager and stage_manager.active_enemies:
        #     for enemy in stage_manager.active_enemies:
        #         if self.get_rect().colliderect(enemy.get_rect()):
        #             self.is_game_over = True
        #             if self.sound_manager:
        #                 self.sound_manager.play("hit")
        #             break

    def handle_collision_x(self, digits, keys):
        """
        X方向の衝突解決
        """
        player_rect = self.get_rect()
        is_down_pressed = (keys[pygame.K_DOWN] or keys[pygame.K_s])

        for digit in digits:
            for group_name, plat_rect, one_way in digit.get_platform_rects():
                # 下キーの足場透過
                if one_way and is_down_pressed:
                    continue

                if player_rect.colliderect(plat_rect):
                    # 一方通行(one_way)の足場は基本的に「上から乗る」処理のみ。
                    # 横の衝突はスルーする(飛び越え用/階段的なものを想定)
                    if one_way:
                        continue  # X軸方向では無視
                    # 通常床の場合は X 軸方向の押し戻し処理
                    if self.velocity_x > 0:  # 右に動いて衝突
                        self.x = plat_rect.left - self.width
                    elif self.velocity_x < 0:
                        self.x = plat_rect.right
                    player_rect = self.get_rect()

    def handle_collision_y(self, digits, keys):
        """
        Y方向の衝突解決
        """
        self.on_ground = False
        player_rect = self.get_rect()
        is_down_pressed = (keys[pygame.K_DOWN] or keys[pygame.K_s])

        for digit in digits:
            for group_name, plat_rect, one_way in digit.get_platform_rects():
                if one_way and is_down_pressed:
                    # 下キー押下中は一方向足場をすり抜ける
                    continue

                if player_rect.colliderect(plat_rect):
                    overlap_x = min(player_rect.right, plat_rect.right) - max(player_rect.left, plat_rect.left)
                    overlap_y = min(player_rect.bottom, plat_rect.bottom) - max(player_rect.top, plat_rect.top)

                    if one_way:
                        #下向きに落下中で、上から降りてきたと判断できれば着地させる
                        player_above = (player_rect.bottom - overlap_y <= plat_rect.top)
                        if self.velocity_y > 0 and player_above:
                            self.y = plat_rect.top - self.height
                            self.velocity_y = 0
                            self.on_ground = True
                            self.coyote_timer = self.coyote_time
                    else:
                        # 通常床の場合の処理
                        if self.velocity_y > 0:
                            if player_rect.top >= plat_rect.top and player_rect.bottom <= plat_rect.bottom:
                                # 完全に内部にいる → 下方向へ押し出す
                                self.y = plat_rect.bottom
                                self.velocity_y = 0
                            else:
                                #　上に補正して足場に乗せる
                                self.y = plat_rect.top - self.height
                                self.velocity_y = 0
                                self.on_ground = True
                                self.coyote_timer = self.coyote_time
                        else:
                            self.y = plat_rect.bottom
                            self.velocity_y = 0

                    # 再計算
                    player_rect = self.get_rect()


    def draw(self, screen, cam_x=0, cam_y=0):
        display_scale = 1.25
        display_width = int(self.width * display_scale)
        display_height = int(self.height * display_scale)

        draw_x = int(self.x - cam_x - (display_width - self.width) / 2)
        draw_y = int(self.y - cam_y - (display_height - self.height) / 2)

        #　キャラクターの向き
        if self.facing_left:
            image_to_draw = pygame.transform.scale(self.image_left, (display_width, display_height))
        else:
            image_to_draw = pygame.transform.scale(self.image_right, (display_width, display_height))

        screen.blit(image_to_draw, (draw_x, draw_y))

import json, random, copy, pygame
from game.game_utils import SCREEN_WIDTH, SCREEN_HEIGHT
from game.objects.digit import Digit
from game.objects.item import Key, FinalKey

class StageManager:
    def __init__(self, sound_manager=None):
        self.digits = []
        self.original_digits = []
        self.current_sequence = []
        self.sequence_index = 0
        self.initial_time_per_number = 2.0
        self.time_per_number = self.initial_time_per_number
        self.last_change_time = pygame.time.get_ticks() / 1000.0

        self.item_spawns = []
        self.sound_manager = sound_manager

        self.global_change_time = 2.0
        self.global_last_change_time = pygame.time.get_ticks() / 1000.0
        self.pi_sound_flags = {"1.1": False, "0.6": False, "0.1": False}

        self.target_keys = 0
        self.is_stage_clear = False

        self.keys_to_spawn = []
        self.active_keys = []
        self.consecutive_keys = 0

        self.game_clear_delay = 0.3
        self.clear_timer_start = None

        self.current_sequence_index = 1
        self.total_sequences = 0
        self.current_loop = 1

        self.digit_controllers = []

        # 最終ステージ用パラメータ
        self.final_stage = False
        self.digit_activation_threshold = None
        self.digit_removal_threshold = None

        # 状態管理フラグ
        self.groupB_activated = False
        self.groupA_removed = False
        
        # ステージデータ
        self.stage_data = {}

    def add_digit(self, digit):
        self.digits.append(digit)

    def load_stage(self, stage_path):
        try:
            # ブラウザ環境対応: fetch APIを使ってJSONを読み込む
            try:
                # デスクトップ環境
                with open(stage_path, 'r') as f:
                    self.stage_data = json.load(f)
            except Exception:
                # ブラウザ環境の場合は相対パスに調整
                import os
                base_name = os.path.basename(stage_path)
                try:
                    with open(f"stage/{base_name}", 'r') as f:
                        self.stage_data = json.load(f)
                except Exception as e:
                    print(f"Failed to load stage: {e}")
                    self.stage_data = {}
                    return

            reference = self.stage_data.get("screen_reference", {"width": 800, "height": 600})
            self.scale_x = SCREEN_WIDTH / reference["width"]
            self.scale_y = SCREEN_HEIGHT / reference["height"]

            if "player_start" in self.stage_data:
                ps = self.stage_data["player_start"]
                ps["x"] = int(ps["x"] * self.scale_x)
                ps["y"] = int(ps["y"] * self.scale_y)

            if "digits" in self.stage_data:
                for d_info in self.stage_data["digits"]:
                    d_info["x"] = int(d_info["x"] * self.scale_x)
                    d_info["y"] = int(d_info["y"] * self.scale_y)
                    d_info["width"] = int(d_info["width"] * self.scale_x)
                    d_info["height"] = int(d_info["height"] * self.scale_y)
                    # グループ指定がなければ、ここで自動判定する
                    if "group" not in d_info:
                        if d_info["y"] < -800:
                            d_info["group"] = "A"
                        else:
                            d_info["group"] = "B"

            if "item_spawns" in self.stage_data:
                for spawn in self.stage_data["item_spawns"]:
                    spawn["x"] = int(spawn["x"] * self.scale_x)
                    spawn["y"] = int(spawn["y"] * self.scale_y)
            if "enemy_spawns" in self.stage_data:
                for spawn in self.stage_data["enemy_spawns"]:
                    if "x" in spawn:
                        spawn["x"] = int(spawn["x"] * self.scale_x)
                    if "y" in spawn:
                        spawn["y"] = int(spawn["y"] * self.scale_y)
                    if "patrol_range" in spawn:
                        spawn["patrol_range"] = int(spawn["patrol_range"] * self.scale_x)
                    if "amplitude" in spawn:
                        spawn["amplitude"] = int(spawn["amplitude"] * self.scale_y)

            # 旧sequence対応
            if "sequence" in self.stage_data:
                global_sequence = self.stage_data.get("sequence", [])
                global_initial_time = self.stage_data.get("initial_time_per_number", 2.0)
                self.stage_data["digits"] = [{
                    "x": di.get("x", 300),
                    "y": di.get("y", 100),
                    "width": di.get("width", 200),
                    "height": di.get("height", 400),
                    "sequence": di.get("sequence", global_sequence),
                    "initial_time": di.get("initial_time", global_initial_time),
                    "group": di.get("group", "B")
                } for di in self.stage_data.get("digits", [])]

            self.target_keys = self.stage_data.get("target_keys", 0)
            self.global_change_time = self.stage_data.get("change_time", 2.0)
            self.world_bottom = int(self.stage_data.get("world_bottom", SCREEN_HEIGHT) * self.scale_y)
            self.world_left = int(self.stage_data.get("world_left", 0) * self.scale_x)
            self.world_right = int(self.stage_data.get("world_right", SCREEN_WIDTH) * self.scale_x)

            # 最終ステージ用情報
            self.final_stage = self.stage_data.get("final_stage", False)
            if self.final_stage:
                self.digit_activation_threshold = float(self.stage_data.get("digit_activation_threshold")) * self.scale_y
                self.digit_removal_threshold = float(self.stage_data.get("digit_removal_threshold")) * self.scale_y

            digits_data = self.stage_data.get("digits", [])
            for d_info in digits_data:
                controller = DigitController(
                    sequence=d_info.get("sequence", []),
                    initial_time=d_info.get("initial_time", 2.0)
                )
                self.digit_controllers.append(controller)
                digit = Digit(
                x=d_info["x"],
                y=d_info["y"],
                width=d_info["width"],
                height=d_info["height"],
                number=d_info["sequence"][0],
                properties_override=self.stage_data.get("segment_properties_override")
                )
                # グループ情報を digit に保持させる
                digit.group = d_info.get("group", "B")
                # 初期状態：Group A の digit は非表示、Group B は表示
                digit.active = (digit.group == "B")
                self.add_digit(digit)

            self.original_digits = copy.deepcopy(self.digits)
            self.load_item_spawns(self.stage_data.get("item_spawns", []))
            self.load_enemy_spawns(self.stage_data.get("enemy_spawns", []))

            if digits_data and "sequence" in digits_data[0]:
                self.total_sequences = len(digits_data[0]["sequence"])
        except Exception as e:
            print(f"Error loading stage {stage_path}: {e}")

    # その他のメソッドは同様に時間関連の部分を修正
    
    def load_item_spawns(self, item_spawns):
        self.item_spawns = item_spawns
        sorted_spawns = sorted(self.item_spawns, key=lambda x: x["index"])
        self.keys_to_spawn = []
        for spawn in sorted_spawns:
            self.keys_to_spawn.append({
                "x": spawn["x"],
                "y": spawn["y"],
                "index": spawn["index"],
                "number": spawn.get("number", 1),
                "delay": spawn.get("delay", 0.0),
                "spawned": False,
                "spawn_time": None,
                "lifespan": spawn.get("lifespan", None)
            })

    def load_enemy_spawns(self, enemy_spawns):
        self.enemy_spawns = enemy_spawns
        self.active_enemies = []
        for spawn in self.enemy_spawns:
            spawn["spawned"] = False
            trigger = spawn.get("trigger", {})
            if trigger.get("type") == "random":
                delay_min, delay_max = trigger.get("delay_range", [5, 15])
                spawn["next_spawn_time"] = self.last_change_time + random.uniform(delay_min, delay_max)
            else:
                spawn["next_spawn_time"] = None

    def reset(self):
        self.sequence_index = 0
        self.current_sequence_index = 1
        self.time_per_number = self.initial_time_per_number
        self.last_change_time = pygame.time.get_ticks() / 1000.0
        self.global_last_change_time = pygame.time.get_ticks() / 1000.0
        self.pi_sound_flags = {"1.1": False, "0.6": False, "0.1": False}
        self.is_stage_clear = False
        self.current_loop = 1
        self.consecutive_keys = 0
        
        self.groupB_activated = False
        self.groupA_removed = False
        self.digits = copy.deepcopy(self.original_digits)

        for controller, digit in zip(self.digit_controllers, self.digits):
            controller.reset()
            if controller.sequence:
                digit.set_number(controller.sequence[0])
        for spawn in self.enemy_spawns:
            spawn["spawned"] = False
        for key_info in self.keys_to_spawn:
            key_info["spawned"] = False
            key_info["spawn_time"] = None
        self.active_keys.clear()

    def new_game_reset(self):
        self.reset()

    def update(self, dt, items, player):
        if self.is_stage_clear:
            return
        
        current_time = pygame.time.get_ticks() / 1000.0
        loop_completed = []

        self._check_index_zero_spawn(current_time)

        # カウント音処理
        if not self.final_stage:
            elapsed = current_time - self.global_last_change_time
            if elapsed < self.global_change_time:
                remaining = self.global_change_time - elapsed
                threshold_1 = self.global_change_time * 0.55
                threshold_2 = self.global_change_time * 0.30
                threshold_3 = self.global_change_time * 0.05
                if remaining <= threshold_1 and not self.pi_sound_flags["1.1"]:
                    if self.sound_manager:
                        self.sound_manager.play("pi")
                    self.pi_sound_flags["1.1"] = True
                if remaining <= threshold_2 and not self.pi_sound_flags["0.6"]:
                    if self.sound_manager:
                        self.sound_manager.play("pi")
                    self.pi_sound_flags["0.6"] = True
                if remaining <= threshold_3 and not self.pi_sound_flags["0.1"]:
                    if self.sound_manager:
                        self.sound_manager.play("pi")
                    self.pi_sound_flags["0.1"] = True
            else:
                self.global_last_change_time = current_time
                self.pi_sound_flags = {"1.1": False, "0.6": False, "0.1": False}

        self._update_keys_and_enemies(dt,items,current_time,player)

        # 各 Digit の更新
        for i, (controller, digit) in enumerate(zip(self.digit_controllers, self.digits)):
            changed, new_number = controller.update(current_time)
            if changed:
                digit.set_number(new_number)
                if controller.sequence_index == 0:
                    loop_completed.append(i)
                self.current_sequence_index = controller.sequence_index + 1
                for key_info in self.keys_to_spawn:
                    if (not key_info["spawned"] and key_info.get("digit_index", 0) == i and 
                        key_info["index"] == controller.sequence_index):
                        key_info["spawn_time"] = current_time + key_info["delay"]
                        key_info["spawned"] = True

        if loop_completed:
            self.current_loop += 1
            for key_info in self.keys_to_spawn:
                key_info["spawned"] = False
                key_info["spawn_time"] = None

        # 最終ステージ専用の出現管理
        if self.final_stage:
            # Group A をアクティブ化する条件の確認
            if not self.groupB_activated:
                if player.y < self.digit_activation_threshold:
                    for digit in self.digits:
                        if getattr(digit, "group", "B") == "A":
                            digit.active = True
                    self.groupB_activated = True
                    self.sound_manager.play("spawn_one")
                    self.sound_manager.play_music("heart.mp3")
            
            # Group B の一部を非表示にする条件の確認
            if self.groupB_activated and not self.groupA_removed:
                if player.y < self.digit_removal_threshold:
                    for digit in self.digits:
                        if getattr(digit, "group", "B") == "B" and digit.y > self.digit_removal_threshold:
                            digit.active = False
                    self.groupA_removed = True

        # Key取得の管理
        # 連続のKey取得　および　クリア時に着地しているかを判定
        if self.consecutive_keys < self.target_keys:
            self.clear_timer_start = None
        else:
            if self.clear_timer_start is None:
                self.clear_timer_start = current_time
            elif current_time - self.clear_timer_start >= self.game_clear_delay:
                if player.on_ground or abs(player.velocity_y) < 1.0:
                    self.is_stage_clear = True
                    if self.sound_manager:
                        self.sound_manager.play("stage_clear")
                    self.clear_timer_start = None
                else:
                    self.clear_timer_start = current_time

    # 以下のメソッドも同様に修正

    def _check_index_zero_spawn(self, current_time):
        if self.sequence_index == 0:
            for key_info in self.keys_to_spawn:
                if key_info["index"] == 0 and not key_info["spawned"]:
                    key_info["spawn_time"] = current_time + key_info["delay"]
                    key_info["spawned"] = True
        if self.final_stage:
            for key_info in self.keys_to_spawn:
                if not key_info["spawned"]:
                    key_info["spawn_time"] = current_time
                    key_info["spawned"] = True

    def _update_keys_and_enemies(self, dt, items, current_time, player):    
        for key_info in self.keys_to_spawn:
            if (key_info["spawned"] and key_info["spawn_time"] is not None and current_time >= key_info["spawn_time"]):
                if self.final_stage:  
                    key = FinalKey(key_info["x"], key_info["y"], duration=key_info["lifespan"], number=key_info["number"])
                else:
                    key = Key(key_info["x"], key_info["y"], duration=key_info["lifespan"], number=key_info["number"])
                
                key.spawn_time = current_time
                items.append(key)
                self.active_keys.append(key)
                key_info["spawn_time"] = None
                
                # **4-3ではキーのスポーン音を鳴らさない**
                if not self.final_stage and self.sound_manager:
                    self.sound_manager.play("key_spawn")

        # **キーが時間切れで消滅する処理**
        for key in self.active_keys[:]:
            if not key.collected:
                elapsed = current_time - key.spawn_time
                if elapsed >= key.duration:
                    self.active_keys.remove(key)
                    if key in items:
                        items.remove(key)
                    self.consecutive_keys = 0

        for item in items:
            if isinstance(item, Key) and item.collected:
                self.increment_consecutive_keys()

    def increment_consecutive_keys(self):
        self.consecutive_keys += 1


class DigitController:
    def __init__(self, sequence, initial_time):
        self.sequence = sequence
        self.sequence_index = 0
        self.initial_time = initial_time
        self.time_per_number = initial_time
        self.last_change_time = pygame.time.get_ticks() / 1000.0

    def update(self, current_time):
        if not self.sequence:
            return False, 0
        time_since_change = current_time - self.last_change_time
        changed = False
        if time_since_change >= self.time_per_number:
            self.sequence_index = (self.sequence_index + 1) % len(self.sequence)
            self.last_change_time = current_time
            changed = True
        return changed, self.sequence[self.sequence_index]

    def speed_up(self):
        pass

    def reset(self):
        self.sequence_index = 0
        self.time_per_number = self.initial_time
        self.last_change_time = pygame.time.get_ticks() / 1000.0
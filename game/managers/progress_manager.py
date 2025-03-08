import json
import copy

# ブラウザ環境かどうかを検出
try:
    import os
    IS_BROWSER = False
except ImportError:
    IS_BROWSER = True

class ProgressManager:
    def __init__(self):
        self.default_progress = {
            "unlocked_stages": {
                "1": [1,2,3],
                "2": [1,2,3],
                "3": [1,2,3],
                "4": [1,2,3], 
                "5": [1] 
            },
            "cleared_stages": {
                "1": [1,2,3],
                "2": [1,2,3],
                "3": [1,2,3],
                "4": [1,2,3],
                "5": [1]
            }
        }
        
        # ブラウザ環境では全ステージを解放
        self.browser_all_unlocked = {
            "unlocked_stages": {
                "1": [1, 2, 3],
                "2": [1, 2, 3],
                "3": [1, 2, 3],
                "4": [1, 2, 3], 
                "5": [1] 
            },
            "cleared_stages": {
                "1": [1,2,3],
                "2": [1,2,3],
                "3": [1,2,3],
                "4": [1,2,3],
                "5": [1]
            }
        }
        
        if not IS_BROWSER:
            # デスクトップ環境
            home_dir = os.path.expanduser("~")
            app_dir = os.path.join(home_dir, ".digitworld")
            os.makedirs(app_dir, exist_ok=True)
            self.save_path = os.path.join(app_dir, "progress.json")
        
        self.load_progress()

    def load_progress(self):
        """進行状況を読み込む"""
        if IS_BROWSER:
            # ブラウザ環境では全ステージ解放済みのデータを使用
            self.progress = copy.deepcopy(self.browser_all_unlocked)
            print("Browser environment detected: All stages unlocked automatically.")
            return
        
        # デスクトップ環境での通常の読み込み処理
        try:
            with open(self.save_path, 'r') as f:
                self.progress = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.progress = copy.deepcopy(self.default_progress)
            self.save_progress()

    def save_progress(self):
        """進行状況を保存する"""
        if IS_BROWSER:
            # ブラウザ環境では保存しない（常に全ステージ解放）
            return
            
        # デスクトップ環境での通常の保存処理
        with open(self.save_path, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def is_stage_unlocked(self, world, stage):
        """ステージが解放されているかを確認"""
        if IS_BROWSER:
            # ブラウザ環境では常にTrue（ただし存在するステージのみ）
            world_str = str(world)
            if world_str in self.browser_all_unlocked["unlocked_stages"]:
                return stage in self.browser_all_unlocked["unlocked_stages"][world_str]
            return False
            
        # 通常の解放チェック
        world_str = str(world)
        return stage in self.progress["unlocked_stages"].get(world_str, [])

    def is_stage_cleared(self, world, stage):
        """ステージがクリア済みかを確認"""
        world_str = str(world)
        return stage in self.progress["cleared_stages"].get(world_str, [])

    def unlock_stage(self, world, stage):
        """ステージを解放する"""
        if IS_BROWSER:
            # ブラウザ環境では操作不要（すでに全て解放済み）
            return
            
        # 通常の解放処理
        world_str = str(world)
        if world_str not in self.progress["unlocked_stages"]:
            self.progress["unlocked_stages"][world_str] = []
        if stage not in self.progress["unlocked_stages"][world_str]:
            self.progress["unlocked_stages"][world_str].append(stage)
            self.progress["unlocked_stages"][world_str].sort()
            self.save_progress()

    def clear_stage(self, world, stage):
        """ステージをクリア済みにする"""
        if IS_BROWSER:
            # ブラウザ環境ではメモリ上のみに記録（永続化しない）
            world_str = str(world)
            if world_str not in self.progress["cleared_stages"]:
                self.progress["cleared_stages"][world_str] = []
            if stage not in self.progress["cleared_stages"][world_str]:
                self.progress["cleared_stages"][world_str].append(stage)
                self.progress["cleared_stages"][world_str].sort()
            return
            
        # 通常のクリア処理
        world_str = str(world)
        if world_str not in self.progress["cleared_stages"]:
            self.progress["cleared_stages"][world_str] = []
        if stage not in self.progress["cleared_stages"][world_str]:
            self.progress["cleared_stages"][world_str].append(stage)
            self.progress["cleared_stages"][world_str].sort()
            self._handle_stage_clear_unlock(world, stage)
            self.save_progress()

    def _handle_stage_clear_unlock(self, world, stage):
        """ステージクリア時の解放処理"""
        if IS_BROWSER:
            # ブラウザ環境では操作不要（すでに全て解放済み）
            return
            
        # 通常の解放処理
        total_stages_per_world = 3
        
        if stage < total_stages_per_world:
            self.unlock_stage(world, stage + 1)
        elif stage == total_stages_per_world:
            if world < 4:
                self.unlock_stage(world + 1, 1)
            elif world == 4:
                self.unlock_stage(5, 1)
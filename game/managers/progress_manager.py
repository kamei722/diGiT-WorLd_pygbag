import os
import json
import copy

class ProgressManager:
    def __init__(self):
        # ホームディレクトリベース
        home_dir = os.path.expanduser("~")
        app_dir = os.path.join(home_dir, ".digitworld")
        os.makedirs(app_dir, exist_ok=True)
        self.save_path = os.path.join(app_dir, "progress.json")
        
        self.default_progress = {
            "unlocked_stages": {
                "1": [1],
                "2": [],
                "3": [],
                "4": [], 
                "5": [] 
            },
            "cleared_stages": {
                "1": [],
                "2": [],
                "3": [],
                "4": [],
                "5": []
            }
        }
        self.load_progress()

    def load_progress(self):
        """進行状況を読み込む"""
        try:
            with open(self.save_path, 'r') as f:
                self.progress = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.progress = copy.deepcopy(self.default_progress)
            self.save_progress()

    def save_progress(self):
        """進行状況を保存する"""
        with open(self.save_path, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def is_stage_unlocked(self, world, stage):
        world_str = str(world)
        return stage in self.progress["unlocked_stages"].get(world_str, [])

    def is_stage_cleared(self, world, stage):
        world_str = str(world)
        return stage in self.progress["cleared_stages"].get(world_str, [])

    def unlock_stage(self, world, stage):
        world_str = str(world)
        if world_str not in self.progress["unlocked_stages"]:
            self.progress["unlocked_stages"][world_str] = []
        if stage not in self.progress["unlocked_stages"][world_str]:
            self.progress["unlocked_stages"][world_str].append(stage)
            self.progress["unlocked_stages"][world_str].sort()
            self.save_progress()

    def clear_stage(self, world, stage):
        world_str = str(world)
        if world_str not in self.progress["cleared_stages"]:
            self.progress["cleared_stages"][world_str] = []
        if stage not in self.progress["cleared_stages"][world_str]:
            self.progress["cleared_stages"][world_str].append(stage)
            self.progress["cleared_stages"][world_str].sort()
            self._handle_stage_clear_unlock(world, stage)
            self.save_progress()

    def _handle_stage_clear_unlock(self, world, stage):
        total_stages_per_world = 3
        total_worlds = 5

        if stage < total_stages_per_world:
            self.unlock_stage(world, stage + 1)
        elif stage == total_stages_per_world:
            if world < 4:
                self.unlock_stage(world + 1, 1)
            elif world == 4:
                self.unlock_stage(5, 1)

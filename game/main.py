# game/main.py
import pygame
import os
import sys
import asyncio

# パス設定を修正
try:
    # デスクトップ環境用
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
except Exception as e:
    print(f"Fatal error in async_main: {e}")
    import traceback
    traceback.print_exc()

from game.game_utils import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, resource_path
from game.managers.soundmanager import SoundManager
from game.scenes.title_scene import TitleScene

# 非同期版のメイン関数
async def async_main():
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=256)
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()

    game_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("dIGIT WorLd")
    # サウンド読み込み
    sound_dir = resource_path("assets/sound")
    sound_manager = SoundManager(sound_dir)

    sound_settings = {
        "jump":         ("jump.ogg", 0.05),
        "hit":          ("hit.ogg", 0.0),
        "pickup":       ("pickup.ogg", 0.02),
        "stage_clear":  ("stage_clear.ogg", 0.01),
        "miss":         ("miss.ogg", 0.02),
        "pi":           ("pi.ogg", 0.1),
        "loop_reset":   ("loop_reset.ogg", 0.1),
        "key_spawn":    ("key_spawn.ogg", 0.05),
        "select":       ("select.ogg", 0.1),
        "stage_in":     ("stage_in.ogg", 0.1),
        "unmove":       ("unmove.ogg", 0.1),
        "ex_open":      ("ex_open.ogg", 0.1),
        "title_in":     ("title_in.ogg", 0.1),
        "spawn_one":    ("spawn_one.ogg", 0.02),
    }

    resources = list(sound_settings.items())

    for name, (filename, vol) in resources:
        sound_manager.load_sound(name, filename)
        sound_manager.set_volume(name, vol)
        await asyncio.sleep(0.01)  # 非同期環境での待機
        
    # メインゲームウィンドウ設定
    
    clock = pygame.time.Clock()

    current_scene = TitleScene(game_screen, sound_manager)

    # メインゲームループ
    while current_scene.is_running:
        dt = clock.tick(FPS) / 1000.0

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return  # 非同期関数では sys.exit() を使わない
                
        current_scene.handle_events(events)
        current_scene.update(dt)
        current_scene.draw()
        pygame.display.flip()

        if current_scene.next_scene:
            current_scene.cleanup()
            current_scene = current_scene.next_scene
        
        # ブラウザ環境のためのフレーム待機
        await asyncio.sleep(0)

    pygame.quit()

# 元のmain関数も互換性のために残しておく
def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
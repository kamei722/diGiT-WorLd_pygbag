# main.py
# game/main.py
import pygame
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from game.game_utils import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, resource_path
from game.managers.soundmanager import SoundManager
from game.scenes.title_scene import TitleScene

def main():
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=256)
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()

    # -------------------------------
    # 1. 小さなウィンドウ作成
    # -------------------------------
    splash_size = (200, 200)
    splash_screen = pygame.display.set_mode(splash_size)
    pygame.display.set_caption("Loading...")

    splash_path = resource_path("assets/pics/splash.png")
    try:
        splash_image = pygame.image.load(splash_path).convert()
        splash_image = pygame.transform.scale(splash_image, splash_size)
    except Exception as e:
        print("Failed to load splash image:", e)
        splash_image = None

    if splash_image:
        splash_screen.blit(splash_image, (0, 0))
    else:
        splash_screen.fill((0, 0, 0))
    pygame.display.flip()

    # -------------------------------
    # 2. リソースを読み込む
    # -------------------------------
    sound_dir = resource_path("assets/sound")
    sound_manager = SoundManager(sound_dir)

    sound_settings = {
        "jump":         ("jump.mp3", 0.05),
        "hit":          ("hit.mp3", 0.0),
        "pickup":       ("pickup.mp3", 0.02),
        "stage_clear":  ("stage_clear.mp3", 0.01),
        "enemy_spawn":  ("enemy_spawn.mp3", 0.1),
        "miss":         ("miss.mp3", 0.02),
        "pi":           ("pi.mp3", 0.1),
        "speed_up":     ("speed.mp3", 0.1),
        "loop_reset":   ("loop_reset.mp3", 0.1),
        "key_spawn":    ("key_spawn.mp3", 0.05),
        "select":       ("select.mp3", 0.1),
        "stage_in":     ("stage_in.mp3", 0.1),
        "unmove":       ("unmove.mp3", 0.1),
        "ex_open":      ("ex_open.mp3", 0.1),
        "title_in":     ("title_in.mp3", 0.1),
        "spawn_one":    ("spawn_one.mp3", 0.02),
    }
    resources = list(sound_settings.items())
    total_resources = len(resources)
    loaded_count = 0

    font = pygame.font.Font(None, 24)

    while resources:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        name, (filename, vol) = resources.pop(0)
        sound_manager.load_sound(name, filename)
        sound_manager.set_volume(name, vol)
        loaded_count += 1
        
        if splash_image:
            splash_screen.blit(splash_image, (0, 0))
        else:
            splash_screen.fill((0, 0, 0))
        # text_rect = text_surface.get_rect(center=(splash_size[0] // 2, splash_size[1] - 30))
        # splash_screen.blit(text_surface, text_rect)
        pygame.display.flip()
        
        pygame.time.delay(100)  # 各リソース読み込み後に少し待機

    # -------------------------------
    # 3. リソース読み込み完了後、通常のゲームウィンドウに切り替え
    # -------------------------------
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    game_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("dIGIT WorLd")
    clock = pygame.time.Clock()

    current_scene = TitleScene(game_screen, sound_manager)

    # -------------------------------
    # 4. メインゲームループ
    # -------------------------------
    while current_scene.is_running:
        dt = clock.tick(FPS) / 1000.0

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        current_scene.handle_events(events)
        current_scene.update(dt)
        current_scene.draw()
        pygame.display.flip()

        if current_scene.next_scene:
            current_scene.cleanup()
            current_scene = current_scene.next_scene

    pygame.quit()

if __name__ == "__main__":
    main()

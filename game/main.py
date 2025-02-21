# main.py
# game/main.py
import pygame
import os
import sys
import threading
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from game.game_utils import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, resource_path
from game.managers.soundmanager import SoundManager
from game.scenes.title_scene import TitleScene

# 初期状態は False（読み込み未完了）
loading_complete = False

def load_resources(sound_manager):
    global loading_complete
    # サウンド設定（必要なリソースをここで読み込む）
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
    for name, (filename, vol) in sound_settings.items():
        sound_manager.load_sound(name, filename)
        sound_manager.set_volume(name, vol)
        # ※ここで、各サウンドの読み込みに時間がかかる実際の処理が走る
    loading_complete = True

def main():
    global loading_complete

    # Pygameの初期化
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=256)
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()

    # -------------------------------
    # 1. スプラッシュ用の小さなウィンドウ作成
    # -------------------------------
    splash_size = (200, 200)  # 小さな正方形のウィンドウ
    splash_screen = pygame.display.set_mode(splash_size)
    pygame.display.set_caption("Loading...")

    splash_path = resource_path("assets/pics/splash.png")
    try:
        splash_image = pygame.image.load(splash_path).convert()
        splash_image = pygame.transform.scale(splash_image, splash_size)
    except Exception as e:
        print("スプラッシュ画像の読み込みに失敗しました:", e)
        splash_image = None

    if splash_image:
        splash_screen.blit(splash_image, (0, 0))
    else:
        splash_screen.fill((0, 0, 0))
    pygame.display.flip()

    # -------------------------------
    # 2. リソース読み込み（サウンドなど）を別スレッドで開始
    # -------------------------------
    sound_dir = resource_path("assets/sound")
    sound_manager = SoundManager(sound_dir)
    loading_thread = threading.Thread(target=load_resources, args=(sound_manager,))
    loading_thread.start()

    # -------------------------------
    # 3. 読み込みが完了するまでスプラッシュ画面を表示
    # -------------------------------
    while not loading_complete:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        # ※ここでアニメーションや進捗表示を追加することも可能
        pygame.display.flip()
        pygame.time.delay(10)  # CPU負荷軽減

    # -------------------------------
    # 4. リソース読み込み完了後、通常のゲームウィンドウに切り替え
    # -------------------------------
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    game_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("dIGIT WorLd")
    clock = pygame.time.Clock()

    # シーン（タイトルなど）を生成
    current_scene = TitleScene(game_screen, sound_manager)

    # -------------------------------
    # 5. メインゲームループ
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

#MusicPlayer by Ian0822
# -*- coding: utf-8 -*-

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import vlc
import random
from player_utils import *
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

# // 初始化
#初始化pygame
pygame.init()

#搜尋資料夾內.mp3檔案
current_folder = os.path.join(os.path.dirname(__file__))
music_folder = os.path.join(current_folder, "musicPlayer", "music")
metadata_list = []
for song_file in os.listdir(music_folder):
    if song_file.endswith(".mp3"):
        path = os.path.join(music_folder, song_file)
        try:
            audio = MP3(path, ID3=EasyID3)
            song_name = song_file[:-4]
            # 嘗試讀取圖片
            img_path = os.path.join(current_folder, "musicPlayer", "img", song_name + ".png")
            if os.path.exists(img_path):
                img = pygame.image.load(os.path.join(img_path))
                img = pygame.transform.scale(img, (240, 240))
            else:
                img = 0
            metadata_list.append({
                "檔名": song_name,
                "演出者": audio.get("artist", ["未知"])[0],
                "專輯": audio.get("album", ["無"])[0],
                "圖片": img
            })
        except Exception as e:
            print(f"⚠️ 無法讀取 {song_file}: {e}")
playlist = {"全部歌曲":[], "收藏歌曲":[], "搜尋結果":[]}
playlist["全部歌曲"] = sorted([song["檔名"].lower() for song in metadata_list])

#初始化vlc
instance = vlc.Instance()
player = instance.media_player_new()

#定義常數
#視窗
FPS = 60
WIDTH = 360
HEIGHT = 720

#顯示視窗
GUI = True

#顏色
BLACK = 0, 0, 0
WHITE = 255, 255, 255
YELLOW = 255, 255, 0
GREEN = 0, 255, 0
DGREEN = 0, 120, 0
RED = 255, 0, 0
LBLUE = 152, 245, 255
BLUE = 30, 144, 255
CYAN = 32, 178, 170
TEAL = 0, 160, 160
GOLD = 255, 215, 0
DGRAY = 105, 105, 105
GRAY = 192, 192, 192
LGRAY = 119, 136, 153
AGRAY = 64, 64, 64
BGRAY = 100, 100, 100
IGRAY = 80, 84, 92
PURPLE = 148, 0, 211
DCGRAY = 49, 51, 56

#設定字體
FONT = os.path.join(current_folder, "MusicPlayer", "img", "font.ttf")
input_box = TextInputBox(80, 600, 140, 32, pygame.font.Font(FONT, 15), True)

importing_imgs = ["icon"]
img_list = {}
for img in importing_imgs:
    img_list.update({img : pygame.image.load(os.path.join(current_folder, "musicPlayer", "img", img + ".png"))})
#設定視窗
if GUI:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("MusicPlayer 1.0")
    pygame.display.set_icon(img_list["icon"])
    clock = pygame.time.Clock()

# // 定義函式
# 撥放音樂
def play_song(name):
    if name.isdigit() and 0 < len(playlist["搜尋結果"]) >= int(name):
        name = playlist["搜尋結果"][int(name) - 1]
    music_path = os.path.join(current_folder, "musicPlayer", "music", name + ".mp3")
    if not os.path.exists(music_path):
        print("錯誤：找不到音檔" + name + ".mp3！")
        return {"name":"沒有歌曲正在撥放", "artist":"未知演出者", "album":"未知專輯", "img":0}
    media = instance.media_new(music_path)
    player.set_media(media)
    player.audio_set_volume(volume)
    # 撥放
    player.play()
    # 從 metadata_list 中找資料
    song_metadata = next((m for m in metadata_list if m["檔名"] == name), None)
    if song_metadata:
        title = song_metadata.get("檔名", "未知")
        artist = song_metadata.get("演出者", "未知")
        album = song_metadata.get("專輯", "無")
        img = song_metadata.get("圖片", 0)
    else:
        audio = MP3(music_path, ID3=EasyID3)
        title = audio.get("title", ["未知"])[0]
        artist = audio.get("artist", ["未知"])[0]
        album = audio.get("album", ["無"])[0]
        img = 0

    print("🎵 現在播放：" + title)
    print(f"🎤 演出者: {artist}")
    print(f"💿 專輯: {album}")
    print()

    return {"name": title, "artist": artist, "album": album, "img": img}

#顯示文字
def text(text, size, x, y, color):
    font = pygame.font.Font(FONT, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    screen.blit(text_surface, text_rect)

#顯示外框文字
def outline_text(text, size, x, y, color):
    font = pygame.font.Font(FONT, size)
    base = font.render(str(text), True, BLACK)  # 渲染外框
    outline = pygame.Surface((base.get_width() + 4, base.get_height() + 4), pygame.SRCALPHA)
    text_surface = font.render(str(text), True, color)  # 渲染主文字
    # 繪製外框 (上下左右四個方向)
    for dx in [-2, 2]:
        for dy in [-2, 2]:
            outline.blit(base, (dx + 2, dy + 2))
    # 中心繪製主文字
    outline.blit(text_surface, (2, 2))
    screen.blit(outline, (x, y))

#時間轉換
def format_time(ms):
    seconds = ms // 1000
    return f"{seconds // 60}:{seconds % 60:02}"

#渲染圖片
def render_img(img, x, y):
    Render_img.draw(1, screen, img, x, y)

#偵測鼠標懸停(長方形)
def is_hovering(x1, x2, y1, y2, mouse_icon = ""):
    if x1 < mouse_x < x2 and y1 < mouse_y < y2 and mouse_icon:
        outline_text(mouse_icon, 30, mouse_y, mouse_x - 10, RED)
    return x1 < mouse_x < x2 and y1 < mouse_y < y2

#偵測鼠標懸停(圓形)
def is_hovering_circle(x, y, radius):
    return abs(mouse_x - x) ** 2 + abs(mouse_y - y) ** 2 <= radius ** 2

# // 定義類別

print("MusicPlayer 1.0 \n 使用 >> help 查詢指令")

volume = 70
loop = "none"
random_song = False
song_ended = False
playing_music_data = {"name":"沒有歌曲正在撥放", "artist":"未知演出者", "album":"未知專輯", "img":0}
progress = 0
cmd = []

# // 程式主迴圈
running = True
while running:
    if GUI:
        clock.tick(FPS)
        screen.fill((DCGRAY))
    
    #取得游標位置
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    #控制台: 接收指令
    #拆解指令
    if not GUI:
        try:
            cmd = [i for i in input(">> ").split()]
        except EOFError:
            cmd = []
            print("error")
    elif GUI and cmd:
        cmd = cmd[3:]
        cmd = [i for i in cmd.split()]
    #執行指令
    if cmd:
        cmd[0] = cmd[0].lower()
        #指令: 播放/暫停
        if cmd[0] in {"p", "play"} and len(cmd) > 1:
            song = ""
            for i in range(1, len(cmd)):
                song += cmd[i] + " "
            playing_music_data = play_song(song[:-1])
        elif cmd[0] in {"p", "play"} and str(player.get_state()) == "State.Paused":
            player.play()
            print("繼續撥放")
        elif cmd[0] in {"p", "pause"} and str(player.get_state()) == "State.Playing":
            player.pause()
            print("已暫停")

        #指令: 循環
        elif cmd[0] == "loop":
            if loop == "none":
                loop = "list"
                print("🔁 清單循環開啟")
            elif loop == "list":
                loop = "single"
                print("🔁 單曲循環開啟" if loop else "🔁 循環關閉")
            else:
                loop = "none"
                print("🔁 循環關閉")
        
        #指令: 隨機播放
        elif cmd[0]in {"random", "rand"}:
            random_song = not random_song
            print("🎲 隨機撥放開啟" if random_song else "🎲 隨機播放關閉")

        #指令: 搜索歌曲
        elif cmd[0] in {"s", "search"} and len(cmd) > 1:
            playlist["搜尋結果"] = []
            #標籤
            search_filter = {"@":"演出者", "#":"專輯"}
            filter = search_filter.get(cmd[1][0], "檔名")
            if filter != "檔名": cmd[1] = cmd[1][1:]
            print(f"🎤 [{filter}] 包含 {cmd[1]} 的歌曲:")
            idx = 0
            for song_data in metadata_list:
                if cmd[1].lower() in song_data[filter].lower():
                    idx += 1 
                    playlist["搜尋結果"].append(song_data["檔名"].lower())
                    print(str(idx) + ". 🎵 曲名：" + song_data["檔名"] + " 🎤 演出者: " + song_data["演出者"] + "  💿 專輯: " + song_data["專輯"])
            print(" >> p [編號] 播放")
        
        #指令:　新增撥放清單
        elif cmd[0] in {"l", "list"}:
            #查詢所有清單
            if len(cmd) == 1:
                idx = 0
                print("📂 所有清單:")
                for idx, lists in enumerate(playlist, 1):
                    print(f" {idx}. [{lists}]，共包含 {len(playlist[lists])} 首歌")
            #搜尋對應名稱撥放清單
            elif len(cmd) == 2:
                if cmd[1] in playlist:
                    print("📄 在" + cmd[1] + "的歌曲:")
                    idx = 0
                    for song_data in metadata_list:
                        if song_data["檔名"].lower() in playlist[cmd[1]]:
                            idx += 1
                            playlist["搜尋結果"].append(song_data["檔名"].lower())
                            print(" " + str(idx) + ". 🎵 曲名：" + song_data["檔名"] + " 🎤 演出者: " + song_data["演出者"] + "  💿 專輯: " + song_data["專輯"])
                    print(" >> p [編號] 播放")
                else:
                    print("❌ " + cmd[1] + "清單不存在!")
            
            #新增/刪除撥放清單
            elif cmd[1] in {"new", "del"}:
                if cmd[1] == "new" and cmd[2] not in playlist:
                    playlist.update({cmd[2] : []})
                    print("✅ 已成功新增 " + cmd[2] + " 清單!")
                elif cmd[1] == "new":
                    print("撥放清單已存在")
                if cmd[1] == "del" and cmd[2] not in {"全部歌曲", "收藏歌曲", "搜尋結果", "new", "del", "add", "remove"} and cmd[2] in playlist:
                    del playlist[cmd[2]]
                    print("🗑️ 已成功刪除 " + cmd[2] + " 清單!")
                elif cmd[1] == "del":
                    print("❌ " + cmd[2] + " 為預設清單或不存在!")
            
            #在撥放清單中新增/刪除歌曲
            elif cmd[1] in {"add", "remove"}:
                song = ""
                for i in range(3, len(cmd)):
                    song += cmd[i] + " "
                song = song[:-1].lower()
                if cmd[1] == "add" and cmd[2] in playlist and song in playlist["全部歌曲"] and cmd[2] not in playlist[cmd[2]] and cmd[2] not in {"全部歌曲", "搜尋結果"}:
                    playlist[cmd[2]].append(song)
                    print("✅ 已將 " + song + " 新增至 " + cmd[2] + " 清單!")
                elif cmd[1] == "add":
                    print("❌ 查無此清單或歌曲!")
                if cmd[1] == "remove" and cmd[2] in playlist and song in playlist[cmd[2]]:
                    playlist[cmd[2]].remove(song)
                    print("🗑️ 已從清單 " + cmd[2] + " 移除" + song)
                elif cmd[1] == "remove":
                    print("❌ 查無此清單或歌曲!")
            
        #指令: 調整/設定音量:
        elif cmd[0] in {"v", "volume"}:
            if len(cmd) == 1 and str(player.get_state()) == "State.Playing":
                print("目前音量為:" + str(player.audio_get_volume()) + "%")
            elif len(cmd) == 2 and str(player.get_state()) == "State.Playing":
                volume = int(cmd[1])
                player.audio_set_volume(int(cmd[1]))
                print("將音量設為" + cmd[1] + "%")
        
        #指令: 設定/查詢播放速度
        elif cmd[0] in {"ss", "speed"}:
            if len(cmd) == 1 and str(player.get_state()) == "State.Playing":
                print("目前播放速度為" + str(round(player.get_rate(), 2)) + "x")
            elif len(cmd) == 2 and str(player.get_state()) == "State.Playing":
                player.set_rate(float(cmd[1]))
                print("以" + cmd[1] + "倍速撥放")
        
        #指令: 查詢/設定播放進度
        elif cmd[0] in {"t", "time"}:
            if len(cmd) == 1 and str(player.get_state()) == "State.Playing":
                print(f"播放進度 {format_time(player.get_time())} / {format_time(player.get_length())}")
            elif len(cmd) == 2:
                cmd[1] = int(cmd[1]) * 1000
                player.set_time(cmd[1])
                print("已從" + format_time(cmd[1]) + "開始撥放")

        #指令: 瑞克搖
        elif cmd[0] == "rickroll" and len(cmd) == 1:
            playing_music_data = play_song("Never Gonna Give You Up")
            print("🎁 You've been rolled.")

        #指令: 結束    
        elif cmd[0] == "exit" and len(cmd) == 1:
            print("關閉")
            running = False
        
        #指令: 簡介
        elif cmd[0] in {"h", "help"} and len(cmd) == 1:
            print("""🎧 MusicPlayer 1.0 指令列表：
▶ 撥放/暫停：
  >> play [音檔]              播放指定音檔
  >> play                    繼續播放目前音樂
  >> pause                   暫停播放
  >> loop                    循環播放
🔊 音訊控制：
  >> volume [音量(%)]        調整音量
  >> speed [速度]            調整播放速度
  >> time                    顯示播放進度
  >> set_time [秒數]         跳轉至指定秒數
🔎 搜尋歌曲：
  >> search [關鍵字]         依照檔名搜尋
  >> search @演出者          搜尋演出者
  >> search #專輯名          搜尋專輯名稱
📂 播放清單管理：
  >> list                    顯示所有播放清單
  >> list [清單名]           顯示指定清單內容
  >> list new [清單名]       新增清單
  >> list del [清單名]       刪除清單
  >> list add [清單] [歌曲]  將歌曲加入清單
  >> list remove [清單] [歌曲] 從清單移除歌曲
🎲 彩蛋指令：
  >> rickroll                瑞克搖
❌ 結束程式：
  >> exit                    關閉播放器
""")

        #無效指令
        else:
            print("無效指令!")
        cmd = []
    
    for event in pygame.event.get():
        result = input_box.handle_event(event)
        if result is not None:
            cmd = result
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if is_hovering(160, 210, 515, 570): player.pause()
    #歌曲結束事件
    state = player.get_state()
    if state == vlc.State.Ended and not song_ended:
        song_ended = True
        if loop == "list":
            if len(playlist["搜尋結果"]) <= playlist["搜尋結果"].index(playing_music_data["name"].lower()) + 1:
                play_song(playlist["搜尋結果"][0])
        elif loop == "single":
            play_song(playing_music_data["name"])
        if random_song and len(playlist["搜尋結果"]) > 0 and loop != "single":
            randResult = random.choices(playlist["搜尋結果"])[0]
            playing_music_data = play_song(randResult)
    elif state != vlc.State.Ended:
        song_ended = False
    
    #更新畫面
    if GUI:
        #顯示播放中歌曲資訊
        if state != vlc.State.Ended and isinstance(playing_music_data, dict) and playing_music_data.get("name", False):
            #顯示圖片
            render_img(playing_music_data["img"], 60, 60)
            pygame.draw.rect(screen, DGRAY, (60, 60, 240, 240), 5)
            #顯示名稱、演出者
            text(playing_music_data.get("name", "沒有歌曲正在撥放"), 25, 180, 380, WHITE)
            text(playing_music_data.get("artist", "未知演出者"), 20, 180, 420, WHITE)
            if playing_music_data.get("album", "無") not in ["無", "未知專輯"]: text(playing_music_data["album"], 20, 180, 450, WHITE)
            #顯示播放進度
            pygame.draw.rect(screen, BGRAY, (60, 486, 240, 8))
            #旋鈕位置 // 座標: (60 + 240 * (播放進度%), 490)
            if player.get_length() > 0:
                progress = player.get_time() / player.get_length()
                text(format_time(player.get_time()), 20, 30, 475, WHITE)
                text(format_time(player.get_length()), 20, 330, 475, WHITE)
            pygame.draw.rect(screen, GRAY, (60, 486, 240 * progress, 8))
            pygame.draw.rect(screen, BLACK, (60, 486, 240, 8), 2)
            if is_hovering_circle(60 + 249 * progress, 490, 10): knob_color = GRAY
            else: knob_color = BLACK
            pygame.draw.circle(screen, DGRAY, (60 + 240 * progress, 490), 9)
            pygame.draw.circle(screen, knob_color, (60 + 240 * progress, 490), 9, 3)
        # 顯示播放/暫停按鈕
        def get_button_color(x1, x2, y1, y2):
            return GRAY if is_hovering(x1, x2, y1, y2) else BLACK
        
        if state != vlc.State.Paused:
            pause_button_color = get_button_color(160, 210, 515, 570)
            pygame.draw.rect(screen, DGRAY, (160, 523, 15, 45))
            pygame.draw.rect(screen, pause_button_color, (160, 523, 15, 45), 3)
            pygame.draw.rect(screen, DGRAY, (185, 523, 15, 45))
            pygame.draw.rect(screen, pause_button_color, (185, 523, 15, 45), 3)
        else:
            play_button_color = get_button_color(160, 210, 523, 570)
            pygame.draw.polygon(screen, DGRAY, [(160, 523), (160, 570), (200, 547)])
            pygame.draw.polygon(screen, play_button_color, [(160, 523), (160, 570), (200, 547)], 3)

        # 顯示上一首與下一首
        if playing_music_data.get("name"):
            # 下一首按鈕
            next_button_color = get_button_color(230, 280, 515, 570)
            pygame.draw.polygon(screen, DGRAY, [(230, 530), (230, 560), (260, 545)])
            pygame.draw.rect(screen, DGRAY, (260, 530, 10, 30))
            pygame.draw.polygon(screen, next_button_color, [(230, 530), (230, 560), (260, 545)], 3)
            pygame.draw.rect(screen, next_button_color, (260, 530, 10, 30), 3)

            # 上一首按鈕（鏡射）
            prev_button_color = get_button_color(90, 140, 515, 570)
            pygame.draw.polygon(screen, DGRAY, [(130, 530), (130, 560), (100, 545)])
            pygame.draw.rect(screen, DGRAY, (90, 530, 10, 30))
            pygame.draw.polygon(screen, prev_button_color, [(130, 530), (130, 560), (100, 545)], 3)
            pygame.draw.rect(screen, prev_button_color, (90, 530, 10, 30), 3)
        
        
        input_box.update()
        input_box.draw(screen)
        pygame.display.flip()

pygame.quit()
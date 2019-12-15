import os
import json
import time
from datetime import datetime
from settings import STATIC_DIR, FULL_VIDEOS_DIR, CUT_VIDEOS_DIR, TRANSITION_VIDEOS_DIR, IMG_DIR,\
    FONTS_DIR, CONTENT_DIR, TS_CUT_VIDEOS_DIR, AUDIOS_DIR, TS_TRANSITION_VIDEOS_DIR, VIDEOS_DIR
from tasks import video, chart, youtube


def create_video(chart_dict):
    chart_dict.sort(key=lambda dictionary: dictionary['position'], reverse=True)
    concat_list = [os.path.join(VIDEOS_DIR, "intro_ts")]

    for row in chart_dict:
        # set vars
        full_video_name = f'{row["youtube_id"]}.mp4'
        full_video = os.path.join(FULL_VIDEOS_DIR, full_video_name)

        cut_video_name = f'{row["youtube_id"]}.mp4'
        cut_video = os.path.join(CUT_VIDEOS_DIR, cut_video_name)

        ts_cut_video_name = f'{row["youtube_id"]}.ts'
        ts_cut_video = os.path.join(TS_CUT_VIDEOS_DIR, ts_cut_video_name)

        transition_video_name = f'{row["position"]:03d}.mp4'
        transition_video = os.path.join(TRANSITION_VIDEOS_DIR, transition_video_name)

        ts_transition_video_name = f'{row["position"]:03d}.ts'
        ts_transition_video = os.path.join(TS_TRANSITION_VIDEOS_DIR, ts_transition_video_name)

        font = os.path.join(FONTS_DIR, "SourceSansPro-Regular.ttf")
        blank_img = os.path.join(IMG_DIR, "blank.png")
        silence_audio = os.path.join(AUDIOS_DIR, "silence_mp3")

        # run funcs
        video.download(f'https://www.youtube.com/watch?v={row["youtube_id"]}', full_video)
        video.create_cut(full_video, cut_video, row, blank_img, font)
        video. create_transition(transition_video, row["position"], blank_img, silence_audio, font)
        video.convert_to_ts(cut_video_name, CUT_VIDEOS_DIR, TS_CUT_VIDEOS_DIR)
        video.convert_to_ts(transition_video_name, TRANSITION_VIDEOS_DIR, TS_TRANSITION_VIDEOS_DIR)

        concat_list.append(ts_transition_video)
        concat_list.append(ts_cut_video)

    video.concat(concat_list, CONTENT_DIR)


def update_general_chart(general_chart, music_base, amount_pos):
    # Добавление youtube_id в chart
    for chart_row in general_chart[:amount_pos]:
        for music_base_row in music_base:
            if chart_row["yandex_id"] == music_base_row["yandex_id"]:
                if music_base_row.get("youtube_id", "") == "":
                    chart_row["youtube_id"] = youtube.get_youtube_id(chart_row["artist"], chart_row["title"])
                    time.sleep(0.5)
                else:
                    chart_row["youtube_id"] = music_base_row["youtube_id"]
                break

    return general_chart


def get_chart_dict(amount_pos):
    with open(os.path.join(STATIC_DIR, "music_base.json"), "r", encoding="utf-8") as f:
        music_base = json.load(f)

    general_chart = chart.get_general_chart(music_base)
    general_chart = update_general_chart(general_chart, music_base, amount_pos)
    music_base = chart.update_music_base(music_base, general_chart)

    with open(os.path.join(STATIC_DIR, "music_base.json"), "w", encoding="utf-8") as f:
        json.dump(music_base, f)

    with open(os.path.join(STATIC_DIR, f'general_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json'),
              "w", encoding="utf-8") as f:
        json.dump(general_chart, f)

    return general_chart


def main():
    amount_pos = 50
    general_chart = get_chart_dict(amount_pos)
    general_chart = general_chart[:amount_pos]
    general_chart.sort(key=lambda dictionary: dictionary['position'], reverse=True)
    create_video(general_chart)


if __name__ == "__main__":
    main()


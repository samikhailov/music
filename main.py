import os
import json
from datetime import datetime
from settings import STATIC_DIR, FULL_VIDEOS_DIR, CUT_VIDEOS_DIR, TRANSITION_VIDEOS_DIR, IMG_DIR,\
    FONTS_DIR, CONTENT_DIR, TS_CUT_VIDEOS_DIR, SOUND_DIR, TS_TRANSITION_VIDEOS_DIR
from tasks import video, base, youtube


def create_video(chart_dict):
    chart_dict.sort(key=lambda dictionary: dictionary['position'], reverse=True)
    concat_list = ["D:/Documents/Code/music/static/videos/intro_ts"]

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
        silence_audio = os.path.join(SOUND_DIR, "silence")

        # run funcs
        video.download(f'https://www.youtube.com/watch?v={row["youtube_id"]}', full_video)
        video.create_cut(full_video, cut_video, row, blank_img, font)
        video. create_transition(transition_video, row["position"], blank_img, silence_audio, font)
        video.convert_to_ts(cut_video_name, CUT_VIDEOS_DIR, TS_CUT_VIDEOS_DIR)
        video.convert_to_ts(transition_video_name, TRANSITION_VIDEOS_DIR, TS_TRANSITION_VIDEOS_DIR)

        concat_list.append(ts_transition_video)
        concat_list.append(ts_cut_video)

    video.concat(concat_list, CONTENT_DIR)


def get_chart_dict(amount_pos, chart=None):
    with open(f"{os.path.join(STATIC_DIR, 'music_base.json')}", "r", encoding="utf-8") as f:
        music_base = json.load(f)

    if chart is None:
        chart = base.get_general_chart()

    # Добавление youtube_id в chart
    for chart_row in chart[:amount_pos]:
        for music_base_row in music_base:
            if chart_row["yandex_id"] == music_base_row["yandex_id"]:
                if music_base_row.get("youtube_id") is None or music_base_row.get("youtube_id") == "":
                    chart_row["youtube_id"] = youtube.get_youtube_id(chart_row["artist"], chart_row["title"])
                else:
                    chart_row["youtube_id"] = music_base_row["youtube_id"]
                break

    music_base = base.append_music_base(music_base, chart)

    with open("static/music_base.json", "w", encoding="utf-8") as f:
        json.dump(music_base, f)

    with open(f'static/chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', "w", encoding="utf-8") as f:
        json.dump(chart, f)

    return chart


def main():
    amount_pos = 25
    with open("static/general_chart 19-12-15 18-41-43.json", "r", encoding="utf-8") as f:
        chart = json.load(f)
    chart = get_chart_dict(amount_pos, chart)
    chart = chart[:amount_pos]
    chart.sort(key=lambda dictionary: dictionary['position'], reverse=True)
    create_video(chart)


if __name__ == "__main__":
    main()


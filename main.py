import os
import json
from datetime import datetime
from settings import (STATIC_DIR, FULL_VIDEOS_DIR, CUT_VIDEOS_DIR, TRANSITION_VIDEOS_DIR,
                      CONTENT_DIR, TS_CUT_VIDEOS_DIR, TS_TRANSITION_VIDEOS_DIR, VIDEOS_DIR, MP3_VIDEOS_DIR)
from tasks import video, data


def create_video(chart):
    with open(os.path.join(STATIC_DIR, "music_base.json"), "r", encoding="utf-8") as f:
        base = json.load(f)

    chart.sort(key=lambda dictionary: dictionary['position'], reverse=True)
    concat_list = [os.path.join(VIDEOS_DIR, "intro_ts")]
    # concat_list = []

    for chart_track in chart:
        # set vars
        full_video = os.path.join(FULL_VIDEOS_DIR, f'{chart_track["youtube_id"]}.mp4')
        mp3_video = os.path.join(MP3_VIDEOS_DIR, f'{chart_track["youtube_id"]}.mp3')

        cut_video_name = f'{chart_track["youtube_id"]}.mp4'
        cut_video = os.path.join(CUT_VIDEOS_DIR, cut_video_name)

        ts_cut_video_name = f'{chart_track["youtube_id"]}.ts'
        ts_cut_video = os.path.join(TS_CUT_VIDEOS_DIR, ts_cut_video_name)

        transition_video_name = f'{chart_track["position"]:03d}.mp4'
        transition_video = os.path.join(TRANSITION_VIDEOS_DIR, transition_video_name)

        ts_transition_video_name = f'{chart_track["position"]:03d}.ts'
        ts_transition_video = os.path.join(TS_TRANSITION_VIDEOS_DIR, ts_transition_video_name)

        # run funcs
        video.download(f'https://www.youtube.com/watch?v={chart_track["youtube_id"]}', full_video)
        video.convert_to_mp3(full_video, MP3_VIDEOS_DIR)

        # Не в тему. Добавление в базу время старта видео
        start_video = "01:20"
        for base_track in base:
            if chart_track["yandex_id"] == base_track["yandex_id"]:
                if base_track.get("video_start", "") == "":
                    chart_track["video_start"] = video.get_video_start(mp3_video, clip_length=8)
                else:
                    chart_track["video_start"] = base_track["video_start"]
                start_video = chart_track["video_start"]
                break

        video.cut_video(full_video, cut_video, chart_track, start_video)
        video.create_transition(transition_video, chart_track["position"])
        video.convert_to_ts(cut_video_name, CUT_VIDEOS_DIR, TS_CUT_VIDEOS_DIR)
        video.convert_to_ts(transition_video_name, TRANSITION_VIDEOS_DIR, TS_TRANSITION_VIDEOS_DIR)

        concat_list.append(ts_transition_video)
        concat_list.append(ts_cut_video)

    data.update_music_base(chart)
    video.concat(concat_list, CONTENT_DIR)


def get_chart_dict(amount_pos):

    general_chart = data.get_general_chart()
    general_chart = data.update_general_chart(general_chart, amount_pos)
    data.update_music_base(general_chart)

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


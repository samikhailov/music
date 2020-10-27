import os
import json
from datetime import datetime
from tasks import video, data
from tasks.models import *
from settings import *


def create_video(chart, amount_pos):
    chart.sort(key=lambda dictionary: dictionary['position'])
    chart = chart[:amount_pos]
    chart.sort(key=lambda dictionary: dictionary['position'], reverse=True)
    concat_list = [os.path.join(VIDEOS_DIR, "intro_ts")]

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
        track = Music.get_or_none(Music.youtube_id == chart_track["youtube_id"])
        if track.video_start is None:
            track = data.update_video_start(mp3_video, chart_track["youtube_id"])

        video.cut_video(full_video, cut_video, chart_track, str(track.video_start))
        video.create_transition(transition_video, chart_track["position"])
        video.convert_to_ts(cut_video_name, CUT_VIDEOS_DIR, TS_CUT_VIDEOS_DIR)
        video.convert_to_ts(transition_video_name, TRANSITION_VIDEOS_DIR, TS_TRANSITION_VIDEOS_DIR)

        concat_list.append(ts_transition_video)
        concat_list.append(ts_cut_video)

    video.concat(concat_list, CONTENT_DIR)


def main():
    amount_pos = 50
    general_chart = data.get_general_chart()
    general_chart = data.update_general_chart(general_chart, amount_pos)

    with open(os.path.join(CONTENT_DIR, f'general_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json'),
              "w", encoding="utf-8") as f:
        json.dump(general_chart, f)

    create_video(general_chart, amount_pos)


if __name__ == "__main__":
    main()


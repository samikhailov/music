import os
import json
import pandas as pd
from settings import STATIC_DIR, FULL_VIDEOS_DIR, CUT_VIDEOS_DIR, TRANSITION_VIDEOS_DIR, IMG_DIR,\
    FONTS_DIR, CONTENT_DIR, TS_CUT_VIDEOS_DIR, SOUND_DIR, TS_TRANSITION_VIDEOS_DIR

from tasks import video, yandex


def create_video(chart_dict):
    concat_list = []

    for row in csv_file_dict:
        # set vars
        full_video_name = f'{row["id"]:05d}-{row["youtube_id"]}.mp4'
        full_video = os.path.join(FULL_VIDEOS_DIR, full_video_name)

        cut_video_name = f'{row["id"]:05d}-{row["youtube_id"]}.mp4'
        cut_video = os.path.join(CUT_VIDEOS_DIR, cut_video_name)

        ts_cut_video_name = f'{row["id"]:05d}-{row["youtube_id"]}.ts'
        ts_cut_video = os.path.join(TS_CUT_VIDEOS_DIR, ts_cut_video_name)

        transition_video_name = f'{row["rank"]:03d}.mp4'
        transition_video = os.path.join(TRANSITION_VIDEOS_DIR, transition_video_name)

        ts_transition_video_name = f'{row["rank"]:03d}.ts'
        ts_transition_video = os.path.join(TS_TRANSITION_VIDEOS_DIR, ts_transition_video_name)

        font = os.path.join(FONTS_DIR, "SourceSansPro-Regular.ttf")
        blank_img = os.path.join(IMG_DIR, "blank.png")
        silence_audio = os.path.join(SOUND_DIR, "silence")

        # run funcs
        video.download(f'https://www.youtube.com/watch?v={row["youtube_id"]}', full_video)
        video.create_cut(full_video, cut_video, row, blank_img, font)
        video. create_transition(transition_video, row["rank"], blank_img, silence_audio, font)
        video.convert_to_ts(cut_video_name, CUT_VIDEOS_DIR, TS_CUT_VIDEOS_DIR)
        video.convert_to_ts(transition_video_name, TRANSITION_VIDEOS_DIR, TS_TRANSITION_VIDEOS_DIR)

        concat_list.append(ts_transition_video)
        concat_list.append(ts_cut_video)

    video.concat(concat_list, CONTENT_DIR)


if __name__ == "__main__":
    '''
    csv_file = os.path.join(STATIC_DIR, "chart 001.csv")
    csv_file_dict = pd.read_csv(csv_file, sep=";").to_dict('records')
    for i in csv_file_dict:
        i["id"] = int(i["id"])
    csv_file_dict.sort(key=lambda dictionary: dictionary['id'], reverse=True)
    create_video(csv_file_dict)
    '''

    with open("a12.json", "w", encoding="utf-8") as f:
        json.dump(yandex.get_chart_info(), f)

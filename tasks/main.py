from settings import STATIC_DIR, FULL_VIDEOS_DIR, CUT_VIDEOS_DIR, TRANSITION_VIDEOS_DIR, IMG_DIR,\
    FONTS_DIR, CONTENT_DIR, TS_CUT_VIDEOS_DIR, TS_TRANSITION_VIDEOS_DIR, SOUND_DIR
import pandas as pd
import json
import youtube_dl
import os.path
import ffmpeg


def download_video(video_url, video_title):
    """
    Download a video using youtube url and video title
    """

    ydl_opts = {
        'format': "bestvideo[height<=?1080][ext=mp4]+bestaudio[ext=m4a]",
        'outtmpl': video_title,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(video_url, download=True)


def set_video_requirements(input_stream):
    vid = (
        input_stream
        .filter("fps", fps=25)
        .filter("scale", w=1920, h=1080, force_original_aspect_ratio="decrease")
        .filter("pad", w=1920, h=1080, x=960, y=540)
    )

    aud = input_stream.audio

    joined = ffmpeg.concat(vid, aud, v=1, a=1)

    return joined


def draw_titles(artist, song):
    output_stream = (
        ffmpeg
        .input(os.path.join(IMG_DIR, "blank_img.png"), loop=1, t="00:04")
        .drawtext(text=artist, x=200, y=800, fontsize=56, fontcolor="white", shadowx=2, shadowy=2,
                  fontfile=os.path.join(FONTS_DIR, "SourceSansPro-Regular.ttf"))
        .drawtext(text=song, x=200, y=880, fontsize=44, fontcolor="white", shadowx=2, shadowy=2,
                  fontfile=os.path.join(FONTS_DIR, "SourceSansPro-Regular.ttf"))

    )

    return output_stream


def create_transition(rank):
    duration = 1
    input_stream = ffmpeg.input(os.path.join(SOUND_DIR, "blank_part.mp4"), ss=0, t=duration)
    aud = (
        input_stream.audio
        .filter_('atrim')
        .filter_('asetpts', 'PTS-STARTPTS')
    )
    vid = (
        ffmpeg
        .input(os.path.join(IMG_DIR, "blank_img.png"), loop=1, t=duration)
        .drawtext(text=rank, x="(w-text_w)/2", y="(h-text_h)/2", fontsize=160,
                  fontfile=os.path.join(FONTS_DIR, "SourceSansPro-Regular.ttf"))
    )

    joined = ffmpeg.concat(vid, aud, v=1, a=1).node
    output = ffmpeg.output(joined[0], joined[6], os.path.join(TRANSITION_VIDEOS_DIR, f"{rank:03d}.mp4"))
    output.run()


def convert_to_ts(file_name, source_dir, output_dir):
    """
    Функция для конвертации mp4 в ts.
    Файлы .ts нужны для функции concat, т.к. она не поддерживатся для mp4.
    :param source_dir: папка, в которой хранятся файлы для конвертации.
    :param file_name: имя файла с расширением.
    :param output_dir: папка, в которую сохранятся ts файлы.
    :return: None
    """
    file_path = os.path.join(source_dir, file_name)
    file_name_ts = file_name.split(".")[0] + ".ts"

    (
        ffmpeg
        .input(file_path)
        .output(os.path.join(output_dir, file_name_ts), c='copy', f='mpegts', **{'bsf:v': 'h264_mp4toannexb'})
        .run()
    )


def concat(video_list, output_path):
    video_list_str = "|".join(video_list)
    (
        ffmpeg
        .input('concat:' + video_list_str)
        .output( os.path.join(output_path, 'out.ts'), c='copy').run()
    )


if __name__ == "__main__":
    csv_file_dir = os.path.join(STATIC_DIR, "chart 001.csv")
    csv_file = pd.read_csv(csv_file_dir, sep=";").to_dict('records')
    concat_list = []

    for row in csv_file[5:6]:
        full_video = os.path.join(FULL_VIDEOS_DIR, f'{row["id"]:05d}-{row["youtube_id"]}.mp4')
        cut_video_name = f'{row["id"]:05d}-{row["youtube_id"]}.mp4'
        cut_video = os.path.join(CUT_VIDEOS_DIR, cut_video_name)
        ts_cut_video_name = f'{row["id"]:05d}-{row["youtube_id"]}.ts'
        ts_cut_video = os.path.join(TS_CUT_VIDEOS_DIR, ts_cut_video_name)
        transition_video_name = f'{row["rank"]:03d}.mp4'
        transition_video = os.path.join(TRANSITION_VIDEOS_DIR, transition_video_name)
        ts_transition_video_name = f'{row["rank"]:03d}.ts'
        ts_transition_video = os.path.join(TS_TRANSITION_VIDEOS_DIR, ts_transition_video_name)

        if os.path.exists(full_video) is False:
            download_video(f'https://www.youtube.com/watch?v={row["youtube_id"]}', full_video)

        if os.path.exists(cut_video) is False:
            start = 40
            duration = 8
            stream = ffmpeg.input(full_video, ss=start, t=duration)
            stream = set_video_requirements(stream)
            titles = draw_titles(row["artist"], row["song"]).setpts("PTS-STARTPTS+40")
            stream = ffmpeg.overlay(stream, titles, eof_action="pass").setpts("PTS-STARTPTS")
            output = ffmpeg.output(stream, cut_video)
            output.run()

        if os.path.exists(transition_video) is False:
            create_transition(row["rank"])

        if os.path.exists(ts_cut_video) is False:
            convert_to_ts(cut_video_name, CUT_VIDEOS_DIR, TS_CUT_VIDEOS_DIR)

        if os.path.exists(ts_transition_video) is False:
            convert_to_ts(transition_video_name, TRANSITION_VIDEOS_DIR, TS_TRANSITION_VIDEOS_DIR)

        concat_list.append(ts_transition_video)
        concat_list.append(ts_cut_video)
    # print(concat_list)
    # concat(concat_list, CONTENT_DIR)

from settings import CONTENT_DIR, FULL_VIDEOS_DIR, CUT_VIDEOS_DIR
import pandas as pd
import json
import youtube_dl
import os.path
import ffmpeg


def download_video(video_url, video_title):
    """
    Download a video using youtube url and video title
    """

    outtmpl = f"{FULL_VIDEOS_DIR}/{video_title}" + '.%(ext)s'
    ydl_opts = {
        'format': "bestvideo[height<=?1080][ext=mp4]+bestaudio[ext=m4a]",
        'outtmpl': outtmpl,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(video_url, download=True)


def trim(input_path, output_path, start=30, end=38):
    input_stream = ffmpeg.input(input_path)

    vid = (
        input_stream.video
        .trim(start=start, end=end)
        .filter("fps", fps=25)
        .filter("scale", w=1920, h=1080, force_original_aspect_ratio="decrease")
        .filter("pad", w=1920, h=1080, x=960, y=360)
        .filter("setsar", sar=1)
        .setpts('PTS-STARTPTS')
    )
    aud = (
        input_stream.audio
        .filter_('atrim', start=start, end=end)
        .filter_('asetpts', 'PTS-STARTPTS')
    )

    joined = ffmpeg.concat(vid, aud, v=1, a=1).node
    output = ffmpeg.output(joined[0], joined[6], output_path)
    output.run()


def concat(concat_list, output_path):
    in_file0 = ffmpeg.input(concat_list[0])
    in_file1 = ffmpeg.input(concat_list[4])

    (
        ffmpeg
        .concat(in_file0, in_file1)
        .output(output_path)
        .run()
    )


if __name__ == "__main__":
    csv_file = pd.read_csv(CONTENT_DIR + "/text_data/chart 001.csv", sep=";").to_dict('records')

    for row in csv_file:
        if os.path.exists(os.path.join(FULL_VIDEOS_DIR, f'{row["id"]:05d}-{row["youtube_id"]}.mp4')) is False:
            download_video(f'https://www.youtube.com/watch?v={row["youtube_id"]}',
                           f'{row["id"]:05d}-{row["youtube_id"]}')
    for row in csv_file[:5]:
        if os.path.exists(os.path.join(CUT_VIDEOS_DIR, f'{row["id"]:05d}-{row["youtube_id"]}.mp4')) is False:
            trim(os.path.join(FULL_VIDEOS_DIR, f'{row["id"]:05d}-{row["youtube_id"]}.mp4'),
                 os.path.join(CUT_VIDEOS_DIR, f'{row["id"]:05d}-{row["youtube_id"]}.mp4'))

    input_list = [os.path.join(CUT_VIDEOS_DIR, f'{row["id"]:05d}-{row["youtube_id"]}.mp4') for row in csv_file]
    concat(input_list, "output_path.mp4")

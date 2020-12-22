import logging
import os
from datetime import datetime, timezone
import youtube_dl
from pychorus import find_and_output_chorus
import ffmpeg
from settings import MEDIA_DIR, ONE_TRACK_LENGTH, STATIC_DIR


def download_video(in_youtube_id, video_path):
    """
    Download a video using in_youtube_id and video path.
    """
    if os.path.exists(video_path):
        logging.info(f"Full video found in media (video_path={video_path})")
    else:
        logging.debug(f"Full video download has started (in_youtube_id={in_youtube_id})")
        ydl_opts = {
            "format": "bestvideo[height<=?1080][ext=mp4]+bestaudio[ext=m4a]",
            "outtmpl": video_path,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(in_youtube_id, download=True)
        logging.info(f"Full video downloaded (video_path={video_path})")


def download_videos(chart):
    for track in chart:
        download_video(track.in_youtube_id, os.path.join(MEDIA_DIR, "mp4_full", f"{track.in_youtube_id}.mp4"))


def convert_to_mp3(mp4_path):
    mp3_name = os.path.basename(mp4_path).split(".")[0] + ".mp3"
    mp3_path = os.path.join(MEDIA_DIR, "mp3", mp3_name)
    if os.path.exists(mp3_path):
        logging.info(f"Mp3 found in media (mp3_path={mp3_path})")
    else:
        logging.debug(f"Mp3 convert has started (mp3_path={mp3_path})")
        input_file = ffmpeg.input(mp4_path)
        audio = input_file.audio
        output_file = ffmpeg.output(audio, mp3_path)
        output_file.run()
        logging.info(f"Mp3 converted (mp3_path={mp3_path})")


def update_chorus_time(chart):
    for track in chart:
        mp4_path = os.path.join(MEDIA_DIR, "mp4_full", f"{track.in_youtube_id}.mp4")
        convert_to_mp3(mp4_path)
    for track in chart:
        if track.chorus_start:
            logging.info(f"Chorus start time found (id={track.id}, chorus_start={track.chorus_start})")
        else:
            logging.debug(f"Chorus find has started (id={track.id})")
            mp3_path = os.path.join(MEDIA_DIR, "mp3", f"{track.in_youtube_id}.mp3")
            chorus_start_sec = find_and_output_chorus(mp3_path, None, 8)
            track.chorus_start = datetime.fromtimestamp(chorus_start_sec, timezone.utc).time()
            track.save()
            logging.info(f"Chorus found (id={track.id}, chorus_start={track.chorus_start})")
    return chart


def set_requirements(in_stream, duration):
    aud = in_stream.audio.filter("afade", type="in", duration=0.5).filter(
        "afade", type="out", start_time=duration - 0.5, duration=0.5
    )
    vid = (
        in_stream.video.filter_("fps", fps=25)
        .filter_("scale", w=1920, h=1080, force_original_aspect_ratio="decrease")
        .filter_("pad", w=1920, h=1080, x="(ow-iw)/2", y="(oh-ih)/2")
        .filter("fade", type="in", duration=0.5)
        .filter("fade", type="out", start_time=duration - 0.5, duration=0.5)
    )

    return ffmpeg.concat(vid, aud, v=1, a=1)


def draw_titles(artist, title):
    duration = ONE_TRACK_LENGTH - 3
    font = os.path.join(STATIC_DIR, "fonts", "SourceSansPro-Regular.ttf")
    output_stream = (
        ffmpeg.input(os.path.join(STATIC_DIR, "images", "blank.png"), loop=1, t=duration)
        .drawtext(text=artist, x=200, y=800, fontsize=56, fontcolor="white", shadowx=2, shadowy=2, fontfile=font)
        .drawtext(text=title, x=200, y=880, fontsize=44, fontcolor="white", shadowx=2, shadowy=2, fontfile=font)
    )

    return output_stream


def trim_video(track):
    mp4_trimmed_path = os.path.join(MEDIA_DIR, "mp4_trimmed", f"{track.in_youtube_id}.mp4")
    if os.path.exists(mp4_trimmed_path):
        logging.info(f"Trimmed video found in media (mp4_trimmed_path={mp4_trimmed_path})")
    else:
        logging.debug(f"Mp4 trim has started (in_youtube_id={track.in_youtube_id})")
        mp4_full_path = os.path.join(MEDIA_DIR, "mp4_full", f"{track.in_youtube_id}.mp4")
        stream = ffmpeg.input(mp4_full_path, ss=track.chorus_start, t=ONE_TRACK_LENGTH)
        stream = set_requirements(stream, ONE_TRACK_LENGTH)
        titles = draw_titles(track.artist, track.title).setpts("PTS-STARTPTS+40")
        stream = ffmpeg.overlay(stream, titles, eof_action="pass").setpts("PTS-STARTPTS")
        output_file = ffmpeg.output(stream, mp4_trimmed_path)
        output_file.run()
        logging.info(f"Trimmed video done (mp4_trimmed_path={mp4_trimmed_path})")


def trim_videos(chart):
    for track in chart:
        trim_video(track)


def create_transition(position: int):
    mp4_transition_path = os.path.join(MEDIA_DIR, "mp4_transitions", f"{position:03d}.mp4")
    if os.path.exists(mp4_transition_path):
        logging.info(f"Mp4 transition found in media (mp4_transition_path={mp4_transition_path})")
    else:
        duration = 1.3
        font = os.path.join(STATIC_DIR, "fonts", "SourceSansPro-Regular.ttf")
        silence_audio = os.path.join(STATIC_DIR, "audios", "silence_mp3")

        video_stream = ffmpeg.input(os.path.join(STATIC_DIR, "images", "black.png"), loop=1, t=duration)
        vid = (
            video_stream.video.drawtext(
                text=position, x="(w-text_w)/2", y="(h-text_h)/2", fontsize=200, fontfile=font, fontcolor="white"
            )
            .filter("fade", type="in", duration=0.3)
            .filter("fade", type="out", start_time=duration - 0.3, duration=0.3)
        )

        audio_stream = ffmpeg.input(silence_audio, t=duration)
        aud = audio_stream.audio

        joined = ffmpeg.concat(vid, aud, v=1, a=1)
        output = ffmpeg.output(joined, mp4_transition_path)
        output.run()


def create_transitions(chart):
    for track in chart:
        create_transition(track.position)


def convert_to_ts(mp4_path, target_dir):
    """
    Функция для конвертации mp4 в ts.
    Файлы .ts нужны для функции concat, т.к. она не поддерживатся для mp4.
    :param mp4_path: путь до mp4.
    :param target_dir: директория, в которую сохранятся ts файлы.
    :return: ts_path
    """
    ts_name = os.path.basename(mp4_path).split(".")[0] + ".ts"
    ts_path = os.path.join(target_dir, ts_name)
    if os.path.exists(ts_path):
        logging.info(f"Ts video found in media (ts_path={ts_path})")
    else:
        (ffmpeg.input(mp4_path).output(ts_path, c="copy", f="mpegts", **{"bsf:v": "h264_mp4toannexb"}).run())
    return ts_path


def concat_videos(chart):
    video_list = [os.path.join(STATIC_DIR, "videos", "intro_ts")]
    for track in sorted(chart, key=lambda x: x.position, reverse=True):
        mp4_path = os.path.join(MEDIA_DIR, "mp4_transitions", f"{track.position:03d}.mp4")
        target_dir = os.path.join(MEDIA_DIR, "ts_transitions")
        ts_path = convert_to_ts(mp4_path, target_dir)
        video_list.append(ts_path)

        mp4_path = os.path.join(MEDIA_DIR, "mp4_trimmed", f"{track.in_youtube_id}.mp4")
        target_dir = os.path.join(MEDIA_DIR, "ts_trimmed")
        ts_path = convert_to_ts(mp4_path, target_dir)
        video_list.append(ts_path)

    concated_ts_path = os.path.join(MEDIA_DIR, f'{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.ts')
    ffmpeg.input("concat:" + "|".join(video_list)).output(concated_ts_path, c="copy").run()

    concated_mp4_path = os.path.splitext(concated_ts_path)[0] + ".mp4"
    ffmpeg.input(concated_ts_path).output(concated_mp4_path, vcodec="libx264", acodec="aac", vf="scale=iw/2:ih/2").run()

import os
import ffmpeg
import youtube_dl
from pychorus import find_and_output_chorus
from settings import IMG_DIR, FONTS_DIR, AUDIOS_DIR


def download(video_url, full_video):
    """
    Download a video using youtube url and video path.
    """
    if os.path.exists(full_video) is False:
        ydl_opts = {
            'format': "bestvideo[height<=?1080][ext=mp4]+bestaudio[ext=m4a]",
            'outtmpl': full_video,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(video_url, download=True)


def set_requirements(in_stream, duration):
    aud = (
        in_stream.audio
        .filter('afade', type='in', duration=0.5)
        .filter('afade', type='out', start_time=duration-0.5, duration=0.5)
    )
    vid = (
        in_stream.video
        .filter_("fps", fps=25)
        .filter_("scale", w=1920, h=1080, force_original_aspect_ratio="decrease")
        .filter_("pad", w=1920, h=1080, x="(ow-iw)/2", y="(oh-ih)/2")
        .filter('fade', type='in', duration=0.5)
        .filter('fade', type='out', start_time=duration-0.5, duration=0.5)
    )

    return ffmpeg.concat(vid, aud, v=1, a=1)


def draw_titles(artist, title):
    duration = 5
    font = os.path.join(FONTS_DIR, "SourceSansPro-Regular.ttf")
    output_stream = (
        ffmpeg
        .input(os.path.join(IMG_DIR, "blank.png"), loop=1, t=duration)
        .drawtext(text=artist, x=200, y=800, fontsize=56, fontcolor="white", shadowx=2, shadowy=2, fontfile=font)
        .drawtext(text=title, x=200, y=880, fontsize=44, fontcolor="white", shadowx=2, shadowy=2, fontfile=font)
    )

    return output_stream


def cut_video(full_video, cut_video, track, start_video):
    if os.path.exists(cut_video) is False:
        duration = 8

        stream = ffmpeg.input(full_video, ss=start_video, t=duration)
        stream = set_requirements(stream, duration)
        titles = draw_titles(track["artist"], track["title"]).setpts("PTS-STARTPTS+40")
        stream = ffmpeg.overlay(stream, titles, eof_action="pass").setpts("PTS-STARTPTS")
        output = ffmpeg.output(stream, cut_video)
        output.run()


def create_transition(transition_video, position):
    if os.path.exists(transition_video) is False:
        duration = 1.3
        font = os.path.join(FONTS_DIR, "SourceSansPro-Regular.ttf")
        silence_audio = os.path.join(AUDIOS_DIR, "silence_mp3")

        video_stream = ffmpeg.input(os.path.join(IMG_DIR, "black.png"), loop=1, t=duration)
        vid = (
            video_stream.video
            .drawtext(text=position, x="(w-text_w)/2", y="(h-text_h)/2", fontsize=200, fontfile=font, fontcolor="white")
            .filter('fade', type='in', duration=0.3)
            .filter('fade', type='out', start_time=duration-0.3, duration=0.3)
        )

        audio_stream = ffmpeg.input(silence_audio, t=duration)
        aud = audio_stream.audio

        joined = ffmpeg.concat(vid, aud, v=1, a=1)
        output = ffmpeg.output(joined, transition_video)
        output.run()


def convert_to_ts(input_file_name, source_dir, output_dir):
    """
    Функция для конвертации mp4 в ts.
    Файлы .ts нужны для функции concat, т.к. она не поддерживатся для mp4.
    :param source_dir: папка, в которой хранятся файлы для конвертации.
    :param input_file_name: имя файла с расширением.
    :param output_dir: папка, в которую сохранятся ts файлы.
    :return: None
    """
    output_file_name = input_file_name.split(".")[0] + ".ts"

    if os.path.exists(os.path.join(output_dir, output_file_name)) is False:
        input_file = os.path.join(source_dir, input_file_name)

        (
            ffmpeg
            .input(input_file)
            .output(os.path.join(output_dir, output_file_name), c='copy', f='mpegts', **{'bsf:v': 'h264_mp4toannexb'})
            .run()
        )


def convert_to_mp3(input_mp4, output_dir):
    output_file_name = input_mp4.replace('\\', '/').split("/")[-1].split(".")[0] + ".mp3"
    output_file = os.path.join(output_dir, output_file_name)
    if os.path.exists(output_file) is False:
        input = ffmpeg.input(input_mp4)
        audio = input.audio
        out = ffmpeg.output(audio, output_file)
        out.run()


def get_video_start(audio_file, clip_length=8):
    chorus_start_sec = find_and_output_chorus(audio_file, None, clip_length)
    result = f'{int(chorus_start_sec // 60):02d}:{int(chorus_start_sec % 60):02d}'
    return result


def concat(video_list, output_path):
    video_list_str = "|".join(video_list)
    (
        ffmpeg
        .input('concat:' + video_list_str)
        .output(os.path.join(output_path, 'out.ts'), c='copy').run()
    )

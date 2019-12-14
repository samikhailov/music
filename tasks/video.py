import os
import ffmpeg
import youtube_dl


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


def set_requirements(in_stream):
    aud = in_stream.audio
    vid = (
        in_stream.video
        .filter_("fps", fps=25)
        .filter_("scale", w=1920, h=1080, force_original_aspect_ratio="decrease")
        .filter_("pad", w=1920, h=1080, x=960, y=540)
    )

    return ffmpeg.concat(vid, aud, v=1, a=1)


def draw_titles(artist, title, blank_img, font):
    output_stream = (
        ffmpeg
        .input(blank_img, loop=1, t="00:05")
        .drawtext(text=artist, x=200, y=800, fontsize=56, fontcolor="white", shadowx=2, shadowy=2, fontfile=font)
        .drawtext(text=title, x=200, y=880, fontsize=44, fontcolor="white", shadowx=2, shadowy=2, fontfile=font)
    )

    return output_stream


def create_cut(full_video, cut_video, row, blank_img, font):
    if os.path.exists(cut_video) is False:
        start = "1:20"
        duration = 8
        stream = ffmpeg.input(full_video, ss=start, t=duration)
        stream = set_requirements(stream)
        titles = draw_titles(row["artist"], row["title"], blank_img, font).setpts("PTS-STARTPTS+40")
        stream = ffmpeg.overlay(stream, titles, eof_action="pass").setpts("PTS-STARTPTS")
        output = ffmpeg.output(stream, cut_video)
        output.run()


def create_transition(transition_video, position, blank_img, silence_audio, font):
    if os.path.exists(transition_video) is False:
        duration = 1

        video_stream = ffmpeg.input(blank_img, loop=1, t=duration)
        vid = (
            video_stream.video
            .drawtext(text=position, x="(w-text_w)/2", y="(h-text_h)/2", fontsize=160, fontfile=font)
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


def concat(video_list, output_path):
    video_list_str = "|".join(video_list)
    (
        ffmpeg
        .input('concat:' + video_list_str)
        .output(os.path.join(output_path, 'out.ts'), c='copy').run()
    )

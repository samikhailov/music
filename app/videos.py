import os
from datetime import datetime, timezone
import youtube_dl
import ffmpeg
from pychorus import find_and_output_chorus
from app.models import GlobalTrack
from settings import Directory, CHORUS_LENGTH


class Video:
    def __init__(self, track) -> None:
        self.track = track
        self.global_track = GlobalTrack.get_global_track(self.track.id, self.track.service)
        self.update_youtube_id()
        self.full_video_path = os.path.join(Directory.full_tracks, self.global_track.youtube_id + ".mp4")
        self.full_audio_path = os.path.join(Directory.full_tracks, self.global_track.youtube_id + ".mp3")
        self.cut_video_path = os.path.join(Directory.cut_tracks, self.global_track.youtube_id + ".mp4")
        self.cut_ts_path = os.path.join(Directory.cut_tracks, self.global_track.youtube_id + ".ts")

    def update_youtube_id(self):
        if not self.global_track.youtube_id:
            self.global_track.update_youtube_id(self.track.get_youtube_track_id())

    def download(self):
        if not os.path.exists(self.full_video_path):
            ydl_opts = {
                "format": "bestvideo[height<=?1080][ext=mp4]+bestaudio[ext=m4a]",
                "outtmpl": self.full_video_path,
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(self.global_track.youtube_id, download=True)

    def convert_to_mp3(self):
        self.download()
        if not os.path.exists(self.full_audio_path):
            input_file = ffmpeg.input(self.full_video_path)
            audio = input_file.audio
            output_file = ffmpeg.output(audio, self.full_audio_path)
            output_file.run()

    def update_chorus_start(self):
        self.convert_to_mp3()
        if not self.global_track.chorus_start:
            chorus_start_sec = find_and_output_chorus(self.full_audio_path, None, 8)
            self.global_track.update_chorus_start(datetime.fromtimestamp(chorus_start_sec, timezone.utc).time())

    @staticmethod
    def _set_requirements(in_stream, duration):
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

    @staticmethod
    def _draw_titles(artist, title):
        duration = CHORUS_LENGTH - 3
        base_font_params = {"fontcolor": "white", "shadowx": 2, "shadowy": 2, "fontfile": Directory.font}
        output_stream = (
            ffmpeg.input(Directory.transparent_image, loop=1, t=duration)
            .drawtext(text=artist, x=200, y=800, fontsize=56, **base_font_params)
            .drawtext(text=title, x=200, y=880, fontsize=44, **base_font_params)
        )

        return output_stream

    def create_cut_video(self):
        self.update_chorus_start()
        if not os.path.exists(self.cut_video_path):
            stream = ffmpeg.input(self.full_video_path, ss=self.global_track.chorus_start, t=CHORUS_LENGTH)
            stream = self._set_requirements(stream, CHORUS_LENGTH)
            titles = self._draw_titles(self.global_track.artist, self.global_track.title).setpts("PTS-STARTPTS+40")
            stream = ffmpeg.overlay(stream, titles, eof_action="pass").setpts("PTS-STARTPTS")
            output_file = ffmpeg.output(stream, self.cut_video_path)
            output_file.run()


class Transition:
    def __init__(self, position) -> None:
        self.position = position
        self.mp4_transition_path = os.path.join(Directory.transitions, f"{self.position:03d}.mp4")
        self.ts_transition_path = os.path.join(Directory.transitions, f"{self.position:03d}.ts")

    def create(self):
        if not os.path.exists(self.mp4_transition_path):
            duration = 1.3
            fade_duration = 0.3

            video_stream = ffmpeg.input(Directory.black_image, loop=1, t=duration)
            vid = (
                video_stream.video.drawtext(
                    text=self.position,
                    x="(w-text_w)/2",
                    y="(h-text_h)/2",
                    fontsize=200,
                    fontfile=Directory.font,
                    fontcolor="white",
                )
                .filter("fade", type="in", duration=fade_duration)
                .filter("fade", type="out", start_time=duration - fade_duration, duration=fade_duration)
            )

            audio_stream = ffmpeg.input(Directory.soundless_audio, t=duration)
            aud = audio_stream.audio

            joined = ffmpeg.concat(vid, aud, v=1, a=1)
            output = ffmpeg.output(joined, self.mp4_transition_path)
            output.run()


def convert_to_ts(mp4_path, ts_path):
    """
    Функция для конвертации mp4 в ts.
    Файлы .ts нужны для функции concat, т.к. она не поддерживатся для mp4.
    :param mp4_path: путь до mp4 файла.
    :param ts_path: путь до ts файла.
    """
    if not os.path.exists(ts_path):
        ffmpeg.input(mp4_path).output(ts_path, c="copy", f="mpegts", **{"bsf:v": "h264_mp4toannexb"}).run()


def create_final_video(chart):
    final_video_paths = [Directory.intro_ts]
    videos = [Video(track) for track in chart.tracks]
    for video in sorted(videos, key=lambda x: x.track.position, reverse=True):
        transition = Transition(video.track.position)
        transition.create()
        convert_to_ts(transition.mp4_transition_path, transition.ts_transition_path)
        final_video_paths.append(transition.ts_transition_path)
        video.create_cut_video()
        convert_to_ts(video.cut_video_path, video.cut_ts_path)
        final_video_paths.append(video.cut_ts_path)

    final_video_ts_path = os.path.join(Directory.media, f'{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.ts')
    ffmpeg.input("concat:" + "|".join(final_video_paths)).output(final_video_ts_path, c="copy").run()

    concated_mp4_path = os.path.splitext(final_video_ts_path)[0] + ".mp4"
    ffmpeg.input(final_video_ts_path).output(
        concated_mp4_path, vcodec="libx264", acodec="aac", vf="scale=iw/2:ih/2"
    ).run()

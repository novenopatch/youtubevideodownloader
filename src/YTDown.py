import re
import sys
from typing import Iterable
from pytube import YouTube
from pytube import Playlist
from pytube import StreamQuery
from pytube import Stream
import os
import subprocess
import argparse

from colorama import init
#from termcolor import colored

from Enumeration import SaveData,YdownVars
from save import Save

WELCOME_STR: str = """ 
            
  wWw  wWw   _     .-.    (O))  ((O)\\\  /// 
  (O)  (O) _||\  c(O_O)c   ||    || ((O)(O)) 
  ( \  / )(_'\  ,'.---.`,  || /\ ||  | \ ||  
   \ \/ / .'  |/ /|_|_|\ \ ||//\\||  ||\\||  
    \o / ((_) || \_____/ | / /  \ \  || \ |  
   _/ /   `-`.)'. `---' .`( /    \ ) ||  ||  
  (_.'       (   `-...-'   )      ( (_/  \_) 

        """


class YTDown:
    def __init__(self, save: Save, graph_mode=False, command=None):
        self.save = save
        self.output_path: str = ""
        self.download_resolutions = ["144p", "240p", "360p", "480p", "720p", "1080p"]
        self.select_resolution = None
        self.graph_mod = graph_mode
        self.command = command if command else self.on_progress
        self.download_streams: list[tuple[YouTube, Stream]] = []

    def display_banner(self):
        self.display_message(WELCOME_STR)
        for i, choice in enumerate(self.save.OPTIONS_CHOICE_STR):
            self.display_message(f"{i + 1}): {choice}")

    def validate_url(self, link: str) -> tuple:
        pattern_video = re.compile(
            r'^(?!.*list=).*((https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?|^(https?://)?(www\.)?youtu\.be/[\w-]+)$'
            )
        pattern_playlist = re.compile(
           r'(https?://)?(www\.)?youtube\.com/((playlist\?list=[\w-]+(&\S*)?)|(watch\?v=[\w-]+(&\S*)?(&list=[\w-]+(&\S*)?)?))$'
            )

        if pattern_video.match(link):
            return link,YdownVars.VIDEO
        elif pattern_playlist.match(link):
             return link,YdownVars.PLAYLIST
        else:
            raise ValueError(self.save.get_message('INVALID_LINK_MSG'))
    def norm_file_name(self, name: str) -> str:
        new: str = ""
        for c in name:
            if c.isalnum() or c in {"_", ".", "-"}:
                new += c
            else:
                new += "_"
        return new

    def after_download_audio(self, video_file: str, audio_file: str, output_file: str):
        os.remove(video_file)
        os.remove(audio_file)
        file_name = os.path.basename(output_file)
        new_name = file_name.replace(self.save.get_data(SaveData.FILE_PREFIX), "")
        new_path = os.path.join(os.path.dirname(output_file), new_name)
        os.rename(output_file, new_path)

    def download_audio_file(self, yt: YouTube, video_file: str, file_extension: str):
        try:
            audio = yt.streams.get_audio_only()
            self.display_message(f"{self.save.get_message('START_DOWNLOAD_MSG')}: {yt.title}-(Audio)")
            yt.register_on_progress_callback(self.command)
            audio_file = audio.download(
                output_path=self.output_path, filename=f"{self.norm_file_name(yt.title)}.mp3"
            )
            if self.save.get_data(SaveData.DEBUG):
                self.display_message(f" yt{yt} , video-path: {video_file}, audio_path: {audio_file}")
            if audio_file:
                name_file = f"{video_file}.{file_extension}"
                output_file = os.path.join(self.output_path,
                                           f"{self.save.get_data(SaveData.FILE_PREFIX)}{os.path.basename(name_file)}")
                cmd = f'ffmpeg -y -i "{video_file}" -i "{audio_file}" -c copy "{output_file}"'
                subprocess.call(cmd, shell=True)
                self.after_download_audio(video_file, audio_file, output_file)
        except Exception as e:
            self.display_message(f"{self.save.get_message('SORRY_ERROR_MSG')}:{str(e)}")

    def download(self, youtube: YouTube, video_choice: Stream):
        self.display_message(f"{self.save.get_message('START_DOWNLOAD_MSG')}:-{youtube.title}")
        youtube.register_on_progress_callback(self.command)
        video_file = video_choice.download(
            output_path=self.output_path,
            filename=self.norm_file_name(
                f"{youtube.title}_{video_choice.resolution}_{video_choice.fps}.{video_choice.mime_type.split('/')[-1]}")
        )

        if not video_choice.is_progressive:
            self.download_audio_file(youtube, video_file, f"{video_choice.mime_type.split('/')[-1]}")
        self.display_message(f"Video saved at {self.output_path}")

    def print_stream(self, streams: StreamQuery):
        if streams:
            self.display_message(self.save.get_message('RESOLUTIONS_MSG') + ":")
            for i, stream in enumerate(streams):
                self.display_message(f"{i + 1}) .{stream.mime_type.split('/')[-1]} {stream.resolution}-{stream.fps}fps")
        else:
            self.display_message(f"{self.save.get_message('SORRY_ERROR_MSG')} ")

    def filter_streams(self, youtube: YouTube) -> StreamQuery:
        return youtube.streams.filter(
            subtype=self.save.get_data(
                SaveData.FILE_EXTENSION), resolution=self.select_resolution
        ).order_by(
            'resolution')

    def print_available_resolution_and_select(self, youtube: YouTube, streams: StreamQuery) -> Stream:
        self.print_stream(streams)
        choice = input(self.save.get_message('CHOICE_QUALITY_MSG') + ":")
        if not choice:
            return youtube.streams.get_highest_resolution()
        else:
            choice = int(choice)
            return streams[choice - 1]

    def print_title(self, title: str):
        self.display_message(f"Title:{title}")


    def save_list_of_streams(self, youtubes: YouTube|Iterable[YouTube]):
        if isinstance(youtubes,Iterable):
            for i, youtube in enumerate(youtubes):
                self.download_streams.append(
                    (youtube, self.filter_streams(youtube).first())
                )
        else:
            self.download_streams.append(
                (youtubes, self.filter_streams(youtubes).first())
            )
        if self.save.get_data(SaveData.DEBUG):
            print(self.get_download_streams())

    def get_download_streams(self)-> list[tuple[YouTube, Stream]]:
        return self.download_streams
    def choice_and_download(self, youtube: YouTube, streams: StreamQuery, is_playlist: bool = False):

        try:
            if not self.select_resolution:
                video_choice = self.print_available_resolution_and_select(youtube, streams)
            else:
                # self.select_resolution
                video_choice = youtube.streams.filter(
                    subtype=self.save.get_data(SaveData.FILE_EXTENSION),
                    resolution=self.select_resolution
                ).first()

                if self.save.get_data(SaveData.DEBUG):
                    for stream in streams:
                        self.display_message(
                            f"{stream.resolution} --reso_select: {self.select_resolution}--choice: {video_choice}")
                if not video_choice:
                    video_choice = self.print_available_resolution_and_select(youtube, streams)

            if not is_playlist:
                self.download(youtube, video_choice)
            else:
                return youtube, video_choice

        except Exception as e:
            self.display_message(f" {self.save.get_message('SORRY_ERROR_MSG')} : {youtube.title}.{str(e)}")

    def get_playlist_stream(self, youtube_list: Iterable[YouTube]) -> list[tuple[YouTube, Stream]]:
        downloads = []
        length = len(youtube_list)
        for i, youtube in enumerate(youtube_list):
            streams = self.filter_streams(youtube)
            self.display_message(f"{i + 1}/{length})-{youtube.title}")

            downloads.append(self.choice_and_download(youtube, streams, True))
        return downloads

    def download_video_file(self, youtube: YouTube):
        streams = self.filter_streams(youtube)
        self.choice_and_download(youtube, streams, False)

    def download_videos_file(self, youtube_list: Iterable[YouTube]):
        downloads = self.get_playlist_stream(youtube_list)
        for youtube, video_choice in downloads:
            try:
                self.download(youtube, video_choice)
            except Exception as e:
                self.display_message(f"{self.save.get_message('SORRY_ERROR_MSG')}: {str(e)}'")

        self.display_message(self.save.get_message('END_MESSAGE'))


    def download_single_video(self, link: str) -> YouTube | None:
        youtube = YouTube(link)
        if not self.graph_mod:
            self.download_video_file(youtube)
        else:
            return youtube
        if self.save.get_data(SaveData.DEBUG):
            print(link,youtube)

    def download_playlist(self, link: str) -> Iterable[YouTube] | None:
        playlist = Playlist(link)
        self.print_title(playlist.title)
        self.output_path = os.path.join(self.output_path, self.norm_file_name(playlist.title))
        if not self.graph_mod:
            self.download_videos_file(playlist.videos)
        else:
            return playlist.videos
        if self.save.get_data(SaveData.DEBUG):
            print(link,playlist)

    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        progress = bytes_downloaded / total_size * 100
        self.display_message(
            f"\r {self.save.get_message('DOWNLOADING_MSG')} {progress:.2f}%: {(bytes_downloaded / 1024 / 1024):.2f}Mb/{(total_size / 1024 / 1024):.2f}Mb ")

    def launch(self, link: str,  output_path: str, selected_resolution: str | None = None) \
            -> YouTube | Iterable[YouTube] | None:

        try:
            link,url_type = self.validate_url(link)
            if self.save.get_data(SaveData.DEBUG):
                print(f"--link: {link},   --url_type: {url_type}")
                #return
            #choice = choice
            if not selected_resolution:
                self.select_resolution = self.display_available_resolution()
            else:
                self.select_resolution = selected_resolution
            self.output_path = output_path
            if url_type == YdownVars.VIDEO:
                return self.download_single_video(link)
            elif url_type ==YdownVars.PLAYLIST:
                return self.download_playlist(link)
            #else:
                
        except Exception as e:
            self.display_message(f"il semble avoir un souci avec votre lien . Erreur: {str(e)}")

    def display_available_resolution(self) -> str:
        for i, resol in enumerate(self.download_resolutions):
            self.display_message(f"{i + 1}) {resol}")
        choice = input(f"{self.save.get_message('YOUR_RESOLUTION_CHOICE_MSG')}:")
        try:
            return self.download_resolutions[int(choice) - 1]
        except Exception as e:
            self.display_message(f"{str(e)}")
            return self.download_resolutions[len(self.download_resolutions) - 1]

    def display_choice_msg(self):
        self.display_banner()
        return input(self.save.get_message('YOUR_CHOICE_MSG'))

    def display_message(self, message: str):
        if not self.graph_mod:
            print(message, end="")


if __name__ == '__main__':
    yt_down = YTDown(Save())
    parser = argparse.ArgumentParser(description='Télécharger une vidéo  ou une playliste Youtube')
    #parser.add_argument('-t', '--url_type', type=int, nargs='?', help='1 pour une video et 2 pour une playliste')
    parser.add_argument('-l', '--link', type=str, nargs='?', help='le lien de la video ou la playliste')
    parser.add_argument('-o', '--output_dir', type=str, nargs='?', help='le dossier de la video')
    parser.add_argument('-r', '--video_resolution', type=str, nargs='?', help='La résolution de la vidéo ex: 1080p')
    if not yt_down.graph_mod:
        video_resolution = None
        args = parser.parse_args()
        #choice = args.url_type if args.url_type else yt_down.display_choice_msg()
        link = args.link if args.link else input("Lien de la vidéo ou le Lien de la playliste : ")
        output_path = args.output_dir if args.output_dir else input(
            "Chemin de téléchargement (laisser vide pour utiliser le répertoire courant) : ").strip()
        video_resolution = args.video_resolution

        if not output_path:
            output_path = os.getcwd()
        yt_down.launch(link, output_path, video_resolution)

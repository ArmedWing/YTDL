import os
import shlex
import subprocess
from django.views import View
from pytube import YouTube
from django.shortcuts import render, redirect

class home(View):
    def __init__(self, url=None):
        self.url = url

    def get(self, request):
        return render(request, 'index.html')

    def post(self, request):
        # for fetching the video
        if request.POST.get('fetch-vid'):
            self.url = request.POST.get('given_url')
            video = YouTube(self.url)

            video_stream = video.streams.filter(res="2160p").first()
            video_1080p = video.streams.filter(res="1080p").first()

            audio = video.streams.filter(only_audio=True).first()

            vidAuthor, vidTitle, vidThumbnail = video.author, video.title, video.thumbnail_url
            quality, stream = [], []

            stream.append(video_stream)
            stream.append(video_1080p)
            stream.append(audio)
            print(stream)

            context = {
                'vidTitle': vidTitle,
                'vidThumbnail': vidThumbnail,
                'vidAuthor': vidAuthor,
                'quality': quality,
                'stream': stream,
                'url': self.url,
                       }

            return render(request, 'index.html', context)

        # for downloading the video
        elif request.POST.get('download-vid'):
            self.url = request.POST.get('given_url')
            video = YouTube(self.url)
            selected_resolution = request.POST.get('download-vid')

            if selected_resolution == '1080p':
                video_stream = video.streams.filter(res="1080p").first()
            elif selected_resolution == '2160p':
                video_stream = video.streams.filter(res="2160p").first()

            audio = video.streams.filter(only_audio=True).first()

            downloads_path = os.path.join(os.path.expanduser("~"), 'Downloads')
            audio_path = os.path.join(downloads_path, 'audio.mp4')
            video_stream_path = os.path.join(downloads_path, 'video_stream.mp4')

            audio.download(filename=audio_path, output_path=downloads_path)
            video_stream.download(filename=video_stream_path, output_path=downloads_path)

            combined_filename = f'{video.author} - {video.title} {selected_resolution}.mp4'
            desktop_path = os.path.expanduser("~") + '/Desktop/'
            output_path = os.path.join(desktop_path, combined_filename)

            # Merging the video and audio streams and deleting the now unnecessary video and audio streams.
            cmd = (
                f'ffmpeg -i "{video_stream_path}" -i "{audio_path}" -c:v copy -c:a aac -strict experimental "{output_path}"'
            )

            try:
                subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
                os.remove(video_stream_path)
                os.remove(audio_path)
            except subprocess.CalledProcessError as e:
                print("FFmpeg error:", e.output.decode())

            return redirect('home')


        elif request.POST.get('download-audio'):
            self.url = request.POST.get('given_url')
            video = YouTube(self.url)
            audio = video.streams.filter(only_audio=True).first()
            username = os.getenv("USERNAME")
            audio.download(output_path=f'C:/Users/{username}/Desktop')

            return redirect('home')
        return render(request, 'index.html')

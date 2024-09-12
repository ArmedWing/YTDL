import os
import yt_dlp as youtube_dl
from django.views import View
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound

class HomeView(View):
    def get(self, request):
        return render(request, 'index.html')

    def post(self, request):
        url = request.POST.get('given_url')
        download_option = request.POST.get('download_option')

        if not url:
            return redirect('home')

        if 'fetch-vid' in request.POST:
            # Fetch video info
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'noplaylist': True,
            }
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    vidTitle = info.get('title')
                    vidThumbnail = info.get('thumbnail')
                    vidAuthor = info.get('uploader')
                    formats = info.get('formats', [])
                    quality_options = ['1080p', '2160p']
                    streams = {f['format_note']: f for f in formats if f.get('format_note') in quality_options}

                context = {
                    'vidTitle': vidTitle,
                    'vidThumbnail': vidThumbnail,
                    'vidAuthor': vidAuthor,
                    'quality': list(streams.keys()),
                    'streams': streams,
                    'url': url,
                }
                return render(request, 'index.html', context)
            except Exception as e:
                print(f"Error fetching video info: {e}")
                context = {
                    'error': 'An error occurred while fetching video info. Please check the URL and try again.',
                }
                return render(request, 'index.html', context)

        elif download_option:
            # Ensure downloads directory exists
            downloads_dir = 'downloads'
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)

            ydl_opts = {}
            if download_option == 'audio':
                # Download audio only
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                    }],
                }
            else:
                # Download video with selected resolution
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': 'downloads/%(title)s.%(ext)s',
                    'merge_output_format': 'mp4',
                }

            # Use yt-dlp to download the video/audio
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # Extract filename based on download_option
                info = ydl.extract_info(url, download=False)
                filename = f"{info['title']}.mp4" if download_option != 'audio' else f"{info['title']}.mp3"
                filepath = os.path.join(downloads_dir, filename)

                if os.path.exists(filepath):
                    context = {
                        'message': f"Download successful! File saved as {filename} in the 'downloads' folder.",
                        'vidTitle': info.get('title'),
                        'vidThumbnail': info.get('thumbnail'),
                        'vidAuthor': info.get('uploader'),
                        'url': url,
                    }
                    return render(request, 'index.html', context)
                else:
                    return HttpResponseNotFound('File not found')
            except Exception as e:
                print(f"Error during download: {e}")
                context = {
                    'error': 'An error occurred during download. Please try again later.',
                }
                return render(request, 'index.html', context)

        return redirect('home')

import tkinter as tk
import yt_dlp
import threading
import sys
import time
import imageio_ffmpeg
from PyQt5.QtWidgets import QApplication, QFileDialog
from PIL import Image, ImageTk
from pathlib import Path
import pyautogui


def main():
    width, height = pyautogui.size()
# Root Window
    BASE_DIR = Path(__file__).resolve().parent
    BG     = "#24272C"
    RING   = "#3daee9"
    NORMAL = "gray"
    mode = 'both'
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    window = tk.Tk()
    window.title("YouTube Downloader")
    window.geometry(f"{int(width/2)}x{int(height/2)}")
    window.minsize(int(width/2.2) , int(height/2.2))
    window.maxsize(int(width/2.1) , int(height/2.1))
    window.resizable(True,True)
    window.config(bg="#151C23")
    icon = tk.PhotoImage(file=str(BASE_DIR / "icon.png"))
    window.iconphoto(True, icon)
    path = "~/Downloads"
# All Main Functions
    def format_bytes(b):
        if b is None:
            return "Unknown"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if b < 1024.0:
                return f"{b:.1f} {unit}"
            b /= 1024.0
        return f"{b:.1f} PB"

    def progress_hook(d):
        info = d.get('info_dict', {})
        vcodec = info.get('vcodec', '')
        acodec = info.get('acodec', '')

        if vcodec != 'none' and acodec == 'none':
            media_type = 'video'
        elif vcodec == 'none' and acodec != 'none':
                media_type = 'audio'

        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            down = d.get('downloaded_bytes', 0)
            download_size.config(text="Downloading...")

            if total:
                new_text=f"{media_type.capitalize()}: {format_bytes(down)} / {format_bytes(total)}"
            else:
                new_text=f"{media_type.capitalize()}: {format_bytes(down)} (unknown total size)"

            if media_type == 'video':
                video_label.config(text=new_text)
            elif media_type == 'audio':
                audio_label.config(text=new_text)

            window.update_idletasks()

        elif d['status'] == 'finished':
            download_size.config(text="Download complete!")
            video_label.config(text="Video: waiting...")
            audio_label.config(text="Audio: waiting...")

    def video_Downloader():
        nonlocal mode
        yt_link = link_Entry.get("1.0", "end-1c")
        if not yt_link:
            download_size.config(text='please enter a valid url')
            return

        if mode == 'video':
            fmt = 'bestvideo'
        elif mode == 'audio':
            fmt = 'bestaudio'
        else:
            fmt = 'bestvideo+bestaudio'
        ydl_opts = {

        'format': fmt,
        'ffmpeg_location': ffmpeg_path,
        'js_runtimes': {'node': {}},
        'remote_components': ['ejs:github'],
        'paths': {'home': path},
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
        'cookiesfrombrowser': ('firefox',),
        'compat_opts': ['no-cookies', 'no-youtube-unavailable-errors'],
        'progress_hooks': [progress_hook],
        'overwrites': True,
        'extractor_args': {
                'youtube': {
                'player_client': ['default', 'web_embedded'],
                    }
                }
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([yt_link])
            except yt_dlp.utils.DownloadError as exc:
                msg = str(exc)
                if "The page needs to be reloaded" in msg:
                    download_size.config(text='Node.js is not found, please install it at https://nodejs.org/')
                    file=sys.stderr,
                    time.sleep(5)
                    download_size.config(text='Please enter an url!')
                    sys.exit(1)
                elif "is not a valid URL" in msg:
                    download_size.config(text='Please enter a valid URL.')
                    file=sys.stderr,
                    time.sleep(5)
                    download_size.config(text='Please enter an url!')
                    sys.exit(1)
                elif "unsupported browser" in msg:
                    download_size.config(text='Your browser is unsupported.')
                    file=sys.stderr,
                    time.sleep(5)
                    download_size.config(text='Please enter an url!')
                    sys.exit(1)
                raise

    def start_download():
            download_size.config(text="Starting...")
            thread = threading.Thread(target=video_Downloader, daemon=True)
            thread.start()
            check_thread(thread)

    def check_thread(thread):
        if thread.is_alive():
            window.after(100, lambda: check_thread(thread))
        else:
            download.config(state='normal')

    def settings():
        Settings.pack_forget()

        if Settings.cget("text") == "Settings":

            download.pack_forget()
            download_size.pack_forget()
            video_label.pack_forget()
            audio_label.pack_forget()
            link_Entry.pack_forget()
            only_video.pack(pady=3,fill="both", expand=True)
            only_audio.pack(pady=3,fill="both", expand=True)
            dir_Change.pack(pady=3,fill="both", expand=True)
            reset.pack(pady=3,fill="both", expand=True)
            path_label.pack(pady=3,fill="both", expand=True)
            Settings.config(text="Back")
            Settings.pack(fill="both", expand=True)
        elif Settings.cget("text") == "Back":
            Settings.pack_forget()
            download_size.pack(pady=3,fill="both", expand=True)
            video_label.pack(pady=3,fill="both", expand=True)
            audio_label.pack(pady=3,fill="both", expand=True)
            link_Entry.pack(pady=3,fill="x", expand=True)
            download.pack(pady=3,fill="both", expand=True)
            only_audio.pack_forget()
            only_video.pack_forget()
            reset.pack_forget()
            dir_Change.pack_forget()
            path_label.pack_forget()

            Settings.config(text="Settings")
            Settings.pack(fill="both", expand=True)

    def Only_Video():
        nonlocal mode
        mode = 'video'
        only_video.config(text="Only Video (Complete)")
        only_audio.config(text="Only Audio")

    def Only_Audio():
            nonlocal mode
            mode = 'audio'
            only_audio.config(text="Only Audio (Complete)")
            only_video.config(text="Only Video")

    def Dir_Change(title="Choose your Directory", start_dir=""):
        nonlocal path, path_label
        app = QApplication.instance() or QApplication(sys.argv)

        path = QFileDialog.getExistingDirectory(
            None,
            title,
            start_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        print(type(path))
        print(path)
        path_label.config(text=f"Current Directory: {path}")
        return path or None


    def settings_Reset():
        nonlocal mode
        only_video.config(text="Only Video")
        only_audio.config(text="Only Audio")
        mode = 'both'

    def add_ring(widget, normal=NORMAL, ring=RING, BG=BG):
        widget.config(
        highlightthickness=1,
        highlightbackground=normal,
        bg=BG,
        activebackground=BG,
        fg="white",
        activeforeground="white",
        highlightcolor=ring,
        bd=0,
        )
        state = {"hover": False}
        def update():
            active = state["hover"] or widget.focus_get() == widget
            widget.configure(highlightbackground=ring  if active else normal)
        widget.bind("<Enter>", lambda e: (state.__setitem__("hover", True),  update()), add="+")
        widget.bind("<Leave>", lambda e: (state.__setitem__("hover", False), update()), add="+")
        widget.bind("<FocusIn>",  lambda e: update(), add="+")
        widget.bind("<FocusOut>", lambda e: update(), add="+")

# Buttons
    window_size = width // 2
    download_size = tk.Label(window, text='Please enter an url!',height=2,bg="#24272C",fg="white",highlightthickness=1,highlightbackground="gray",wraplength=window_size, justify="left")
    video_label = tk.Label(window, text="Video: waiting...", font=("Arial", 9),bg="#24272C",fg="white",highlightthickness=1,highlightbackground="gray")
    audio_label = tk.Label(window, text="Audio: waiting...", font=("Arial", 9), bg="#24272C",fg="white",highlightthickness=1,highlightbackground="gray")
    link_Entry = tk.Text(bg="#24272C",fg="white",height=2,highlightthickness=1,highlightbackground="gray")
    download = tk.Button(window, text="Download", command=start_download)

    Settings = tk.Button(window, text="Settings", command=settings)
    only_audio = tk.Button(window, text="Only Audio", command=Only_Audio)
    only_video = tk.Button(window, text="Only Video", command=Only_Video)
    dir_Change = tk.Button(window, text="Change Directory", command=Dir_Change)
    reset = tk.Button(window, text="Reset", command=settings_Reset)

    download_size.pack(pady=3,fill="both", expand=True)
    video_label.pack(pady=3,fill="both", expand=True)
    audio_label.pack(pady=3,fill="both", expand=True)
    link_Entry.pack(pady=3,fill="both", expand=True)
    download.pack(pady=3,fill="both", expand=True)
    Settings.pack(pady=3,fill="both", expand=True)


    path_label = tk.Label(window, text=f"Current Directory: {path}",bg="#24272C",fg="white",highlightthickness=1,highlightbackground="gray")

    add_ring(download)
    add_ring(Settings)
    add_ring(only_audio)
    add_ring(only_video)
    add_ring(dir_Change)
    add_ring(reset)

    def on_resize(event):

        if event.widget != window:
            return

        size = max(8, min(40, event.width // 25))
        link_Entry.config(font=("FreeSans", size))
        download_size.config(font=("FreeSans", size))
        video_label.config(font=("FreeSans", size))
        audio_label.config(font=("FreeSans", size))
        link_Entry.config(font=("FreeSans", size))
        download.config(font=("FreeSans", size))
        Settings.config(font=("FreeSans", size))
        only_video.config(font=("FreeSans", size))
        only_audio.config(font=("FreeSans", size))
        dir_Change.config(font=("FreeSans", size))
        reset.config(font=("FreeSans", size))
        path_label.config(font=("FreeSans", int(size/2)))



    window.icon = icon
    window.bind("<Configure>", on_resize)
    window.mainloop()

if __name__ == "__main__":
   main()








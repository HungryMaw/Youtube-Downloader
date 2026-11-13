import customtkinter as ctk
import tkinter as tk
import yt_dlp
import threading
import sys
import time
import imageio_ffmpeg
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QFileDialog
import pyautogui
import configparser
import subprocess

def get_system_hover_color(bg_hex):
    """Fetch the system's native hover/focus accent color."""
    

    kdeglobals = Path.home() / ".config" / "kdeglobals"
    if kdeglobals.exists():
        try:
            cfg = configparser.ConfigParser()
            cfg.read(kdeglobals)
            
            search_keys = [
                ("Colors:Selection", "BackgroundNormal"),
                ("Colors:Button", "DecorationFocus"),
                ("Colors:Window", "DecorationFocus"),
                ("Colors:Button", "DecorationHover")
            ]
            
            for section, key in search_keys:
                if cfg.has_section(section) and cfg.has_option(section, key):
                    raw = cfg.get(section, key)
                    parts = raw.split(",")
                    if len(parts) == 3:
                        hex_color = "#" + "".join(f"{int(x):02X}" for x in parts)
                        if hex_color not in ("#000000", "#FFFFFF"):
                            return hex_color
        except Exception as e:
            print(f"KDE read error: {e}")

    try:
        out = subprocess.check_output(
            ["gsettings", "get", "org.gnome.desktop.interface", "accent-color"],
            text=True, stderr=subprocess.DEVNULL
        ).strip().strip("'")
        
        gnome_accents = {
            "blue": "#3584e4", "teal": "#2190a4", "green": "#3a944a",
            "yellow": "#c64600", "orange": "#ed5b00", "red": "#e62d42",
            "pink": "#d56199", "purple": "#9141ac", "slate": "#6f8396"
        }
        if out in gnome_accents:
            print(f"Found GNOME accent color: {out}")
            return gnome_accents[out]
    except Exception:
        pass

    try:
        from PyQt5.QtGui import QPalette
        app = QApplication.instance() or QApplication(sys.argv)
        highlight = app.palette().color(QPalette.Highlight).name()
        # Qt might return gray if the platform theme plugin isn't loaded
        if highlight not in ("#000000", "#FFFFFF", "#efefef", "#d9d9d9"):
            print(f"Found color via Qt QPalette: {highlight}")
            return highlight
    except Exception:
        pass


    print("Falling back to shaded background...")
    try:
        bg_hex = bg_hex.lstrip('#')
        r, g, b = int(bg_hex[0:2], 16), int(bg_hex[2:4], 16), int(bg_hex[4:6], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        factor = 1.3 if luminance < 0.5 else 0.8  # Lighten for dark themes, darken for light themes
        
        return "#{:02X}{:02X}{:02X}".format(
            max(0, min(255, int(r * factor))),
            max(0, min(255, int(g * factor))),
            max(0, min(255, int(b * factor)))
        )
    except Exception:
        return "#3daee9"
    
def get_system_button_colors():
    """Fetch the system's button background/foreground colors (KCalc-style)."""
    kdeglobals = Path.home() / ".config" / "kdeglobals"
    if kdeglobals.exists():
        try:
            cfg = configparser.ConfigParser()
            cfg.read(kdeglobals)
            if cfg.has_section("Colors:Button"):
                bg_raw = cfg.get("Colors:Button", "BackgroundNormal", fallback="")
                fg_raw = cfg.get("Colors:Button", "ForegroundNormal", fallback="")
                if bg_raw and fg_raw:
                    bg_hex = "#" + "".join(f"{int(x):02X}" for x in bg_raw.split(","))
                    fg_hex = "#" + "".join(f"{int(x):02X}" for x in fg_raw.split(","))
                    return bg_hex, fg_hex
        except Exception:
            pass

    try:
        out = subprocess.check_output(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-color-scheme"],
            text=True, stderr=subprocess.DEVNULL
        ).strip().strip("'")
        scheme = dict(item.split(":") for item in out.split(";") if ":" in item)
        if "fbutton_bg_color" in scheme and "fbutton_fg_color" in scheme:
            return scheme["fbutton_bg_color"], scheme["fbutton_fg_color"]
    except Exception:
        pass

    try:
        from PyQt5.QtGui import QPalette
        app = QApplication.instance() or QApplication(sys.argv)
        palette = app.palette()
        bg = palette.color(QPalette.Button).name()
        fg = palette.color(QPalette.ButtonText).name()
        hg = palette.color(QPalette.HoverText).name()
        return bg, fg
    except Exception:
        pass

    return "#24272C", "white"

def get_used_system_font():
    """Read the ACTUAL desktop UI font (the one KCalc would use).

    Order: KDE kdeglobals -> GNOME gsettings -> fontconfig -> fallback.
    """

    kdeglobals = Path.home() / ".config" / "kdeglobals"
    if kdeglobals.exists():
        try:
            cfg = configparser.ConfigParser()
            cfg.read(kdeglobals)
            if cfg.has_option("General", "font"):
                raw = cfg.get("General", "font")   
                parts = raw.split(",")
                family = parts[0].strip()
                size = int(parts[1]) if len(parts) > 1 and parts[1].lstrip("-").isdigit() else 10
                if family:
                    return family, size
        except Exception:
            pass


    try:
        out = subprocess.check_output(
            ["gsettings", "get", "org.gnome.desktop.interface", "font-name"],
            text=True, stderr=subprocess.DEVNULL
        ).strip().strip("'")
        parts = out.rsplit(" ", 1)
        if len(parts) == 2 and parts[1].isdigit() and parts[0]:
            return parts[0], int(parts[1])
        if out:
            return out, 10
    except Exception:
        pass


    try:
        out = subprocess.check_output(
            ["fc-match", "-f", "%{family}", "sans-serif"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        return out.split(",")[0], 10
    except Exception:
        pass

    return "Sans Serif", 10

system_font_family, system_font_size = get_used_system_font()
system_bg, system_fg = get_system_button_colors() 
class Youtube_Downloader:
    def __init__(self, root):
        self.root = root
        width, height = pyautogui.size()
        
        
    # Root Window
        BASE_DIR = Path(__file__).resolve().parent
        BG     = "#24272C"
        RING   = "#3daee9"
        NORMAL = "gray"
        mode = 'both'
        
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        self.root.title("YouTube Downloader")
        self.root.geometry(f"{int(width/2)}x{int(height/2)}")
        self.root.minsize(int(width/2.2) , int(height/2.2))
        self.root.maxsize(int(width/2.1) , int(height/2.1))
        self.root.resizable(True,True)
        icon = tk.PhotoImage(file=str(BASE_DIR / "icon.png"))
        self.root.iconphoto(True, icon)
        hover_bg=get_system_hover_color(system_bg)
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
                download_size.configure(text="Downloading...")

                if total:
                    new_text=f"{media_type.capitalize()}: {format_bytes(down)} / {format_bytes(total)}"
                else:
                    new_text=f"{media_type.capitalize()}: {format_bytes(down)} (unknown total size)"

                if media_type == 'video':
                    video_label.configure(text=new_text)
                elif media_type == 'audio':
                    audio_label.configure(text=new_text)

                self.root.update_idletasks()

            elif d['status'] == 'finished':
                download_size.configure(text="Download complete!")
                video_label.configure(text="Video: waiting...")
                audio_label.configure(text="Audio: waiting...")

        def video_Downloader():
            nonlocal mode
            yt_link = link_Entry.get("1.0", "end-1c").strip()
            if not yt_link:
                download_size.configure(text='please enter a valid url')
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
            'remote_components': ['ejs:github'],
            'js_runtimes': {'node': {}},
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
                        download_size.configure(text='Deno is not found, please install it at https://deno.com/')
                        file=sys.stderr,
                        time.sleep(5)
                        download_size.configure(text='Please enter an url!')
                        sys.exit(1)
                    elif "is not a valid URL" in msg:
                        download_size.configure(text='Please enter a valid URL.')
                        file=sys.stderr,
                        time.sleep(5)
                        download_size.configure(text='Please enter an url!')
                        sys.exit(1)
                    elif "unsupported browser" in msg:
                        download_size.configure(text='Your browser is unsupported.')
                        file=sys.stderr,
                        time.sleep(5)
                        download_size.configure(text='Please enter an url!')
                        sys.exit(1)
                    raise

        def start_download():
                download_size.configure(text="Starting...")
                thread = threading.Thread(target=video_Downloader, daemon=True)
                thread.start()
                check_thread(thread)

        def check_thread(thread):
            if thread.is_alive():
                self.root.after(100, lambda: check_thread(thread))
            else:
                download.configure(state='normal')

        def make_bordered_label(parent, text="", justify="center", anchor="center"):
            frame = ctk.CTkFrame(parent, fg_color="transparent", border_width=1, border_color=NORMAL)
            label = ctk.CTkLabel(
                frame, text=text, fg_color=system_bg, text_color=system_fg,
                font=(system_font_family, 9), justify=justify, anchor=anchor,
            )
            label.pack(fill="both", expand=True, padx=6, pady=2)
            return frame, label

        def settings():
            Settings.pack_forget()

            if Settings.cget("text") == "Settings":
                download.pack_forget()
                download_size_frame.pack_forget()
                video_label_frame.pack_forget()
                audio_label_frame.pack_forget()
                link_Entry.pack_forget()
                only_video.pack(pady=3, fill="both", expand=True)
                only_audio.pack(pady=3, fill="both", expand=True)
                dir_Change.pack(pady=3, fill="both", expand=True)
                reset.pack(pady=3, fill="both", expand=True)
                path_label_frame.pack(pady=3, fill="both", expand=True)
                Settings.configure(text="Back")
                Settings.pack(fill="both", expand=True)
            elif Settings.cget("text") == "Back":
                Settings.pack_forget()
                download_size_frame.pack(pady=3, fill="both", expand=True)
                video_label_frame.pack(pady=3, fill="both", expand=True)
                audio_label_frame.pack(pady=3, fill="both", expand=True)
                link_Entry.pack(pady=3, fill="both", expand=True)
                download.pack(pady=3, fill="both", expand=True)
                only_audio.pack_forget()
                only_video.pack_forget()
                reset.pack_forget()
                dir_Change.pack_forget()
                path_label_frame.pack_forget()
                Settings.configure(text="Settings")
                Settings.pack(fill="both", expand=True)

        def Only_Video():
            nonlocal mode
            mode = 'video'
            only_video.configure(text="Only Video (Complete)")
            only_audio.configure(text="Only Audio")

        def Only_Audio():
                nonlocal mode
                mode = 'audio'
                only_audio.configure(text="Only Audio (Complete)")
                only_video.configure(text="Only Video")

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
            path_label.configure(text=f"Current Directory: {path}")
            return path or None


        def settings_Reset():
            nonlocal mode
            only_video.configure(text="Only Video")
            only_audio.configure(text="Only Audio")
            mode = 'both'

        def add_ring(widget, normal=NORMAL, ring=hover_bg):
            widget.configure(border_width=1, border_color=normal)
            widget.bind("<Enter>", lambda e: widget.configure(border_color=ring), add="+")
            widget.bind("<Leave>", lambda e: widget.configure(border_color=normal), add="+")

    # Buttons
        download_size_frame, download_size = make_bordered_label(
            self.root, text='Please enter an url!'
        )
        video_label_frame, video_label = make_bordered_label(self.root, text="Video: waiting...")
        audio_label_frame, audio_label = make_bordered_label(self.root, text="Audio: waiting...")

        link_Entry = ctk.CTkTextbox(
            self.root, text_color=system_fg,fg_color="transparent", height=28,
            border_width=1, border_color=NORMAL, font=(system_font_family, system_font_size)
        )
        download   = ctk.CTkButton(self.root, text="Download",text_color=system_fg ,       command=start_download,  font=(system_font_family, system_font_size),fg_color="transparent")
        Settings   = ctk.CTkButton(self.root, text="Settings",text_color=system_fg ,        command=settings,        font=(system_font_family, system_font_size),fg_color="transparent")
        only_audio = ctk.CTkButton(self.root, text="Only Audio",text_color=system_fg,       command=Only_Audio,      font=(system_font_family, system_font_size),fg_color="transparent")
        only_video = ctk.CTkButton(self.root, text="Only Video",text_color=system_fg,       command=Only_Video,      font=(system_font_family, system_font_size),fg_color="transparent")
        dir_Change = ctk.CTkButton(self.root, text="Change Directory",text_color=system_fg, command=Dir_Change,      font=(system_font_family, system_font_size),fg_color="transparent")
        reset      = ctk.CTkButton(self.root, text="Reset",text_color=system_fg,           command=settings_Reset,  font=(system_font_family, system_font_size),fg_color="transparent")

        download_size_frame.pack(pady=3, fill="both", expand=True)
        video_label_frame.pack(pady=3, fill="both", expand=True)
        audio_label_frame.pack(pady=3, fill="both", expand=True)
        link_Entry.pack(pady=3, fill="both", expand=True)
        download.pack(pady=3, fill="both", expand=True)
        Settings.pack(pady=3, fill="both", expand=True)

        path_label_frame, path_label = make_bordered_label(self.root, text=f"Current Directory: {path}")

        add_ring(download)
        add_ring(Settings)
        add_ring(only_audio)
        add_ring(only_video)
        add_ring(dir_Change)
        add_ring(reset)

        all_buttons = [download, Settings, only_audio, only_video, dir_Change, reset]

        def on_resize(event):
            global system_font_size
            if event.widget != self.root:
                return

            system_font_size = max(8, min(40, event.width // 25))
            link_Entry.configure(font=(system_font_family, system_font_size))
            download_size.configure(font=(system_font_family, system_font_size))
            video_label.configure(font=(system_font_family, system_font_size))
            audio_label.configure(font=(system_font_family, system_font_size))
            download.configure(font=(system_font_family, system_font_size))
            Settings.configure(font=(system_font_family, system_font_size))
            only_video.configure(font=(system_font_family, system_font_size))
            only_audio.configure(font=(system_font_family, system_font_size))
            dir_Change.configure(font=(system_font_family, system_font_size))
            reset.configure(font=(system_font_family, system_font_size))
            path_label.configure(font=(system_font_family, int(system_font_size / 2)))

            # ← NEW: wrap the status label to the real inner width, minus padding



        self.root.icon = icon
        self.root.bind("<Configure>", on_resize)
 
if __name__ == "__main__":
    root = ctk.CTk(fg_color=system_bg)
    app = Youtube_Downloader(root)
    root.mainloop()
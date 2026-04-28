#!/usr/bin/env python3
"""
cctv.py — Simple RTSP launcher with Tkinter GUI
Created by Fajar Julyana (Bandung, Indonesia)

Features:
 - Cross-platform (Linux + Windows)
 - Launch / Stop ffplay RTSP stream
 - Auto-detect ffplay binary
 - Optional config window skip on Linux
 - Custom app icon (cctv.ico / cctv.png)
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import shutil
import sys
import os
import platform

# --- CONFIGURATION ---
RTSP_URL = "rtsp://78604392:Fajar07.@172.16.131.15:554/live/ch00_0"
WMCTRL_CMD = "wmctrl"  # Linux only
ICON_NAME = "cctv.ico" if os.name == "nt" else "cctv.png"
# ----------------------


def get_resource_path(filename):
    """Return resource path, works inside PyInstaller bundle."""
    if getattr(sys, "_MEIPASS", None):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)


def get_ffplay_path():
    """Return ffplay executable path (cross-platform)."""
    exe_name = "ffplay.exe" if os.name == "nt" else "ffplay"
    if getattr(sys, "_MEIPASS", None):
        ffplay_path = os.path.join(sys._MEIPASS, exe_name)
    else:
        local_ff = os.path.join(os.path.dirname(os.path.abspath(__file__)), exe_name)
        ffplay_path = local_ff if os.path.exists(local_ff) else shutil.which("ffplay") or exe_name
    return ffplay_path


class FFPlayController:
    def __init__(self):
        self.proc = None
        self.lock = threading.Lock()

    def start(self, url):
        with self.lock:
            if self.proc is not None and self.proc.poll() is None:
                return False  # already running

            cmd = [
                get_ffplay_path(),
                "-rtsp_transport", "tcp",
                "-window_title", "CCTV Stream — Fajar Julyana",
                "-x", "640", "-y", "480",
                "-loglevel", "warning",
                url
            ]

            try:
                if platform.system().lower() == "windows":
                    self.proc = subprocess.Popen(
                        cmd,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    # Linux: detached session
                    self.proc = subprocess.Popen(
                        cmd,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True,
                    )
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start ffplay:\n{e}")
                return False

    def stop(self):
        with self.lock:
            if self.proc is None:
                return False
            if self.proc.poll() is None:
                try:
                    self.proc.terminate()
                    self.proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
                    self.proc.wait(timeout=2)
                except Exception:
                    pass
            self.proc = None
            return True

    def is_running(self):
        with self.lock:
            return self.proc is not None and self.proc.poll() is None


def has_config_window():
    """Detect if any window title contains 'config' (Linux only)."""
    if platform.system().lower() != "linux":
        return False
    if shutil.which(WMCTRL_CMD) is None:
        return False
    try:
        out = subprocess.check_output([WMCTRL_CMD, "-l"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return False
    keywords = ("config", "konfig", "configuration", "pengaturan", "settings")
    for line in out.splitlines():
        if any(k in line.lower() for k in keywords):
            return True
    return False


class App(tk.Tk):
    def __init__(self, ff_ctrl):
        super().__init__()
        self.ff = ff_ctrl
        self.title("CCTV Viewer — Fajar Julyana")
        self.geometry("420x160")
        self.resizable(False, False)

        # --- Load icon (ICO or PNG) ---
        icon_path = get_resource_path(ICON_NAME)
        if os.path.exists(icon_path):
            try:
                if os.name == "nt":
                    self.iconbitmap(icon_path)
                else:
                    icon_img = tk.PhotoImage(file=icon_path)
                    self.iconphoto(False, icon_img)
            except Exception:
                pass
        # -------------------------------

        self.status_var = tk.StringVar(value="Ready")
        self.create_widgets()
        self.update_status_loop()

    def create_widgets(self):
        fr = tk.Frame(self, padx=12, pady=12)
        fr.pack(fill="both", expand=True)

        tk.Label(fr, text="RTSP URL:").grid(row=0, column=0, sticky="w")
        self.url_entry = tk.Entry(fr, width=50)
        self.url_entry.grid(row=0, column=1, sticky="w")
        self.url_entry.insert(0, RTSP_URL)

        btn_frame = tk.Frame(fr)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))

        self.launch_btn = tk.Button(btn_frame, text="Start Stream", width=15, command=self.on_launch)
        self.launch_btn.pack(side="left", padx=6)

        self.stop_btn = tk.Button(btn_frame, text="Stop Stream", width=15, command=self.on_stop, state="disabled")
        self.stop_btn.pack(side="left", padx=6)

        self.skip_chk_var = tk.IntVar(value=1)
        self.skip_chk = tk.Checkbutton(fr, text="Skip if a config window exists (Linux only)", variable=self.skip_chk_var)
        self.skip_chk.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))

        tk.Label(fr, textvariable=self.status_var, fg="blue").grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))

    def on_launch(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter an RTSP URL first.")
            return

        if self.skip_chk_var.get() and has_config_window():
            messagebox.showinfo("Skipped", "Config window detected — skipping ffplay launch.")
            self.status_var.set("Skipped due to config window.")
            return

        def start_thread():
            self.status_var.set("Starting ffplay...")
            ok = self.ff.start(url)
            if ok:
                self.status_var.set("ffplay running.")
            else:
                self.status_var.set("Already running.")
        threading.Thread(target=start_thread, daemon=True).start()
        self.after(200, self.refresh_buttons)

    def on_stop(self):
        def stop_thread():
            self.status_var.set("Stopping ffplay...")
            self.ff.stop()
            self.status_var.set("Stopped.")
        threading.Thread(target=stop_thread, daemon=True).start()
        self.after(200, self.refresh_buttons)

    def refresh_buttons(self):
        if self.ff.is_running():
            self.launch_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
        else:
            self.launch_btn.config(state="normal")
            self.stop_btn.config(state="disabled")

    def update_status_loop(self):
        self.refresh_buttons()
        self.after(500, self.update_status_loop)


def main():
    ff = FFPlayController()
    app = App(ff)
    app.mainloop()
    if ff.is_running():
        ff.stop()


if __name__ == "__main__":
    main()


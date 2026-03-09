import os
import sys
import threading
import socket
import shutil
import subprocess
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

APP_TITLE = "Cybersecurity Toolkit"
HOST = "127.0.0.1"
LOG_FILE = "launcher.log"


def log(msg: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def app_base_dir() -> Path:
    """
    - Normal run: base is where launcher.py is located
    - PyInstaller EXE: base is sys._MEIPASS (extracted bundle folder)
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


BASE_DIR = app_base_dir()

# Adjust these if your apps are located elsewhere
PHISHING_APP = BASE_DIR / "phishing" / "web" / "phishing_app.py"
MALWARE_APP  = BASE_DIR / "malware"  / "web" / "malware_app.py"


def find_free_port() -> int:
    s = socket.socket()
    s.bind((HOST, 0))
    port = s.getsockname()[1]
    s.close()
    return port


def resolve_streamlit_command():
    """
    Prefer streamlit.exe found on PATH (same one you use in terminal).
    Fallback to current python -m streamlit.
    """
    st_exe = shutil.which("streamlit")
    if st_exe:
        return [st_exe]
    return [sys.executable, "-m", "streamlit"]


def show_temporary_notification(title: str, message: str, duration_ms: int = 5000):
    """
    Non-blocking popup that auto-closes after duration_ms.
    """
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("420x140")
    win.resizable(False, False)

    # Center on screen
    win.update_idletasks()
    x = (win.winfo_screenwidth() - win.winfo_width()) // 2
    y = (win.winfo_screenheight() - win.winfo_height()) // 2
    win.geometry(f"+{x}+{y}")

    tk.Label(
        win,
        text=message,
        font=("Segoe UI", 10),
        wraplength=380,
        justify="center"
    ).pack(expand=True, padx=20, pady=25)

    win.after(duration_ms, win.destroy)


def run_streamlit_in_thread(app_path: Path):
    """
    Runs: streamlit run <app_path> in background.
    Does NOT manually open browser; Streamlit will auto-open if allowed.
    Shows a 5-second notification popup.
    """
    if not app_path.exists():
        messagebox.showerror("Missing app", f"Cannot find:\n{app_path}")
        return

    port = find_free_port()
    st_cmd = resolve_streamlit_command()

    cmd = st_cmd + [
        "run",
        str(app_path),
        "--server.address", HOST,
        "--server.port", str(port),
        "--global.developmentMode", "false",
        "--client.showErrorDetails", "false",
    ]

    def _worker():
        try:
            os.chdir(str(BASE_DIR))
            log(f"[INFO] CWD={os.getcwd()}")
            log(f"[INFO] sys.executable={sys.executable}")
            log(f"[INFO] Using Streamlit command: {' '.join(st_cmd)}")
            log(f"[INFO] Starting Streamlit app={app_path}")
            log(f"[INFO] URL=http://{HOST}:{port}")
            log(f"[INFO] FULL CMD: {' '.join(cmd)}")

            subprocess.Popen(
                cmd,
                cwd=str(BASE_DIR),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

        except Exception:
            err = traceback.format_exc()
            log("[ERROR] Streamlit failed:\n" + err)
            try:
                messagebox.showerror(
                    "Launch failed",
                    "Streamlit did not start.\n\nCheck launcher.log for details."
                )
            except Exception:
                pass

    threading.Thread(target=_worker, daemon=True).start()

    # ✅ Auto-close notification in 5 seconds (non-blocking)
    show_temporary_notification(
        title="Starting Streamlit",
        message=(
            "Streamlit is starting in the background.\n\n"
            "Your browser will open automatically."
        ),
        duration_ms=5000
    )


def main_ui():
    global root
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("460x260")
    root.resizable(False, False)

    tk.Label(root, text="Select a tool to run", font=("Segoe UI", 14, "bold")).pack(pady=(18, 6))

    frame = tk.Frame(root)
    frame.pack(pady=8)

    tk.Button(
        frame, text="Phishing Detection", font=("Segoe UI", 11), width=28,
        command=lambda: run_streamlit_in_thread(PHISHING_APP)
    ).grid(row=0, column=0, padx=10, pady=8)

    tk.Button(
        frame, text="Malware Detection", font=("Segoe UI", 11), width=28,
        command=lambda: run_streamlit_in_thread(MALWARE_APP)
    ).grid(row=1, column=0, padx=10, pady=8)

    tk.Label(
        root,
        text="Developed for Capstone Project by Chun Fan Sim · All rights reserved.",
        font=("Segoe UI", 8)
    ).pack(side="bottom", pady=10)

    root.mainloop()


if __name__ == "__main__":
    # reset log each run
    try:
        Path(LOG_FILE).unlink(missing_ok=True)
    except Exception:
        pass

    log("[INFO] Launcher started")
    log(f"[INFO] BASE_DIR={BASE_DIR}")
    log(f"[INFO] PHISHING_APP={PHISHING_APP}")
    log(f"[INFO] MALWARE_APP={MALWARE_APP}")

    main_ui()
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import pygame
from pynput import keyboard

# Initialize Pygame Mixer at 48kHz to match Discord sample rate
pygame.mixer.init(frequency=48000)

CONFIG_FILE = "soundboard_config.json"
MAX_DURATION = 10.0  # Max sound length in seconds


class SoundboardApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Soundboard with Trimmer & Anti-Spam")
        self.root.geometry("550x480")
        self.root.configure(bg="#1e1e2e")

        self.config = self.load_config()

        # Cache pre-sliced sound objects in memory for instant playback
        self.loaded_sounds = {}
        self.reload_all_sounds()

        self.hotkey_map = {
            "1": 0,
            "2": 1,
            "3": 2,
            "4": 3,
            "5": 4,
            "6": 5,
            "7": 6,
            "8": 7,
            "9": 8,
        }

        self.create_widgets()
        self.start_global_listener()

    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="🔊 Soundboard (Trimmer Enabled)",
            font=("Helvetica", 14, "bold"),
            fg="#cdd6f4",
            bg="#1e1e2e",
        )
        title.pack(pady=10)

        # Pad Grid
        grid_frame = tk.Frame(self.root, bg="#1e1e2e")
        grid_frame.pack(expand=True, fill="both", padx=20, pady=5)

        self.buttons = []
        for i in range(9):
            row, col = divmod(i, 3)
            btn = tk.Button(
                grid_frame,
                font=("Helvetica", 9),
                wrap=130,
                activebackground="#585b70",
                relief="flat",
                command=lambda idx=i: self.play_sound(idx),
            )
            # Right-click opens the Audio Trimmer / Editor window
            btn.bind(
                "<Button-3>", lambda event, idx=i: self.open_edit_dialog(idx)
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)

            grid_frame.rowconfigure(row, weight=1)
            grid_frame.columnconfigure(col, weight=1)

            self.buttons.append(btn)

        self.update_button_labels()

        # Stop Button
        stop_btn = tk.Button(
            self.root,
            text="⏹ Stop Current Sound (ESC)",
            bg="#f38ba8",
            fg="#11111b",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            command=self.stop_all_sounds,
        )
        stop_btn.pack(fill="x", padx=20, pady=10)

    def update_button_labels(self):
        for i in range(9):
            pad_data = self.config.get(str(i), {})
            path = pad_data.get("path", "")
            if path and os.path.exists(path):
                filename = os.path.basename(path)
                start = pad_data.get("start", 0.0)
                end = pad_data.get("end", 10.0)
                dur = round(end - start, 1)
                text = f"[{i+1}] {filename}\n⏱ {start}s - {end}s ({dur}s)"
                bg_color = "#313244"
            else:
                text = f"[{i+1}]\n(Right-click to set)"
                bg_color = "#45475a"

            self.buttons[i].config(text=text, bg=bg_color, fg="#cdd6f4")

    def play_sound(self, index):
        # Stop currently playing audio to prevent audio spam/overlapping
        pygame.mixer.stop()

        sound = self.loaded_sounds.get(str(index))
        if sound:
            sound.play(maxtime=10000)

    def stop_all_sounds(self):
        pygame.mixer.stop()

    def process_trimmed_sound(self, path, start_sec, end_sec):
        """Loads audio file and trims it in-memory between start_sec and end_sec."""
        try:
            full_sound = pygame.mixer.Sound(path)
            freq = pygame.mixer.get_init()[0]

            arr = pygame.sndarray.array(full_sound)

            start_sample = int(start_sec * freq)
            end_sample = int(end_sec * freq)

            # Clamp boundaries within actual audio length
            start_sample = max(0, min(start_sample, len(arr)))
            end_sample = max(start_sample, min(end_sample, len(arr)))

            trimmed_arr = arr[start_sample:end_sample]
            return pygame.sndarray.make_sound(trimmed_arr)
        except Exception as e:
            print(f"Error trimming sound {path}: {e}")
            return None

    def reload_sound_pad(self, index):
        pad_data = self.config.get(str(index))
        if pad_data and os.path.exists(pad_data.get("path", "")):
            start = pad_data.get("start", 0.0)
            end = pad_data.get("end", 10.0)
            path = pad_data["path"]
            self.loaded_sounds[str(index)] = self.process_trimmed_sound(
                path, start, end
            )
        else:
            self.loaded_sounds.pop(str(index), None)

    def reload_all_sounds(self):
        for i in range(9):
            self.reload_sound_pad(i)

    def open_edit_dialog(self, index):
        pad_data = self.config.get(str(index), {})

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Configure Pad {index+1}")
        dialog.geometry("380x300")
        dialog.configure(bg="#1e1e2e")
        dialog.grab_set()

        # Sound Path Selection
        tk.Label(dialog, text="Audio File:", fg="#cdd6f4", bg="#1e1e2e").pack(
            anchor="w", padx=20, pady=(15, 2)
        )
        path_var = tk.StringVar(value=pad_data.get("path", ""))
        path_entry = tk.Entry(
            dialog, textvariable=path_var, width=35, bg="#313244", fg="#cdd6f4"
        )
        path_entry.pack(padx=20)

        def browse():
            f = filedialog.askopenfilename(
                filetypes=[("Audio Files", "*.wav *.mp3 *.ogg")]
            )
            if f:
                path_var.set(f)

        tk.Button(
            dialog,
            text="Browse...",
            command=browse,
            bg="#45475a",
            fg="#cdd6f4",
            relief="flat",
        ).pack(pady=5)

        # Start Time Input
        tk.Label(
            dialog,
            text="Start Time (seconds):",
            fg="#cdd6f4",
            bg="#1e1e2e",
        ).pack(anchor="w", padx=20, pady=(10, 2))
        start_var = tk.StringVar(value=str(pad_data.get("start", 0.0)))
        start_entry = tk.Entry(
            dialog, textvariable=start_var, bg="#313244", fg="#cdd6f4"
        )
        start_entry.pack(padx=20, anchor="w")

        # End Time Input
        tk.Label(
            dialog,
            text="End Time (seconds, max 10s clip):",
            fg="#cdd6f4",
            bg="#1e1e2e",
        ).pack(anchor="w", padx=20, pady=(10, 2))
        end_var = tk.StringVar(value=str(pad_data.get("end", 5.0)))
        end_entry = tk.Entry(
            dialog, textvariable=end_var, bg="#313244", fg="#cdd6f4"
        )
        end_entry.pack(padx=20, anchor="w")

        # Save Action
        def save():
            path = path_var.get()
            if not path or not os.path.exists(path):
                messagebox.showerror("Error", "Please select a valid audio file.")
                return

            try:
                start = float(start_var.get())
                end = float(end_var.get())
            except ValueError:
                messagebox.showerror(
                    "Error", "Start and End times must be numbers."
                )
                return

            if start < 0 or end <= start:
                messagebox.showerror(
                    "Error", "End time must be greater than Start time."
                )
                return

            if (end - start) > MAX_DURATION:
                end = start + MAX_DURATION
                messagebox.showinfo(
                    "Duration Capped",
                    f"Clip length capped to 10 seconds maximum (End set to {end}s).",
                )

            self.config[str(index)] = {"path": path, "start": start, "end": end}
            self.save_config()
            self.reload_sound_pad(index)
            self.update_button_labels()
            dialog.destroy()

        tk.Button(
            dialog,
            text="Save Pad Settings",
            bg="#a6e3a1",
            fg="#11111b",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            command=save,
        ).pack(pady=20)

    def start_global_listener(self):
        def on_press(key):
            try:
                if key.char in self.hotkey_map:
                    self.play_sound(self.hotkey_map[key.char])
            except AttributeError:
                if key == keyboard.Key.esc:
                    self.stop_all_sounds()

        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = SoundboardApp(root)
    root.mainloop()
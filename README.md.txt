# 🔊 Python Soundboard (Trimmable & Anti-Spam)

A lightweight Tkinter and Pygame-based GUI soundboard for Windows that supports live audio trimming, anti-overlap sound cutting, and global hotkeys.

## ✨ Features
- **9 Custom Sound Pads:** Right-click any pad to assign audio files (.mp3, .wav, .ogg) and trim start/end times.
- **Anti-Spam Playback:** Prevents overlapping noise by cutting off current audio when a new sound or `ESC` is pressed.
- **Discord Ready:** Sample rate optimized at 48kHz for crisp, clear playback over virtual audio cables.
- **Global Hotkeys:** Trigger sounds using keyboard keys `1–9` even when tabbed into games.

---

## 🛠 Prerequisites & Audio Routing (For Discord)
To stream your soundboard and microphone into Discord simultaneously:

1. Download and install [VB-Audio Virtual Cable](https://vb-audio.com/Cable/).
2. Open **Windows Volume Mixer** and set the output of this Soundboard app to `CABLE Input (VB-Audio Virtual Cable)`.
3. In Windows Sound Control Panel (`mmsys.cpl`):
   - Under **Recording**, right-click your **Microphone** > **Properties** > **Listen** tab. Check **"Listen to this device"** and select `CABLE Input`.
   - Under **Recording**, right-click **CABLE Output** > **Properties** > **Listen** tab. Check **"Listen to this device"** and select your Headphones (so you can hear the sounds too).
4. In **Discord Voice Settings**, set your **Input Device** to `CABLE Output (VB-Audio Virtual Cable)` and turn off **Noise Suppression**.

---

## 🚀 Running from Source

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git)
   cd YOUR_REPOSITORY
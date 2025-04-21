import cv2
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from itertools import cycle
from pathlib import Path


# GUI setup
class VideoShufflerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Frame Shuffler")

        self.video_paths = []

        # UI Elements
        self.fps_var = tk.StringVar(value="24")
        fps_options = ["24", "30", "60"]

        ttk.Label(root, text="Select Target FPS:").pack(pady=5)
        self.fps_dropdown = ttk.Combobox(
            root, values=fps_options, textvariable=self.fps_var
        )
        self.fps_dropdown.pack(pady=5)

        self.select_button = ttk.Button(
            root, text="Select Videos", command=self.select_videos
        )
        self.select_button.pack(pady=5)

        self.process_button = ttk.Button(
            root, text="Shuffle and Export", command=self.shuffle_and_export
        )
        self.process_button.pack(pady=10)

        self.status_label = ttk.Label(root, text="")
        self.status_label.pack(pady=5)

    def select_videos(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if files:
            self.video_paths = list(files)
            self.status_label.config(text=f"Selected {len(self.video_paths)} videos.")

    def shuffle_and_export(self):
        if not self.video_paths:
            messagebox.showerror("No Videos", "Please select at least 2 video files.")
            return

        try:
            target_fps = int(self.fps_var.get())
        except ValueError:
            messagebox.showerror("Invalid FPS", "Please select a valid FPS.")
            return

        self.status_label.config(text="Processing...")

        # open video file
        caps = [cv2.VideoCapture(path) for path in self.video_paths]

        # get comon frame dimenstions
        width = int(caps[0].get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(caps[0].get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Ensure all videos are same resolution
        # Find maximum resolution among all videos
        max_width = max(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) for cap in caps)
        max_height = max(int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) for cap in caps)

        # ask for output path
        out_path = filedialog.asksaveasfilename(
            defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")]
        )
        if not out_path:
            for cap in caps:
                cap.release()
            return

        # video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(out_path, fourcc, target_fps, (max_width, max_height))

        # Round robin interleaving
        exhausted = [False] * len(caps)
        while not all(exhausted):
            for i, cap in enumerate(caps):
                if not exhausted[i]:
                    ret, frame = cap.read()
                    if ret:
                        resized = cv2.resize(
                            frame,
                            (max_width, max_height),
                            interpolation=cv2.INTER_LINEAR,
                        )
                        out.write(resized)
                    else:
                        exhausted[i] = True  # This video is done

        # cleanup
        for cap in caps:
            cap.release()
        out.release()

        self.status_label.config(text="Export completed!")
        messagebox.showinfo("Done", "Video successfully created!")


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoShufflerApp(root)
    root.mainloop()

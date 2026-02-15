import tkinter as tk
from tkinter import ttk, messagebox
import csv
import json
import os
import time
from datetime import datetime
from threading import Thread
from pynput import mouse, keyboard
from PIL import ImageGrab
import platform

class StepSnapRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("StepSnap Recorder - Dark Mode")
        self.root.geometry("350x280")
        self.root.attributes("-topmost", True)  # Keep window on top
        
        # Color Palette (Dark Mode)
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#007acc',
            'recording': '#d13438',
            'text_secondary': '#cccccc'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # State variables
        self.is_recording = False
        self.steps = []
        self.start_time = None
        self.session_folder = ""
        self.mouse_listener = None
        self.hotkey_listener = None
        
        self.setup_ui()

    def setup_ui(self):
        """Creates a sleek Dark Mode GUI."""
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure Styles
        style.configure("TFrame", background=self.colors['bg'])
        style.configure("TLabel", background=self.colors['bg'], foreground=self.colors['fg'], font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=self.colors['bg'], foreground=self.colors['fg'], font=("Segoe UI", 14, "bold"))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"))
        
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.status_label = ttk.Label(
            self.main_frame, text="READY", style="Header.TLabel"
        )
        self.status_label.pack(pady=(0, 10))

        # Visual indicator for recording
        self.indicator = tk.Canvas(self.main_frame, width=20, height=20, bg=self.colors['bg'], highlightthickness=0)
        self.indicator_circle = self.indicator.create_oval(2, 2, 18, 18, fill="gray")
        self.indicator.pack(pady=5)

        self.btn_toggle = tk.Button(
            self.main_frame, 
            text="START RECORDING", 
            command=self.toggle_recording,
            bg=self.colors['accent'],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20,
            pady=10
        )
        self.btn_toggle.pack(fill=tk.X, pady=10)

        self.help_label = ttk.Label(
            self.main_frame, 
            text="[Ctrl+Alt+S] to Stop Early\nScreenshots + CSV + JSON + Wiki", 
            font=("Segoe UI", 8),
            justify="center",
            foreground=self.colors['text_secondary']
        )
        self.help_label.pack(pady=10)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.steps = []
        self.start_time = time.time()
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_folder = f"recording_{timestamp}"
        os.makedirs(self.session_folder, exist_ok=True)
        os.makedirs(os.path.join(self.session_folder, "screenshots"), exist_ok=True)

        # UI Update
        self.status_label.config(text="RECORDING", foreground=self.colors['recording'])
        self.indicator.itemconfig(self.indicator_circle, fill=self.colors['recording'])
        self.btn_toggle.config(text="STOP", bg=self.colors['recording'])
        
        # Listeners
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()
        
        self.hotkey_listener = keyboard.GlobalHotkeys({
            '<ctrl>+<alt>+s': self.stop_recording
        })
        self.hotkey_listener.start()

    def on_click(self, x, y, button, pressed):
        if pressed and self.is_recording:
            timestamp_str = datetime.now().strftime("%H:%M:%S")
            elapsed = round(time.time() - self.start_time, 2)
            
            ss_name = f"step_{len(self.steps) + 1}.png"
            ss_path = os.path.join(self.session_folder, "screenshots", ss_name)
            
            # Capture logic with safety for dual monitors
            try:
                bbox = (x - 150, y - 150, x + 150, y + 150)
                screenshot = ImageGrab.grab(bbox=bbox)
                screenshot.save(ss_path)
            except:
                ss_name = "ERROR_CAPTURING"

            step_data = {
                "step": len(self.steps) + 1,
                "time": timestamp_str,
                "seconds": elapsed,
                "action": str(button),
                "x": x,
                "y": y,
                "screenshot": ss_name,
                "wiki_entry": f"User performed a {button} at screen coordinates {x}, {y}."
            }
            self.steps.append(step_data)

    def stop_recording(self):
        if not self.is_recording: return
        self.is_recording = False
        
        if self.mouse_listener: self.mouse_listener.stop()
        if self.hotkey_listener: self.hotkey_listener.stop()

        self.save_data()
        
        self.status_label.config(text="READY", foreground=self.colors['fg'])
        self.indicator.itemconfig(self.indicator_circle, fill="gray")
        self.btn_toggle.config(text="START RECORDING", bg=self.colors['accent'])
        
        messagebox.showinfo("Saved", f"Files generated in:\n{self.session_folder}")

    def save_data(self):
        # JSON
        with open(os.path.join(self.session_folder, "data.json"), 'w') as f:
            json.dump(self.steps, f, indent=4)

        # CSV
        if self.steps:
            with open(os.path.join(self.session_folder, "data.csv"), 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.steps[0].keys())
                writer.writeheader()
                writer.writerows(self.steps)

        # Wiki / Training Text
        with open(os.path.join(self.session_folder, "training_guide.txt"), 'w') as f:
            f.write(f"TRAINING DOCUMENT - Generated {datetime.now()}\n")
            f.write("="*40 + "\n\n")
            for s in self.steps:
                f.write(f"STEP {s['step']}: {s['wiki_entry']}\n")
                f.write(f"Visual Reference: screenshots/{s['screenshot']}\n\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = StepSnapRecorder(root)
    root.mainloop()

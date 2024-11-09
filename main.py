import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import sounddevice as sd
import wave
import numpy as np

layer = "main"  # Current screen layer

# =============================== Audio Recording ===================================

# Global variables
recording = False
audio_data = []
current_stream = None

# Check available devices and get default input device info
print(sd.query_devices())
device_info = sd.query_devices(sd.default.device['input'])
sample_rate = int(device_info['default_samplerate'])
print(f"Input Device Sample Rate: {sample_rate} Hz, Channels: {device_info['max_input_channels']}")

# Set default sample rate and channels (1 channel, 32-bit float input)
sd.default.samplerate = sample_rate
sd.default.channels = 1

def record_audio():
    global recording, audio_data, current_stream

    if not recording:
        # Start recording
        audio_data = []
        recording = True
        record_button.configure(text="Stop Recording")

        # Initialize the input stream with a larger block size
        current_stream = sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype='float32',  # Use 32-bit float input as per your device settings
            callback=audio_callback,
            blocksize=2048
        )
        current_stream.start()
    else:
        # Stop recording and save the audio
        recording = False
        current_stream.stop()
        current_stream.close()
        current_stream = None
        record_button.configure(text="Start Recording")
        save_audio()

def audio_callback(indata, frames, time, status):
    global audio_data
    if recording:
        # Convert 32-bit float data to 16-bit PCM format
        pcm_data = np.int16(indata * 32767)  # Scale float data to 16-bit PCM range
        audio_data.append(pcm_data)

def save_audio():
    """Save the recorded audio to a WAV file."""
    if not audio_data:
        messagebox.showinfo("No Data", "No audio data recorded.")
        return

    # Concatenate the recorded audio chunks
    audio_array = np.concatenate(audio_data, axis=0)

    # Save the audio as a 16-bit PCM WAV file
    with wave.open("output.wav", "w") as wf:
        wf.setnchannels(1)          # Mono
        wf.setsampwidth(2)          # 16-bit PCM
        wf.setframerate(sample_rate)
        wf.writeframes(audio_array.tobytes())

    messagebox.showinfo("Recording Saved", "Audio saved as 'output.wav'.")



# =============================== Button Functions ==================================

# Function to create rounded button images
def create_rounded_button_image(width, height, color, radius):
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=color)
    return ImageTk.PhotoImage(image)

# Custom Button Class with Hover Effect
class CustomButton(tk.Label):
    def __init__(self, master, text, command, relx=0.5, rely=0.5, width=0.3, height=0.15, **kwargs):
        self.default_bg = "#4c5f7a"
        self.hover_color = "#5a6b8a"
        self.text_color = "#ffffff"
        self.widthScale = width
        self.heightScale = height
        self.relx = relx
        self.rely = rely

        super().__init__(master, text=text, **kwargs)
        self.configure(
            compound="center",
            font=("Futura", 20),
            fg=self.text_color,
            bg="#0a1a2b",
        )
        self.command = command

        # Initialize the button images
        self.image = None
        self.hover_image = None

        # Bind hover and click events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", lambda e: self.command())

    def on_enter(self, event):
        self.configure(image=self.hover_image)

    def on_leave(self, event):
        self.configure(image=self.image)

    def hideButton(self):
        self.place_forget()
        self.configure(image=self.image)


    def drawButton(self):
        w = max(int(root.winfo_width() * self.widthScale), 50)
        h = max(int(root.winfo_height() * self.heightScale), 50)

        # Create the button images
        self.image = create_rounded_button_image(w, h, self.default_bg, 10)
        self.hover_image = create_rounded_button_image(w, h, self.hover_color, 10)

        # Update the button configuration with the images
        self.configure(image=self.image)

        # Place the button using relx and rely
        self.place(relx=self.relx, rely=self.rely, anchor="center")
        self.update_idletasks()

# Screen navigation functions
def show_main_screen():
    global layer
    layer = "main"
    hide_all()
    title_label.place(relx=0.5, rely=0.1, anchor="center")
    image_label.place(relx=0.25, rely=0.5, anchor="center")
    memory_options_label.place(relx=0.75, rely=0.25, anchor="center")
    start_button.drawButton()
    relive_button.drawButton()

def start_new_memory():
    global layer
    layer = "start_memory"

    recording = False
    audio_data = []

    hide_all()

    back_button.drawButton()
    cancel_button.drawButton()
    done_button.drawButton()
    record_button.drawButton()

def relive_past_memories():
    global layer
    layer = "relive_memories"
    hide_all()
    back_button.drawButton()
    messagebox.showinfo("Relive Past Memories", "Reliving past memories!")

def go_back():
    if layer == "start_memory" or layer == "relive_memories":
        show_main_screen()

def hide_all():
    start_button.hideButton()
    relive_button.hideButton()
    cancel_button.hideButton()
    done_button.hideButton()
    back_button.hideButton()
    record_button.hideButton()
    memory_options_label.place_forget()
    # fill the background with the main color
    root.configure(bg="#0a1a2b")

# ================================ Main Program =====================================

# Initialize the main window
root = tk.Tk()
root.title("Mem-inisce")
root.configure(bg="#0a1a2b")
root.geometry("800x600")
root.minsize(600, 400)

# Main Title
title_label = tk.Label(root, text="Mem-inisce", font=("Helvetica", 50, "bold"), fg="#ffffff", bg="#0a1a2b")

# Load the image
original_image = Image.open("images/194.png").resize((300, 300), Image.Resampling.LANCZOS)
photo = ImageTk.PhotoImage(original_image)
image_label = tk.Label(root, image=photo, bg="#0a1a2b")

# Memory Options Section
memory_options_label = tk.Label(root, text="Memory Options", font=("Arial", 20), fg="#ffffff", bg="#0a1a2b")

# Create Buttons
start_button = CustomButton(root, text="Start New Memory", command=start_new_memory, relx=0.75, rely=0.4)
relive_button = CustomButton(root, text="Relive Past Memories", command=relive_past_memories, relx=0.75, rely=0.6)
cancel_button = CustomButton(root, text="Cancel", command=go_back, relx=0.3, rely=0.85)
done_button = CustomButton(root, text="Done", command=go_back, relx=0.7, rely=0.85)
back_button = CustomButton(root, text="Back", command=go_back, relx=0.1, rely=0.1, width=0.1, height=0.1)
record_button = CustomButton(root, text="Start Recording", command=record_audio, relx=0.5, rely=0.85, width=0.3, height=0.15)

# Function to scale UI elements dynamically
def on_resize(event):
    if start_button.winfo_ismapped(): start_button.drawButton()
    if relive_button.winfo_ismapped(): relive_button.drawButton()
    if cancel_button.winfo_ismapped(): cancel_button.drawButton()
    if done_button.winfo_ismapped(): done_button.drawButton()
    if back_button.winfo_ismapped():back_button.drawButton()

# Bind the resize event
root.bind("<Configure>", on_resize)

# Show the main screen initially
show_main_screen()

# Run the main loop
root.mainloop()

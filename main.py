import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import sounddevice as sd
import wave
import numpy as np

import tts

layer = "main"  # Current screen layer

# =============================== Audio Recording ===================================

global recording, audio_data, current_stream, record_count, max_recordings
recording = False
audio_data = []
current_stream = None
record_count = 0
max_recordings = 5

# Device and audio settings
device_info = sd.query_devices(sd.default.device['input'])
sample_rate = int(device_info['default_samplerate'])
sd.default.samplerate = sample_rate
sd.default.channels = 1

def record_audio():
    global recording, audio_data, current_stream

    if not recording:
        audio_data = []
        recording = True
        record_button.configure(text="Stop Recording")

        current_stream = sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype='float32',
            callback=audio_callback,
            blocksize=2048
        )
        current_stream.start()
    else:
        recording = False
        current_stream.stop()
        current_stream.close()
        current_stream = None
        save_audio()
        play_audio()
        record_button.configure(text="Start Recording")

def audio_callback(indata, frames, time, status):
    global audio_data
    if recording:
        pcm_data = np.int16(indata * 32767)
        audio_data.append(pcm_data)

def save_audio():
    global record_count
    if not audio_data:
        messagebox.showinfo("No Data", "No audio data recorded.")
        return

    audio_array = np.concatenate(audio_data, axis=0)
    filename = f"inputs/input_{record_count}.wav"

    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_array.tobytes())

    # messagebox.showinfo("Recording Saved", f"Audio saved as '{filename}'.")

def wrap_text(text, line_length=70):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        # Check if adding the word exceeds the line length
        if len(current_line) + len(word) + 1 <= line_length:
            # Add the word to the current line
            if current_line:
                current_line += " "
            current_line += word
        else:
            # Start a new line if the word doesn't fit
            lines.append(current_line)
            current_line = word

    # Add the last line
    if current_line:
        lines.append(current_line)

    return "\n".join(lines)

def play_audio():
    filename = f"inputs/input_{record_count}.wav"
    new_filename = f"outputs/output_{record_count}.wav"

    text = tts.wav2txt(filename)

    if record_count == max_recordings - 1:
        text = "Thanks for sharing your story with us today! Press back to navigate to the home page! We look forward to talking with you again soon!"

    prompt_label.configure(text=wrap_text(text))

    tts.txt2wav(text, new_filename)

    try:
        with wave.open(new_filename, "rb") as wf:
            n_channels = wf.getnchannels()
            frame_rate = wf.getframerate()
            sample_width = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())

            # Check if the format is 32-bit float (sample width of 4 bytes)
            if sample_width == 4:
                # Convert from 32-bit float to 16-bit PCM
                audio_data = np.frombuffer(frames, dtype=np.float32)
                audio_data = np.int16(audio_data * 32767)
            else:
                # Assume it's already 16-bit PCM
                audio_data = np.frombuffer(frames, dtype=np.int16)

            # Reshape for stereo if necessary
            if n_channels == 2:
                audio_data = audio_data.reshape(-1, 2)

            # Play the audio
            sd.play(audio_data, samplerate=frame_rate)
            # sd.wait()

            prompt_next_recording()
    except Exception as e:
        messagebox.showerror("Playback Error", str(e))

def prompt_next_recording():
    #if this is the last one save the audio to a saved folder
    
    global record_count
    record_count += 1

    if record_count < max_recordings:
        print("Continue", f"Recording {record_count} complete. Prepare for the next recording.")
        record_button.configure(text="Start Recording")
    else:
        record_button.hideButton()
        print("Session Complete", "You have completed 5 recordings. Session ended.")


def play_story(i):
    new_filename = f"outputs/output_{i}.wav"

    try:
        with wave.open(new_filename, "rb") as wf:
            n_channels = wf.getnchannels()
            frame_rate = wf.getframerate()
            sample_width = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())

            # Check if the format is 32-bit float (sample width of 4 bytes)
            if sample_width == 4:
                # Convert from 32-bit float to 16-bit PCM
                audio_data = np.frombuffer(frames, dtype=np.float32)
                audio_data = np.int16(audio_data * 32767)
            else:
                # Assume it's already 16-bit PCM
                audio_data = np.frombuffer(frames, dtype=np.int16)

            # Reshape for stereo if necessary
            if n_channels == 2:
                audio_data = audio_data.reshape(-1, 2)

            # Play the audio
            sd.play(audio_data, samplerate=frame_rate)
            # sd.wait()

    except Exception as e:
        messagebox.showerror("Playback Error", str(e))

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
            font=("Futura", 25),
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
    title_label.place(relx=0.5, rely=0.15, anchor="center")
    image_label.place(relx=0.5, rely=0.35, anchor="center")
    start_button.drawButton()
    relive_button.drawButton()

def start_new_memory():
    global layer
    layer = "start_memory"

    recording = False
    audio_data = []

    hide_all()

    for i, flower in enumerate(flowers):
        flower.place(relx=0.1 + 0.2 * i, rely=0.9, anchor="center")

    back_button.drawButton()
    record_button.drawButton()
    prompt_label.place(relx=0.5, rely=0.45, anchor="center")

def relive_past_memories():
    global layer
    layer = "relive_memories"
    hide_all()
    
    for i, flower in enumerate(flowers):
        flower.place(relx=0.1 + 0.2 * i, rely=0.9, anchor="center")

    back_button.drawButton()
    play0_button.drawButton()
    play1_button.drawButton()
    play2_button.drawButton()
    play3_button.drawButton()


def play0():
    play_story(0)

def play1():
    play_story(1)

def play2():
    play_story(2)

def play3():
    play_story(3)

def go_back():
    if layer == "start_memory" or layer == "relive_memories":
        show_main_screen()

def hide_all():
    for flower in flowers:
        flower.place_forget()

    start_button.hideButton()
    relive_button.hideButton()
    back_button.hideButton()
    record_button.hideButton()
    prompt_label.place_forget()
    image_label.place_forget()
    play0_button.hideButton()
    play1_button.hideButton()
    play2_button.hideButton()
    play3_button.hideButton()
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
title_label = tk.Label(root, text="Mem-inisce", font=("Futura", 80, "bold"), fg="#ffffff", bg="#0a1a2b")

# Prompt label
prompt_label = tk.Label(root, text="", font=("Futura", 20, "bold"), fg="#ffffff", bg="#0a1a2b")


#Load the image
original_image = Image.open("images/Mem.png").resize((800, 400), Image.Resampling.LANCZOS)
photo = ImageTk.PhotoImage(original_image)
image_label = tk.Label(root, image=photo, bg="#0a1a2b")

#Flower image
flowers = []
flower_photos = []
for i in range(5):
    flower_image = Image.open("images/flower.png").resize((100, 100), Image.Resampling.LANCZOS)
    flower_photo = ImageTk.PhotoImage(flower_image)
    flower_label = tk.Label(root, image=flower_photo, bg="#0a1a2b")
    flower_photos.append(flower_photo)
    flowers.append(flower_label)

# Create Buttons
start_button = CustomButton(root, text="New Memory", command=start_new_memory, relx=0.3, rely=0.8)
relive_button = CustomButton(root, text="Relive the Past", command=relive_past_memories, relx=0.7, rely=0.8)
back_button = CustomButton(root, text="Back", command=go_back, relx=0.1, rely=0.1, width=0.1, height=0.1)
record_button = CustomButton(root, text="Start Recording", command=record_audio, relx=0.5, rely=0.7, width=0.5, height=0.15)

play0_button = CustomButton(root, text="Play Memory 0", command=play0, relx=0.5, rely=0.4, width=0.5, height=0.1)
play1_button = CustomButton(root, text="Play Memory 1", command=play1, relx=0.5, rely=0.55, width=0.5, height=0.1)
play2_button = CustomButton(root, text="Play Memory 2", command=play2, relx=0.5, rely=0.7, width=0.5, height=0.1)
play3_button = CustomButton(root, text="Play Memory 3", command=play3, relx=0.5, rely=0.85, width=0.5, height=0.1)


# Function to scale UI elements dynamically
def on_resize(event):
    if start_button.winfo_ismapped(): start_button.drawButton()
    if relive_button.winfo_ismapped(): relive_button.drawButton()
    if back_button.winfo_ismapped():back_button.drawButton()
    if record_button.winfo_ismapped(): record_button.drawButton()
    if play0_button.winfo_ismapped(): play0_button.drawButton()
    if play1_button.winfo_ismapped(): play1_button.drawButton()
    if play2_button.winfo_ismapped(): play2_button.drawButton()
    if play3_button.winfo_ismapped(): play3_button.drawButton()

# Bind the resize event
root.bind("<Configure>", on_resize)

# Show the main screen initially
show_main_screen()

# Run the main loop
root.mainloop()

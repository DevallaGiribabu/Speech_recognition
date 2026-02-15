import speech_recognition as sr
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from deep_translator import GoogleTranslator
from langdetect import detect
import time
import math

# ---------------------------
# CONFIG
# ---------------------------
recognizer = sr.Recognizer()
recording = False

# Languages to translate into:
TRANSLATE_TARGETS = {
    "English": "en",
    "Telugu": "te",
    "Tamil": "ta",
    "Hindi": "hi"
}

LANGUAGE_NAMES = {
    "en": "English",
    "te": "Telugu",
    "ta": "Tamil",
    "hi": "Hindi",
    "kn": "Kannada",
    "ml": "Malayalam"
}

# ---------------------------
# GUI WINDOW
# ---------------------------
root = tk.Tk()
root.title("AI Speech Recognition & Translator – Auto Detect Language")
root.geometry("820x650")
root.configure(bg="#121212")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#121212", foreground="white", font=("Segoe UI", 12))
style.configure("TButton", font=("Segoe UI", 11), padding=6)

# ---------------------------
# WAVEFORM
# ---------------------------
wave_canvas = tk.Canvas(root, width=780, height=120, bg="#1e1e1e", highlightthickness=0)
wave_canvas.pack(pady=10)

# ---------------------------
# OUTPUT BOX
# ---------------------------
output_box = tk.Text(root, height=18, width=95, bg="#1e1e1e", fg="white",
                     font=("Segoe UI", 12), wrap="word")
output_box.pack(pady=15)

# ---------------------------
# ACCURACY BAR
# ---------------------------
accuracy_label = ttk.Label(root, text="Recognition Accuracy Estimate:")
accuracy_label.pack()
accuracy_bar = ttk.Progressbar(root, length=350)
accuracy_bar.pack(pady=5)

# ---------------------------
# FUNCTIONS
# ---------------------------

def animate_waveform():
    """Mic waveform animation."""
    while recording:
        wave_canvas.delete("all")
        for i in range(0, 780, 15):
            h = 30 + 30 * math.sin(time.time() * 8 + i / 20)
            wave_canvas.create_line(i, 60 - h, i, 60 + h, fill="#00ffcc", width=3)
        root.update()
        time.sleep(0.03)


def estimate_accuracy(text):
    """Simple accuracy estimation."""
    if len(text) < 3:
        return 10
    elif len(text) < 10:
        return 40
    elif len(text) < 30:
        return 65
    else:
        return 85


def detect_language_name(text):
    try:
        code = detect(text)
        name = LANGUAGE_NAMES.get(code, "Unknown")
        return code, name
    except:
        return "unknown", "Unknown"


def recognize_speech():
    global recording
    recording = True

    threading.Thread(target=animate_waveform).start()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.8)
        output_box.insert(tk.END, "\n🎙️ Listening...\n")
        output_box.see(tk.END)

        try:
            audio = recognizer.listen(source, phrase_time_limit=10)

            # AUTO DETECT LANGUAGE
            text = recognizer.recognize_google(audio)
            output_box.insert(tk.END, f"\nYou said: {text}\n")

            # -------------------------
            # Detect Language Name
            # -------------------------
            lang_code, lang_name = detect_language_name(text)
            output_box.insert(tk.END, f"🌐 Detected Language: {lang_name} ({lang_code})\n")

            # -------------------------
            # Estimated Accuracy
            # -------------------------
            accuracy = estimate_accuracy(text)
            accuracy_bar['value'] = accuracy

            # -------------------------
            # MULTI TRANSLATION
            # -------------------------
            output_box.insert(tk.END, "\n--- Translations ---\n")
            for lang, code in TRANSLATE_TARGETS.items():
                translated = GoogleTranslator(source='auto', target=code).translate(text)
                output_box.insert(tk.END, f"{lang} ({code}): {translated}\n")

        except Exception as e:
            output_box.insert(tk.END, f"Error: {str(e)}\n")

        output_box.see(tk.END)

    recording = False


def start_recording():
    threading.Thread(target=recognize_speech).start()


def save_to_file():
    data = output_box.get("1.0", tk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data)

# ---------------------------
# BUTTONS
# ---------------------------
button_frame = tk.Frame(root, bg="#121212")
button_frame.pack(pady=10)

start_btn = tk.Button(button_frame, text="🎙️ Start Recording", command=start_recording,
                      bg="#00ffaa", fg="black", font=("Segoe UI", 12, "bold"),
                      relief="flat", width=18)
start_btn.grid(row=0, column=0, padx=10)

save_btn = tk.Button(button_frame, text="💾 Save Output", command=save_to_file,
                     bg="#ffaa00", fg="black", font=("Segoe UI", 12, "bold"),
                     relief="flat", width=18)
save_btn.grid(row=0, column=1, padx=10)

clear_btn = tk.Button(button_frame, text="🧹 Clear",
                      command=lambda: output_box.delete("1.0", tk.END),
                      bg="#ff5555", fg="white", font=("Segoe UI", 12, "bold"),
                      relief="flat", width=10)
clear_btn.grid(row=0, column=2, padx=10)

# ---------------------------
# MAINLOOP
# ---------------------------
root.mainloop()

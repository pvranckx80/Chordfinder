import os
import os
import sys
import wave
import struct
import random   
import tempfile
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageDraw, ImageFont, ImageTk

# Enable ANSI colors in older Windows terminals
os.system("")

# ANSI Color Codes
RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
DIM = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Standard tuning open-string chromatic indices (E2=4, A2=9, D3=2, G3=7, B3=11, E4=4)
OPEN_STRING_INDICES = [4, 9, 2, 7, 11, 4]
# Exact open-string frequencies in Hz (E2, A2, D3, G3, B3, E4)
OPEN_STRING_FREQS = [82.41, 110.00, 146.83, 196.00, 246.94, 329.63]

SHARP_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_NOTES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

ENHARMONICS = {
    "Db": "C#",
    "Eb": "D#",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
}

CHORD_TYPES = [
    "", "m", "7", "maj7", "m7", "add9", "sus2", "sus4", 
    "dim", "dim7", "aug", "6", "m6", "9", "m7b5"
]

# Base movable barre shapes (rooted on E-string = fret 0, or A-string = fret 0)
MOVABLE_SHAPES = {
    "E_root": {
        "":     [0, 2, 2, 1, 0, 0],
        "m":    [0, 2, 2, 0, 0, 0],
        "7":    [0, 2, 0, 1, 0, 0],
        "maj7": [0, 2, 1, 1, 0, 0],
        "m7":   [0, 2, 0, 0, 0, 0],
        "add9": [0, 2, 4, 1, 0, 0],
        "sus2": [0, 2, 4, 4, 0, 0],
        "sus4": [0, 2, 2, 2, 0, 0],
        "dim":  [0, 1, 2, 1, 2, 1],
        "dim7": [0, 1, 2, 1, 2, 0],
        "aug":  [0, 2, 2, 2, 1, 0],
        "6":    [0, 2, 2, 1, 2, 0],
        "m6":   [0, 2, 2, 0, 2, 0],
        "9":    [0, 2, 0, 1, 2, 0],
        "m7b5": [0, 1, 0, 0, 2, 0],
    },
    "A_root": {
        "":     ["x", 0, 2, 2, 2, 0],
        "m":    ["x", 0, 2, 2, 1, 0],
        "7":    ["x", 0, 2, 0, 2, 0],
        "maj7": ["x", 0, 2, 1, 2, 0],
        "m7":   ["x", 0, 2, 0, 1, 0],
        "add9": ["x", 0, 2, 4, 2, 0],
        "sus2": ["x", 0, 2, 2, 0, 0],
        "sus4": ["x", 0, 2, 2, 3, 0],
        "dim":  ["x", 0, 1, 2, 1, 2],
        "dim7": ["x", 0, 1, 2, 1, 1],
        "aug":  ["x", 0, 2, 2, 2, 1],
        "6":    ["x", 0, 2, 1, 2, 2],
        "m6":   ["x", 0, 2, 0, 2, 2],
        "9":    ["x", 0, 2, 0, 2, 1],
        "m7b5": ["x", 0, 1, 2, 1, 2],
    },
}

# Preferred open chords
OPEN_CHORDS = {
    "C":      ["x", 3, 2, 0, 1, 0],
    "C7":     ["x", 3, 2, 3, 1, 0],
    "Cmaj7":  ["x", 3, 2, 0, 0, 0],
    "Cadd9":  ["x", 3, 2, 0, 3, 3],
    "Csus2":  ["x", 3, 0, 0, 1, 3],
    "Csus4":  ["x", 3, 3, 0, 1, 1],

    "D":      ["x", "x", 0, 2, 3, 2],
    "Dm":     ["x", "x", 0, 2, 3, 1],
    "D7":     ["x", "x", 0, 2, 1, 2],
    "Dmaj7":  ["x", "x", 0, 2, 2, 2],
    "Dm7":    ["x", "x", 0, 2, 1, 1],
    "Dadd9":  ["x", "x", 0, 2, 3, 0],
    "Dsus2":  ["x", "x", 0, 2, 3, 0],
    "Dsus4":  ["x", "x", 0, 2, 3, 3],

    "E":      [0, 2, 2, 1, 0, 0],
    "Em":     [0, 2, 2, 0, 0, 0],
    "E7":     [0, 2, 0, 1, 0, 0],
    "Emaj7":  [0, 2, 1, 1, 0, 0],
    "Em7":    [0, 2, 0, 0, 0, 0],
    "Eadd9":  [0, 2, 4, 1, 0, 0],
    "Esus2":  [0, 2, 4, 4, 0, 0],
    "Esus4":  [0, 2, 2, 2, 0, 0],

    "Fmaj7":  ["x", "x", 3, 2, 1, 0],
    "Fadd9":  ["x", "x", 3, 2, 1, 3],
    "Fsus2":  ["x", "x", 3, 0, 1, 1],

    "G":      [3, 2, 0, 0, 0, 3],
    "G7":     [3, 2, 0, 0, 0, 1],
    "Gmaj7":  [3, 2, 0, 0, 0, 2],
    "Gadd9":  [3, 2, 0, 2, 0, 3],
    "Gsus2":  [3, 0, 0, 0, 3, 3],
    "Gsus4":  [3, 3, 0, 0, 1, 1],

    "A":      ["x", 0, 2, 2, 2, 0],
    "Am":     ["x", 0, 2, 2, 1, 0],
    "A7":     ["x", 0, 2, 0, 2, 0],
    "Amaj7":  ["x", 0, 2, 1, 2, 0],
    "Am7":    ["x", 0, 2, 0, 1, 0],
    "Aadd9":  ["x", 0, 2, 4, 2, 0],
    "Asus2":  ["x", 0, 2, 2, 0, 0],
    "Asus4":  ["x", 0, 2, 2, 3, 0],

    "B7":     ["x", 2, 1, 2, 0, 2],
    
    # Add dim, dim7, aug, 6, m6, 9, m7b5 for open positions where available
    "Cdim":   ["x", 3, 1, 0, 1, 0],
    "Ddim":   ["x", "x", 0, 1, 0, 1],
    "Edim":   [0, 1, 2, 1, 2, 1],
    "Gdim":   [3, 1, 0, 1, 2, 1],
    "Adim":   ["x", 0, 1, 2, 1, 2],
    
    "Caug":   ["x", 3, 2, 1, 1, 0],
    "Daug":   ["x", "x", 0, 2, 2, 2],
    "Eaug":   [0, 2, 2, 2, 1, 0],
    "Gaug":   [3, 2, 0, 1, 1, 3],
    "Aaug":   ["x", 0, 2, 2, 2, 1],
    
    "C6":     ["x", 3, 2, 2, 1, 0],
    "D6":     ["x", "x", 0, 2, 2, 2],
    "E6":     [0, 2, 2, 1, 2, 0],
    "G6":     [3, 2, 0, 0, 0, 2],
    "A6":     ["x", 0, 2, 2, 2, 2],
}

# Classic hand-crafted slash chord voicings
CUSTOM_SLASH_CHORDS = {
    "C/G":   [3, 3, 2, 0, 1, 0],
    "C/E":   [0, 3, 2, 0, 1, 0],
    "C/B":   ["x", 2, 2, 0, 1, 0],

    "D/F#":  [2, "x", 0, 2, 3, 2],
    "D/A":   ["x", 0, 0, 2, 3, 2],
    "Dm/F":  [1, "x", 0, 2, 3, 1],

    "E/G#":  [4, 2, 2, 1, 0, 0],
    "Em/B":  ["x", 2, 2, 0, 0, 0],
    "Em/G":  [3, 2, 2, 0, 0, 0],

    "F/C":   ["x", 3, 3, 2, 1, 1],

    "G/B":   ["x", 2, 0, 0, 3, 3],
    "G/D":   ["x", "x", 0, 0, 0, 3],
    "G/F#":  [2, 2, 0, 0, 0, 3],

    "Am/G":  [3, 0, 2, 2, 1, 0],
    "Am/E":  [0, 0, 2, 2, 1, 0],
    "Am/C":  ["x", 3, 2, 2, 1, 0],
}

def shift_shape(base_shape, semitones):
    return [f + semitones if isinstance(f, int) else f for f in base_shape]

def build_chord_library():
    library = {}
    e_roots = {"F": 1, "F#": 2, "G": 3, "G#": 4}
    a_roots = {"A#": 1, "B": 2, "C": 3, "C#": 4, "D": 5, "D#": 6}

    for note in SHARP_NOTES:
        for suffix in CHORD_TYPES:
            chord_name = f"{note}{suffix}"
            if chord_name in OPEN_CHORDS:
                library[chord_name] = OPEN_CHORDS[chord_name]
            elif note in e_roots:
                library[chord_name] = shift_shape(MOVABLE_SHAPES["E_root"][suffix], e_roots[note])
            elif note in a_roots:
                library[chord_name] = shift_shape(MOVABLE_SHAPES["A_root"][suffix], a_roots[note])
            else:
                # For notes not in e_roots or a_roots, calculate offset from E or A
                if note in SHARP_NOTES:
                    e_index = SHARP_NOTES.index("E")
                    note_index = SHARP_NOTES.index(note)
                    offset = (note_index - e_index) % 12
                    library[chord_name] = shift_shape(MOVABLE_SHAPES["E_root"][suffix], offset)
                else:
                    library[chord_name] = shift_shape(MOVABLE_SHAPES["E_root"][suffix], 0)

    for flat, sharp in ENHARMONICS.items():
        for suffix in CHORD_TYPES:
            library[f"{flat}{suffix}"] = library[f"{sharp}{suffix}"]

    library.update(CUSTOM_SLASH_CHORDS)
    return library

CHORDS = build_chord_library()

# --- AUDIO SYNTHESIS (KARPLUS-STRONG PLUCKED STRING) ---
def synthesize_plucked_string(freq, duration=2.2, sample_rate=44100, decay=0.996):
    """Generates a realistic plucked guitar string waveform using Karplus-Strong synthesis."""
    period = max(2, int(sample_rate / freq))
    total_samples = int(sample_rate * duration)
    ring_buffer = [random.uniform(-1.0, 1.0) for _ in range(period)]
    samples = [0.0] * total_samples

    idx = 0
    for i in range(total_samples):
        samples[i] = ring_buffer[idx]
        next_idx = (idx + 1) % period
        ring_buffer[idx] = decay * 0.5 * (ring_buffer[idx] + ring_buffer[next_idx])
        idx = next_idx

    return samples

def play_chord_audio(shape, strum_delay=0.045, duration=2.2, sample_rate=44100):
    """Mixes all active strings into a downward strum and plays via OS audio."""
    total_samples = int(sample_rate * (duration + 6 * strum_delay))
    mix = [0.0] * total_samples

    active_strings = 0
    for s_idx, fret in enumerate(shape):
        if fret == "x":
            continue
        active_strings += 1
        freq = OPEN_STRING_FREQS[s_idx] * (2 ** (fret / 12.0))
        string_wave = synthesize_plucked_string(freq, duration=duration, sample_rate=sample_rate)
        offset = int(s_idx * strum_delay * sample_rate)

        for i, val in enumerate(string_wave):
            if offset + i < total_samples:
                mix[offset + i] += val

    if active_strings == 0:
        return

    peak = max(abs(x) for x in mix) or 1.0
    scale = 0.85 / peak

    tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_path = tmp_file.name
    tmp_file.close()

    try:
        with wave.open(tmp_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            pcm_data = bytearray()
            for sample in mix:
                int_sample = int(max(-32767, min(32767, sample * scale * 32767)))
                pcm_data.extend(struct.pack("<h", int_sample))
            wf.writeframes(pcm_data)

        if sys.platform.startswith("win"):
            import winsound
            winsound.PlaySound(tmp_path, winsound.SND_FILENAME)
        elif sys.platform == "darwin":
            subprocess.run(["afplay", tmp_path], check=False)
        else:
            for player in ("aplay", "paplay", "ffplay"):
                if subprocess.run(["which", player], capture_output=True).returncode == 0:
                    cmd = [player, "-nodisp", "-autoexit", tmp_path] if player == "ffplay" else [player, tmp_path]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                    break
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- CHORD RESOLUTION & DIAGRAM RENDERING ---
def normalize_note(note_str):
    cleaned = note_str.strip()
    if not cleaned:
        return ""
    if len(cleaned) > 1 and cleaned[1] in ("#", "b"):
        return cleaned[0].upper() + cleaned[1]
    return cleaned[0].upper()

def normalize_chord_part(chord_str):
    cleaned = chord_str.strip()
    if not cleaned:
        return ""
    root = cleaned[0].upper()
    rest = cleaned[1:]
    if rest.startswith("#") or rest.startswith("b"):
        return root + rest[0] + rest[1:].lower()
    return root + rest.lower()

def extract_root_note(chord_name):
    if len(chord_name) > 1 and chord_name[1] in ("#", "b"):
        return chord_name[:2]
    return chord_name[0]

def get_note_index(note_name):
    canonical = ENHARMONICS.get(note_name, note_name)
    return SHARP_NOTES.index(canonical) if canonical in SHARP_NOTES else None

def get_fret_note(string_idx, fret, use_flats=False):
    """Calculates the note played on a string at a given fret safely for 6 strings."""
    if fret == "x":
        return None
    semitone_offset = fret
    if use_flats:
        return FLAT_NOTES[(OPEN_STRING_INDICES[string_idx] + semitone_offset) % 12]
    return SHARP_NOTES[(OPEN_STRING_INDICES[string_idx] + semitone_offset) % 12]

def group_chord_notes(chord_name, shape):
    """Determines the highest and lowest notes played in a chord, ignoring muted strings."""
    lowest, highest = 127, -1

    for s_idx, fret in enumerate(shape):
        if fret == "x":
            continue
        note_index = (OPEN_STRING_INDICES[s_idx] + fret) % 12
        if note_index < lowest:
            lowest = note_index
        if note_index > highest:
            highest = note_index

    if lowest > highest:
        return None, None

    return lowest, highest

def render_chord_diagram(chord_name, shape, file_path):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print(f"{RED}Error: matplotlib is not installed.{RESET}")
        print(f"{YELLOW}Install it with: pip install matplotlib{RESET}")
        return

    plt.figure(figsize=(4, 5))
    plt.title(chord_name, fontsize=14, fontweight="bold")

    # Fretboard (6 strings -> x spans from 0 to 5; 5 frets -> y spans from 0 to 5)
    for fret in range(6):
        plt.plot([0, 5], [fret, fret], color="black", lw=2)

    # Strings
    for string in range(6):
        plt.plot([string, string], [0, 5], color="black", lw=2)

    # Notes
    for string_idx, fret in enumerate(shape):
        if fret == "x":
            plt.text(string_idx, 5.2, "x", fontsize=12, ha="center", color="red")
            continue
        note = get_fret_note(string_idx, fret)
        if fret == 0:
            plt.text(string_idx, 5.2, "o", fontsize=12, ha="center", color="green")
        else:
            plt.scatter([string_idx], [5 - fret + 0.5], s=200, color="black")
            plt.text(string_idx, 5 - fret + 0.4, note, fontsize=10, ha="center", va="center", color="white", fontweight="bold")

    plt.xlim(-0.5, 5.5)
    plt.ylim(-0.5, 6.0)
    plt.axis("off")
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    plt.savefig(file_path, dpi=300, bbox_inches="tight")
    plt.close()

def find_alternate_shapes(chord_name, max_distance=2):
    """Finds chord shapes close to the target shape by comparing individual string frets safely."""
    if chord_name not in CHORDS:
        return {}
    target_shape = CHORDS[chord_name]
    target_frets = [fret if isinstance(fret, int) else 0 for fret in target_shape]
    min_fret = min([f for f in target_shape if isinstance(f, int)] or [0])

    similar_shapes = {}
    for other_name, other_shape in CHORDS.items():
        if other_name == chord_name:
            continue
        other_frets = [fret if isinstance(fret, int) else 0 for fret in other_shape]
        distance = sum(abs(f1 - f2) for f1, f2 in zip(target_frets, other_frets))
        if distance <= max_distance and (min_fret + max_distance) >= 0:
            similar_shapes[other_name] = other_shape

    return similar_shapes

def display_chord_info(chord_name, shape):
    """Prints information about a chord and renders a popup-safe text block."""
    note_indices = [(OPEN_STRING_INDICES[i] + s) % 12 if isinstance(s, int) else None for i, s in enumerate(shape)]
    note_names = [SHARP_NOTES[ni] if ni is not None else "X" for ni in note_indices]
    
    print(f"Chord: {chord_name}")
    print("Notes: ", " ".join(note_names))
    print("Shape (Frets):", shape)

def validate_chord_shapes(chord_shapes):
    for chord_name, shape in chord_shapes.items():
        if len(shape) != 6:
            raise ValueError(
                f"{chord_name} must contain exactly six string positions."
            )

        for fret in shape:
            if fret != "x" and (not isinstance(fret, int) or fret < 0):
                raise ValueError(
                    f"{chord_name} contains an invalid fret value: {fret!r}"
                )

# Validate nested shapes and collections safely
validate_chord_shapes(MOVABLE_SHAPES["E_root"])
validate_chord_shapes(MOVABLE_SHAPES["A_root"])
validate_chord_shapes(OPEN_CHORDS)
validate_chord_shapes(CUSTOM_SLASH_CHORDS)

# --- GUI APPLICATION ---
class ChordFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chord Finder - Visual Tab Display")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")

        # Title
        title_frame = tk.Frame(root, bg="#2c3e50")
        title_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = tk.Label(title_frame, text="Guitar Chord Finder", 
                               font=("Arial", 18, "bold"), 
                               bg="#2c3e50", fg="white")
        title_label.pack(pady=10)

        # Input Frame
        input_frame = tk.Frame(root, bg="#ecf0f1", relief=tk.RAISED, bd=2)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        label = tk.Label(input_frame, text="Enter Chord:", font=("Arial", 12, "bold"),
                        bg="#ecf0f1")
        label.pack(side=tk.LEFT, padx=5, pady=5)

        self.chord_input = tk.Entry(input_frame, font=("Arial", 12), width=20)
        self.chord_input.pack(side=tk.LEFT, padx=5, pady=5)
        self.chord_input.bind('<Return>', lambda e: self.display_chord())

        self.display_btn = tk.Button(input_frame, text="Display Chord", 
                                     command=self.display_chord,
                                     bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                                     padx=10, pady=5)
        self.display_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.play_btn = tk.Button(input_frame, text="Play Sound", 
                                  command=self.play_sound,
                                  bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                                  padx=10, pady=5)
        self.play_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.alt_btn = tk.Button(input_frame, text="Alternative Voicings", 
                                 command=self.show_alternatives,
                                 bg="#e67e22", fg="white", font=("Arial", 10, "bold"),
                                 padx=10, pady=5)
        self.alt_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.barre_btn = tk.Button(input_frame, text="Barre Alternatives", 
                                   command=self.show_barre_alternatives,
                                   bg="#9b59b6", fg="white", font=("Arial", 10, "bold"),
                                   padx=10, pady=5)
        self.barre_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Main Canvas Frame
        self.canvas_frame = tk.Frame(root, bg="white", relief=tk.SUNKEN, bd=2)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Info Frame
        self.info_frame = tk.Frame(root, bg="#ecf0f1", relief=tk.RAISED, bd=2)
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.info_label = tk.Label(self.info_frame, text="Enter a chord to display its tab",
                                   font=("Arial", 11), bg="#ecf0f1", justify=tk.LEFT)
        self.info_label.pack(padx=10, pady=10, anchor="w")

        self.current_chord = None
        self.show_barre_line = False  # Flag to show barre line only for barre alternatives

    def display_chord(self):
        """Display the chord diagram graphically."""
        chord_name = self.chord_input.get().strip()
        normalized = normalize_chord_part(chord_name)

        if not normalized:
            messagebox.showwarning("Input Error", "Please enter a chord name")
            return

        if normalized not in CHORDS:
            messagebox.showerror("Not Found", f"Chord '{chord_name}' not found in library.\n\n"
                                f"Try one of these:\n{', '.join(list(CHORDS.keys())[:10])}")
            return

        self.current_chord = normalized
        self.show_barre_line = False  # Regular chord display, don't show barre line
        shape = CHORDS[normalized]
        self.draw_chord_diagram(normalized, shape)
        self.update_info(normalized, shape)


    def draw_chord_diagram(self, chord_name, shape):
        """Draw the chord diagram on the canvas - rotated 90 degrees with vertical strings."""
        self.canvas.delete("all")

        # Canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1:
            canvas_width = 500
        if canvas_height <= 1:
            canvas_height = 400

        # Diagram parameters - now strings are vertical
        margin_top = 60
        margin_left = 100
        fret_width = 40  # Width of each fret (was fret_height)
        string_height = 50  # Distance between strings vertically (was string_width)
        num_frets = 6

        diagram_width = fret_width * num_frets  # Frets go horizontally
        diagram_height = string_height * 5  # 6 strings = 5 intervals

        start_x = margin_left
        start_y = (canvas_height - diagram_height) // 2

        # Draw the chord name centered above the fretboard
        self.canvas.create_text(start_x + diagram_width // 2, 20, text=chord_name,
                               font=("Arial", 16, "bold"), fill="#2c3e50")

        # Draw frets (vertical lines now, since we rotated 90 degrees)
        for fret in range(num_frets + 1):
            x = start_x + fret * fret_width
            self.canvas.create_line(x, start_y, x, start_y + diagram_height, 
                                   fill="#34495e", width=2)

        # Draw strings (horizontal lines now, since we rotated 90 degrees)
        # Reversed order: lower E at bottom, higher E at top
        string_names = ["E", "B", "G", "D", "A", "E"]
        for string in range(6):
            y = start_y + (5 - string) * string_height
            self.canvas.create_line(start_x, y, start_x + diagram_width, y, 
                                   fill="#34495e", width=2)
            # Draw string names on the left
            self.canvas.create_text(margin_left - 30, y, text=string_names[string],
                                   font=("Arial", 11, "bold"), fill="#2c3e50")

        # Draw nut (thick line on the left if no high frets)
        min_fret = min([f for f in shape if isinstance(f, int)], default=0)
        if min_fret == 0:
            self.canvas.create_line(start_x, start_y, start_x, start_y + diagram_height,
                                   fill="black", width=4)

        # Draw fret numbers at the top
        for fret in range(1, num_frets + 1):
            x = start_x + fret * fret_width
            self.canvas.create_text(x, start_y - 25, text=str(fret),
                                   font=("Arial", 10, "bold"), fill="#7f8c8d")

        # Detect barre chords and draw barre line (only if viewing a barre alternative)
        if self.show_barre_line:
            self._draw_barre_line(shape, start_x, start_y, string_height)

        # Draw notes and markers
        # Reversed order: string 0 (low E) at bottom, string 5 (high E) at top
        for string_idx, fret in enumerate(shape):
            y = start_y + (5 - string_idx) * string_height

            if fret == "x":
                # Muted string marker - X to the left of nut
                self.canvas.create_text(start_x - 50, y, text="✕", 
                                       font=("Arial", 16, "bold"), fill="#e74c3c")
            elif fret == 0:
                # Open string marker - O to the left of nut
                self.canvas.create_oval(start_x - 65, y - 10, start_x - 45, y + 10,
                                       outline="#27ae60", width=2, fill="white")
                self.canvas.create_text(start_x - 55, y, text="o", 
                                       font=("Arial", 14, "bold"), fill="#27ae60")
            else:
                # Fretted note - place dot in the middle of the fret, ON the string line
                # Position x: in the middle of the fret (between fret lines)
                x = start_x + (fret - 0.5) * fret_width
                # Position y: on the string line
                dot_y = y
                self.canvas.create_oval(x - 12, dot_y - 12, x + 12, dot_y + 12,
                                       outline="#2c3e50", width=2, fill="#3498db")
                note = get_fret_note(string_idx, fret)
                self.canvas.create_text(x, dot_y, text=note, 
                                       font=("Arial", 10, "bold"), fill="white")

    def _draw_barre_line(self, shape, start_x, start_y, string_height):
        """Draw a thick vertical line for barre chords at the lowest fret."""
        # Find frets that are played by multiple strings (barre frets)
        fret_strings = {}
        for string_idx, fret in enumerate(shape):
            if isinstance(fret, int) and fret > 0:
                if fret not in fret_strings:
                    fret_strings[fret] = []
                fret_strings[fret].append(string_idx)

        # Find the lowest fret that has 2+ strings (the barre fret)
        barre_frets = [fret for fret, strings in fret_strings.items() if len(strings) >= 2]

        if barre_frets:
            # Use the lowest fret number (leftmost on the diagram)
            barre_fret = min(barre_frets)
            string_indices = fret_strings[barre_fret]

            # Find the highest and lowest string indices
            min_string = min(string_indices)
            max_string = max(string_indices)

            # Convert string indices to y coordinates (reversed order)
            y_top = start_y + (5 - max_string) * string_height
            y_bottom = start_y + (5 - min_string) * string_height

            # Draw the barre line in the middle of the fret
            x = start_x + (barre_fret - 0.5) * 40  # 40 is the fret_width
            self.canvas.create_line(x, y_top, x, y_bottom, 
                                   fill="black", width=6)

    def update_info(self, chord_name, shape):
        """Update the information panel."""
        # Get note indices and names
        note_indices = [(OPEN_STRING_INDICES[i] + s) % 12 if isinstance(s, int) else None 
                        for i, s in enumerate(shape)]
        note_names = [SHARP_NOTES[ni] if ni is not None else "✕" for ni in note_indices]

        # Create info text
        info_text = f"Chord: {chord_name}\n"
        info_text += f"Frets: {str(shape)}\n"
        info_text += f"Notes: {' - '.join(note_names)}"

        self.info_label.config(text=info_text)

    def play_sound(self):
        """Play the current chord."""
        if not self.current_chord:
            messagebox.showwarning("No Chord", "Please display a chord first")
            return

        shape = CHORDS[self.current_chord]
        self.play_btn.config(state=tk.DISABLED, text="Playing...")
        self.root.after(100, lambda: self._play_async(shape))

    def _play_async(self, shape):
        """Play sound asynchronously."""
        try:
            play_chord_audio(shape)
        finally:
            self.play_btn.config(state=tk.NORMAL, text="Play Sound")

    def on_canvas_resize(self, event):
        """Redraw when canvas is resized."""
        if self.current_chord:
            shape = CHORDS[self.current_chord]
            self.draw_chord_diagram(self.current_chord, shape)

    def show_alternatives(self):
        """Show alternative voicings for the current chord in a scrollable window."""
        if not self.current_chord:
            messagebox.showwarning("No Chord", "Please display a chord first")
            return

        # Extract root note from the current chord
        root_note = extract_root_note(self.current_chord)

        # Get all voicings for the same root note
        voicings = {}
        for chord_name, shape in CHORDS.items():
            if extract_root_note(chord_name) == root_note and chord_name != self.current_chord:
                voicings[chord_name] = shape

        if not voicings:
            messagebox.showinfo("No Alternatives", 
                              f"No alternative voicings found for {root_note}")
            return

        # Create a new window for alternatives
        alt_window = tk.Toplevel(self.root)
        alt_window.title(f"Alternative Voicings for {root_note}")
        alt_window.geometry("700x600")
        alt_window.configure(bg="#ecf0f1")

        # Header
        header_frame = tk.Frame(alt_window, bg="#2c3e50")
        header_frame.pack(fill=tk.X, pady=(0, 10))

        header_label = tk.Label(header_frame, 
                               text=f"Alternative Voicings for {root_note}", 
                               font=("Arial", 14, "bold"), 
                               bg="#2c3e50", fg="white")
        header_label.pack(pady=10)

        # Create a frame for the scrollable area
        canvas_frame = tk.Frame(alt_window, bg="white", relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Canvas with scrollbar
        alt_canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=alt_canvas.yview)
        scrollable_frame = tk.Frame(alt_canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: alt_canvas.configure(scrollregion=alt_canvas.bbox("all"))
        )

        alt_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        alt_canvas.configure(yscrollcommand=scrollbar.set)

        alt_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            alt_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        alt_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Add alternative voicings (sorted by name)
        sorted_voicings = sorted(voicings.items())
        for idx, (chord_name, shape) in enumerate(sorted_voicings):
            self._create_voicing_item(scrollable_frame, chord_name, shape, idx)

        # Close button
        close_btn = tk.Button(alt_window, text="Close", command=alt_window.destroy,
                            bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                            padx=20, pady=5)
        close_btn.pack(pady=10)

    def _create_voicing_item(self, parent, chord_name, shape, index):
        """Create a visual item for an alternative voicing."""
        item_frame = tk.Frame(parent, bg="#ecf0f1", relief=tk.RAISED, bd=1)
        item_frame.pack(fill=tk.X, padx=5, pady=5)

        # Left side: chord name and shape
        left_frame = tk.Frame(item_frame, bg="#ecf0f1")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        name_label = tk.Label(left_frame, text=chord_name, 
                             font=("Arial", 12, "bold"), 
                             bg="#ecf0f1", fg="#2c3e50")
        name_label.pack(anchor="w")

        # Get note names
        note_indices = [(OPEN_STRING_INDICES[i] + s) % 12 if isinstance(s, int) else None 
                        for i, s in enumerate(shape)]
        note_names = [SHARP_NOTES[ni] if ni is not None else "✕" for ni in note_indices]

        shape_label = tk.Label(left_frame, text=f"Frets: {str(shape)}", 
                              font=("Arial", 9), 
                              bg="#ecf0f1", fg="#7f8c8d")
        shape_label.pack(anchor="w")

        notes_label = tk.Label(left_frame, text=f"Notes: {' - '.join(note_names)}", 
                              font=("Arial", 9), 
                              bg="#ecf0f1", fg="#7f8c8d")
        notes_label.pack(anchor="w")

        # Right side: buttons
        btn_frame = tk.Frame(item_frame, bg="#ecf0f1")
        btn_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        view_btn = tk.Button(btn_frame, text="View", 
                            command=lambda: self._view_voicing(chord_name, shape),
                            bg="#3498db", fg="white", font=("Arial", 9, "bold"),
                            padx=10, pady=5)
        view_btn.pack(side=tk.LEFT, padx=2)

        play_btn = tk.Button(btn_frame, text="Play", 
                            command=lambda: self._play_voicing(shape),
                            bg="#27ae60", fg="white", font=("Arial", 9, "bold"),
                            padx=10, pady=5)
        play_btn.pack(side=tk.LEFT, padx=2)

    def _view_voicing(self, chord_name, shape):
        """Display the selected voicing (without barre line)."""
        self.current_chord = chord_name
        self.show_barre_line = False  # Disable barre line for regular voicings
        self.chord_input.delete(0, tk.END)
        self.chord_input.insert(0, chord_name)
        self.draw_chord_diagram(chord_name, shape)
        self.update_info(chord_name, shape)

    def _play_voicing(self, shape):
        """Play the selected voicing."""
        self.play_btn.config(state=tk.DISABLED, text="Playing...")
        self.root.after(100, lambda: self._play_async(shape))

    def show_barre_alternatives(self):
        """Show selectable barre alternatives in a separate window."""
        if not self.current_chord:
            messagebox.showwarning("No Chord", "Please display a chord first")
            return

        root_note = extract_root_note(self.current_chord)
        chord_type = self.current_chord[len(root_note):]
        barre_chords = {
            name: shape for name, shape in CHORDS.items()
            if name != self.current_chord
            and name.endswith(chord_type)
            and self._is_barre_chord(shape)
        }

        if not barre_chords:
            messagebox.showinfo("No Barre Chords",
                                f"No barre chord alternatives found for {self.current_chord}")
            return

        barre_window = tk.Toplevel(self.root)
        barre_window.title(f"Barre Alternatives for {self.current_chord}")
        barre_window.geometry("700x600")
        barre_window.configure(bg="#ecf0f1")

        header_frame = tk.Frame(barre_window, bg="#9b59b6")
        header_frame.pack(fill=tk.X, pady=(0, 10))

        header_label = tk.Label(header_frame,
                                text=f"Barre Alternatives for {self.current_chord}",
                                font=("Arial", 14, "bold"),
                                bg="#9b59b6", fg="white")
        header_label.pack(pady=10)

        canvas_frame = tk.Frame(barre_window, bg="white", relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        barre_canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL,
                                 command=barre_canvas.yview)
        scrollable_frame = tk.Frame(barre_canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda event: barre_canvas.configure(
                scrollregion=barre_canvas.bbox("all")
            )
        )

        barre_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        barre_canvas.configure(yscrollcommand=scrollbar.set)
        barre_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def on_mousewheel(event):
            barre_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        barre_canvas.bind("<MouseWheel>", on_mousewheel)

        for index, (alternative_name, shape) in enumerate(sorted(barre_chords.items())):
            self._create_barre_item(
                scrollable_frame, alternative_name, shape, index
            )

        close_btn = tk.Button(barre_window, text="Close", command=barre_window.destroy,
                              bg="#e74c3c", fg="white",
                              font=("Arial", 10, "bold"), padx=20, pady=5)
        close_btn.pack(pady=10)

    def _is_barre_chord(self, shape):
        """Check if a chord shape is a barre chord."""
        # A barre chord has at least 2 strings on the same fret (excluding open strings and mutes)
        fret_counts = {}
        for fret in shape:
            if isinstance(fret, int) and fret > 0:
                fret_counts[fret] = fret_counts.get(fret, 0) + 1

        # Return True if any fret has 2 or more strings
        return any(count >= 2 for count in fret_counts.values())

    def _create_barre_item(self, parent, chord_name, shape, index):
        """Create a visual item for a barre chord alternative."""
        item_frame = tk.Frame(parent, bg="#ecf0f1", relief=tk.RAISED, bd=1)
        item_frame.pack(fill=tk.X, padx=5, pady=5)

        # Left side: chord name and shape
        left_frame = tk.Frame(item_frame, bg="#ecf0f1")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        name_label = tk.Label(left_frame, text=chord_name, 
                             font=("Arial", 12, "bold"), 
                             bg="#ecf0f1", fg="#2c3e50")
        name_label.pack(anchor="w")

        # Get note names
        note_indices = [(OPEN_STRING_INDICES[i] + s) % 12 if isinstance(s, int) else None 
                        for i, s in enumerate(shape)]
        note_names = [SHARP_NOTES[ni] if ni is not None else "✕" for ni in note_indices]

        shape_label = tk.Label(left_frame, text=f"Frets: {str(shape)}", 
                              font=("Arial", 9), 
                              bg="#ecf0f1", fg="#7f8c8d")
        shape_label.pack(anchor="w")

        notes_label = tk.Label(left_frame, text=f"Notes: {' - '.join(note_names)}", 
                              font=("Arial", 9), 
                              bg="#ecf0f1", fg="#7f8c8d")
        notes_label.pack(anchor="w")

        # Right side: buttons
        btn_frame = tk.Frame(item_frame, bg="#ecf0f1")
        btn_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        view_btn = tk.Button(btn_frame, text="View", 
                            command=lambda: self._view_barre_voicing(chord_name, shape),
                            bg="#3498db", fg="white", font=("Arial", 9, "bold"),
                            padx=10, pady=5)
        view_btn.pack(side=tk.LEFT, padx=2)

        play_btn = tk.Button(btn_frame, text="Play", 
                            command=lambda: self._play_voicing(shape),
                            bg="#27ae60", fg="white", font=("Arial", 9, "bold"),
                            padx=10, pady=5)
        play_btn.pack(side=tk.LEFT, padx=2)

    def _view_barre_voicing(self, chord_name, shape):
        """Display a barre chord voicing with barre line visible."""
        self.current_chord = chord_name
        self.show_barre_line = True  # Enable barre line drawing for barre chords
        self.chord_input.delete(0, tk.END)
        self.chord_input.insert(0, chord_name)
        self.draw_chord_diagram(chord_name, shape)
        self.update_info(chord_name, shape)

# --- INTERACTIVE MENU ---
def main_menu():
    """Interactive menu for the chord finder application."""
    while True:
        print(f"\n{BOLD}{CYAN}=== CHORD FINDER ==={RESET}")
        print(f"{GREEN}1.{RESET} Display chord information")
        print(f"{GREEN}2.{RESET} Play chord audio")
        print(f"{GREEN}3.{RESET} Find alternate chord shapes")
        print(f"{GREEN}4.{RESET} List all available chords")
        print(f"{GREEN}5.{RESET} Open GUI")
        print(f"{GREEN}6.{RESET} Exit")

        choice = input(f"\n{YELLOW}Enter your choice (1-6): {RESET}").strip()

        if choice == "1":
            chord_name = input(f"{YELLOW}Enter chord name (e.g., C, Am, G7): {RESET}").strip()
            normalized = normalize_chord_part(chord_name)
            if normalized in CHORDS:
                shape = CHORDS[normalized]
                display_chord_info(normalized, shape)
            else:
                print(f"{RED}Chord '{chord_name}' not found in library.{RESET}")

        elif choice == "2":
            chord_name = input(f"{YELLOW}Enter chord name to play: {RESET}").strip()
            normalized = normalize_chord_part(chord_name)
            if normalized in CHORDS:
                print(f"{GREEN}Playing {normalized}...{RESET}")
                play_chord_audio(CHORDS[normalized])
            else:
                print(f"{RED}Chord '{chord_name}' not found.{RESET}")

        elif choice == "3":
            chord_name = input(f"{YELLOW}Enter chord name: {RESET}").strip()
            normalized = normalize_chord_part(chord_name)
            if normalized in CHORDS:
                alternates = find_alternate_shapes(normalized, max_distance=2)
                if alternates:
                    print(f"{CYAN}Alternate shapes for {normalized}:{RESET}")
                    for alt_name, alt_shape in list(alternates.items())[:5]:
                        print(f"  {GREEN}{alt_name}: {alt_shape}{RESET}")
                else:
                    print(f"{YELLOW}No alternate shapes found within distance.{RESET}")
            else:
                print(f"{RED}Chord '{chord_name}' not found.{RESET}")

        elif choice == "4":
            notes = SHARP_NOTES[:5]
            print(f"{CYAN}Available chords by root note:{RESET}")
            for note in notes:
                note_chords = [name for name in CHORDS.keys() if name.startswith(note)]
                print(f"  {GREEN}{note}: {RESET}{', '.join(note_chords[:8])}")
            print(f"  {DIM}(showing first 8 chords per note){RESET}")

        elif choice == "5":
            print(f"{GREEN}Opening GUI...{RESET}")
            root = tk.Tk()
            app = ChordFinderGUI(root)
            root.mainloop()
            print(f"{GREEN}GUI closed.{RESET}")

        elif choice == "6":
            print(f"{GREEN}Goodbye!{RESET}")
            break

        else:
            print(f"{RED}Invalid choice. Please try again.{RESET}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ChordFinderGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Program interrupted.{RESET}")
        sys.exit(0)
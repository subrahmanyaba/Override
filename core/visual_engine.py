import pdb
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import os


def visualize_waveform(track_path):
    y, sr = librosa.load(track_path)
    plt.figure(figsize=(14, 5))
    librosa.display.waveshow(y, sr=sr)
    plt.title("Waveform")
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.show()


def visualize_spectrogram(track_path):
    y, sr = librosa.load(track_path)
    D = np.abs(librosa.stft(y))
    DB = librosa.amplitude_to_db(D, ref=np.max)
    plt.figure(figsize=(14, 5))
    librosa.display.specshow(DB, sr=sr, x_axis='time', y_axis='hz')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.tight_layout()
    plt.show()


# 🔮 Main function used by your VisualGenTool
def generate_visuals_from_mood(mood_curve, save_path=None):
    """
    Generates abstract visuals based on a given mood curve (e.g. ["calm", "intense", "uplifting"]).
    Each mood triggers a different style of visual output.
    """
    print(f"Generating visuals based on mood curve: {mood_curve}")

    for i, mood in enumerate(mood_curve):
        fig, ax = plt.subplots(figsize=(10, 6))
        np.random.seed(i)  # for repeatability

        if mood == "calm":
            x = np.linspace(0, 10, 500)
            y = np.sin(x) * np.cos(x / 2)
            ax.plot(x, y, color="skyblue", linewidth=2)
            ax.set_title("Calm Mood Visual")
        elif mood == "intense":
            data = np.random.normal(size=(1000,))
            ax.hist(data, bins=50, color="red", alpha=0.7)
            ax.set_title("Intense Mood Visual")
        elif mood == "uplifting":
            x = np.random.rand(100)
            y = np.random.rand(100)
            colors = np.random.rand(100)
            sizes = 1000 * np.random.rand(100)
            ax.scatter(x, y, c=colors, s=sizes, alpha=0.6, cmap='viridis')
            ax.set_title("Uplifting Mood Visual")
        else:
            ax.text(0.5, 0.5, mood, fontsize=20, ha='center', va='center')
            ax.set_title(f"Custom Mood: {mood}")

        ax.axis('off')

        if save_path:
            os.makedirs(save_path, exist_ok=True)
            out_file = os.path.join(save_path, f"{i}_{mood}.png")
            fig.savefig(out_file, bbox_inches='tight')
            print(f"Saved: {out_file}")
        else:
            plt.show()

        plt.close(fig)

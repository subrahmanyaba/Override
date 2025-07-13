import librosa
import json
import os

def analyze_track(track_path, save_json=True):
    print(f"Analyzing: {track_path}")
    
    y, sr = librosa.load(track_path, sr=None)
    
    # BPM and beats
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)

    # Key detection via chroma
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)
    key_index = chroma_mean.argmax()
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 
            'F#', 'G', 'G#', 'A', 'A#', 'B']
    detected_key = keys[key_index]

    # Energy (RMS)
    rms = librosa.feature.rms(y=y)[0]
    avg_energy = float(rms.mean())

    metadata = {
        'filename': os.path.basename(track_path),
        'tempo_bpm': float(round(tempo, 2)),
        'key': detected_key,
        'beats': beat_times.tolist(),
        'average_energy': avg_energy
    }

    if save_json:
        out_path = f"data/metadata/{os.path.splitext(os.path.basename(track_path))[0]}.json"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(metadata, f, indent=4)
        print(f"Metadata saved to {out_path}")

    return metadata


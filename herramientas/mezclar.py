"""Trata la voz, le pone la música de fondo (estilo B) y codifica el audio final del episodio.

Uso:
    python3 mezclar.py narracion.wav musica.wav salida.m4a [--sin-musica]

Estilo B: la música suena todo el rato, unos 14 dB por debajo de la voz en las pausas y unos 19 dB
por debajo mientras se habla, con transiciones suaves. Salida: AAC mono a 64 kbps y 44,1 kHz
(unos 13 MB por media hora). Para los vídeos se usa este mismo archivo como pista de audio.
"""
import argparse, subprocess
import numpy as np

SR = 44100
FX = "highpass=f=70,bass=g=2:f=180,aecho=0.85:0.6:35|70:0.10|0.05,loudnorm=I=-18:TP=-2"

def cargar(p, af=None):
    cmd = ["ffmpeg", "-loglevel", "error", "-i", p] + (["-af", af] if af else []) + ["-f", "s16le", "-ac", "1", "-ar", str(SR), "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.int16).astype(np.float32) / 32768

def bucle(m, n, cruce=6.0):
    """Repite la música con fundidos cruzados hasta cubrir n muestras."""
    c = int(cruce * SR); out = m.copy()
    while len(out) < n:
        a = out[-c:] * np.linspace(1, 0, c) + m[:c] * np.linspace(0, 1, c)
        out = np.concatenate([out[:-c], a, m[c:]])
    return out[:n]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("voz"); ap.add_argument("musica"); ap.add_argument("salida"); ap.add_argument("--sin-musica", action="store_true")
    a = ap.parse_args()
    v = cargar(a.voz, FX)
    rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 1e-4] ** 2))
    y = v
    if not a.sin_musica:
        mu = bucle(cargar(a.musica), len(v)); mu = mu / rms(mu) * rms(v)
        win = int(0.05 * SR); env = np.sqrt(np.convolve(v ** 2, np.ones(win) / win, "same"))
        act = (env > rms(v) * 0.15).astype(np.float32)
        blk = int(0.01 * SR); bl = act[: len(act) // blk * blk].reshape(-1, blk).max(1)
        g = np.zeros_like(bl); cur = 0.0
        for i, x in enumerate(bl):
            cur = min(1.0, cur + 0.01 / 0.25) if x > cur else max(0.0, cur - 0.01 / 0.9); g[i] = cur
        g = np.interp(np.arange(len(v)), np.arange(len(g)) * blk, g)
        db = lambda d: 10 ** (d / 20)
        y = v + mu * (db(-14) * (1 - g) + db(-19) * g)
        f = int(3 * SR); y[:f] = v[:f] + (y[:f] - v[:f]) * np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    raw = (np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", a.salida], input=raw, check=True)

if __name__ == "__main__":
    main()

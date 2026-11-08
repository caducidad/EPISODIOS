"""Compone un fondo ambiental sencillo (acordes lentos, campanitas y reverberación) que luego se repite en bucle.

Uso:
    python3 musica.py salida.wav [--segundos 240] [--semilla 3]
"""
import argparse, wave
import numpy as np
import scipy.signal as ss

SR = 44100

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("salida"); ap.add_argument("--segundos", type=float, default=240); ap.add_argument("--semilla", type=int, default=3)
    a = ap.parse_args()
    rng = np.random.default_rng(a.semilla)
    dur = a.segundos; n = int(dur * SR); t = np.arange(n) / SR
    f = lambda m: 440 * 2 ** ((m - 69) / 12)
    # Re menor: Dm9 - Bbmaj7 - Fmaj7 - C(add9)
    acordes = [[50, 57, 62, 65, 69, 76], [46, 53, 58, 62, 65, 69], [41, 53, 57, 60, 64, 69], [48, 55, 60, 62, 67, 74]]
    seg = 9.0
    pad = np.zeros(n)
    for k in range(int(np.ceil(dur / seg)) + 1):
        ac = acordes[k % 4]; ini = k * seg - 2.0
        i0 = max(0, int(ini * SR)); i1 = min(n, int((ini + seg + 4.0) * SR))
        if i1 <= i0:
            continue
        tt = t[i0:i1] - ini; L = seg + 4.0
        env = (np.clip(tt / 3.0, 0, 1) * np.clip((L - tt) / 3.5, 0, 1)) ** 1.5
        s = np.zeros(i1 - i0)
        for m in ac:
            for det in (-0.12, 0.0, 0.11):
                fr = f(m + det)
                s += np.sin(2 * np.pi * fr * tt + rng.uniform(0, 6.28)) * (1.0 if m < 60 else 0.6)
                s += 0.25 * np.sin(2 * np.pi * 2 * fr * tt) * (0.5 if m < 60 else 0.3)
        pad[i0:i1] += s * env
    pad *= 1 + 0.15 * np.sin(2 * np.pi * 0.07 * t)
    campanas = np.zeros(n); penta = [74, 77, 79, 81, 84, 86, 89]; tb = 1.5
    while tb < dur - 3:
        m = penta[rng.integers(len(penta))]; i0 = int(tb * SR); i1 = min(n, i0 + int(4.0 * SR))
        tt = np.arange(i1 - i0) / SR
        campanas[i0:i1] += (np.sin(2 * np.pi * f(m) * tt) + 0.3 * np.sin(2 * np.pi * f(m) * 2.76 * tt)) * np.exp(-tt * 1.3) * 0.35
        tb += rng.uniform(2.5, 6.0)
    x = pad / np.max(np.abs(pad)) * 0.6 + campanas / max(1e-9, np.max(np.abs(campanas))) * 0.18
    ir_len = int(2.8 * SR); ir = rng.standard_normal(ir_len) * np.exp(-np.arange(ir_len) / SR * 2.2); ir[0] = 1.0
    wet = ss.fftconvolve(x, ir)[:n]
    y = 0.55 * x + 0.45 * wet / np.max(np.abs(wet)) * np.max(np.abs(x))
    b, aa = ss.butter(2, 3500 / (SR / 2)); y = ss.lfilter(b, aa, y)
    fade = int(3 * SR); y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
    y = y / np.max(np.abs(y)) * 0.8
    w = wave.open(a.salida, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((y * 32767).astype(np.int16).tobytes()); w.close()

if __name__ == "__main__":
    main()

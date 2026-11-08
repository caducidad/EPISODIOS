"""Narra un guion con Pocket TTS (modelo spanish_24l, voz lola), frase a frase y con pausas controladas.

Uso:
    python3 narrar.py guion.txt carpeta_salida [--max-segundos 540]

El guion puede ser texto normal (párrafos separados por una línea en blanco) o un guion de vídeo
con escenas: líneas "@@ id | tipo | {json}" seguidas del texto de cada escena.

Es reanudable: cada frase generada se guarda en carpeta_salida/cache. Si se agota el tiempo
(--max-segundos), el script termina con código 3 y basta con volver a lanzarlo hasta que termine
con código 0. Al terminar escribe:
    carpeta_salida/escenas/<id>.wav   (una pista por escena, con sus silencios)
    carpeta_salida/escenas.json       (id, tipo, params, texto y duración de cada escena)
    carpeta_salida/narracion.wav      (todas las escenas seguidas)
"""
import argparse, hashlib, json, os, re, sys, time, wave
import numpy as np

SR = 24000
MODELO, VOZ = "spanish_24l", "lola"
P_PUNTO, P_PARRAFO = 0.62, 1.15          # pausas tras frase y tras párrafo (s)
LEAD, LEAD_TITULO, COLA = 0.9, 1.5, 1.0  # silencios al principio y final de cada escena (s)
MIN_PALABRAS = 6                          # las frases más cortas se unen a la siguiente (Pocket TTS corta las muy cortas)

def leer_guion(path):
    s = open(path, encoding="utf-8").read()
    if re.search(r"^@@ ", s, flags=re.M):
        partes = re.split(r"^@@ (.*)$", s, flags=re.M)[1:]
        escenas = []
        for i in range(0, len(partes), 2):
            sid, tipo, params = [x.strip() for x in partes[i].split("|", 2)]
            escenas.append({"id": sid, "tipo": tipo, "params": json.loads(params), "text": partes[i + 1].strip()})
        return escenas
    return [{"id": "ep", "tipo": "audio", "params": {}, "text": s.strip()}]

def frases_de(parrafo):
    fr = [f.strip() for f in re.split(r"(?<=[.!?…])\s+", parrafo) if f.strip()]
    out = []
    for f in fr:
        if out and len(out[-1].split()) < MIN_PALABRAS:
            out[-1] = out[-1] + " " + f
        else:
            out.append(f)
    if len(out) > 1 and len(out[-1].split()) < MIN_PALABRAS:
        ultima = out.pop()
        out[-1] = out[-1] + " " + ultima
    return out

def plan(escenas):
    """Lista de (escena_id, índice_párrafo, es_última_del_párrafo, frase)."""
    items = []
    for e in escenas:
        pars = [p.strip() for p in e["text"].split("\n\n") if p.strip()]
        for pi, p in enumerate(pars):
            fs = frases_de(" ".join(p.split()))
            for fi, f in enumerate(fs):
                items.append((e["id"], pi, fi == len(fs) - 1, f))
    return items

def clave(f):
    return hashlib.sha1(f"{MODELO}|{VOZ}|{f}".encode()).hexdigest()[:16]

def recortar(a, umbral=0.004):
    idx = np.where(np.abs(a) > umbral)[0]
    if not len(idx):
        return a
    a = a[max(0, idx[0] - 960): idx[-1] + 1440].copy()
    n = min(192, len(a) // 4)
    a[:n] *= np.linspace(0, 1, n); a[-n:] *= np.linspace(1, 0, n)
    return a

def guardar_wav(x, path):
    w = wave.open(path, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion"); ap.add_argument("salida")
    ap.add_argument("--max-segundos", type=float, default=540)
    a = ap.parse_args()
    t0 = time.time()
    escenas = leer_guion(a.guion)
    items = plan(escenas)
    cache = os.path.join(a.salida, "cache"); os.makedirs(cache, exist_ok=True)
    pendientes = [it for it in items if not os.path.exists(os.path.join(cache, clave(it[3]) + ".npy"))]
    print(f"{len(items)} frases, {len(pendientes)} pendientes", flush=True)
    if pendientes:
        from pocket_tts import TTSModel
        import subprocess
        m = TTSModel.load_model(language=MODELO)
        st = m.get_state_for_audio_prompt(VOZ)
        for k, it in enumerate(pendientes):
            if time.time() - t0 > a.max_segundos:
                print(f"Tiempo agotado: quedan {len(pendientes) - k} frases. Vuelve a lanzar el script.", flush=True)
                sys.exit(3)
            au = m.generate_audio(st, it[3]).numpy().astype(np.float32)
            if m.sample_rate != SR:
                raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", str(m.sample_rate), "-ac", "1", "-i", "-",
                                      "-f", "f32le", "-ar", str(SR), "-"], input=au.tobytes(), capture_output=True, check=True).stdout
                au = np.frombuffer(raw, np.float32)
            np.save(os.path.join(cache, clave(it[3]) + ".npy"), recortar(au))
            print(f"  {k + 1}/{len(pendientes)}", flush=True)
    # Montaje: nivel parejo entre frases, pausas y silencios de escena
    trozos = {it[3]: np.load(os.path.join(cache, clave(it[3]) + ".npy")) for it in items}
    rms = lambda x: float(np.sqrt(np.mean(x[np.abs(x) > 1e-3] ** 2))) if np.any(np.abs(x) > 1e-3) else 1.0
    objetivo = float(np.median([rms(v) for v in trozos.values()]))
    os.makedirs(os.path.join(a.salida, "escenas"), exist_ok=True)
    total, salida = [], []
    for e in escenas:
        lead = LEAD_TITULO if e["tipo"] == "titulo" else LEAD
        partes = [np.zeros(int(SR * lead), np.float32)]
        for (sid, pi, ultima, f) in items:
            if sid != e["id"]:
                continue
            x = trozos[f]
            g = np.clip(objetivo / rms(x), 0.5, 2.0)
            partes.append(x * g)
            partes.append(np.zeros(int(SR * (P_PARRAFO if ultima else P_PUNTO)), np.float32))
        partes[-1] = np.zeros(int(SR * COLA), np.float32)
        y = np.concatenate(partes)
        guardar_wav(y * 0.5, os.path.join(a.salida, "escenas", e["id"] + ".wav"))
        e["dur"] = len(y) / SR
        total.append(y); salida.append(e)
    guardar_wav(np.concatenate(total) * 0.5, os.path.join(a.salida, "narracion.wav"))
    json.dump(salida, open(os.path.join(a.salida, "escenas.json"), "w"), ensure_ascii=False, indent=1)
    print(f"Listo: {sum(e['dur'] for e in salida) / 60:.1f} min", flush=True)

if __name__ == "__main__":
    main()

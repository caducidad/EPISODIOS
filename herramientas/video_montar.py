# Monta el vídeo: un MP4 por escena (imagen fija con fundidos) a partir de escenas.json y frames/<id>.jpg.
# Se ejecuta en la carpeta de trabajo; espera voz/escenas.json (o ajusta la ruta) y crea clips/lista.txt para el concat.
import json, subprocess, os, sys
sc = json.load(open("voz/escenas.json"))
with open("clips/lista.txt", "w") as L:
    for s in sc:
        d = s["dur"]; out = f"clips/{s['id']}.mp4"; tmp = f"clips/{s['id']}.tmp.mp4"
        if not os.path.exists(out):
            vf = f"format=yuv420p,loop=-1:1,trim=duration={d:.3f},fade=t=in:st=0:d=0.5,fade=t=out:st={d-0.5:.3f}:d=0.5"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", f"frames/{s['id']}.jpg", "-vf", vf,
                            "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", tmp], check=True)
            os.rename(tmp, out)
        L.write(f"file '{s['id']}.mp4'\n")
        w = f"voz/{s['id']}.wav"
with open("voz/lista.txt", "w") as A:
    for s in sc: A.write(f"file '{s['id']}.wav'\n")
print("ok")

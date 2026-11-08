"""Monta el vídeo de un episodio: una imagen fija por escena, con fundidos, y el audio final del episodio.

Uso:
    python3 montar_video.py escenas.json carpeta_imagenes audio.m4a salida.mp4 [--trabajo carpeta]

Cada escena dura lo que indica escenas.json (lo deja narrar.py) y su imagen es carpeta_imagenes/<id>.jpg.
Se codifica un MP4 por escena (H.264 para imagen fija, CRF 23, 1280x720, 30 fps, fundido de 0,5 s al entrar y al salir), se unen con el
concat de ffmpeg sin recodificar y se añade el audio también sin recodificar. Es reanudable: las escenas ya
codificadas no se repiten.
"""
import argparse, json, os, subprocess

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("escenas"); ap.add_argument("imagenes"); ap.add_argument("audio"); ap.add_argument("salida")
    ap.add_argument("--trabajo", default="clips")
    a = ap.parse_args()
    escenas = json.load(open(a.escenas, encoding="utf-8"))
    os.makedirs(a.trabajo, exist_ok=True)
    lista = os.path.join(a.trabajo, "lista.txt")
    with open(lista, "w") as L:
        for s in escenas:
            d = s["dur"]; out = os.path.join(a.trabajo, f"{s['id']}.mp4"); tmp = os.path.join(a.trabajo, f"{s['id']}.tmp.mp4")
            if not os.path.exists(out):
                vf = f"format=yuv420p,loop=-1:1,trim=duration={d:.3f},fade=t=in:st=0:d=0.5,fade=t=out:st={max(0, d - 0.5):.3f}:d=0.5"
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", os.path.join(a.imagenes, f"{s['id']}.jpg"),
                                "-vf", vf, "-c:v", "libx264", "-crf", "23", "-tune", "stillimage", "-g", "900", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", tmp], check=True)
                os.rename(tmp, out)
            L.write(f"file '{os.path.abspath(out)}'\n")
    mudo = os.path.join(a.trabajo, "mudo.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", mudo], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mudo, "-i", a.audio, "-map", "0:v", "-map", "1:a", "-c", "copy",
                    "-shortest", "-movflags", "+faststart", a.salida], check=True)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.salida], capture_output=True, text=True).stdout.strip()
    print(f"{a.salida}: {float(dur) / 60:.1f} min, {os.path.getsize(a.salida) / 1e6:.1f} MB")

if __name__ == "__main__":
    main()

# Herramientas

Scripts para producir los episodios. Requisitos: `ffmpeg`, `numpy`, `scipy` y, para la voz,
PyTorch para CPU y Pocket TTS:

```bash
pip install --break-system-packages torch --index-url https://download.pytorch.org/whl/cpu
pip install --break-system-packages pocket-tts
```

| Script | Para qué |
| --- | --- |
| `narrar.py` | Narra el guion con Pocket TTS (modelo `spanish_24l`, voz `lola`), frase a frase, con pausas controladas. Reanudable: si se agota el tiempo sale con código 3 y se vuelve a lanzar. |
| `musica.py` | Compone el fondo musical ambiental (bucle de 4 minutos). |
| `mezclar.py` | Trata la voz, añade la música de fondo (estilo B) y crea el `.m4a` final (AAC mono 64 kbps). |
| `video_ligero.py` | Vídeo ligero: dibuja un rótulo por escena (título, dato, fecha, persona, cita, lista, comparación, mapa, línea de tiempo) sobre el fondo propio de cada serie, con cabecera y barra de progreso. |
| `montar_video.py` | Monta el MP4 final: una imagen fija por escena con fundidos y el audio de `mezclar.py`, sin recodificar. |
| `video_ilustrado.py` | Vídeo ilustrado: igual que `video_ligero.py` más el tipo `ilus` (`{"fig": nombre, "pie": texto}`), con ilustraciones SVG hechas a propósito en `FIGURAS` (episodios ia01 y sc02). Mismos argumentos que `video_ligero.py`. |
| `video_escenas.py` | Vídeo ilustrado: plantillas e ilustraciones del piloto de filosofía (punto de partida para episodios ilustrados). |
| `video_montar.py` | Montaje usado en el piloto (sustituido por `montar_video.py`). |

Flujo de un episodio de audio:

```bash
python3 narrar.py guion.txt trabajo          # repetir mientras salga con código 3
python3 musica.py trabajo/musica.wav
python3 mezclar.py trabajo/narracion.wav trabajo/musica.wav <id>-<slug>.m4a
```

Todos los episodios son vídeo, con su audio aparte para el botón "Solo escuchar". El guion lleva escenas
(`@@ id | tipo | {json}`, tipos en la cabecera de `video_ligero.py`); `narrar.py` deja `escenas.json` con sus duraciones:

```bash
python3 narrar.py guion.txt trabajo                       # repetir mientras salga con código 3
python3 musica.py trabajo/musica.wav
python3 mezclar.py trabajo/narracion.wav trabajo/musica.wav ../media/<id>-<slug>.m4a
python3 video_ligero.py trabajo/escenas.json trabajo/img --serie <sc|sh|ia|an|fi> --titulo "<título>" --hoja trabajo/hoja.jpg
python3 montar_video.py trabajo/escenas.json trabajo/img ../media/<id>-<slug>.m4a ../media/<id>-<slug>.mp4 --trabajo trabajo/clips
```

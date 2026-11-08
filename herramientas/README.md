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
| `video_escenas.py` | Dibuja las imágenes 1280x720 de cada escena (plantillas del piloto de filosofía). |
| `video_montar.py` | Monta un MP4 por escena con fundidos para unirlos después con el concat de ffmpeg. |

Flujo de un episodio de audio:

```bash
python3 narrar.py guion.txt trabajo          # repetir mientras salga con código 3
python3 musica.py trabajo/musica.wav
python3 mezclar.py trabajo/narracion.wav trabajo/musica.wav <id>-<slug>.m4a
```

En vídeo, el guion lleva escenas (`@@ id | tipo | {json}`); `narrar.py` deja una pista por escena y
`escenas.json` con sus duraciones para sincronizar las imágenes. El audio del vídeo es el mismo `.m4a`.

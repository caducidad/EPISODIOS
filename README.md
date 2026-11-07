# Episodios

Documentales en audio y vídeo, en castellano, para escuchar andando.

Página: https://caducidad.github.io/EPISODIOS/

## Cómo está organizado

- `index.html`: la página (catálogo, buscador, filtros, reproductor y marcas de escuchado guardadas en el navegador).
- `catalogo.json`: series, temporadas y episodios. Cada episodio tiene `estado` (`publicado` o `pendiente`) y `formato` (`audio` o `video`).
- `media/`: audios (`.m4a`, AAC mono 48 kbps) y vídeos (`.mp4`).
- `guiones/`: el texto de cada episodio.

## Añadir un episodio

1. Copiar el audio o vídeo en `media/` y el guion en `guiones/`, con el id del episodio en el nombre (por ejemplo `sc02-lobos-yellowstone.m4a`).
2. En `catalogo.json`, cambiar el episodio a `"estado": "publicado"` y añadir `archivo`, `guion`, `duracion`, `fecha` y `fuentes`.
3. Commit y push a `main`. GitHub Pages actualiza la página en uno o dos minutos.

GitHub no admite archivos de más de 100 MB y recomienda que el repositorio no pase de 1 GB.

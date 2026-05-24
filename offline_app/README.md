# SCM Analytics Studio Offline

This folder is a static, no-backend edition of the SCM Analytics Studio app.

## Open it

Open `index.html` in a browser to upload local CSV or Excel files. All parsing,
cleaning, column mapping, KPIs, charts, validation, and CSV exports run in the
browser.

For the bundled sample button, serve this folder locally first:

```bash
python3 -m http.server 8097
```

Then open:

```text
http://localhost:8097/
```

The local server only serves the static files in this folder. It is not an API
backend and does not send data anywhere.

## Included files

- `index.html`: app shell
- `styles.css`: offline UI styling
- `app.js`: browser-side analytics engine
- `vendor/xlsx.full.min.js`: local Excel parser
- `assets/integrated_scm_data.csv`: bundled test dataset

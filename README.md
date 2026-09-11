This is a repo collating all the prayers I know, written in English.

## Adding a prayer

Add a `src/<Name>.md` file (a `# Title` heading, then the prayer, blank
lines between stanzas). Run `./build.sh` to regenerate `build/` — a
print-friendly HTML page and a `.txt` download for each prayer, plus
`build/index.html` listing them all. No external tools required, just
Python 3.

## Running locally

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python run_server.py
```

Then open http://localhost:8007/ (pass `--port` to use a different one).

When run as part of the `WebServices` monorepo, port 8007 is this
service's assigned slot alongside the other apps there.

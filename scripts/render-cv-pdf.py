#!/usr/bin/env python3
"""Render the current /cv/ page to the downloadable PDF using local Chromium."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', default='http://localhost:1313/cv/', help='URL of the running CV preview')
parser.add_argument('--browser', help='Path to a Chromium or Chrome executable')
parser.add_argument('--no-sandbox', action='store_true', help='Disable the Chrome sandbox for the trusted local CV build in CI')
args = parser.parse_args()

candidates = [
    args.browser,
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    shutil.which('chromium'),
    shutil.which('chromium-browser'),
    shutil.which('google-chrome'),
    shutil.which('google-chrome-stable'),
]
browser = next((candidate for candidate in candidates if candidate and Path(candidate).is_file()), None)
if not browser:
    raise SystemExit('Chromium or Chrome is required. Use --browser to supply its executable path.')
try:
    with urlopen(args.url, timeout=10) as response:
        if response.status != 200:
            raise SystemExit(f'CV preview returned HTTP {response.status}.')
except OSError as error:
    raise SystemExit(f'Start the Hugo preview before generating the PDF: {error}')

(root / 'tmp').mkdir(exist_ok=True)
(root / 'out').mkdir(exist_ok=True)
output = root / 'static/downloads/curriculum-vitae.pdf'
with tempfile.TemporaryDirectory(prefix='cv-pdf-', dir=root / 'tmp') as temporary:
    temporary = Path(temporary)
    rendered = temporary / 'curriculum-vitae.pdf'
    command = [
        browser,
        '--headless',
        '--no-pdf-header-footer',
        '--run-all-compositor-stages-before-draw',
        '--virtual-time-budget=2000',
        f'--user-data-dir={temporary / "browser-profile"}',
        f'--print-to-pdf={rendered}',
    ]
    if args.no_sandbox:
        command.extend(['--no-sandbox', '--disable-dev-shm-usage'])
    command.append(args.url)
    log_path = root / 'out/cv-pdf-render.log'
    print(f'Rendering CV with {browser}', flush=True)
    with log_path.open('w') as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 20
        deadline_expired = False
        try:
            while time.monotonic() < deadline:
                if rendered.is_file() and rendered.read_bytes().rstrip().endswith(b'%%EOF'):
                    break
                if process.poll() is not None:
                    break
                time.sleep(0.1)
            else:
                deadline_expired = True
        finally:
            # Some macOS Chromium builds remain open after writing the PDF.
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    if not rendered.is_file() or not rendered.read_bytes().rstrip().endswith(b'%%EOF'):
        if deadline_expired:
            reason = 'Chrome did not finish writing the PDF before the deadline.'
        elif process.returncode is not None and process.returncode < 0:
            reason = f'Chrome exited on signal {-process.returncode}.'
        else:
            reason = f'Chrome exited with code {process.returncode}.'
        print(reason, file=sys.stderr)
        print('Chrome output (last 60 lines):', file=sys.stderr)
        print('\n'.join(log_path.read_text(errors='replace').splitlines()[-60:]), file=sys.stderr)
        raise SystemExit('Chromium did not produce a complete PDF. Full log: out/cv-pdf-render.log.')
    shutil.copyfile(rendered, output)
print(f'Generated {output.relative_to(root)} ({output.stat().st_size:,} bytes).')

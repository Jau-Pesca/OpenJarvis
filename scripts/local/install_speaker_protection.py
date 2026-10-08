"""Install reviewed voice echo protection only, preserving helper/config/data."""
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timezone
EXPECTED = {'chamada_continua.py': '95aeea569778ec527844cd8381d62cdb38a27f260ca5317d5f7bf68803d585d1', 'audio_continuo.py': '0eb0dd8d127667b1dcaf3fae91a81e00f0a3fb054c9b787487547457ac648a81'}
root = Path.home()/'OpenJarvis-local'
for name, digest in EXPECTED.items():
    if hashlib.sha256((root/name).read_bytes()).hexdigest() != digest:
        raise SystemExit('Runtime changed since review; installation refused: '+name)
    compile(Path(__file__).with_name(name).read_text(), name, 'exec')
backup = root/'backups'/('speaker-protection-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
backup.mkdir(parents=True)
for name in EXPECTED:
    shutil.copy2(root/name, backup/name)
    shutil.copy2(Path(__file__).with_name(name), root/name)
print('Voice scripts installed; backup: '+str(backup))

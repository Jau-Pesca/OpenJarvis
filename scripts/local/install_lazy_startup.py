"""Install only the reviewed cold-start checker, with checksum guard and backup."""
import argparse
import hashlib
import shutil
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone

EXPECTED = 'f6ad50201492a876d023f281a10733bcd4465c9c9aa4473f03350a8389a8d902'
parser = argparse.ArgumentParser()
parser.add_argument('--install', action='store_true')
args = parser.parse_args()
target = Path.home()/'OpenJarvis-local/preparar_modelos.py'
source = Path(__file__).with_name('preparar_modelos.py')
compile(source.read_text(), str(source), 'exec')
current = hashlib.sha256(target.read_bytes()).hexdigest()
if not args.install:
    print('Dry-run: substituir somente preparar_modelos.py; sem mudanças em config, modelos ou helper.')
elif current != EXPECTED:
    raise SystemExit('O script mudou desde a revisão; instalação recusada.')
else:
    backup = target.parent/'backups'/('lazy-startup-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    backup.mkdir(parents=True)
    shutil.copy2(target, backup/target.name)
    fd, stage = tempfile.mkstemp(dir=target.parent, prefix='.lazy-startup-')
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(source.read_bytes())
        shutil.copymode(target, stage)
        os.replace(stage, target)
    finally:
        if Path(stage).exists(): Path(stage).unlink()
    print('Instalado. Backup: '+str(backup))

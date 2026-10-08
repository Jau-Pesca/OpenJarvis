#!/usr/bin/env python3
"""Reviewable local runtime update; inspection is the default."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import plistlib
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path(__file__).resolve().parent
LOCAL = Path.home() / "OpenJarvis-local"
APP = Path.home() / "Applications/JarvisMacControl.app"
SDK = Path("/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk")
# Snapshot of existing runtime before this change, used to reject concurrent edits.
BASE = {
    "voice": "53140fd241e38076ce6c96599ccb4fb19613868d3a10a40a855e434a4dc38fed",
    "native": "4e86d63e5c4b194af3c14cd65bd5a3ea9c1f686eaa892c4ef74fb9481d46f82d",
    "helper": "df3fbd5bdcd6dae111433a523f8328cdb240d80481e9b3349b44cf0210c6f981",
}
VOICE = LOCAL / "chamada_continua.py"
NATIVE = LOCAL / "mac-control/control.m"
HELPER = APP / "Contents/MacOS/JarvisMacControl"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, timeout=120, **kwargs)


def require(args: list[str]) -> None:
    result = run(args)
    if result.returncode:
        raise RuntimeError(f"Falhou: {args[0]}\n{result.stderr.strip()}")


def snapshot(paths: dict[str, Path]) -> dict[str, str]:
    return {name: digest(path) for name, path in paths.items()}


def check() -> None:
    # Match the runtime transport and its TCC identity rather than a diagnostic-only child.
    from openjarvis.tools.mac_desktop import native
    print(json.dumps(native("status"), ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true", help="Executa instalação com backup e rollback")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--voice-only", action="store_true")
    scope.add_argument("--native-only", action="store_true")
    parser.add_argument("--check", action="store_true", help="Consulta status pelo transporte do runtime; não move o cursor")
    args = parser.parse_args()
    voice, native = not args.native_only, not args.voice_only
    targets = {}
    if voice:
        targets["voice"] = VOICE
    if native:
        targets.update(native=NATIVE, helper=HELPER)
    before = snapshot(targets)
    print(json.dumps({"mode": "install" if args.install else "dry-run", "current_sha256": before,
                      "expected_sha256": {k: BASE[k] for k in targets},
                      "sources": [str(SOURCE / "chamada_continua.py")] * voice +
                                 [str(SOURCE / "mac-control/control.m")] * native}, indent=2))
    if native:
        for command in (["/usr/bin/codesign", "-v", "--strict", str(APP)],
                        ["/usr/bin/codesign", "-d", "-r-", str(APP)]):
            audit = run(command)
            print((audit.stdout + audit.stderr).strip())
            if audit.returncode:
                raise RuntimeError("Assinatura existente não passou na auditoria; instalação interrompida.")
        print("Reconstruir e assinar ad hoc altera o hash de identidade; o macOS pode exigir reabilitar Acessibilidade/Gravação de Tela.")
    if args.check and not args.install:
        check()
    if not args.install:
        print("Nenhum arquivo alterado. Use --install para aplicar após encerrar a chamada/interface.")
        return
    if before != {k: BASE[k] for k in targets}:
        raise RuntimeError("Runtime mudou desde a revisão. Compare as alterações antes de atualizar este instalador.")
    if voice:
        compile((SOURCE / "chamada_continua.py").read_text(), str(SOURCE / "chamada_continua.py"), "exec")
    if native and not SDK.is_dir():
        raise RuntimeError(f"SDK necessário ausente: {SDK}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = LOCAL / "backups" / f"runtime-{stamp}"
    # Stage beside the existing app: replacement and restoration use atomic renames.
    stage_parent = APP.parent if native else LOCAL
    with tempfile.TemporaryDirectory(prefix=".openjarvis-update-", dir=stage_parent) as temporary:
        stage = Path(temporary)
        prepared = {}
        if voice:
            prepared[VOICE] = stage / "chamada_continua.py"
            shutil.copy2(SOURCE / "chamada_continua.py", prepared[VOICE])
        if native:
            staged_app = stage / APP.name
            app_before = {str(p.relative_to(APP)): digest(p) for p in APP.rglob("*") if p.is_file()}
            shutil.copytree(APP, staged_app, symlinks=True)
            info_before = (APP / "Contents/Info.plist").read_bytes()
            info = plistlib.loads(info_before)
            identifier = info["CFBundleIdentifier"]
            require(["/usr/bin/xcrun", "clang", "-isysroot", str(SDK), "-fobjc-arc",
                     "-framework", "Cocoa", "-framework", "ApplicationServices", "-framework", "ImageIO",
                     str(SOURCE / "mac-control/control.m"), "-o",
                     str(staged_app / "Contents/MacOS/JarvisMacControl")])
            require(["/usr/bin/codesign", "--force", "--sign", "-", "--identifier", identifier, str(staged_app)])
            require(["/usr/bin/codesign", "-v", "--strict", str(staged_app)])
            if (staged_app / "Contents/Info.plist").read_bytes() != info_before:
                raise RuntimeError("Info.plist mudou durante preparação.")
            prepared[NATIVE] = stage / "control.m"
            shutil.copy2(SOURCE / "mac-control/control.m", prepared[NATIVE])
            # Include all app contents, not only executable, in concurrent-edit guard.
        if snapshot(targets) != before:
            raise RuntimeError("Runtime mudou durante preparação; nenhum destino foi substituído.")
        if native and app_before != {str(p.relative_to(APP)): digest(p) for p in APP.rglob("*") if p.is_file()}:
            raise RuntimeError("Aplicativo mudou durante preparação; instalação interrompida.")
        backup.mkdir(parents=True)
        saved = {}
        changed = []
        app_moved = False
        try:
            for destination in prepared:
                saved[destination] = backup / destination.relative_to(LOCAL)
                saved[destination].parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destination, saved[destination])
            if native:
                os.replace(APP, backup / APP.name)
                app_moved = True
                os.replace(staged_app, APP)
            for destination, replacement in prepared.items():
                os.replace(replacement, destination)
                changed.append(destination)
            if native:
                require(["/usr/bin/codesign", "-v", "--strict", str(APP)])
            print(f"Instalado. Backup preservado: {backup}")
        except BaseException:
            for destination in reversed(changed):
                shutil.copy2(saved[destination], destination)
            if app_moved:
                if APP.exists():
                    os.replace(APP, backup / "JarvisMacControl.failed.app")
                os.replace(backup / APP.name, APP)
            print(f"Instalação falhou; runtime anterior restaurado. Backup: {backup}")
            raise
    if args.check:
        check()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit(f"Erro: {error}")

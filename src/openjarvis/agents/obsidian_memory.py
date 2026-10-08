"""Personal memory backed by editable Obsidian Markdown notes and wikilinks."""
from __future__ import annotations
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time

KINDS = {'preferencia', 'objetivo', 'contexto', 'ideia', 'correcao'}


class ObsidianGraph:
    def __init__(self, path=None):
        self.path = Path(path or os.environ.get('OJ_OBSIDIAN_VAULT', str(Path.home() / 'OpenJarvis-local/Obsidian Jarvis')))
        self.path.mkdir(parents=True, exist_ok=True)
        for name in ('Declaracoes', 'Temas'):
            (self.path / name).mkdir(exist_ok=True)

    @contextlib.contextmanager
    def _lock(self):
        with (self.path / '.jarvis.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def _write(self, path, text):
        if path.is_symlink() or self.path.resolve() not in path.resolve().parents:
            raise ValueError('A nota deve estar dentro do cofre.')
        with tempfile.NamedTemporaryFile('w', dir=path.parent, encoding='utf-8', delete=False) as output:
            output.write(text)
            temporary = output.name
        try:
            os.replace(temporary, path)
        finally:
            Path(temporary).unlink(missing_ok=True)

    @staticmethod
    def _slug(text):
        return re.sub(r'[^\w -]', '', text, flags=re.UNICODE).strip()[:55] or 'Nota'

    @staticmethod
    def _front(meta):
        return '---\n' + ''.join(k + ': ' + json.dumps(v, ensure_ascii=False) + '\n' for k, v in meta.items()) + '---\n\n'

    def _read(self, path):
        if path.is_symlink() or path.stat().st_size > 65536:
            return None
        text = path.read_text(encoding='utf-8')
        if not text.startswith('---\n') or '\n---\n' not in text[4:]:
            return None
        front, body = text[4:].split('\n---\n', 1)
        meta = {}
        # Our properties are scalars. JSON scalars are valid YAML; plain YAML
        # scalars edited in Obsidian are accepted without loading YAML tags.
        for line in front.splitlines():
            key, colon, value = line.partition(':')
            if not colon:
                continue
            value = value.strip()
            try:
                meta[key.strip()] = json.loads(value)
            except ValueError:
                meta[key.strip()] = value.strip("'\"")
        if not isinstance(meta.get('jarvis_id'), str):
            return None
        return {'path': path, 'meta': meta, 'body': body.strip()}

    def _files(self):
        records = []
        for path in sorted(self.path.rglob('*.md')):
            if any(part.startswith('.') for part in path.relative_to(self.path).parts):
                continue
            try:
                record = self._read(path)
                if record:
                    records.append(record)
            except (OSError, UnicodeError):
                continue
            if len(records) >= 3000:
                break
        return records

    def _links(self, record, records):
        by_path = {r['path'].relative_to(self.path).with_suffix('').as_posix(): r['meta']['jarvis_id'] for r in records}
        by_name = {r['path'].stem: r['meta']['jarvis_id'] for r in records}
        links = set()
        for target in re.findall(r'\[\[([^\]]+)\]\]', record['body']):
            target = target.split('|')[0].split('#')[0].removesuffix('.md')
            identity = by_path.get(target) or by_name.get(target)
            if identity:
                links.add(identity)
        return links

    def _reference(self, record):
        return '[[' + record['path'].relative_to(self.path).with_suffix('').as_posix() + ']]'

    def _index(self, records):
        user = next((r for r in records if r['meta']['jarvis_id'] == 'usuario'), None)
        if not user:
            path = self.path / 'Usuario.md'
            if path.exists():
                raise ValueError('Usuario.md já existe sem identificação do Jarvis.')
            self._write(path, self._front({'jarvis_id': 'usuario', 'jarvis_type': 'user'}) + '# Usuário\n\n')
            user = self._read(path)
        notes = [r for r in records if r['meta'].get('jarvis_type') == 'personal_statement']
        start, end = '<!-- jarvis-links:start -->', '<!-- jarvis-links:end -->'
        block = start + '\n' + '\n'.join('- ' + self._reference(r) for r in notes) + '\n' + end
        text = user['path'].read_text(encoding='utf-8')
        if start in text and end in text:
            first, rest = text.split(start, 1)
            _, last = rest.split(end, 1)
            text = first + block + last
        else:
            text += '\n## Declarações\n\n' + block + '\n'
        self._write(user['path'], text)

    def remember(self, quote, kind='contexto', topic='usuario', origin='explicit_user', *, identity=None, recorded_at=None):
        quote = quote.strip()
        if not quote or len(quote) > 2000 or kind not in KINDS:
            raise ValueError('Memória inválida: use até 2000 caracteres e um tipo pessoal.')
        if re.search(r'(?i)(senha|password|token|api.?key)\s*[:=]', quote):
            raise ValueError('Credenciais não podem ser armazenadas nesta memória.')
        key = identity or 'nota:' + hashlib.sha256(quote.casefold().encode()).hexdigest()[:16]
        if not re.fullmatch(r'nota:[a-f0-9]{16}', key):
            raise ValueError('Identificador de memória inválido.')
        topic = str(topic)[:80].strip() or 'usuario'
        topic_hash = hashlib.sha256(topic.casefold().encode()).hexdigest()[:16]
        topic_id = 'tema:' + topic_hash
        with self._lock():
            records = self._files()
            if any(r['meta']['jarvis_id'] == key for r in records):
                return key
            theme = next((r for r in records if r['meta']['jarvis_id'] == topic_id), None)
            if not theme:
                path = self.path / 'Temas' / (self._slug(topic) + ' - ' + topic_hash[:8] + '.md')
                if path.exists():
                    raise ValueError('O arquivo do tema já existe sem identificação correspondente.')
                self._write(path, self._front({'jarvis_id': topic_id, 'jarvis_type': 'topic', 'name': topic}) + '# ' + topic + '\n')
                theme = self._read(path)
                records.append(theme)
            user = next((r for r in records if r['meta']['jarvis_id'] == 'usuario'), None)
            user_link = self._reference(user) if user else '[[Usuario]]'
            meta = {'jarvis_id': key, 'jarvis_type': 'personal_statement', 'kind': kind, 'topic': topic, 'origin': origin, 'status': 'user_statement', 'external_fact': False, 'recorded_at': recorded_at or time.time()}
            path = self.path / 'Declaracoes' / (kind + ' - ' + self._slug(quote) + ' - ' + key[5:13] + '.md')
            if path.exists():
                raise ValueError('O arquivo da declaração já existe sem identificação correspondente.')
            self._write(path, self._front(meta) + '# Declaração pessoal\n\n' + quote + '\n\n## Conexões\n\n' + user_link + '\n' + self._reference(theme) + '\n')
            records.append(self._read(path))
            self._index(records)
        return key

    def notes(self):
        notes = []
        for record in self._files():
            meta = record['meta']
            if meta.get('jarvis_type') != 'personal_statement' or meta.get('kind') not in KINDS:
                continue
            body = re.sub(r'^# [^\n]*\n*', '', record['body']).split('\n## Conexões', 1)[0].strip()
            if not body or len(body) > 2000 or re.search(r'(?i)(senha|password|token|api.?key)\s*[:=]', body):
                continue
            notes.append({'id': meta['jarvis_id'], 'content': body, 'kind': meta['kind'], 'topic': str(meta.get('topic', 'usuario')), 'origin': meta.get('origin', 'obsidian_edit'), 'recorded_at': meta.get('recorded_at', 0), 'status': 'user_statement', 'external_fact': False})
        return sorted(notes, key=lambda n: float(n['recorded_at']) if isinstance(n['recorded_at'], (float, int)) else 0, reverse=True)[:1000]

    def forget(self, key):
        if not key.startswith('nota:'):
            return False
        with self._lock():
            records = self._files()
            record = next((r for r in records if r['meta']['jarvis_id'] == key and r['meta'].get('jarvis_type') == 'personal_statement'), None)
            if not record:
                return False
            record['path'].unlink()
            self._index([r for r in records if r is not record])
            return True

    def recall(self, query):
        words = set(re.findall(r'\w{4,}', query.casefold()))
        notes = self.notes()
        def score(n):
            return len(words & set(re.findall(r'\w{4,}', (n['content'] + ' ' + n['topic']).casefold()))) + (1 if n['kind'] in {'preferencia', 'objetivo', 'correcao'} else 0)
        relevant = sorted((n for n in notes if score(n)), key=score, reverse=True)[:4]
        records = self._files()
        links = {r['meta']['jarvis_id']: self._links(r, records) for r in records}
        by_id = {n['id']: n for n in notes}
        seen = {n['id'] for n in relevant}
        for note in list(relevant[:2]):
            # Direct note links and two hops through a topic, excluding the
            # user hub so all memories do not become relevant to every query.
            neighbors = links.get(note['id'], set()) - {'usuario'}
            related = set(neighbors)
            for node in neighbors:
                related.update(k for k, targets in links.items() if node in targets)
            for key in sorted(related):
                if key in by_id and key not in seen and len(relevant) < 6:
                    relevant.append(by_id[key]); seen.add(key)
        while relevant and len(json.dumps(relevant, ensure_ascii=False)) > 3000:
            relevant.pop()
        return json.dumps(relevant, ensure_ascii=False)

"""Small real XLSX files without a Python office dependency."""
import math
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
from openjarvis.tools._stubs import BaseTool, ToolSpec
from openjarvis.core.types import ToolResult


class SpreadsheetCreateTool(BaseTool):
    tool_id = 'spreadsheet_create'
    is_local = True

    @property
    def spec(self):
        return ToolSpec(name=self.tool_id, description='Crie uma planilha Excel .xlsx REAL na pasta arquivos. Informe nome, colunas e linhas completas. Pode abrir o arquivo no aplicativo padrão do Mac. Para dados fictícios, declare que são exemplos.', parameters={'type': 'object', 'properties': {'name': {'type': 'string'}, 'columns': {'type': 'array', 'items': {'type': 'string'}}, 'rows': {'type': 'array', 'items': {'type': 'array', 'items': {'type': ['string', 'number', 'boolean', 'null']}}}, 'open': {'type': 'boolean'}}, 'required': ['name', 'columns', 'rows']}, category='file', timeout_seconds=30)

    def execute(self, **params):
        try:
            name = params.get('name', '')
            columns, rows = params.get('columns'), params.get('rows')
            if not isinstance(name, str) or Path(name).name != name or not name.endswith('.xlsx'):
                raise ValueError('Use um nome de arquivo .xlsx sem diretórios.')
            if not isinstance(columns, list) or not 1 <= len(columns) <= 30 or not all(isinstance(c, str) and len(c) <= 200 for c in columns):
                raise ValueError('Informe de 1 a 30 colunas.')
            if not isinstance(rows, list) or len(rows) > 1000 or any(not isinstance(row, list) or len(row) != len(columns) for row in rows):
                raise ValueError('Informe até 1000 linhas com o mesmo número de colunas.')
            for row in rows:
                for value in row:
                    if value is not None and not isinstance(value, (str, int, float, bool)):
                        raise ValueError('Célula inválida.')
                    if isinstance(value, str) and len(value) > 4000:
                        raise ValueError('Célula muito longa.')
                    if isinstance(value, float) and not math.isfinite(value):
                        raise ValueError('Número inválido.')
            base = Path.home() / 'OpenJarvis-local/arquivos'
            base.mkdir(parents=True, exist_ok=True)
            target = base / name
            if target.exists():
                raise ValueError('Esse arquivo já existe. Escolha um novo nome para preservar o original.')
            def col(index):
                value = ''
                while index:
                    index, mod = divmod(index - 1, 26)
                    value = chr(65 + mod) + value
                return value
            parts = []
            for rid, row in enumerate([columns, *rows], 1):
                cells = []
                for cid, value in enumerate(row, 1):
                    ref = col(cid) + str(rid)
                    if value is None:
                        continue
                    if isinstance(value, bool):
                        cells.append(f'<c r="{ref}" t="b"><v>{int(value)}</v></c>')
                    elif isinstance(value, (int, float)):
                        cells.append(f'<c r="{ref}"><v>{value}</v></c>')
                    else:
                        # Literal inline text: never silently execute formulas.
                        text = ''.join(ch for ch in str(value) if ch in '\t\n\r' or ord(ch) >= 32)
                        cells.append(f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{escape(text)}</t></is></c>')
                parts.append(f'<row r="{rid}">' + ''.join(cells) + '</row>')
            ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
            files = {
                '[Content_Types].xml': '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>',
                '_rels/.rels': '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
                'xl/workbook.xml': f'<workbook xmlns="{ns}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Dados" sheetId="1" r:id="rId1"/></sheets></workbook>',
                'xl/_rels/workbook.xml.rels': '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
                'xl/worksheets/sheet1.xml': f'<worksheet xmlns="{ns}"><sheetData>' + ''.join(parts) + '</sheetData></worksheet>'}
            # Exclusive creation also prevents racing overwrites/symlink replacement.
            with target.open('xb') as output:
                with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
                    for key, value in files.items():
                        archive.writestr(key, '<?xml version="1.0" encoding="UTF-8"?>' + value)
            opened = False
            if params.get('open', True):
                result = subprocess.run(['/usr/bin/open', str(target)], capture_output=True, timeout=15)
                opened = result.returncode == 0
            return ToolResult(tool_name=self.tool_id, success=True, content=f'Planilha criada: {target}. {len(rows)} linhas de dados, {len(columns)} colunas. Aberta no aplicativo padrão: {opened}.', metadata={'path': str(target), 'opened': opened, 'rows': len(rows), 'columns': len(columns)})
        except Exception as exc:
            return ToolResult(tool_name=self.tool_id, success=False, content=str(exc))

"""Syntax-check each cell without loading private data or executing model training."""
from pathlib import Path
import ast, json
ROOT = Path(__file__).resolve().parents[1]
count = 0
for path in sorted((ROOT / 'notebooks').glob('*.ipynb')):
    data = json.loads(path.read_text())
    for i, cell in enumerate(data['cells']):
        if cell['cell_type'] == 'code':
            ast.parse(''.join(cell['source']), filename=f'{path.name}:cell{i}')
            count += 1
    print(path.name, 'syntax OK')
print(count, 'code cells checked; this is not an execution test')

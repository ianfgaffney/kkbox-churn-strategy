"""Execute the four notebooks sequentially in separate fresh kernels on local data.

Requires dependencies in requirements.txt. Writes outputs in place only after each
notebook succeeds. Stops on errors. Model training can take several minutes.
"""
from pathlib import Path
import argparse
import nbformat
from nbclient import NotebookClient
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--kernel', default='python3', help='Registered Jupyter kernel name')
args = parser.parse_args()
ROOT = Path(__file__).resolve().parents[1]
for path in sorted((ROOT / 'notebooks').glob('*.ipynb')):
    print('Executing', path.name, flush=True)
    nb = nbformat.read(path, as_version=4)
    NotebookClient(nb, timeout=3600, kernel_name=args.kernel,
        resources={'metadata': {'path': str(ROOT)}}).execute()
    nbformat.write(nb, path)
print('All four notebooks executed successfully.')

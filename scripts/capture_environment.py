"""Run with the same Python interpreter/kernel used for the notebooks."""
from pathlib import Path
import subprocess, sys
root = Path(__file__).resolve().parents[1]
output = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], text=True)
(root / 'requirements-local-lock.txt').write_text(output)
print('Saved requirements-local-lock.txt. Review unrelated packages before publishing.')

import os
import sys

# Ensure the repository root is importable so tests can `import scripts.*`
# regardless of the directory pytest is invoked from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

"""Run local package checks without installation."""
from pathlib import Path
import runpy
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root.parent/"video-production-skills"))
sys.path.insert(0,str(root))
if __name__=="__main__":
    _ = runpy.run_module("postproduction.package_checks",run_name="__main__")

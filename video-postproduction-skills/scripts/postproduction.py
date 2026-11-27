"""Run this source package and its actual sibling production contract without installing either package."""
from pathlib import Path
import runpy
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root.parent/"video-production-skills"))
sys.path.insert(0,str(root))
if __name__=="__main__":
    _ = runpy.run_module("postproduction.cli",run_name="__main__")

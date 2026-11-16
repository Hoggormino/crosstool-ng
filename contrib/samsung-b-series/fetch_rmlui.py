#!/usr/bin/env python3
"""Fetch the RmlUi consumer checkpoint without following a moving branch."""
import argparse,json,subprocess
from pathlib import Path
pin=json.loads((Path(__file__).resolve().parent/'rmlui-source.json').read_text())
ap=argparse.ArgumentParser();ap.add_argument('destination',type=Path);a=ap.parse_args()
if a.destination.exists():raise SystemExit('Refusing an existing consumer checkout')
subprocess.run(['git','init',str(a.destination)],check=True)
subprocess.run(['git','-C',str(a.destination),'remote','add','origin',pin['url']],check=True)
subprocess.run(['git','-C',str(a.destination),'fetch','--depth=1','origin',pin['commit']],check=True)
subprocess.run(['git','-C',str(a.destination),'checkout','--detach',pin['commit']],check=True)

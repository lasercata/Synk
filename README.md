# Synk
Analyse trees and show diffencies. Useful to make backups.

## Installing
Download the script `Synk.py`
Make it executable : `chmod +x Synk.py`
Then you can copy it to `/bin` to ba able to launch it from anywhere (or add the path to the PATH)

## Usage
```
Synk.py -h
usage: Synk [-h] [-v] [-x EXCLUDE] [-f] [-nc] path1 path2

List differencies between path1 and path2.

positional arguments:
  path1                 Path to the first folder to synchronise
  path2                 Path to the second folder to synchronise

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Show Synk version and exit
  -x EXCLUDE, --exclude EXCLUDE
                        Patterns to exclude. ";" (semicolon, without spaces) between them.
  -f, --format          Change format of the printed paths.
  -nc, --no_color       Don't use color.

Examples :
        Synk path1 path2
        Synk path1 path2 -x .pyc;.dll
```

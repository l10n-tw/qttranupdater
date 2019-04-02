# Qt Translations File Updater
## WARNING
The further updates will be updated on [Qt Code Review #247698](https://codereview.qt-project.org/#/c/247698/),
I will not push further update here.

## Usage
Copy `download_ts.py` and `locale` directory to the path where ts files located.

## Translating
Please refer `TRANSLATING.md` in `locale` dir.

## Using
```
$ python3 download_ts.py --help
usage: download_ts.py [-h] [--branch branch_name] [--no-merge] [--clean-tags]
                      [--no-backups]
                      component_name language_name

The tool can make updating TS file more convenient.
It will fetch the latest daily updated template file from http://l10n-files.qt.io,
and auto merge the template with your ts file.

Read https://wiki.qt.io/Qt_Localization for the information about how to translate.

positional arguments:
  component_name        e.g: qtbase, qtscript, assistant, designer...
                        
                        If you don't know what component you want to merge, or
                        you just want to merge all components, just use
                        'all'.
  language_name         e.g: zh_TW, zh_CN, ar, ko, pl...
                        
                        The target language to merge.

optional arguments:
  -h, --help            show this help message and exit
  --branch branch_name  e.g: qt5-current, qt5-stable...
                        
                        It isn't needed to specify it; the program will ask
                        you what branch you want to merge.
  --no-merge            Don't merge the translation file, just download the template file.
  --clean-tags          Remove <location> tags in ts files.
                        Please use this before pushing your changes to the repository.
  --no-backups          Don't backup translate file before merging. (NOT RECOMMENDED!)

Report any bugs to <pan93412@gmail.com>.
```

## Copyright
```
## Copyright (C) 2019 Yi-Jyun Pan <pan93412@gmail.com>
##               2019 Oswald Buddenhagen <oswald.buddenhagen@gmx.de>
```

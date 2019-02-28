# How to translate Qt Translations File Updater?
The program has done I18N already, you can translate this program easily.

The tutorial will teach you how to translate.

## Requirement
- Python 3.7 or newer version installed.
- gettext libraries and gettext-tools installed.

## Step 1
You can find the language file in your language from "./locale".

> Just translate when the po file isn't exists or incomplete,
  Do not do something which others have been done.

If you didn't find the po file for your language, read from *Step 2*.
But if you found it, just read from *Step 5* ! :)

## Step 2
Input `ARGPARSE_PATH=$(python3 ./locale/getLibraryPath.py)"/argparse.py"`

`./getLibraryPath.py` is a tool which will print the path where the Python libraries
located.

## Step 3
Input `xgettext -o qttranupdater.pot download_ts.py $ARGPARSE_PATH`

It will extract all the strings in this program and the `argparse' library.

## Step 4
Input `msginit -l (your_language[2]) -i qttranupdater.pot` to
make the human-readable translate file of your language.

After doing those, translate (your_language).po!

## Step 5
First input `mkdir -p ./locale/(your_language[2])/LC_MESSAGES` to make the locale directory,<br />
and then input `msgfmt -co ./locale/(your_language[2])/LC_MESSAGES/qttranupdater.mo (your_language[2]).po`

> Note: If you are in `locale` directory, just input `(your_language[2])/LC_MESSAGES` !!!

It will output the human-readable po file to a program-readable mo file.

[2]: like zh_TW, zh_CN, ru, kr...

## Step 6
Restart program to apply translations.

If the translation is complete and no big problem, you can
optionally make a Pull Request to this program! :)

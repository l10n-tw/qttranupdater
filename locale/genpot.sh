#!/usr/bin/bash

scriptPath=$(dirname $0)

if [ ! -f download_ts.py ]
then
  echo "Please ensure download_ts.py is existing!"
  exit 1
fi

ARGPARSE_PATH=$(python3 $scriptPath/getLibraryPath.py)"/argparse.py"
xgettext -o qttranupdater.pot download_ts.py $ARGPARSE_PATH

echo "qttranupdater.pot is generated in $(pwd) directory."
exit 0

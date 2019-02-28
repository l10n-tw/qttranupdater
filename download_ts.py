#!/usr/bin/env python3
#############################################################################
## Qt Translations File Updater
##
## Copyright (C) 2019 Yi-Jyun Pan <pan93412@gmail.com>
##               2019 Oswald Buddenhagen <oswald.buddenhagen@gmx.de>
##
## This file is part of the translations module of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with e.g:eptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

'''Imports'''
import urllib.request as urlReqFunc
import sys
import subprocess
import os
import shlex  # used for subprocess.Popen()
import argparse as arg
import gettext # Experimental Support!
import shutil

'''Consts'''
downloadURL = "http://l10n-files.qt.io/l10n-files/{branch_name}/"

# The file with branch info. If you can't access this file,
# please contact `ossi` at IRC.
branchMap = "http://l10n-files.qt.io/l10n-files/branch-map.txt"

# The filename format. If the format is modified, please
# edit here and do a Merge Request to qt code-review.
filenameFormat = "{component}_{langcode}.ts"

# The untranslated filename. It will apply to
# {langcode} in filenameFormat.
untranslatedFilename = "untranslated"

# The merge command. It requires install `linguist` first.
# * (fn = filename)
mergeCmd = "lconvert {extraTag} -no-obsolete -target-language {targetLang} -i {template} {langFile} -o {destfn}"

# The path to save language files (mo) for this program.
# When you set it up, please copy the mo file to
# localePath/(your_language_code)/LC_MESSAGES/qttranupdater.mo
localePath = "./locale"

# Edit it and make a Merge Request if something changed.
# It can't automatically update, may outdated
# if nobody to update that.
#
# If `component_name` is `all`, it will recursive the component listed
# in this list.
compList = [
    "qt", "qtbase", "qtdeclarative", "qtquickcontrols", "qtquickcontrols2",
    "qtscript", "qtmultimedia", "qtxmlpatterns", "qtconnectivity",
    "qtlocation", "assistant", "designer", "linguist", "qt_help"
]

'''Set up gettext'''
gettext.bindtextdomain("qttranupdater", localePath)
gettext.textdomain("qttranupdater")
_ = gettext.gettext

'''Arguments'''
argv = arg.ArgumentParser(
    description=_("""The tool can make updating TS file more convenient.
It will fetch the latest daily updated template file from
http://l10n-files.qt.io, and auto merge the template with
your ts file."""),
    epilog=_("Read https://wiki.qt.io/Qt_Localization for the information about how to translate."),
    formatter_class=arg.RawTextHelpFormatter
)

argv.add_argument("component_name", action="store", type=str,
    help=_("""\
e.g: qtbase, qtscript, assistant, designer...

If you don't know what component you want to merge, or
you just want to merge all components, just use
'all'."""))
argv.add_argument("language_name", action="store", type=str,
    help=_("""\
e.g: zh_TW, zh_CN, ar, ko, pl...

The target language to merge."""))

# TRANSLATOR NOTE: branch_name is available to translate!
# It will be appeared like `[--branch branch_name]`.
argv.add_argument("--branch", action="store", type=str, metavar=_("branch_name"),
    help=_("""\
e.g: qt5-current, qt5-stable...

It isn't needed to specify it; the program will ask
you what branch you want to merge.""")
)
argv.add_argument("--no-merge", action="store_false", dest="toMerge",
    help=_("Don't merge the translation file, just download the template file."))
argv.add_argument("--clean-tags", action="store_true", dest="cleanTags",
    help=_("Remove <location> tags in ts files.\nPlease use this before pushing your changes to the repository."))
argv.add_argument("--no-backups", action="store_false", dest="backup",
    help=_("Don't backup translate file before merging. (NOT RECOMMENDED!)"))

def downObj(url):
  '''
  It will call urllib to download
  the specified file and return
  the RAW file object.

  We recommend you to use downFile() which
  will download the file to target directory,
  this function is low-level.
  '''
  try:
    reqObj = urlReqFunc.Request(url, method="GET")
    fileRaw = urlReqFunc.urlopen(reqObj)
  except:
    # After `Downloading xxx...`
    print(_(""" Something wrong!

The reason why the tool can't work properly:
  1) No internet connection.
  2) This connection was blocked by your
     country or the server.
  3) URL Wrong: {url}

If all looks normal but you still can't use this
tool, please report this error to:
    pan93412@gmail.com

and attach this error:
    {exceptInfo}

Authors will reply you as soon as possible. :)
""").format(url=url, exceptInfo=str(sys.exc_info())))
    exit(1)
  return fileRaw

def downFile(url, dest, description=""):
  '''
  Download files from <url> to <dest>.

  description (optional, default=""):
      the description of the <url>.
  [return code]: 0
  '''
  print(_("Downloading {description}... ").format(description=description), end="")

  fileObj = downObj(url)
  destFile = open(dest, "w")

  fileContent = fileObj.read().decode("UTF-8") # We assume the encoding of <url> is `UTF-8'
  destFile.write(fileContent)

  fileObj.close()
  destFile.close()

  # TRANSLATOR NOTE: The string is after `Downloading {description}...`
  print(_("Success."))
  return 0

def mergeTS(templateFile, langFile, targetLang, destFile="", preserveLocation=True):
  '''
  Merge <langFile> with <templateFile>.

  It is needed to install Qt Linguist 5, otherwise the merge
  process will fail.

  templateFile (required):
      The template used for merge <langFile>
  langFile (required):
      The language file to be merged.
  targetLang (required):
      The language file's target language.
      e.g: zh_TW, zh_CN, ja...
  destFile (optional, default=<langFile>):
      The merged file will save to <destFile>.
  preserveLocation (optional, default=True):
      Whether we preserve <location> tags or not (False).
  [return code]: 0, if no errors.
                 otherwise return the return code lconvert returned.
  '''
  print(_("Merging: {langFile}... ").format(langFile=langFile), end="")

  if destFile == "":
    destFile = langFile # Save to the original path.

  lconvertProcess = subprocess.Popen(
    shlex.split(
      mergeCmd.format(
        # "lconvert {extraTag} -no-obsolete -target-language {targetLang} -i {template} {langFile} -o {destfn}"
        extraTag = "--locations none" if preserveLocation else "",
        targetLang = targetLang,
        template = templateFile,
        langFile = langFile,
        destfn = destFile
      )
    )
  )
  lconvertProcess.wait()

  # TRANSLATOR NOTE: The string is after `Merging: {langFile}... `
  print(_("Success."))

  # The normal case might return `0'.
  return lconvertProcess.returncode

def parseBranch(bName="", bMap=branchMap):
  '''
  The function will check if the <bName> is
  in <bMap>. If <bName> not in <bMap>, the
  function also let user pick the branch
  they want to merge.

  bName (optional, default=""):
      The branch name that user specified.

      If <bName> not in <bMap>, that it will
      ignore the bName and let user pick the
      branch they want to merge.
  bMap (optional, default=branchMap):
      The branch map url.
      The format like:
          qt5 dev current
          qt5 5.11 stable
          qt5 5.9 old9
          qt5 5.6 old
      The normal case, you can just ignore the option.
  [return value]: the branch that corresponding to l10n-files.qt.io.
                  ex. qt5-current, qt5-stable, qt5-old9...
  '''

  # Downloading branchMap
  branchesObj = downObj(bMap)
  branchesRaw = branchesObj.readlines()
  branchesObj.close()
  branchesDict = []
  vaildBranchList = []

  # Parse branchMap and make it structure.
  for branch in branchesRaw:
    branchInfo = branch.decode("UTF-8").split(" ")

    if "qt" not in branchInfo[0]:
      continue

    branchesDict.append(
      {
        "bID": f"{branchInfo[0]}-{branchInfo[2]}".replace("\n", ""), # ex. qt5-current
        "bName": f"{branchInfo[0].capitalize()[:-1]} {branchInfo[1]}".replace("\n", "") # ex. Qt 5.11
      }
    )

    # I know I repeat the action twice times.
    # But I need to avoid too many for-loops and it is the
    # simplest way.
    vaildBranchList.append(f"{branchInfo[0]}-{branchInfo[2]}".replace("\n", ""))

  # The loop let user pick branch, also it will check whether <bName>
  # is vaild or not.
  while True:
    for branch in branchesDict:
      if branch["bID"] == bName:
        # Hey, it is vaild! the user gave us a correct branch! :)
        return bName

    print(_("BranchName\tBranchID"))
    for branch in branchesDict:
      print(f"{branch['bName']}\t\t{branch['bID']}")

    # TRANSLATOR NOTE: Please ensure the BranchID is same as
    # the above `BranchID`
    userBranch = input(_("Please input the BranchID that you want to merge: "))
    if userBranch in vaildBranchList:
      # Hey, it is vaild! the user gave us a correct branch! :)
      return userBranch
    else:
      # Oops. Please input the correct answer. :(
      print(_("BranchID invaild: {userBranch}\n").format(userBranch=userBranch))
      continue


def main():
  '''
  `main' is entrance of this program.
  Do not call it DIRECTLY.

  [return code]:
    - If all successful, return 0.
    - If it has some issues, but no big deal,
      still return 0
    - If it has some issues which makes problem
      can't run successfuly, return 1.
    - If it has some fatal issues, return 2.
    - If exception has been triggered, return 1.
  '''
  argList = argv.parse_args()

  # BRANCH PART: If user specified `branch', it will
  # check whether `branch' is valid or not, otherwise
  # let users choose branch.
  branch = ""
  if argList.branch:
    branch = parseBranch(argList.branch)
  else:
    branch = parseBranch()

  # DOWNLOAD PART: It will download the templates
  # of those ts files.
  # If user specified `all', then it will reversive
  # compList.
  mergeFn = {}
  if argList.component_name == "all":
    for comp in compList:
      untranFn = filenameFormat.format(component=comp, langcode=untranslatedFilename)
      mergeFn.update({untranFn: filenameFormat.format(component=comp, langcode=argList.language_name)})
      downFile(f"{downloadURL.format(branch_name=branch)}{untranFn}", untranFn, _("The template of {comp}").format(comp=comp))
  else:
      untranFn = filenameFormat.format(component=argList.component_name, langcode=untranslatedFilename)
      mergeFn.update({untranFn: filenameFormat.format(component=argList.component_name, langcode=argList.language_name)})
      downFile(f"{downloadURL.format(branch_name=branch)}{untranFn}", untranFn, _("The template of {comp}").format(comp=argList.component_name))

  # MERGE PART: It will merge the translate file with template file.
  # It will make a backup like "qtbase-zh_TW.ts~" first, and then to merge.
  for templateFn in mergeFn:
    tranFn = mergeFn[templateFn]
    if argList.toMerge:
      if os.path.exists(tranFn) != True or os.path.isfile(tranFn) != True:
        shutil.copy(templateFn, tranFn)
      else:
        if argList.backup:
          shutil.copy(tranFn, f"{tranFn}~")
        mergeTS(templateFn, tranFn, argList.language_name, preserveLocation= argList.cleanTags)
    else:
      print(_("You can merge {translate_file} manually, template file: {template_file}").format(translate_file=tranFn, template_file=templateFn))

# It also can be used for module, I have written completed
# documentation in this program.
if __name__ == "__main__":
  main()

"""
FIXME(nll) comment
Copyright (C) 2019 Nicolas Lelong (nicolas@nllsoft.fr)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import os
import sys

assert sys.version_info >= (3, 6)         # NOTE(nll) may run on lower python versions, untested

#-----------------------------------------------------------------------------

def main(argv):

  args = validateCmdLineArgs(argv)
  if args is None:
    return

  if args.folderPath2 is None:

    # Compare images in the same folder
    # Variants are found using '-' in image names

    folderPath = args.folderPath1
    imageNames = findImagesInFolder(folderPath)

    variants = findImagesVariants(imageNames, '-')

    encVariants = encodeVariantsConfiguration(variants)

    isOk = validateImagesVariants(encVariants)

    if isOk:

      configurationJSstr = "window.CFG_COMPARISONS =" + json.dumps(encVariants, indent=2)

      writeAssetsToFolder(args.folderPath1)
      writeConfigurationJS(args.folderPath1, configurationJSstr)

  else:

    # Compare images between two folders
    # One folder per variant

    folderPath1 = args.folderPath1
    folderPath2 = args.folderPath2

    rootFolderPath = os.path.split(folderPath1)[0]

    if rootFolderPath.lower() != os.path.split(folderPath2)[0].lower():
      logError("Both folders must be in the same root folder")
      input('\nPress Enter to close.')
      return

    folderName1 = os.path.split(folderPath1)[1]
    imageNames1 = findImagesInFolder(folderPath1, recursive=True)

    folderName2 = os.path.split(folderPath2)[1]
    imageNames2 = findImagesInFolder(folderPath2, recursive=True)

    encVariants = encodeVariantsConfiguration2folder(folderName1, imageNames1, folderName2, imageNames2)

    isOk = validateImagesVariants(encVariants)

    if isOk:

      configurationJSstr = "window.CFG_COMPARISONS = " + json.dumps(encVariants, indent=2)

      writeAssetsToFolder(rootFolderPath)
      writeConfigurationJS(rootFolderPath, configurationJSstr)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

def findImagesVariants(imageNames, separator):

  logInfo("Searching for variants...")
  logInfo("    * separator is '%c'" % separator)

  variants = {}           # NOTE(nll) will be { basename: { variant: filename, ... } }

  imageNames = sorted(imageNames)

  for filename in imageNames:
    name, ext = os.path.splitext(filename)
    split = splitlast(name, sep=separator)
    
    if len(split) != 2:
      print("    * skipping image, no variant name found in '%s'." % filename)
      continue
    
    basename, variantname = split
    basename = basename.strip()
    variantname = variantname.strip()
    variants.setdefault(basename, {})[variantname] = filename

  logInfo("    * found %d images with variants." % len(variants))

  return variants


def splitlast(str, sep):

  index = str.rfind(sep)
  if index == -1:
    return [str]
  else:
    return [str[:index], str[index+1:]]

#-----------------------------------------------------------------------------

def findImagesInFolder(folderPath, recursive=False):

  EXTENSIONS = ['.png', '.jpg', '.jpeg']

  logInfo("Scan folder for images : '%s'..." % folderPath)
  
  imagenames = []

  for curdir, dirs, files in os.walk(folderPath):

    if not recursive:
      del dirs[:]
    
    filenames = [ x for x in files if os.path.isfile(os.path.join(curdir,x)) ]
    filenames = [ os.path.relpath( os.path.join(curdir,x), folderPath ) for x in filenames ]
    filenames = [ x.replace('\\', '/') for x in filenames ]
  
    for filename in filenames:
      name, ext = os.path.splitext(filename)
      if ext.lower() not in EXTENSIONS:
        continue
      imagenames.append(filename)

  logInfo("    found %d images." % len(imagenames))

  return imagenames

#-----------------------------------------------------------------------------

def encodeVariantsConfiguration(variants):

  result = []

  names = list(variants.keys())
  names.sort()

  for name in names:
    imagevariants = variants[name]
    encoded = encodeCmpValue(name, imagevariants)
    result.append(encoded)

  return result

#-----------------------------------------------------------------------------

def encodeVariantsConfiguration2folder(folderName1, imageNames1, folderName2, imageNames2):

  logInfo("Searching for variants...")

  allImages = dict()
  for name in imageNames1:
    allImages[name] = 1 | allImages.get(name,0) 
  for name in imageNames2:
    allImages[name] = 2 | allImages.get(name,0)

  allImageNames = list( allImages.keys() )
  allImageNames.sort()

  result = []

  for name in allImageNames:

    foldersBitMask = allImages[name]

    value = {}
    value['title'] = os.path.splitext(name)[0]

    if foldersBitMask != 3:
      logInfo("   * Skipped image without variant : '%s'" % name)
      continue

    url = None
    if foldersBitMask & 1 != 0:
      url = "%s/%s" % (folderName1, name)
    value['before'] = { 'label': folderName1, 'url': url }

    url = None
    if foldersBitMask & 2 != 0:
      url = "%s/%s" % (folderName2, name)
    value['after'] = { 'label': folderName2, 'url': url }

    result.append(value)

  logInfo("    * found %d images with variants." % len(result))

  return result

#-----------------------------------------------------------------------------

def encodeCmpValue(title, variants):
  
  keys = list(variants.keys())[:2]        # FIXME(nll) maximum 2 variants
  assert len(keys) == 2

  keys.sort()
  value = {}
  value['title'] = title
  value['before'] = { 'label': keys[0], 'url': variants[keys[0]] }
  value['after']  = { 'label': keys[1], 'url': variants[keys[1]] }
  return value

#-----------------------------------------------------------------------------

class Arguments:

  def __init__(self):
    self.folderPath1 = None
    self.folderPath2 = None


def validateCmdLineArgs(argv):

  numArgs = len(argv)
  showUsageMessage = False
  result = None
  
  if numArgs == 1:
    showUsageMessage = True

  elif numArgs == 2:

    folderPath1 = argv[1]
    folderPath1 = os.path.abspath( os.path.normpath(folderPath1) )
    if not os.path.isdir(folderPath1):
      logError("Invalid folder path '%s'" % folderPath1)

    else:
      result = Arguments()
      result.folderPath1 = folderPath1

  elif numArgs == 3:

    folderPath1 = argv[1]
    folderPath1 = os.path.abspath( os.path.normpath(folderPath1) )
    if not os.path.isdir(folderPath1):
      logError("Invalid folder path '%s'" % folderPath1)
      folderPath1 = None

    folderPath2 = argv[2]
    folderPath2 = os.path.abspath( os.path.normpath(folderPath2) )
    if not os.path.isdir(folderPath2):
      logError("Invalid folder path '%s'" % folderPath2)
      folderPath2 = None

    if None not in (folderPath1, folderPath2):
      result = Arguments()
      result.folderPath1 = folderPath1
      result.folderPath2 = folderPath2

  else:
    logError("Too many arguments")
    logError("")
    showUsageMessage = True

  if showUsageMessage:
    logInfo(argv[0])
    logInfo(__file__)

  return result

#-----------------------------------------------------------------------------

def writeAssetsToFolder(dstFolderPath):

  srcNames = [
    'index.html',
    'nll-image-compare-report-files/configuration.js',
    'nll-image-compare-report-files/BeerSlider.js',
    'nll-image-compare-report-files/BeerSlider.css',
  ]

  for name in srcNames:
    data = _getAssetData("assets/"+name)
    
    dstFilePath = os.path.join(dstFolderPath, name)
    dstFilePath = os.path.normpath(dstFilePath)
    
    dstSubfolderPath = os.path.dirname(dstFilePath)
    if not os.path.isdir(dstSubfolderPath):
      os.makedirs(dstSubfolderPath)
    
    with open(dstFilePath, 'wb') as f:
      f.write(data)


"""
Get absolute path to resource, works for dev and for PyInstaller
"""
_RSC_BASE_PATH = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

def _getAssetData(relativeFilePath):

  # NOTE(nll) I could not get pkgutil.get_data work both in dev & PyInstaller so I rely on 
  #   https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
  absFilePath = os.path.join(_RSC_BASE_PATH, relativeFilePath)
  absFilePath = os.path.normpath(absFilePath)
  with open(absFilePath, 'rb') as f:
    return f.read()


def writeConfigurationJS(dstFolderPath, configurationJSstr):

  dstFilePath = 'nll-image-compare-report-files/configuration.js'
  dstFilePath = os.path.join(dstFolderPath, dstFilePath)
  dstFilePath = os.path.normpath(dstFilePath)
  
  dstSubfolderPath = os.path.dirname(dstFilePath)
  if not os.path.isdir(dstSubfolderPath):
    os.makedirs(dstSubfolderPath)
  
  with open(dstFilePath, 'w') as f:
    f.write(configurationJSstr)

#-----------------------------------------------------------------------------

def validateImagesVariants(images):

  logInfo("Images variants are :")

  for image in images:
    title = image['title']
    variantNames = [ image['before']['label'], image['after']['label'] ]
    logInfo("* '%s' :" % title)
    logInfo("    * %s" % variantNames)
  
  logInfo("")
  continueStr = input("Continue ?    enter yes to continue : ")
  return (continueStr.strip().lower() in ('yes', 'y'))

#-----------------------------------------------------------------------------

def logError(msg):
  print("*ERROR*", msg)

def logInfo(msg):
  print(msg)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

if __name__ == "__main__":
  main(sys.argv)

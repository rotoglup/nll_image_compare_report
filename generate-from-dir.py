import json
import os
import sys


def main(argv):

  folderPath = sys.argv[1]
  imageNames = findImagesInFolder(folderPath)
  imageNames.sort()

  variants = findImagesVariants(imageNames, '-')

  encVariants = encodeVariantsConfiguration(variants)
  print( "window.CFG_COMPARISONS =", json.dumps(encVariants, indent=2) )


def findImagesVariants(imageNames, separator):

  variants = {}           # NOTE(nll) will be { basename: { variant: filename, ... } }

  for filename in imageNames:
    name, ext = os.path.splitext(filename)
    split = splitlast(name, sep=separator)
    
    if len(split) != 2:
      continue
    
    basename, variantname = split
    variants.setdefault(basename, {})[variantname] = filename

  return variants


def splitlast(str, sep):

  index = str.rfind(sep)
  if index == -1:
    return [str]
  else:
    return [str[:index], str[index+1:]]


def findImagesInFolder(folderPath):

  EXTENSIONS = ['.png', '.jpg', '.jpeg']
  
  filenames = os.listdir(folderPath)
  filenames = [ x for x in filenames if os.path.isfile(os.path.join(folderPath,x)) ]
  imagenames = []

  for filename in filenames:
    name, ext = os.path.splitext(filename)
    if ext.lower() not in EXTENSIONS:
      continue
    imagenames.append(filename)

  return imagenames


def encodeVariantsConfiguration(variants):

  result = []

  names = list(variants.keys())
  names.sort()

  for name in names:
    imagevariants = variants[name]
    encoded = encodeCmpValue(name, imagevariants)
    result.append(encoded)

  return result


def encodeCmpValue(title, variants):
  
  keys = list(variants.keys())[:2]        # FIXME(nll) maximum 2 variants
  assert len(keys) == 2

  keys.sort()
  value = {}
  value['title'] = title
  value['before'] = { 'label': keys[0], 'url': variants[keys[0]] }
  value['after']  = { 'label': keys[1], 'url': variants[keys[1]] }
  return value


if __name__ == "__main__":
  main(sys.argv)
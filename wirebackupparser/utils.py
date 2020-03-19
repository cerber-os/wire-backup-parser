import os
import magic
from tqdm import tqdm
from PIL import Image


def generateThumbnail(inputFile, outputFile):
    with magic.Magic()as m:
        fileType = m.id_filename(inputFile)
    if not fileType:
        # Unknown file format
        return
    elif 'image data' in fileType:
        im = Image.open(inputFile)
        im.thumbnail((100, 100))
        im.save(outputFile + '.png')
    else:
        # TODO: Add additional file formats
        return


def genThumbsForFilesInDir(inputDir, outputDir):
    print("Generating thumbnails...")
    for fileName in tqdm(os.listdir(inputDir)):
        file = os.path.join(inputDir, fileName)
        if os.path.isfile(file):
            generateThumbnail(file, os.path.join(outputDir, fileName))

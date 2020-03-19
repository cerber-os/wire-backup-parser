import os
from tqdm import tqdm
from PIL import Image


def generateThumbnail(inputFile, outputFile):
    try:
        im = Image.open(inputFile)
        crop = min(im.size)
        im = im.crop(((im.size[0] - crop) // 2,
                      (im.size[1] - crop) // 2,
                      (im.size[0] + crop) // 2,
                      (im.size[1] + crop) // 2))
        im.thumbnail((100, 100))
        im.save(outputFile)
    except OSError:
        return
        # TODO: Add additional file formats


def genThumbsForFilesInDir(inputDir, outputDir):
    print("Generating thumbnails...")
    for fileName in tqdm(os.listdir(inputDir)):
        file = os.path.join(inputDir, fileName)
        out = os.path.join(outputDir, fileName) + '.png'
        if os.path.isfile(file) and not os.path.exists(out):
            generateThumbnail(file, out)

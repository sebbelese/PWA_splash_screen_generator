from PIL import Image
import math
import os


# Force the scaling factor to be an integer to avoid interpolation - this is useful e.g. for pixel art images. 
# To use this setting, it is better if the input image is small regards to the output image dimensions otherwise there may be large void areas
forceIntegerScaling = True 
# Percentage of the image dimensions reserved for the borders, to avoid the image touching the borders of the screen
minPercentageBorders = 10 
# Original image to be placed on the splash screen
inputSplash = "splash.png"
# Local folder where to place the splash screens
outputFolder = "resized"
#Location on server where will be served the images
serverImagesPath = "static/images/splash/"

try:
    os.makedirs(outputFolder) 
except:
    pass

sizes = [(2048, 2732), (1668, 2388), (1668, 2224), (1536, 2048), (1242, 2688), (1125, 2436), (828, 1792), (1242, 2208), (750, 1334), (640, 1136)]

#Landscape
sizes = sizes + [(size[1], size[0]) for size in sizes]


inputImg = Image.open(inputSplash)
inputWidth, inputHeight = inputImg.size

manifestFile = open(os.path.join(outputFolder, "splash.json"),"w")
manifestFile.write('[\n') 

htmlFile = open(os.path.join(outputFolder, "splash.html"),"w")


for size in sizes:
    
    scaleFactor = min(size[0]*(1-minPercentageBorders/100)/inputWidth, size[1]*(1-minPercentageBorders/100)/inputHeight)
    if forceIntegerScaling:
        scaleFactor = math.floor(scaleFactor) #We use an integer as factor to avoid interpolation - this is useful e.g. for pixel art images
    print("Image size %ix%i, scaling factor %.2f"%(*size,scaleFactor))
    scaledSize = (math.floor(inputWidth*scaleFactor), math.floor(inputHeight*scaleFactor))
    scaledImg = inputImg.resize(scaledSize)
    finalImage = Image.new(mode="RGBA", size=size)
    offsetX = int(0.5*(size[0]-scaledSize[0]))
    offsetY = int(0.5*(size[1]-scaledSize[1]))
    finalImage.paste(scaledImg, (offsetX,offsetY,offsetX+scaledSize[0],offsetY+scaledSize[1]))
    imageFname = "splash_%ix%i.png"%(size[0],size[1])
    finalImage.save(os.path.join(outputFolder, imageFname))
    
    def manifestLine(pixelRatio):
        if int(size[0]/pixelRatio)*pixelRatio == size[0] and int(size[1]/pixelRatio)*pixelRatio == size[1]:
            manifestFile.write('\t{\n')
            manifestFile.write('\t\t"src": "'+serverImagesPath+imageFname+'",\n')
            manifestFile.write('\t\t"media": "(device-width: %ipx) and (device-height: %ipx) and (-webkit-device-pixel-ratio: %i)",\n'%(size[0],size[1],pixelRatio))
            manifestFile.write('\t\t"type": "image/png",\n')
            manifestFile.write('\t\t"sizes": "%ix%i",\n'%(size[0],size[1]))
            manifestFile.write('\t},\n')
    
    # We should probably limit these
    manifestLine(1)
    manifestLine(2)
    manifestLine(3)
    
    htmlFile.write('<link rel="apple-touch-startup-image" media="(device-width: %ipx) and (device-height: %ipx) and (-webkit-device-pixel-ratio: 1)" href="%s%s">\n'%(size[0],size[1],serverImagesPath,imageFname))
    if int(size[0]/2)*2 == size[0] and int(size[1]/2)*2 == size[1]:
        htmlFile.write('<link rel="apple-touch-startup-image" media="(device-width: %ipx) and (device-height: %ipx) and (-webkit-device-pixel-ratio: 2)" href="%s%s">\n'%(size[0]/2,size[1]/2,serverImagesPath,imageFname))
    if int(size[0]/3)*3 == size[0] and int(size[1]/3)*3 == size[1]:
        htmlFile.write('<link rel="apple-touch-startup-image" media="(device-width: %ipx) and (device-height: %ipx) and (-webkit-device-pixel-ratio: 2)" href="%s%s">\n'%(size[0]/3,size[1]/3,serverImagesPath,imageFname))
htmlFile.write('<meta name="apple-mobile-web-app-capable" content="yes"> \n')     
manifestFile.write(']\n')

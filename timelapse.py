import sys
import os
from PIL import Image
import pygame
import shutil

def computeCrop(beforeKey, afterKey) :
    if (beforeKey + 1) == afterKey:
        # the two key frames are next to each other: nothing to do!
        print("adjacent key frames.")
        return
    framesToAdjust = (afterKey - beforeKey)
    for frame in range(beforeKey + 1, afterKey):
        frameLX[frame] = frameLX[beforeKey] + ((frame - beforeKey) * int((frameLX[afterKey] - frameLX[beforeKey]) / framesToAdjust))
        frameLY[frame] = frameLY[beforeKey] + ((frame - beforeKey) * int((frameLY[afterKey] - frameLY[beforeKey]) / framesToAdjust))
        frameRX[frame] = frameRX[beforeKey] + ((frame - beforeKey) * int((frameRX[afterKey] - frameRX[beforeKey]) / framesToAdjust))
        frameRY[frame] = frameRY[beforeKey] + ((frame - beforeKey) * int((frameRY[afterKey] - frameRY[beforeKey]) / framesToAdjust))

def findLeftKey(Frame):
    while 0 <= Frame:
        Frame = Frame - 1
        if "k" == frameKey[Frame]:
            return Frame
    return 0
    
def findRightKey(Frame):
    while Frame < (len(frameKey) - 1):
        print(Frame)
        Frame = Frame + 1
        if "k" == frameKey[Frame]:
            return Frame
    return len(frameKey) - 1

frameLX = []
frameLY = []
frameRX = []
frameRY = []
frameKey = []

if len(sys.argv) < 2:
    print("Usage: " + sys.argv[0] + " image_folder")
    exit(1)
filelist = os.listdir(sys.argv[1])
numberOfFrames = 0
for file in filelist:
    if file.endswith("jpg") or file.endswith("JPG"):
        numberOfFrames = numberOfFrames + 1
if not os.path.exists(sys.argv[1] + "/temp/config.txt"):
    # new project: create the directory and default config file.
    if not os.path.exists(sys.argv[1] + "/temp"):
        os.mkdir(sys.argv[1] + "/temp")
    configFileHandle = open(sys.argv[1] + "/temp/config.txt", "w")
    configFileHandle.write("# time lapse config file. The following line is the general config. Each line thereafter is one frame.\n")
    configFileHandle.write(str(numberOfFrames) + " " + str(int(numberOfFrames / 2)) + "\n")
    for i in range(numberOfFrames):
        if (0 == i) or ((numberOfFrames - 1) == i):
            # first and last frames are always key.
            configFileHandle.write("0,312 5999,3687 K\n")
        else:
            # all other frames are basic (non key), by default.
            configFileHandle.write("0,312 5999,3687\n")
    configFileHandle.close()
else:
    # existing project: load the config from file.
    print("Loading config from " + sys.argv[1] + "/temp/config.txt")
with open(sys.argv[1] + "/temp/config.txt") as fp:  
    cnt = 0
    for line in fp:
        if cnt >  numberOfFrames:
            print("Warning: missing frames! Config file not fully loaded. Stopped at " + str(cnt - 1) + " frames.")
            break
        if not line.startswith("#"):
            if 0 == cnt:
                settings = line.split(" ")
                currentFrame = int(settings[1])                
                if not numberOfFrames == int(settings[0]):
                    print("Error: mismatched number of frames. " + str(numberOfFrames) + " original files found. " + line + " frames in config file.")
                    exit(1)
            else:
                data = line.split(" ")
                if 3 == len(data):
                    frameKey.append("k")
                else:
                    frameKey.append(" ")
                lData = data[0].split(",")
                frameLX.append(int(lData[0]))
                frameLY.append(int(lData[1]))
                rData = data[1].split(",")
                frameRX.append(int(rData[0]))
                frameRY.append(int(rData[1]))
            cnt = cnt + 1
#print(frameLX, frameLY, frameRX, frameRY, frameKey)
#print(filelist)
filelist.sort()
filelist.remove("temp")
#print(filelist)
cnt = 0
# generate the thumbnails, as needed
for file in filelist:
    if file.endswith("jpg") or file.endswith("JPG"):
        if not os.path.exists(sys.argv[1] + "/temp/thumb" + file):
            im = Image.open(sys.argv[1] + "/" + file)
            im = im.resize((600, 400))
            im.save(sys.argv[1] + "/temp/thumb" + file)
        cnt = cnt + 1
# initial display 
leftFrame = findLeftKey(currentFrame)
rightFrame = findRightKey(currentFrame)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)
BLUE =  (  0,   0, 255)
# now let's get serious...
pygame.init()
size = width, height = 1800, 500
screen = pygame.display.set_mode(size)
while 1:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN: 
            if (event.key == pygame.K_x) or (event.key == pygame.K_q):
                configFileHandle = open(sys.argv[1] + "/temp/config.txt", "w")
                configFileHandle.write("# time lapse config file. The following line is the general config. Each line thereafter is one frame.\n")
                configFileHandle.write(str(numberOfFrames) + " " + str(currentFrame) + "\n")
                for i in range(numberOfFrames):
                    if "k" == frameKey[i]:
                        # key frame.
                        configFileHandle.write(str(frameLX[i]) + "," + str(frameLY[i]) + " " + str(frameRX[i]) + "," + str(frameRY[i]) + " K\n")
                    else:
                        # basic (non key) frame.
                        configFileHandle.write(str(frameLX[i]) + "," + str(frameLY[i]) + " " + str(frameRX[i]) + "," + str(frameRY[i]) + "\n")
                configFileHandle.close()
                if os.path.exists(sys.argv[1] + "/temp/processed"):
                    shutil.rmtree(sys.argv[1] + "/temp/processed")
                sys.exit()
            if event.key == pygame.K_LEFT:
                if currentFrame > 0:
                    currentFrame = currentFrame - 1
                    leftFrame = findLeftKey(currentFrame)
                    rightFrame = findRightKey(currentFrame)
            if event.key == pygame.K_RIGHT:
                if currentFrame < (numberOfFrames - 1):
                    currentFrame = currentFrame + 1
                    leftFrame = findLeftKey(currentFrame)
                    rightFrame = findRightKey(currentFrame)
            if event.key == pygame.K_DOWN:
                if (currentFrame - 10) >= 0:
                    currentFrame = currentFrame - 10
                else :
                    currentFrame = 0
                leftFrame = findLeftKey(currentFrame)
                rightFrame = findRightKey(currentFrame)
            if event.key == pygame.K_UP:
                if (currentFrame + 10) <= (numberOfFrames - 1):
                    currentFrame = currentFrame + 10
                else :
                    currentFrame = numberOfFrames - 1
                leftFrame = findLeftKey(currentFrame)
                rightFrame = findRightKey(currentFrame)
            if event.key == pygame.K_PAGEUP:
                    currentFrame = findRightKey(currentFrame)
            if event.key == pygame.K_PAGEDOWN:
                    currentFrame = findLeftKey(currentFrame)
                    
            if event.key == pygame.K_k:
                frameKey[currentFrame] = "k"
                computeCrop(findLeftKey(currentFrame), currentFrame)
                computeCrop(currentFrame, findRightKey(currentFrame))
            if event.key == pygame.K_b:
                frameKey[currentFrame] = " "
                computeCrop(findLeftKey(currentFrame), findRightKey(currentFrame))
            if(pygame.key.get_mods() & pygame.KMOD_SHIFT):
                z = 200
            else:
                z = 20
            if event.key == pygame.K_p:
                if os.path.exists(sys.argv[1] + "/temp/processed"):
                    shutil.rmtree(sys.argv[1] + "/temp/processed")
                os.mkdir(sys.argv[1] + "/temp/processed")
                frameCnt = 0
                for fileName in filelist:
                    if fileName.endswith("jpg") or fileName.endswith("JPG"):
                        im = Image.open(sys.argv[1] + "/" + fileName)
                        im = im.resize((1920, 1080), Image.NEAREST, (frameLX[frameCnt], frameLY[frameCnt], frameRX[frameCnt], frameRY[frameCnt]))
                        im.save(sys.argv[1] + "/temp/processed/" + fileName)
                        frameCnt = frameCnt + 1
            if "k" == frameKey[currentFrame]:
                if event.key == pygame.K_i:
                    if (frameRX[currentFrame] - frameLX[currentFrame]) - z >= 1920:
                        frameRX[currentFrame] = frameRX[currentFrame] - z
                    else:
                        frameRX[currentFrame] = frameLX[currentFrame] + 1920
                    frameRY[currentFrame] = frameLY[currentFrame] + int(((frameRX[currentFrame] - frameLX[currentFrame]) * 9) / 16)
                    computeCrop(findLeftKey(currentFrame), currentFrame)
                    computeCrop(currentFrame, findRightKey(currentFrame))
                if event.key == pygame.K_o:
                    if (frameRX[currentFrame] + z) <= 5999:
                        if (frameRX[currentFrame] - frameLX[currentFrame]) + z <= 6000:
                            frameRX[currentFrame] = frameRX[currentFrame] + z
                        else:
                            frameRX[currentFrame] = 5999
                    else:
                        frameRX[currentFrame] = 5999
                    frameRY[currentFrame] = frameLY[currentFrame] + int(((frameRX[currentFrame] - frameLX[currentFrame]) * 9) / 16)
                    computeCrop(findLeftKey(currentFrame), currentFrame)
                    computeCrop(currentFrame, findRightKey(currentFrame))
                if event.key == pygame.K_d:
                    if (frameRY[currentFrame] + z) <= 3999:
                        frameRY[currentFrame] = frameRY[currentFrame] + z
                        frameLY[currentFrame] = frameLY[currentFrame] + z
                    else:
                        frameLY[currentFrame] = 3999 - (frameRY[currentFrame] - frameLY[currentFrame])
                        frameRY[currentFrame] = 3999
                    computeCrop(findLeftKey(currentFrame), currentFrame)
                    computeCrop(currentFrame, findRightKey(currentFrame))
                if event.key == pygame.K_r:
                    if (frameRX[currentFrame] + z) <= 5999:
                        frameRX[currentFrame] = frameRX[currentFrame] + z
                        frameLX[currentFrame] = frameLX[currentFrame] + z
                    else:
                        frameLX[currentFrame] = 5999 - (frameRX[currentFrame] - frameLX[currentFrame])
                        frameRX[currentFrame] = 5999
                    computeCrop(findLeftKey(currentFrame), currentFrame)
                    computeCrop(currentFrame, findRightKey(currentFrame))
                if event.key == pygame.K_l:
                    if (frameLX[currentFrame] - z) >= 0:
                        frameRX[currentFrame] = frameRX[currentFrame] - z
                        frameLX[currentFrame] = frameLX[currentFrame] - z
                    else:
                        frameRX[currentFrame] = (frameRX[currentFrame] - frameLX[currentFrame])
                        frameLX[currentFrame] = 0
                    computeCrop(findLeftKey(currentFrame), currentFrame)
                    computeCrop(currentFrame, findRightKey(currentFrame))
                if event.key == pygame.K_u:
                    if (frameLY[currentFrame] - z) >= 0:
                        frameRY[currentFrame] = frameRY[currentFrame] - z
                        frameLY[currentFrame] = frameLY[currentFrame] - z
                    else:
                        frameRY[currentFrame] = (frameRY[currentFrame] - frameLY[currentFrame])
                        frameLY[currentFrame] = 0
                    computeCrop(findLeftKey(currentFrame), currentFrame)
                    computeCrop(currentFrame, findRightKey(currentFrame))
                    
    leftImage = pygame.image.load(sys.argv[1] + "/temp/thumb" + filelist[leftFrame])
    currentImage = pygame.image.load(sys.argv[1] + "/temp/thumb" + filelist[currentFrame])
    rightImage = pygame.image.load(sys.argv[1] + "/temp/thumb" + filelist[rightFrame])
    screen.fill(0)
    my_small_font = pygame.font.SysFont('comicsansms', 36)
    frameCounter = my_small_font.render(str(currentFrame) + " / " + str(numberOfFrames), 0, (255, 255, 255))
    if currentFrame > 0 :
        screen.blit(leftImage, (0, 50))
        pygame.draw.rect(screen, RED, [int(frameLX[leftFrame] / 10), 50 + int(frameLY[leftFrame] / 10), int((frameRX[leftFrame] - frameLX[leftFrame]) / 10),  int((frameRY[leftFrame] - frameLY[leftFrame]) / 10)], 1)
    screen.blit(currentImage, (600, 50))
    if "k" == frameKey[currentFrame]:
        pygame.draw.rect(screen, RED, [600 + int(frameLX[currentFrame] / 10), 50 + int(frameLY[currentFrame] / 10), int((frameRX[currentFrame] - frameLX[currentFrame]) / 10), int((frameRY[currentFrame] - frameLY[currentFrame]) / 10)], 1)
    else :
        pygame.draw.rect(screen, GREEN, [600 + int(frameLX[currentFrame] / 10), 50 + int(frameLY[currentFrame] / 10), int((frameRX[currentFrame] - frameLX[currentFrame]) / 10), int((frameRY[currentFrame] - frameLY[currentFrame]) / 10)], 1)
    if currentFrame < (numberOfFrames - 1) :
        screen.blit(rightImage, (1200, 50))
        pygame.draw.rect(screen, RED, [1200 + int(frameLX[rightFrame] / 10), 50 + int(frameLY[rightFrame] / 10), int((frameRX[rightFrame] - frameLX[rightFrame]) / 10), int((frameRY[rightFrame] - frameLY[rightFrame]) / 10)], 1)
    screen.blit(frameCounter, (0, 440))
    pygame.display.flip()
    
    

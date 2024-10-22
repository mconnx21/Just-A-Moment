#MOMENTS EDUCATIONAL TOOL
#Open-source pygame library liscencing and information available at https://www.pygame.org
#*******************************************************************************************


#BASIC PROGRAM SET UP:
#------------------------------------------------
import pygame #import and initiate pygame
pygame.init()
import random #import random module
import logging #import logging module used for logging errors
logging.basicConfig(level=logging.ERROR)
import math #import math module

window_Width = 1200 #set constants for display window width and height
window_Height = 800

screen = pygame.display.set_mode((window_Width, window_Height)) #creates the window
pygame.display.set_caption('Moments Education Tool') #set the window title

smallFont = pygame.font.Font('freesansbold.ttf', 17) #define two font sizes for use later
bigFont = pygame.font.Font('freesansbold.ttf', 20)



#GLOBAL CONSTANTS:
#-------------------------------------------
groundHeight = 25 #height of the green grass ground
beamWidth = 800 #balance beam width
beamHeight = 30 # balence beam height
initialPivotPos = (600, 650)#intial position of the pivot, and so centre of the beam
backgroundBlue = (139, 240, 247)#rgb for sky blue which will be used for the background
white = (255, 255, 255)#assigning the rgb for white to a variable to make coding faster
darkGrey = (140,140,140) #assigning the rgb for the desired dark grey to a variable
OrigBlockSurfaceHeight = 800 #constant to hold the original height of the blockSurface surface
beamMass = 4 #constant that stores the mass of the balence beam


#VARIABLES:
#-------------------------------------------
running = True #boolean condition used to exit the display window while loop if quit is pressed
practiceMode = False #boolean variable that is true when in Practice Mode, and false in Simulator Mode
beamLeftEdgeX = initialPivotPos[0]-beamWidth//2 #x coord of  left edge of  balence beam, relative to the screen
beamRightEdgeX = initialPivotPos[0]+beamWidth//2#y coord of  right edge of  balence beam, relative to the screen
leftBeamEdgeOnBs = 0 #x coordinate of the left edge of the balence beam, relative to blockSurface
rightBeamEdgeOnBs = beamWidth #y coordinate of the left edge of the balence beam, relative to blockSurface
angle = 0 #angle of rotation is initally 0 as the system is level
CoMDistance = 0 #distance of COM from the pivot
massLblOn = True #boolean variable that is True when mass labels are on, and false when mass labels are off.
distLblOn = True #boolean variable that is True when distance labels are on, and false when distance labels are off.
levelLine = True #boolean variable that is True when level lines are on, and false when level lines are off.
supportsOn = True #boolean variable that is true whenever the beam supports are on, and false when off.



#DECLARING DISPLAY BACKGROUND AND SURFACES:
#-------------------------------------------

background = pygame.Surface((window_Width+1000, window_Height))#surface to display the background 
background.fill(backgroundBlue) #fill the background with a blue sky, and draw on green ground to represents grass:
pygame.draw.rect(background, (38, 166, 42), [0, window_Height - groundHeight, window_Width, groundHeight])

blockSurface = pygame.Surface((beamWidth, OrigBlockSurfaceHeight))#set up blockSurface for beam and blocks to be drawn on
blockSurface.fill(white) #fill the surface in white
blockSurface.set_colorkey(white)#set 'colorkey' to white so the white background is not shown when surface is blitted
pygame.draw.rect(blockSurface, (214, 94, 152), [0, int((OrigBlockSurfaceHeight/2))-beamHeight, beamWidth, beamHeight])#draw beam
centreOfMassPos = (int(beamWidth/2), int((OrigBlockSurfaceHeight/2)- (beamHeight/2)))#work out corrdinates of centre of mass
pygame.draw.circle(blockSurface, (30, 255, 0), centreOfMassPos, 5)#draw centre of mass dot
blockSurfaceRect = blockSurface.get_rect()#get the pygame rect of the surface so we can set its position in the display window
blockSurfaceRect.center = initialPivotPos #centre the blockSurface around the pivot position
origBlockSurface = blockSurface.copy() #make a copy of this inital set up of blockSurface. As the program runs, blockSurface\
#will change as blocks are added and removed to the simulator. Thus we copy this initial 'blank beam' version so we can always access it.
origBlockSurfaceRect = blockSurfaceRect.copy()

supportsHeight = (window_Height- initialPivotPos[1]) - groundHeight #calculate height between ground and base of beam
supportsSurf = pygame.Surface((beamWidth, supportsHeight))#create a surface to draw the supports onto
supportsSurf.fill(white) #fill background in white
supportsSurf.set_colorkey(white)#set colourkey to white so background not blitted
pygame.draw.rect(supportsSurf, (9, 15, 133), [0,0,50,supportsHeight])#draw on supports at either end of surface
pygame.draw.rect(supportsSurf, (9, 15, 133), [beamWidth - 50,0,50,supportsHeight])
supportsRect = supportsSurf.get_rect()
supportsRect.midtop = initialPivotPos #Line up the top of the supports with the base of the beam

#create a text surface which displays a basic error message:
errorSurf = bigFont.render((str('  There has been an error. Please exit and restart the program.  ')), True, (255,0,0), (255,255,255))

SMinstructionsImg = pygame.image.load('SMinstructionsNew.png')#load image of Simulator Mode instrucitons
SMinstructionsImg.convert()
SMinstructions = pygame.transform.scale(SMinstructionsImg, (1200, 250))#scale to correct dimensions

PMinstructionsImg = pygame.image.load('PMinstructions.png')#load image of Practice Mode instructions
PMinstructionsImg.convert()
PMinstructions = pygame.transform.scale(PMinstructionsImg, (1200,250))#scale to correct dimensions

beamInfoSurface = pygame.Surface((window_Width, 25))#create a surface which will display the beam properties
beamInfoSurfaceRect = beamInfoSurface.get_rect() #obtain the rect so we can position the surface on the display
beamInfoSurfaceRect.topleft = (PMinstructions.get_rect()).bottomleft #update the rect with the desired position
beamInfoSurface.fill(darkGrey)#fill the background as dark grey
#create a text surface to display the information:
initialBeamInfo = bigFont.render(str('   Beam mass = '+ str(beamMass)+ 'kg      Centre of mass distance to pivot = '\
                                     + str(CoMDistance) + 'm   '), True, (255,255,255), darkGrey) 
beamInfoSurface.blit(initialBeamInfo, (300,5)) #blit the text to the surface





#CLASSES AND SUBROUTINES
#-------------------------------------------

class Block(pygame.sprite.Sprite): 
    def __init__(self, colorGiven, width, height, pivotPos, leftBeamEdgeOnBs): #constructor
        super().__init__()
        #assigning all private attributes:
        self.image = pygame.Surface([width, height])#creating graphical image for the block
        self.image.fill((colorGiven))#fill with the color given
        self.rect = self.image.get_rect()#set up a rect attribute for the block
        self.rect.midbottom = pivotPos#position block at the required coordinates (will be pivotPos)
        
        self.color = colorGiven
        
        self.mass = round((width/10),2) #set mass as a scalar of the width
        #create a text surface for mass label:
        self.massLbl = smallFont.render((str(self.mass)) + 'kg', True, (0,0,0), colorGiven)
        self.massLblRect = self.massLbl.get_rect()#set a rect for the text surface
        self.massLblRect.midtop = (int(width/2), 0) #position the mass label at the top of the block
        self.image.blit(self.massLbl, self.massLblRect)#blit the text to the block
        
        self.distance = 0 #repeat the above process but for the distance and its label
        self.distLbl = smallFont.render((str(self.distance)) +'m', True, (0,0,0), colorGiven)
        self.distLblRect = self.distLbl.get_rect()
        self.distLblRect.midbottom = (int(width/2), height)
        self.image.blit(self.distLbl, self.distLblRect)

        #set the x coordinate of the block relative to the left edge of the beam:
        self.xRelativeToBeam = self.rect.midbottom[0] -leftBeamEdgeOnBs 


    def getMass(self): #mass getter method
        return self.mass

    def updateMass(self, givenMass): #mass setter method
        self.mass = givenMass

    def getDistance(self): #distance getter method
        return self.distance

    def updateDistance(self, givenDistance): #distance setter method
        self.distance = givenDistance

    def moveRight(self, step, supportsOn, rightBeamEdgeOnBs, blockSurface):
        if supportsOn == True and self.rect.bottomright[0] + abs(step) <= rightBeamEdgeOnBs:
            blockSurface.blit(background, self.rect, self.rect)#cover up the blocks old position
            self.rect.x += abs(int(step)) #add the given number of pixels to the block's x coordinate
            self.xRelativeToBeam += abs(int(step))
        return blockSurface

    def moveLeft(self, step, supportsOn, leftBeamEdgeOnBs, blockSurface): #left equivilent of moveRight()
        if supportsOn == True and int(self.rect.bottomleft[0]) - abs(step) >= leftBeamEdgeOnBs:
            blockSurface.blit(background, self.rect, self.rect)
            self.rect.x -= abs(int(step))
            self.xRelativeToBeam -= abs(int(step))
        return blockSurface

    def bigger(self, step, supportsOn, blockSurface): #increases block size
        if supportsOn == True:
            blockSurface.blit(background, self.rect, self.rect)#cover up old position
            newSideLength = self.image.get_width() + abs(step)#calculate increased side length
            if newSideLength >200: #VALIDATION to ensure size doesn't get too big
                newSideLength = 200
            oldBottom = self.rect.midbottom #store the old coordinates of the bottom of the Block
            self.image = pygame.Surface([int(newSideLength), int(newSideLength)])#create the new, bigger surface
            self.image.fill(self.color)
            self.mass = round(newSideLength/10, 2)#update mass to reflect new size
            self.rect = self.image.get_rect()
            self.rect.midbottom = oldBottom #position the new block at the same beam position as the old block
        return blockSurface

    def smaller(self, step, supportsOn, blockSurface): #ecreases block size
        if supportsOn == True:
            blockSurface.blit(background, self.rect, self.rect)#cover up old position
            newSideLength = self.image.get_width() - abs(step)#calculate decreased side length
            if newSideLength <40: #VALIDATION to ensure size doesn't get too small
                newSideLength = 40
            oldBottom = self.rect.midbottom #store the old coordinates of the bottom of the Block
            self.image = pygame.Surface([newSideLength, newSideLength])#create the new, smaller surface
            self.image.fill(self.color)
            self.mass = round(newSideLength/10, 2)#update mass to reflect new size
            self.rect = self.image.get_rect()
            self.rect.midbottom = oldBottom #position the new block at the same beam position as the old block
        return blockSurface

    def updateRect(self, leftBeamEdgeOnBs): #method to reset the block in the same position on the beam,\
        #after the dimensions of blockSurface have been changed
        self.rect.midbottom = (leftBeamEdgeOnBs + self.xRelativeToBeam, self.rect.midbottom[1])

    def setDistance(self, blockSurfaceRect): #calculates a block's distance to the pivot
        lengthBetween = (blockSurfaceRect.width//2) - self.rect.midbottom[0] #calculate distnce from blockSurface centre
        #note if the block is left of centre, the sign will be +, if it is right of centre it will be -
        self.distance = round(lengthBetween/100, 2)#set distance attribute to scalar multiple of length from pivot

    def updateMoment(self): #calculates the moment provided by this block
        moment = self.mass * 9.81 * self.distance #use physics equation to calculate moment from mass and dist
        return moment

    def updateMassLbl(self, massLblOn):
        #create a text surface with the current value of the mass attribute written on it:
        self.massLbl = smallFont.render((str(self.mass)) + 'kg', True, (0,0,0), self.color)
        self.massLblRect = self.massLbl.get_rect()#set a rect for the text surface
        self.massLblRect.midtop = (int(self.rect.width/2), 0) #position the mass label at the top of the block
        if massLblOn == True:
            pygame.draw.rect(self.image, self.color, self.massLblRect)#draw a rectangle of background color\
            #over the text to cover the old label up
            self.image.blit(self.massLbl, self.massLblRect)#blit the mass label to the block image

    def turnOnMassLbl(self):
        self.image.blit(self.massLbl, self.massLblRect)#blit the mass label to the block image

    def turnOffMassLbl(self):
        pygame.draw.rect(self.image, self.color, self.massLblRect)#draw a rectangle of background color\
        #over the text to cover it up

    def updateDistLbl(self, distLblOn):
        #create a text surface with the current value of the distance attribute written on it:
        self.distLbl = smallFont.render((str(abs(self.distance))) +'m', True, (0,0,0), self.color)
        self.distLblRect = self.distLbl.get_rect()#find the rect
        self.distLblRect.midbottom = (int(self.rect.width/2), self.rect.height)#position label at bottom of square
        if distLblOn == True:
            pygame.draw.rect(self.image, self.color, self.distLblRect)#draw a rectangle of background color\
            #over the text to cover old label up
            self.image.blit(self.distLbl, self.distLblRect)#blit the distance label to the block image

    def turnOnDistLbl(self):
        self.image.blit(self.distLbl, self.distLblRect)#blit the distance label to the block image

    def turnOffDistLbl(self):
        pygame.draw.rect(self.image, self.color, self.distLblRect)#draw a rectangle of background color\
        #over the text to cover it up

    def getRect(self): #rect getter method
        return self.rect

        
        

            
        
class Pivot(pygame.sprite.Sprite):
    def __init__(self, colorGiven, width, height, givenPivotPos):
        super().__init__() #inherit from pygame sprite class
        self.image = pygame.Surface([width, height]) #set up a surface for the image of the pivot
        self.image.fill(white)
        self.image.set_colorkey(white)#colorkey = white so background is not visible when the image is blitted
        pygame.draw.polygon(self.image, colorGiven, [(0,height), (width, height), (width//2,0)])#draw a triangle
        self.rect = self.image.get_rect()#set the rect attribute
        self.pivotPos = givenPivotPos#assign the pivotPos attribute
        self.rect.midtop = self.pivotPos #position the top of the triangle at the given pivot point coordinates
        self.color = colorGiven #assign the color attribute

    def moveRight(self, step, supportsOn, beamRightEdgeX): #moves pivot right
        if supportsOn == True:
            screen.blit(background, self.rect, self.rect)#cover up old position
            if self.rect.midtop[0] + abs(step) >= beamRightEdgeX: #VALIDATION: if out of range, set to max right boundary
                self.rect.midtop = (beamRightEdgeX-50, self.rect.midtop[1])
            else:
                self.rect.x += abs(step)#move pivot pivot right by 'step' pixels
            self.pivotPos = self.rect.midtop #update the new point of pivot coodinates
        

    def moveLeft(self, step, supportsOn, beamLeftEdgeX): #moves pivot left
        if supportsOn == True:
            screen.blit(background, self.rect, self.rect)#cover up old position
            if self.rect.midtop[0] - abs(step) <=beamLeftEdgeX: #VALIDATION: if out of range, set to max left boundary
                self.rect.midtop = (beamLeftEdgeX+50, self.rect.midtop[1])
            else:
                self.rect.x -= abs(step)#move pivot pivot left by 'step' pixels
            self.pivotPos = self.rect.midtop #update the new point of pivot coodinates
        

    def getPivotPos(self):
        return self.pivotPos
    
    def getRect(self):
        return self.rect
        

def findNewBlockSurface(origBlockSurface, origBlockSurfaceRect, currentPivotPos, beamWidth):
    if currentPivotPos[0] > origBlockSurfaceRect.center[0]: #then pivot has moved to the right of centre of beam
        offset = currentPivotPos[0] - origBlockSurfaceRect.x #calculate the amount the pivot has moved by
        
        newSurface = pygame.Surface((2*offset, origBlockSurfaceRect.height))#make a new surface with a width \
        #two times the offset, so that its centre will be just one offset away i.e. at the new pivot position
        newSurface.fill(darkGrey)#set the surface color and colorkey
        newSurface.set_colorkey(darkGrey)

        newSurface.blit(origBlockSurface, [0,0])#blit the empty beam onto the new surface
        
        newSurfaceRect = newSurface.get_rect()#find the rect of the newsurface
        newSurfaceRect.topleft = origBlockSurfaceRect.topleft#match the top left corners of the old and new surfaces\
        #so that the beam does not visably move positions

        leftBeamEdgeOnBs = 0 #update the limits of the beam RELATIVE to the blockSurface, so these can be used as\
        #limits for block movement
        rightBeamEdgeOnBs = beamWidth
        
        return newSurface, newSurfaceRect, leftBeamEdgeOnBs, rightBeamEdgeOnBs #return the new surface and its rect\
        #so we can assign these to blockSurface and blockSurfaceRect. 

    elif currentPivotPos[0] < origBlockSurfaceRect.center[0]: #then pivot has moved left of centre
        offset = (origBlockSurfaceRect.x + origBlockSurfaceRect.width) - currentPivotPos[0] #calculate the amount the\

        newSurface = pygame.Surface((2*offset, origBlockSurfaceRect.height))#make a new surface with a width \
        #pivot has moved by two times the offset, so that its centre will be just one offset away i.e. at the \
        #new pivot position.
        newSurface.fill(darkGrey)
        newSurface.set_colorkey(darkGrey)

        newSurfaceRect = newSurface.get_rect()#find the rect of the newsurface
        newSurfaceRect.topright = origBlockSurfaceRect.topright #match the top right corners so the beam doesnt move
        
        leftBeamEdgeOnBs = newSurfaceRect.width-beamWidth #calculate new left beam edge RELATIVE \
        #to the new blockSurface
        rightBeamEdgeOnBs = newSurfaceRect.width
        newSurface.blit(origBlockSurface, [leftBeamEdgeOnBs, 0])#blit the empty beam onto the new surface

        return newSurface, newSurfaceRect, leftBeamEdgeOnBs, rightBeamEdgeOnBs #return the new surface and its rect\
        #so we can assign these to blockSurface and blockSurfaceRect.

    else:
        return origBlockSurface.copy(), origBlockSurfaceRect.copy(), 0, beamWidth

def updateBeamInfo(blockSurfaceRect, leftBeamEdgeOnBs, beamWidth, beamMass):
    #calculate new disatance of centre of mass to the pivot using that the pivot is always at the centre of blockSurface
    newCoMDistance = round((blockSurfaceRect.width//2 - (leftBeamEdgeOnBs + beamWidth//2))/100, 2)
    #create updated text surface:
    beamInfo = bigFont.render(str('   Beam mass = '+ str(beamMass)+ 'kg      Centre of mass distance to pivot = '\
                                  + str(abs(newCoMDistance)) + 'm    '), True, (255,255,255), darkGrey)
    beamInfoSurface.blit(beamInfo, (300,5)) #blit the text surface onto a grey surface called beamInfoSurface
    return newCoMDistance #return newCoMDistance so it can be used in resultantMoment() instead of recalculating
    
def resultantMoment(blocks, beamMass, CoMDistance):
    resultantMoment = 0 #initialise resultantMoment variable
    for block in blocks: #iterate through all blocks, find their moment and add to resultantMoment
        
        moment = block.updateMoment()
        resultantMoment += moment

    CoMMoment = beamMass * 9.81 * CoMDistance #calculate moment using physics equation

    resultantMoment += CoMMoment
    rotationSpeed = round(resultantMoment/1000,4)#find a rotations speed that is proportional to the resultant moment
    return resultantMoment, rotationSpeed


def rotate(rotSpeed, angle, blockSurface, blockSurfaceRect, leftBeamEdgeOnBs, rightBeamEdgeOnBs, supportsHeight):
    angle = (angle + rotSpeed)%360 #increment the angle of the surface by the rotation speed
    #lines 356-370: VALIDATION range check to ensure the surface stops rotating once it hits the ground
    beamToLeftOfPiv = (blockSurfaceRect.width//2) - leftBeamEdgeOnBs #work out the length of beam either side of pivot
    beamToRightOfPiv = rightBeamEdgeOnBs - (blockSurfaceRect.width//2)
    if supportsHeight/beamToLeftOfPiv >1 or supportsHeight/beamToLeftOfPiv <-1:
        anticlockLimit = 15
    else:
        anticlockLimit = math.degrees(math.asin(supportsHeight/beamToLeftOfPiv))#use trigonometry to work out the angle\
        #to ground either clockwise or anticlockwise
    if supportsHeight/beamToRightOfPiv >1 or supportsHeight/beamToRightOfPiv <-1:
        clockLimit = 345
    else:
        clockLimit = 360 - math.degrees(math.asin(supportsHeight/beamToRightOfPiv))
    if rotSpeed > 0 and angle > anticlockLimit: #if angle gets higher than relavant limits, set it to limit
        angle = anticlockLimit
    elif rotSpeed<0 and angle < clockLimit:
        angle = clockLimit
    rotatedSurface = pygame.transform.rotate(blockSurface, angle)#rotate the surface by angle
    rotatedRect = rotatedSurface.get_rect()
    rotatedRect.center = blockSurfaceRect.center#centre new surface so that rotation is around a constant centre
    return angle, rotatedSurface, rotatedRect#return surfaces to be blitted to screen and used in next rotation

    
def sortLevelLine(levelLine, supportsRect):
    if levelLine == True: #if user has chosen markers to be on
        lineColor = (255, 50, 50)#make line color red so markers are visable
    else:
        lineColor = backgroundBlue #make line color background color so markers are not visible
    pygame.draw.line(screen, lineColor, (supportsRect.x-100, window_Height - supportsRect.height - groundHeight),\
                     (supportsRect.x,  window_Height - supportsRect.height- groundHeight),3) #draw firs marker\
                        #using the coordinates of the supports to work out the needed coordinates of the line
    #second marker:
    pygame.draw.line(screen, lineColor, (supportsRect.x + supportsRect.width,  \
                                         window_Height - supportsRect.height- groundHeight),\
                                         (supportsRect.x + supportsRect.width + 100 ,
                                          window_Height -supportsRect.height- groundHeight),3)
        

def selectionIndicator(currentSprite, blockSurfaceRect, color, pivot):
    if bool(currentSprite) == True: #if a sprite has been selected
            if currentSprite.sprite == pivot: #if it is the pivot
                currentRect = currentSprite.sprite.getRect()#get the current rect of the pivot
                point1 = (currentRect.x, currentRect.y+currentRect.height)#work out triangle coordinates
                point2 = (currentRect.x + currentRect.width, currentRect.y+currentRect.height)
                point3 = (currentRect.x + currentRect.width//2, currentRect.y)
                pygame.draw.polygon(screen, color, [point1, point2, point3], 5)#draw a white triangle around pivot
            else:
                rectRelToBs = currentSprite.sprite.getRect()#get the rect of the block relative to blockSurface
                #work out top left corner of rect relative to the SCREEN:
                topleft = (blockSurfaceRect.x +  rectRelToBs.x, blockSurfaceRect.y + rectRelToBs.y)
                #translate this into a rect:
                currentRect = pygame.Rect(topleft, (rectRelToBs.width, rectRelToBs.height))
                pygame.draw.rect(screen, color, currentRect, 3)#draw a white rectangle around block


def checkForExit(event, running, practiceMode): #short function to change the value of running if quit is pressed
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
        practiceMode = not practiceMode
    return running, practiceMode


def keyDownHandler(keyPressed, supportsOn, currentSprite, beamWidth, origBlockSurface, origBlockSurfaceRect,\
                   blocks, inblockSurface, blockSurfaceRect, leftBeamEdgeOnBs, rightBeamEdgeOnBs, distLblOn,\
                   massLblOn, levelLine, beamMass, CoMDistance, practiceMode, pivotGroup):
    pivot = pivotGroup.sprite #access the pivot object and assign to a variable
    blockSurface = inblockSurface #assign blockSurface to the same as the input parameter as we are not changing it
    blockSurfaeRect = blockSurfaceRect
    if keyPressed == pygame.K_LEFT: #user has pressed the left arrow
        if currentSprite.has(pivot): #if the current sprite is the pivot
            currentSprite.sprite.moveLeft(50, supportsOn, beamLeftEdgeX) #move pivot left
            currentPivotPos = currentSprite.sprite.getPivotPos() #update the coordinates of the pivot point
            pivotGroup.update() 
            #since pivot has moved, we next find a new blockSurface with dimensions such that the new pivot position is at its centre:
            blockSurface, blockSurfaceRect, leftBeamEdgeOnBs, rightBeamEdgeOnBs =\
                          findNewBlockSurface(origBlockSurface, origBlockSurfaceRect, currentPivotPos, beamWidth)
            for block in blocks: #iterate through all blocks on the system
                block.updateRect(leftBeamEdgeOnBs) #update their rects relative to this new blockSuface
                block.setDistance(blockSurfaceRect) #set the updated distance to the pivot
                block.updateDistLbl(distLblOn) #update the distance labels
                blocks.update()
            CoMDistance = updateBeamInfo(blockSurfaceRect, leftBeamEdgeOnBs, beamWidth, beamMass)#calculate the new\
            #distance from the centre of mass to the pivot
        elif len(currentSprite) != 0:#else if its a block
            blockSurface = currentSprite.sprite.moveLeft(50, supportsOn, leftBeamEdgeOnBs, inblockSurface)#move currently\
            #selected sprite left
            currentSprite.sprite.setDistance(blockSurfaceRect) #set the new distance to the pivot 
            currentSprite.sprite.updateDistLbl(distLblOn) #update the distance label
            blocks.update()
            
    elif keyPressed == pygame.K_RIGHT:#user has pressed the right arrow
        if currentSprite.has(pivot): #the following code is the right key equivilent of the left clause above
            currentSprite.sprite.moveRight(50, supportsOn, beamRightEdgeX)
            currentPivotPos = currentSprite.sprite.getPivotPos()
            blockSurface, blockSurfaceRect, leftBeamEdgeOnBs, rightBeamEdgeOnBs =\
                          findNewBlockSurface(origBlockSurface, origBlockSurfaceRect, currentPivotPos, beamWidth)
            for block in blocks:
                block.updateRect(leftBeamEdgeOnBs)
                block.setDistance(blockSurfaceRect)
                block.updateDistLbl(distLblOn)
                blocks.update()
            CoMDistance = updateBeamInfo(blockSurfaceRect, leftBeamEdgeOnBs, beamWidth, beamMass)
        elif len(currentSprite) != 0: #else if it's a block
            blockSurface = currentSprite.sprite.moveRight(50, supportsOn, rightBeamEdgeOnBs, inblockSurface)
            currentSprite.sprite.setDistance(blockSurfaceRect)
            currentSprite.sprite.updateDistLbl(distLblOn)
            blocks.update()
    
    elif keyPressed == pygame.K_UP: #the user has pressed the up arrow
        if currentSprite.has(pivot): #VALIDATION: if the selected object is the pivot, the up key input must be rejected
            pass
        elif len(currentSprite) != 0: #VALIDATION: if there is no selected object, this input must be rejected.
            blockSurface = currentSprite.sprite.bigger(5, supportsOn, blockSurface) #else access the currently selected block\
            #and increase its size
            currentSprite.sprite.updateMassLbl(massLblOn)#update the mass to reflect the new size
            currentSprite.sprite.updateDistLbl(distLblOn)#update the mass label
            
    elif keyPressed == pygame.K_DOWN: #this is the down key equivilent of the up key code above
        if currentSprite.has(pivot):
            pass
        elif len(currentSprite) != 0:
            blockSurface = currentSprite.sprite.smaller(5, supportsOn, blockSurface)
            currentSprite.sprite.updateMassLbl(massLblOn)
            currentSprite.sprite.updateDistLbl(distLblOn)
            
    elif keyPressed == pygame.K_RETURN and supportsOn == True and len(blocks)<40: #if enter pressed
        #VALIDATION used in if condition so that the input is rejected if the supports are not\
        #on, or the number of blocks on the system is already greater or equal to 40
        color = (random.randint(100,255), random.randint(100,255),random.randint(100,200))#random color
        newBlock = Block(color, 50,50, (blockSurfaceRect.width//2, blockSurfaceRect.height//2-beamHeight), leftBeamEdgeOnBs)#create block
        blocks.add(newBlock)#add the block to the group so it can be drawn onto the surface alter
        currentSprite.add(newBlock)

        
    elif keyPressed == pygame.K_BACKSPACE and supportsOn == True:#backspace is command to remove selected object
        if len(currentSprite) != 0 and currentSprite.has(pivot) == False: #VALIDATION: only allow deletion if a particular sprite is selected
            rectToCover = currentSprite.sprite.rect #work out the rect of the image that needs covering
            blockSurface.blit(background,rectToCover,rectToCover) #cover up the image
            currentSprite.sprite.kill()#remove this sprite from all groups
            
    elif keyPressed == pygame.K_s: #user has pressed s key
        if supportsOn == True: #change value of supportsOn boolean variable, to trigger the supports coming on/off
            supportsOn = False 
        else:
            supportsOn = True
            
    elif keyPressed == pygame.K_m: #user has pressed m key
        if massLblOn == True: #change value of massLblOn boolean variable, to trigger the mass labels coming on/off
            massLblOn = False
            for block in blocks:
                block.turnOffMassLbl()
        else:
            massLblOn = True
            for block in blocks:
                block.turnOnMassLbl()
                
    elif keyPressed == pygame.K_d: #user has pressed d key
        if distLblOn == True: #change value of distLblOn boolean variable, to trigger the distance labels coming on/off
            distLblOn = False
            for block in blocks:
                block.turnOffDistLbl()
        else:
            distLblOn = True
            for block in blocks:
                block.turnOnDistLbl()
                
    elif keyPressed == pygame.K_l: #user has pressed l key
        if levelLine == True: #change value of levelLine boolean variable, to trigger the levelLines coming on/off
            levelLine = False
        else:
            levelLine = True
        
    return blockSurface, blockSurfaceRect, blocks, leftBeamEdgeOnBs,\
           rightBeamEdgeOnBs, supportsOn, massLblOn, distLblOn, levelLine, CoMDistance, currentSprite,\
           practiceMode


def mouseDownHandler(pivot, pivotGroup, blocks, blockSurfaceRect, currentSprite):
    mousePos = pygame.mouse.get_pos()#get coordinates of where mouse was clicked
    mousePosRect = pygame.Rect(mousePos, (0,0))#convert these coordinates into rect form
    if pivotGroup.sprite.rect.contains(mousePosRect):#check if within the pivot rect
        currentSprite.add(pivot)#if so, make pivot the current sprite
    else: 
        for block in blocks:  #check each block on the system
            XRelToScreen = blockSurfaceRect.x + block.rect.x #find coordinates relative to screen\
            #rather than blockSurface
            YRelToScreen = blockSurfaceRect.y + block.rect.y
            rectRelToScreen = pygame.Rect(XRelToScreen, YRelToScreen, block.rect.width, block.rect.height)
            if rectRelToScreen.contains(mousePosRect): #if mouse was clicked within this block's rect 
                currentSprite.add(block)#make this block the current sprite
                break #no need to keep looking
    return currentSprite #return the current sprite



def randomDistance(block, step, blockSurface, blockSurfaceRect):
    leftOrRight = random.randint(0,1) #randomly decide whether to move block left or right
    numMoves = random.randint(0,6) #randomly decide the number of moves in the decided direction
    if leftOrRight == 0:
        for i in range(numMoves):
            block.moveLeft(step, True, 0, blockSurface)#move the block appropriately
    else:
        for i in range(numMoves):
            block.moveRight(step, True, blockSurfaceRect.width, blockSurface)
    block.setDistance(blockSurfaceRect)#update distance from pivot
    block.updateDistLbl(True)#update distance label
    

def randomSize(block, step, blockSurface):
    biggerOrSmaller = random.randint(0,1)#randomly decide to go bigger or smaller
    changeInSize = random.randint(0,12)#decide random number of size increases/decreases
    if biggerOrSmaller == 0:
        for i in range(changeInSize):
            block.bigger(step, True, blockSurface)#change size of block appropriately
    else:
        for i in range(changeInSize):
            block.smaller(step, True, blockSurface)
    block.updateMassLbl(True)#update mass label
    block.updateDistLbl(True)#update distance label
    

def randomPivotPos(pivot, step, beamLeftEdgeX, beamRightEdgeX, pivotGroup):
    pivotLeftOrRight = random.randint(0,1)#randomly decide whether to move left or right
    numPivotMoves = random.randint(1,3)#random number of pivot moves
    if pivotLeftOrRight == 0:
        for i in range(numPivotMoves):
            pivot.moveLeft(step, True, beamLeftEdgeX)#move pivot appropriately
    else:
        for i in range(numPivotMoves):
            pivot.moveRight(step, True, beamRightEdgeX)
    pivotGroup.update()#update the pivot group
    

def generateRandomSystem(origBlockSurface, origBlockSurfaceRect, beamLeftEdgeX, beamRightEdgeX, beamWidth, beamMass, beamHeight, supportsHeight, initialPivotPos):
    pivotGroup = pygame.sprite.GroupSingle()
    blocks = pygame.sprite.Group()#generate blocks group
    numBlocks = random.randint(1,3)#decide a random number of blocks between 1-3
    for i in range(numBlocks): #generate the correct number of blocks, and set their paramters randomly using\
        #the procedures defined:
        color = (random.randint(100,255), random.randint(100,255),random.randint(100,200))#random color
        #create new instance of Block:
        newBlock = Block(color, 100,100, (origBlockSurfaceRect.width//2, origBlockSurfaceRect.height//2-beamHeight), 0)
        blocks.add(newBlock)
        randomDistance(newBlock, 50, origBlockSurface.copy(), origBlockSurfaceRect.copy())#randomly set the position on the beam
        blocks.update()
        randomSize(newBlock, 5, origBlockSurface.copy()) #randomly set the block's size
        blocks.update()

    
    pivot = Pivot((255, 147, 5), 100, supportsHeight, initialPivotPos)#create instance of Pivot
    pivotGroup = pygame.sprite.GroupSingle()#create the pivot group to control the pivot
    pivotGroup.add(pivot)
    randomPivotPos(pivot, 50, beamLeftEdgeX, beamRightEdgeX, pivotGroup)#randomly set pivot position
    pivotPos = pivot.getPivotPos()
    #find the new blockSurface based on the new pivot position, as to keep centre of blockSurface at the pivotPos:
    blockSurface, blockSurfaceRect, leftBeamEdgeOnBs, rightBeamEdgeOnBs =\
                          findNewBlockSurface(origBlockSurface, origBlockSurfaceRect, pivotPos, beamWidth)    
    for block in blocks: #update all block rects and relevant attribures based on new pivot position
        block.updateRect(leftBeamEdgeOnBs)
        block.setDistance(blockSurfaceRect)
        block.updateDistLbl(distLblOn)
        blocks.update()
    CoMDistance = updateBeamInfo(blockSurfaceRect, leftBeamEdgeOnBs, beamWidth, beamMass)#find new CoM distance

    
    #return all variables required for later use:
    return blockSurface, blockSurfaceRect, leftBeamEdgeOnBs, rightBeamEdgeOnBs, pivotGroup, blocks, CoMDistance



def checkValidSetUp(resultantMoment, maxLeft, maxRight):
    noGravityResMoment = resultantMoment / 9.81 #divide by gravitational constant to get the resultant moment\
    #just in terms of mass and distance
    validSolutions = [] #two dimensional array which will hold all possible distance-mass pairs where a live\
    #block could be placed to balance the system
    if resultantMoment < 0: #then system is tippinf clockwise, so liveBlock needs to be left of pivot to balance
        for i in range(1,maxLeft): #iterate through all possible positions liveBlock could be, to the left of pivot
            dist = i /2
            massNeeded = abs(noGravityResMoment/dist)#find the mass that would be needed to balance the system,\
            #if the liveBlock were to be placed at this distance
            if massNeeded*2 == int(massNeeded*2) and massNeeded<=20 and massNeeded >= 4: #if this mass is\
            #a valid mass that can be created through the increments that can be made with arrow keys...
                validSolutions.append([dist,massNeeded])#...this is a valid pair of solutions so add to array
    if resultantMoment > 0: #repeat the same process as above, but for the case where liveBlock needs to\
    #be to the right of the pivot
        for i in range (1, maxRight):
            dist = i /2
            massNeeded = abs(noGravityResMoment/dist)
            if massNeeded*2 == int(massNeeded*2) and massNeeded<=20 and massNeeded >= 4:
                validSolutions.append([-dist,massNeeded])
    return validSolutions #return all valid solutions


def findMaxLeft(blockSurfaceRect, leftBeamEdgeOnBs, step):
    #work out the literal pixel distance between the pivot point and the left edge of beam:
    pixelDistance = blockSurfaceRect.width//2 - leftBeamEdgeOnBs
    #work out the max number of arrow key increments can be applied before block would reach end of beam
    numSteps = (pixelDistance // step) -1
    return numSteps


def findMaxRight(blockSurfaceRect, rightBeamEdgeOnBs, step):
    #work out the literal pixel distance between the pivot point and the right edge of beam:
    pixelDistance = rightBeamEdgeOnBs - blockSurfaceRect.width//2
    #work out the max number of arrow key increments can be applied before block would reach end of beam:
    numSteps = (pixelDistance // step)-1
    return numSteps


def setUpLiveBlock(blockSurfaceRect, blockSurface, beamHeight, validSolutions, rightBeamEdgeOnBs,leftBeamEdgeOnBs):
    #create new instance of Block, in white, to signify that this is the live block.
    liveBlock = Block(white, 40,40, (blockSurfaceRect.width//2, blockSurfaceRect.height//2-beamHeight),leftBeamEdgeOnBs)
    chosenSolution = random.randint(0,len(validSolutions)-1)#randomly choose a solution FROM THE SET OF VALID\
    #SOLUTIONS for this system 
    solutionDistance = validSolutions[chosenSolution][0]
    solutionMass = validSolutions[chosenSolution][1]
    canEditDistOrMass = random.randint(0,1)#randomly decide whether to fix its distance or mass
    if canEditDistOrMass == 0: #then fix size, and allow the user to edit the distance
        desiredBlockWidth = solutionMass * 10 #fix size to the solutionMass, as we know there is a valid\
        #distance that goes with this which the user can find
        liveBlock.bigger(desiredBlockWidth - 40, True, blockSurface)#visably change the size
        liveBlock.updateMassLbl(True)#update mass label
        liveBlock.updateDistLbl(True)#update distance label
    else:#then fix distance, and allow user to calulate the corresponding mass needed
        if solutionDistance <0: #need to move block to the right
            liveBlock.moveRight(abs(solutionDistance*100), True, rightBeamEdgeOnBs, blockSurface)
        else:
            liveBlock.moveLeft(abs(solutionDistance*100), True, leftBeamEdgeOnBs, blockSurface)
        liveBlock.setDistance(blockSurfaceRect)#update distance attribute
        liveBlock.updateDistLbl(True)#update distance label
    liveBlockRect = liveBlock.getRect()
    return liveBlock, liveBlockRect, canEditDistOrMass, validSolutions[chosenSolution]


def PMkeyDownHandler(keyPressed, blockSurface, blockSurfaceRect, leftBeamEdgeOnBs,
                     rightBeamEdgeOnBs, canEditDistOrMass, liveBlock, blocks, practiceMode):
    newBlockSurface = blockSurface
    supportsOn = True
    if canEditDistOrMass == 0: #distance can be changed in this question
        if keyPressed == pygame.K_LEFT: #move liveBlock left using the moveLeft method
            newBlockSurface = liveBlock.moveLeft(50, True, leftBeamEdgeOnBs, blockSurface)
        elif keyPressed == pygame.K_RIGHT: #move liveBlock right using the moveRight method
            newBlockSurface = liveBlock.moveRight(50, True, rightBeamEdgeOnBs, blockSurface)
        liveBlock.setDistance(blockSurfaceRect) #set the new distance from the pivot
        liveBlock.updateDistLbl(True) #update the distance labels
        
    elif canEditDistOrMass ==1: #mass can be changed in this question
        if keyPressed == pygame.K_UP: #make liveBlock bigger using bigger method
            newBlockSurface = liveBlock.bigger(5, True, blockSurface)
        elif keyPressed == pygame.K_DOWN:#make liveBlock smaller using smaller method
            newBlockSurface = liveBlock.smaller(5, True, blockSurface)
        liveBlock.updateMassLbl(True)#update labels
        liveBlock.updateDistLbl(True)
    blocks.update()
    
    if keyPressed == pygame.K_RETURN: #if the enter key is pressed
        supportsOn = False #turn the supports off. This signifies when the user has completed their input\
        #and wants to check if they have correctly balanced the system.
    return newBlockSurface, liveBlock, blocks, supportsOn, practiceMode


def checkAnswer(blocks, beamMass, CoMDistance, background, blockSurface, blockSurfaceRect,
                leftBeamEdgeOnBs, rightBeamEdgeOnBs, supportsHeight, pivotGroup, supportsRect):
    angle = 0 #set original angle of rotation as 0 because blockSurface is currently level
    prevAngle = 999 #set prevAngle as a dummy value
    newResultantMoment, rotationSpeed = resultantMoment(blocks, beamMass, CoMDistance)#calculate rotationSpeed
    print(rotationSpeed)
    if abs(rotationSpeed) < 0.04 and rotationSpeed < 0: #if the rotation speed is too slow, set it to a minimum
        rotationSpeed = -0.04
    if abs(rotationSpeed) < 0.04 and rotationSpeed > 0:
        rotationSpeed = 0.04
    while angle != prevAngle: #keep rotating the system until the previous angle is the same as the new one\
        #meaning there is no more rotating to be done
        prevAngle = angle
        screen.blit(background, [0,0])#cover up old images
        #use rotate function coded earlier to rotate blockSurface:
        angle, rotatedSurface, rotatedSurfaceRect = rotate(rotationSpeed*1.2, angle, blockSurface, blockSurfaceRect, leftBeamEdgeOnBs, rightBeamEdgeOnBs, supportsHeight)
        screen.blit(rotatedSurface, rotatedSurfaceRect)
        screen.blit(PMinstructions, [0,0])
        screen.blit(beamInfoSurface, PMinstructions.get_rect().bottomleft)
        pivotGroup.draw(screen)
        sortLevelLine(True, supportsRect)
        pygame.display.update()
    if angle == 0: #if after the system has finished moving, the angle is 0, it is correctly balanced
        correct = True #user has got the answer correct
    else:
        correct = False
    return correct


def incrementScore(score, numQsAnswered, correct):
    if correct == True: #if the user answered correctly
        score +=1 #increment score by 1
    scoreString = ' Score: ' + str(score) + '/' + str(numQsAnswered)#create the string that displays new score
    scoreBox = bigFont.render(scoreString, True, (255,0,0), white)#create a text surface with the string on
    scoreBoxSurf = pygame.Surface((150,50))
    scoreBoxSurf.fill((255,255,255))
    scoreBoxSurfRect = scoreBoxSurf.get_rect()
    scoreBoxSurfRect.topright = (((PMinstructions.get_rect()).bottomright)[0],((PMinstructions.get_rect()).bottomright)[1]+50) #position under other panels
    scoreBoxSurf.blit(scoreBox, (0,15))
    return score, scoreBoxSurf, scoreBoxSurfRect #return all updated values to the main program


def calculateCorrection(solution, canEditDistOrMass, correct, beamInfoSurfaceRect):
    commentSurf = pygame.Surface((window_Width,25))#create a surface to blit the comments onto
    commentSurfRect = commentSurf.get_rect()
    commentSurfRect.topleft = beamInfoSurfaceRect.bottomleft #position it under the beam info panel
    if correct == True: #if they answered correctly
        commentSurf.fill((198, 247, 192)) #fill the comments surface in green
        comment = 'Well done! You have correctly balanced the system.' #create the string to be displayed
    else: #they answered wrong, so find the correction
        commentSurf.fill((249,164,164))#fill the comments surface in red
        answerDistance = solution[0]#find what the correct distance and mass should havbe been
        answerMass = solution[1]
        if answerDistance >= 0: #then the block needed to be put left of the pivot
            sideOfPivot = 'left'
            momentDirection = 'anticlockwise' #block needed an anticlockwise moment
        else: #block needed to be put right of the pivot
            sideOfPivot = 'right'
            momentDirection = 'clockwise'
        
        answerMoment = str(abs(round(answerDistance * answerMass *9.81,1))) + 'Nm ' #calculate the moment that needed to be\
        #created by the block to balance the system
            
        if canEditDistOrMass == 0: #then the user was controlling distance so the comment say what the correct\
        #distance should have been:
            comment = 'Not quite. The block needed to be placed '+ str(abs(answerDistance))+ 'm to the ' +\
                      sideOfPivot + ' of the pivot, to create a moment of ' + answerMoment + momentDirection +\
                      ' to balance the system.'
        else:#then the user was controlling mass, so comment says what the correct mass should have been
            comment = 'Not quite. The block needed to have a mass of '+ str(answerMass)+ 'kg, to create a moment of ' +\
                      answerMoment + momentDirection + ' to balance the system.  '
            
    commentText = smallFont.render(comment, True, (0,0,0)) #create a text surface for the comment
    commentSurf.blit(commentText, (5,5))#blit the text to the comment panel
    return commentSurf, commentSurfRect #return the comment panel so it can be blit to the screen

        
def highlightLiveBlock(liveBlock, blockSurfaceRect):
    LBrectRelToBs = liveBlock.getRect()#get the rect of the liveBlock relative to blockSurface
    #work out top left corner of rect relative to the SCREEN:
    LBtopleft = (blockSurfaceRect.x +  LBrectRelToBs.x, blockSurfaceRect.y + LBrectRelToBs.y)
    #translate this into a rect:
    LBcurrentRect = pygame.Rect(LBtopleft, (LBrectRelToBs.width, LBrectRelToBs.height))
    pygame.draw.rect(screen, (255,0,0), LBcurrentRect, 1)#draw a red rectangle around liveBlock
   
        
def waitForSpace(running, practiceMode):
    while True:
        for event in pygame.event.get(): 
            running,practiceMode = checkForExit(event, running, practiceMode)
            if running == False:
                return running, practiceMode
                break #if the user exits the programvor practice mode we need to stop waiting
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                return running, practiceMode
                break #once the user presses space, we break the while loop to stop waiting
            

def simMode(running, practiceMode, origBlockSurface, origBlockSurfaceRect, beamWidth,
                  leftBeamEdgeOnBs, rightBeamEdgeOnBs, distLblOn, massLblOn, levelLine,beamMass,
                  CoMDistance, background, supportsHeight, SMinstructions, beamInfoSurface, supportsRect): 
    #set up local variables only needed in simulator mode:
    blockSurface =origBlockSurface.copy() #use origBlockSurface so that a 'fresh slate' is started when SM starts
    blockSurfaceRect = origBlockSurfaceRect.copy()
    blocks = pygame.sprite.Group() #initialise the blocks group
    currentSprite = pygame.sprite.GroupSingle() #initialise the current sprite group
    pivot = Pivot((255, 147, 5), 100, supportsHeight, initialPivotPos)
    pivotGroup = pygame.sprite.GroupSingle()
    pivotGroup.add(pivot)
    supportsOn = True
    angle = 0
    while practiceMode == False and running == True: #while the user has not quit Simulator Mode or the program
        try: #using try and except to stop the program crashing if there is an error
            for event in pygame.event.get(): #check pygame event queue
                running, practiceMode = checkForExit(event, running, practiceMode)#check if quit has been pressed\
                #or modes have been switched
                if event.type == pygame.KEYDOWN: #if a keyboard command has been pressed, run he keydown handler
                    blockSurface, blockSurfaceRect, blocks,leftBeamEdgeOnBs, rightBeamEdgeOnBs, \
                    supportsOn, massLblOn, distLblOn, levelLine, CoMDistance, currentSprite, \
                    practiceMode = keyDownHandler(event.key, supportsOn, currentSprite, beamWidth,
                                                  origBlockSurface, origBlockSurfaceRect, blocks,
                                                  blockSurface, blockSurfaceRect, leftBeamEdgeOnBs,
                                                  rightBeamEdgeOnBs, distLblOn, massLblOn, levelLine,beamMass,CoMDistance,
                                                  practiceMode, pivotGroup)
                elif event.type == pygame.MOUSEBUTTONDOWN: #if the mouse button has been pressed, run the mouse down handler
                    currentSprite = mouseDownHandler(pivot, pivotGroup, blocks, blockSurfaceRect, currentSprite)

            blocks.update()
            blocks.draw(blockSurface)#blocks are drawn to blockSurface

            resultMoment, rotationSpeed = resultantMoment(blocks, beamMass, CoMDistance) #find resultant moment of the system
            if abs(rotationSpeed) < 0.2: #if the rotation speed is too small, set it to a minimum
                rotationSpeed = rotationSpeed * 2

            screen.blit(background, [0,0])#blit the background to the screen to cover any old systems
            
            

            if supportsOn == False: #if the supports are NOT on, then rotate the system:
                angle, rotatedSurface, rotatedSurfaceRect = rotate(rotationSpeed, angle, blockSurface, blockSurfaceRect,
                                                                   leftBeamEdgeOnBs, rightBeamEdgeOnBs, supportsHeight)
                screen.blit(rotatedSurface, rotatedSurfaceRect) #blit the rotated system to the screen
            
            else: #else if the supports ARE on
                screen.blit(blockSurface, blockSurfaceRect)#a level blockSurface is drawn to screen
                screen.blit(supportsSurf, supportsRect)#supports are drawn to screen.
                angle = 0 #the angle of the system is reset to zero
                selectionIndicator(currentSprite, blockSurfaceRect, white, pivot)#indicate which block is currently selected

            screen.blit(SMinstructions, [0,0]) #blit the instruction panel to the screen
            screen.blit(beamInfoSurface, SMinstructions.get_rect().bottomleft) #blit the beam info to the screen

            pivotGroup.update() #pivot is updated and drawn to screen
            pivotGroup.draw(screen)
            sortLevelLine(levelLine, supportsRect) #level line is drawn to the screen if it is on

            
        except: #if an error occurs
            for event in pygame.event.get():
                running, practiceMode = checkForExit(event, running, practiceMode) #still allow the user to quit the program
            screen.blit(background, (0,0)) 
            screen.blit(blockSurface, blockSurfaceRect)
            screen.blit(supportsSurf, supportsRect)
            screen.blit(errorSurf, (200,400))#display the error message to the user
            logging.exception('Error was:')#show diagnostics of error that caused the exception to aid MAINTENANCE
        

        pygame.display.update()#update the screen at the end of every iteration
    return running, practiceMode #once the while loop has been exited, one of these values has changed so they\
    #need to be returned.


def pracMode(running, practiceMode, background, origBlockSurface, origBlockSurfaceRect, beamLeftEdgeX,
                 beamRightEdgeX,beamWidth, beamMass, beamHeight, supportsHeight, initialPivotPos,
                 PMinstructions, beamInfoSurface, supportsSurf, supportsRect, beamInfoSurfaceRect):
    #set up the local variables and surfaces only needed in pracMode:
    blocks = pygame.sprite.Group()
    numQsAnswered = 0
    score, scoreBox, scoreBoxRect = incrementScore(0,numQsAnswered, False)
    while practiceMode == True and running == True:#while the mode has not been switched and the program not quit
        try:
            for event in pygame.event.get(): #check pygame event queue for mode switch or quit
                running, practiceMode = checkForExit(event, running, practiceMode)#if quit pressed, running is set to false
            validSolutions = []#initialise this array
            screen.blit(background, [0,0])#reset the screen
            
            while len(validSolutions) == 0: #keep generating a new system until one is found that has valid\
            #solutions for liveBlock's position and size
                blockSurface, blockSurfaceRect, leftBeamEdgeOnBs, rightBeamEdgeOnBs, pivotGroup, blocks, CoMDistance =\
                              generateRandomSystem(origBlockSurface, origBlockSurfaceRect, beamLeftEdgeX, beamRightEdgeX,
                                                   beamWidth,beamMass, beamHeight, supportsHeight, initialPivotPos)
                #find max moves left and right possible, as needed to check if there are valid solutions
                maxLeft = findMaxLeft(blockSurfaceRect, leftBeamEdgeOnBs, 50)
                maxRight = findMaxRight(blockSurfaceRect, rightBeamEdgeOnBs, 50)
                resultMoment, rotationSpeed = resultantMoment(blocks, beamMass, CoMDistance)
                validSolutions = checkValidSetUp(resultMoment, maxLeft, maxRight)
            #once there is a system with valid solutions, liveBlock can be generated:
            liveBlock, liveBlockRect, canEditDistOrMass, solution = setUpLiveBlock(blockSurfaceRect, blockSurface,
                                                                                   beamHeight, validSolutions,
                                                                                   rightBeamEdgeOnBs,leftBeamEdgeOnBs)
    
            screen.blit(PMinstructions, [0,0]) #blit instructions to screen
            screen.blit(beamInfoSurface, PMinstructions.get_rect().bottomleft)#blit beam info to screen
            screen.blit(scoreBox, scoreBoxRect)#blit score box to screen

            blocks.add(liveBlock)#draw all the blocks onto blockSurface in their randomly set positions
            blocks.draw(blockSurface)#draw all the blocks onto blockSurface in their randomly set positions
            screen.blit(blockSurface, blockSurfaceRect)#blockSurface is drawn to screen
            screen.blit(supportsSurf, supportsRect)#supports are drawn to screen
            pivotGroup.draw(screen)#pivot is drawn to screen
            highlightLiveBlock(liveBlock, blockSurfaceRect)#liveBlock is highlighted
            
            pygame.display.update()#update the screen to reflect changes

            #initialise the varaibles needed for the rotation:
            supportsOn = True
            angle = 0
            prevAngle = 999
            
            #while the mode is still running, AND the supports are still on, use the key handler to allow user inputs
            while supportsOn == True and running == True and practiceMode ==True:
                for event in pygame.event.get(): #check pygame event queue
                    running, practiceMode = checkForExit(event, running, practiceMode)#check no quitting
                    if event.type ==pygame.KEYDOWN:
                        blockSurface, liveBlock, blocks, supportsOn, practiceMode =\
                                      PMkeyDownHandler(event.key, blockSurface, blockSurfaceRect, leftBeamEdgeOnBs,
                                                       rightBeamEdgeOnBs, canEditDistOrMass, liveBlock, blocks,
                                                       practiceMode)
                        blocks.draw(blockSurface)#redraw the updated blocks
                        screen.blit(blockSurface, blockSurfaceRect)#blockSurface is drawn to screen
                        screen.blit(supportsSurf, supportsRect)#supports are drawn back on
                        pivotGroup.draw(screen)#pivot is drawn back on
                        highlightLiveBlock(liveBlock, blockSurfaceRect)#live block is highlighted in new position
                        pygame.display.update()#screen is updated
                        
            if running == True and practiceMode == True:#don't bother running this code at all if mode has been quit
                correct = checkAnswer(blocks, beamMass, CoMDistance, background, blockSurface, blockSurfaceRect,
                                      leftBeamEdgeOnBs, rightBeamEdgeOnBs, supportsHeight, pivotGroup, supportsRect)

                numQsAnswered +=1#increment the number of questions answered

                #update and draw score box to screen:
                score, scoreBox, scoreBoxRect = incrementScore(score, numQsAnswered, correct)
                screen.blit(scoreBox, scoreBoxRect)

                #find feedback comment and draw to screen:
                commentSurf, commentSurfRect = calculateCorrection(solution, canEditDistOrMass, correct, beamInfoSurfaceRect)
                screen.blit(commentSurf, commentSurfRect)
                
                pygame.display.flip()#update screen
                running, practiceMode = waitForSpace(running, practiceMode)#wait to generate next question until\
                #user presses space

        except:
            for event in pygame.event.get():
                running, practiceMode = checkForExit(event, running, practiceMode)
            screen.blit(background, (0,0))
            screen.blit(errorSurf, (200,400)) #display error message
            logging.exception('Error was:')#show diagnostics for error that caused the exception
            pygame.display.update()
    return running, practiceMode



#MAIN PROGRAM
#-------------------------------------------

prevRect = origBlockSurfaceRect.copy()
screen.blit(background, (0,0)) #background is drawn on screen



while running == True: #while the user has not quit the program
    if practiceMode == False: #if in Simulator Mode, run Simulator Mode
        running, practiceMode = simMode(running, practiceMode, origBlockSurface, origBlockSurfaceRect,\
                                              beamWidth, leftBeamEdgeOnBs, rightBeamEdgeOnBs, distLblOn, massLblOn, levelLine, beamMass, CoMDistance,\
                                              background,supportsHeight, SMinstructions, beamInfoSurface, supportsRect)
    if practiceMode == True: #if in Practice Mode, run Practice Mode
        running, practiceMode = pracMode(running, practiceMode, background, origBlockSurface.copy(), origBlockSurfaceRect.copy(),
                                             beamLeftEdgeX,beamRightEdgeX,beamWidth, beamMass, beamHeight, supportsHeight,
                                             initialPivotPos, PMinstructions, beamInfoSurface, supportsSurf, supportsRect,
                                             beamInfoSurfaceRect)
        
pygame.quit() #once while loop has ended, pygame quits the program



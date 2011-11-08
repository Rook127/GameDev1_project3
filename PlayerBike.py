#player bike class

#importing all the panda stuff since I'm not sure which ones i need

import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import *    #basic Panda modules
from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import *  #for compound intervals
from direct.task import Task         #for update fuctions
import sys, math, random
from Bullet import Bullet
from weapon1 import weapon1
from weapon2 import weapon2
from weapon3 import weapon3

class PlayerBike(DirectObject):
    def __init__(self, cTrav):
        #create speed vars
        self.max_vel = 50
        self.accel = 2
        self.current_vel = 0
        self.cTrav = cTrav
        self.weapon = 2
        
        self.tempHeading = 0
        self.temp_vel = 0
        self.count = 0
        self.first_time = False
        self.jump = False
        self.dz = 0
        
        
        #create empty list for bullets and a task for updating the positions
        self.bullet = Bullet(cTrav)
        self.spreadshot = weapon1(cTrav)
        self.explode = weapon2(cTrav)
        self.wallshot = weapon3(cTrav)
        
        taskMgr.add(self.bullet.update, "bulletTask")
        taskMgr.add(self.spreadshot.update, "bulletTask")
        taskMgr.add(self.explode.update, "bulletTask")
        taskMgr.add(self.wallshot.update, "bulletTask")
    
        
        #load the bike actor and parent it to a physics node
        self.bike = Actor("motorcycle2.egg", {"move":"bike-move", "shoot":"bike-shoot"})
        #self.bike = loader.loadModel('motorcycle2.egg')
        #self.bike.setScale(.5)
        #self.bike.setH(180)
        self.bike.reparentTo(render)
        
        
        """#load the gun actors
        self.gun1 = Actor("temp_gun.egg", {"shoot":"gun-shoot"})
        self.gun1.reparentTo(self.bike)
        self.gun1.setPos(-.5, 0, .5)
        self.gun1.setH(180)
        
        self.gun2 = Actor("temp_gun.egg", {"shoot":"gun-shoot"})
        self.gun2.reparentTo(self.bike)
        self.gun2.setPos(.46, 0, 1)
        self.gun2.setH(180)
        self.gun2.setR(180)
        
        #load the headlight models
        self.headlight1 = loader.loadModel("temp_light.egg")
        self.headlight1.reparentTo(self.bike)
        self.headlight1.setPos(.3, .55, .4)
        self.headlight1.setScale(.75)
        
        #load the headlight models
        self.headlight2 = loader.loadModel("temp_light.egg")
        self.headlight2.reparentTo(self.bike)
        self.headlight2.setPos(-.3, .55, .4)
        self.headlight2.setScale(.75)"""
        
        #setup a move task for the bike
        taskMgr.add(self.move, "moveTask")
        self.prevTime = 0
        self.isMoving = False
        
        #setup a shoot task for the bike
        taskMgr.add(self.shoot, "shootTask")
        self.shotClock = 25
        # for shooting anim self.isShooting = False
        
        #setup a moving dictionary
        self.moveMap = {"left":0, "right":0, "forward":0}
        
        #setup a shoot check
        self.shootCheck = 0
        

        #setup a wall collision check
        self.wallCheck = False
        
        #pusher collision sphere
        collisionPusher = CollisionHandlerPusher()
        collisionPusher.setInPattern("p_bike-%in")
        cPushSphere = CollisionSphere((0,0,1),4.5)
        
        cNode = CollisionNode("p_bike_push")
        cNode.addSolid(cPushSphere)
        cNode.setIntoCollideMask(0x10)
        cNode.setFromCollideMask(0x1)
        cNodePath = self.bike.attachNewNode(cNode)
        
        #cNodePath.show()
        
        collisionPusher.addCollider(cNodePath, self.bike)
        self.cTrav.addCollider(cNodePath, collisionPusher)
        
        #collision rays for faux-gravity
        #front wheel
        lifter = CollisionHandlerFloor()
        lifter.setMaxVelocity(1)
        
        cRay1 = CollisionRay(0, 3, 1, 0, 0, -1)
        cRayNode1 = CollisionNode('playerRay')
        cRayNode1.addSolid(cRay1)
        cRayNode1.setIntoCollideMask(BitMask32.allOff())
        cRayNode1.setCollideMask(2)
        cRayNodePath1 = self.bike.attachNewNode(cRayNode1)
        cRayNodePath1.show()
         
        self.cTrav.addCollider(cRayNodePath1, lifter)
        lifter.addCollider(cRayNodePath1, self.bike)
        
        #setup and parent spotlights to the player
        self.spotlight = Spotlight("headlight")
        self.spotlight.setColor((1, 1, 1, 1))
        lens = PerspectiveLens()
        #can change size of cone
        lens.setFov(20)
        self.spotlight.setLens(lens)
        self.spotlight.setExponent(100)
        lightNode = self.bike.attachNewNode(self.spotlight)
        render.setLight(lightNode)
        
    def setDirection(self, key, value):
        #set the direction as on or off
        self.moveMap[key] = value
        
    def setShoot(self, value):
        
        self.shootCheck = value
        print("set shoot =", self.shootCheck)
    
    def shoot(self, task):
        #check if space bar is pressed
        if self.shootCheck:

            #Check which weapon is being used
            #standard weapon
            if self.weapon == 0:
                #check if able to shoot
                if self.shotClock >= 25:
                    #print("Shooting a bullet!")
                    self.bullet.createBullet(self.bike)
                    self.shotClock = 0
                else:
                    self.shotClock += 1
            #Weapon 1 - macinhe gun
            #Nothing is changed about the bullet itself, it simply changes the cool down time.
            elif self.weapon == 1:
                if self.shotClock >= 7:
                    #print("Shooting a bullet!")
                    self.bullet.createBullet(self.bike)
                    self.shotClock = 0
                else:
                    self.shotClock += 1    
            #Weapon 2 - Spreadshot/Shotgun
            elif self.weapon == 2:
                if self.shotClock >= 40:
                    #print("Shooting a bullet!")
                    self.spreadshot.createBullet(self.bike)
                    self.shotClock = 0
                else:
                    self.shotClock += 1 
            #Weapon 3 - explosion (Like spread but in every direction by 15 degree increments
            elif self.weapon == 3:
                if self.shotClock >= 250:
                    #print("Shooting a bullet!")
                    self.explode.createBullet(self.bike)
                    self.shotClock = 0
                else:
                    self.shotClock += 1 
            #Weapon 4 - Wall shot (Not sure how I feel about this one yet)
            elif self.weapon == 4:
                if self.shotClock >= 50:
                    #print("Shooting a bullet!")
                    self.wallshot.createBullet(self.bike)
                    self.shotClock = 0
                else:
                    self.shotClock += 1 

        else:
            self.shotClock += 1
        return Task.cont
        
    def move(self, task):
        elapsed = task.time - self.prevTime
        
        #keep track of all the bike's previous Pos and Hpr
        prevX = self.bike.getX()
        prevY = self.bike.getY()
        prevZ = self.bike.getZ()
        prevH = self.bike.getH()
        prevP = self.bike.getP()
        prevR = self.bike.getR()
        
        #check key map
        if self.moveMap['left']:
            self.bike.setH(self.bike.getH() + elapsed * 150)
        if self.moveMap['right']:
            self.bike.setH(self.bike.getH() - elapsed * 150)
        
        #check if at jump height
        if prevZ >= 4.8:
            #set jump check
            self.jump = True
            
            #check for when temp_vel needs to be increased instead of decreased
            if self.first_time == False:
                self.temp_vel -= 9.8
            if self.temp_vel <= 0 and self.first_time == False:
                self.first_time = True
                self.temp_vel += 9.8
            elif self.first_time == True:
                self.temp_vel += 9.8
                
            #make sure temp_vel doesn't increase too much
            if self.temp_vel > self.current_vel:
                self.temp_vel = self.current_vel
                
            #calculate dist for dy and dx normally, then do trig for dz
            dist = self.current_vel * elapsed
            angle = deg2Rad(self.bike.getH())
            dy = dist * -math.cos(angle)
            dx = dist * math.sin(angle)
            self.dz = math.sqrt((dy*dy)+(dx*dx))
            
            #debug prints
            """print('new')
            print('dy', dy)
            print('dx', dx)
            print('dz', dz)
            print('angle', angle)
            print('bike heading', self.bike.getH())
            print('bike x', self.bike.getX())
            print('bike y', self.bike.getY())
            print('temp_vel', self.temp_vel)"""
            
            #use a count to determine when to decrease or increase the bike's Z
            if self.count < 20:
                self.bike.setPos(self.bike.getX() - dx, self.bike.getY() - dy, self.bike.getZ() + self.dz)
            else:
                self.bike.setPos(self.bike.getX() - dx, self.bike.getY() - dy, self.bike.getZ() - self.dz)
            self.count += 1
            
        else:
            #reset counters used in jumping
            self.first_time = False
            self.count = 0
            
            #check keymap for forward motion
            #accelerate
            if self.moveMap['forward']:
                #print(prevZ)
                self.current_vel += self.accel
                self.temp_vel = self.current_vel
                if(self.current_vel > self.max_vel):
                    self.current_vel = self.max_vel
                dist = self.current_vel * elapsed
                angle = deg2Rad(self.bike.getH())
                dx = dist * math.sin(angle)
                dy = dist * -math.cos(angle)
                if self.jump == True:
                    self.bike.setPos(self.bike.getX() - dx, self.bike.getY() - dy, self.bike.getZ() - self.dz)
                    if self.bike.getZ() <= 0:
                        self.jump = False
                        self.bike.setZ(0)
                else:
                    self.bike.setPos(self.bike.getX() - dx, self.bike.getY() - dy, self.bike.getZ())
                
                
            else:
                #decelerate
                self.current_vel -= 20 * self.accel * elapsed
                self.temp_vel = self.current_vel
                if(self.current_vel < 0):
                    self.current_vel = 0
                dist = self.current_vel * elapsed
                angle = deg2Rad(self.bike.getH())
                dx = dist * math.sin(angle)
                dy = dist * -math.cos(angle)
                if self.jump == True:
                    self.bike.setPos(self.bike.getX() - dx, self.bike.getY() - dy, self.bike.getZ() - self.dz)
                    if self.bike.getZ() <= 0:
                        self.jump = False
                        self.bike.setZ(0)
                else:
                    self.bike.setPos(self.bike.getX() - dx, self.bike.getY() - dy, self.bike.getZ())
        
        #attempt to change pitch
        if self.bike.getZ() != prevZ:
            ang = math.atan2(self.bike.getY(), self.bike.getZ())
            self.bike.setP(ang)
            
        if self.moveMap['left'] or self.moveMap['right'] or self.moveMap['forward']:
            #print('heading', self.bike.getH())
            if self.isMoving == False:
                self.isMoving = True
                #self.bike.loop("walk")
        else:
            if self.isMoving:
                self.isMoving = False
                #self.bike.stop()
                #self.bike.pose("walk", 4)
        
        self.prevTime = task.time
        #print(self.current_vel)
        return Task.cont
        
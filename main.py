#main function

import direct.directbase.DirectStart #starts Panda
from pandac.PandaModules import *    #basic Panda modules
from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import *  #for compound intervals
from direct.task import Task         #for update fuctions
from panda3d.ai import *
from panda3d.core import *
from panda3d.physics import *
import sys, math, random

#our modules
from PlayerBike import PlayerBike
from Terrain import Terrain
from EnemyBike import EnemyBike

class World(DirectObject):
    def __init__(self):
        #load physics
        base.enableParticles()
        
        #add gravity
        #gravityFN = ForceNode('world-forces')
        #gravityFNP = render.attachNewNode(gravityFN)
        #gravityForce = LinearVectorForce(0,0,-9.8)
        #gravityFN.addForce(gravityForce)
        #base.physicsMgr.addLinearForce(gravityForce)
        
        #create a traverser
        base.cTrav = CollisionTraverser()
        
        self.cevent = CollisionHandlerEvent()
        
        self.cevent.addInPattern('into-%in')
        self.cevent.addOutPattern('outof-%in')
        
        #load all the models
        self.w_terrain = Terrain()
        self.p_bike = PlayerBike(base.cTrav)
        
        #disable mouse
        base.disableMouse()
        
        #parent the camera to the player bike and offset the initial location
        camera.reparentTo(self.p_bike.bike)
        camera.setZ(7)
        camera.setP(-15)
        camera.setY(-15)
        
        #set up accept tasks
        #close the game
        self.accept("escape", sys.exit)
        
        #handle movement
        self.accept("arrow_up", self.p_bike.setDirection, ["forward", 1])
        self.accept("arrow_right", self.p_bike.setDirection, ["right", 1])
        self.accept("arrow_left", self.p_bike.setDirection, ["left", 1])
        self.accept("arrow_up-up", self.p_bike.setDirection, ["forward", 0])
        self.accept("arrow_right-up", self.p_bike.setDirection, ["right", 0])
        self.accept("arrow_left-up", self.p_bike.setDirection, ["left", 0])
        
        #handle shooting
        self.accept("space", self.p_bike.setShoot, [1])
        self.accept("space-up", self.p_bike.setShoot, [0])
        
        self.accept("p_bike-test", self.testCollision)
        self.accept("bullet-test", self.testCollision)
        
        #setup basic environment lighting
        self.ambientLight = AmbientLight("ambientLight")
        self.ambientLight.setColor((.25, .25, .25, 1))
        self.ambientLightNP = render.attachNewNode(self.ambientLight)
        render.setLight(self.ambientLightNP)
        render.setShaderAuto()
        
        self.initAI()
        self.e_bikes = [self.addEnemy()]
        self.e_bikes[0].AIbehaviors.pursue(self.p_bike.bike, 0.7)
    
    def testCollision(self, cEntry):
        """handles panda eating a smiley"""
        #remove from scene graph
        print("test")
        cEntry.getIntoNodePath().remove()
        
    def initAI(self):
        self.AIworld = AIWorld(render)
 
        #AI World update        
        taskMgr.add(self.AIUpdate,"AIUpdate")
    
    def AIUpdate(self, task):
        self.AIworld.update()
        for i in self.e_bikes:
            i.update()
            i.bike.setHpr(i.bike.getH(), 0, i.bike.getR())
        return Task.cont
        
    def addEnemy(self):
        enemy = EnemyBike(base.cTrav, self.cevent)
        self.AIworld.addAiChar(enemy.AIchar)
        return enemy
        
w = World()
run()

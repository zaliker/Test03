# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 10:52:47 2018

@author: ic_admin
"""

import pygame as pg
import traceback
import numpy as np
import math as m

pg.init()

W = 800
H = 600
gameDisplay = pg.display.set_mode((W,H))
pg.display.set_caption('Test Window')

clock = pg.time.Clock()

pg.font.init()
sysfont = pg.font.SysFont('Arial', 15)

class Hexgrid(object):
    def __init__(self, shape):
        self.shape = shape
        
        self.grid = [] #grid locs in x-y tile coordinates
        
        #Generate blank hexgrid
        for x in range(self.shape[0]):
            self.grid.append([])
            for y in range(self.shape[1]):
                self.grid[x].append(Hextile([1], (x,y)))
        
        self.sc_loc = (50,200)
        self.mouse_hold = set()
        self.mode_list = ["Edit", "Test"]
        self.mode_idx = 0
        
        self.tdim = (65,24,11)
        self.tile_grass = scale_y(pg.image.load("Hexset\\Tiles\\tileGrass.png"), 1/2)
        self.tile_dirt = scale_y(pg.image.load("Hexset\\Tiles\\tileDirt_full.png"), 1/2)
        self.marker_red = pg.image.load("Hexset\\Tiles\\flowerRed.png")
        self.marker_yellow = pg.image.load("Hexset\\Tiles\\flowerYellow.png")

    def grid_xy(self, loc_xy):
        return self.grid[loc_xy[0]][loc_xy[1]]
    
    def parse_input(self, event):
        #print(event)
        if event.type == pg.MOUSEBUTTONDOWN:
            self.mouse_hold.add(event.button)
            if event.button == 1:
                if self.mode_idx == 0:
                    cursorloc = self.nearest(tpldiff(pg.mouse.get_pos(), self.sc_loc))
                    self.grid_xy(cursorloc).add_layer([1])
            if event.button == 3:
                if self.mode_idx == 0:
                    cursorloc = self.nearest(tpldiff(pg.mouse.get_pos(), self.sc_loc))
                    self.grid_xy(cursorloc).remove_layer()
            if event.button in [4,5]:
                if self.mode_idx < len(self.mode_list)-1:
                    self.mode_idx += 1
                else: self.mode_idx = 0
                    
        if event.type == pg.MOUSEBUTTONUP:
            self.mouse_hold.remove(event.button)
        if event.type == pg.MOUSEMOTION:
            if 2 in self.mouse_hold:
                self.sc_loc = tplsum(self.sc_loc, event.rel)
    
    def nearest(self, loc_px):
        nearest = []
        nearest_dist = m.inf
        for x in range(self.shape[0]):
            for y in range(self.shape[1]):
                dist = tpldist(self.grid_xy((x,y)).loc_px, loc_px)
                if dist < nearest_dist:
                    nearest = (x,y)
                    nearest_dist = dist
        return nearest
    
    def draw_grid(self):
        gameDisplay.fill((200,230,255))
        for y in range(self.shape[1]):
            for x in range(self.shape[0]):
                height = self.grid_xy((x,y)).height()
                for z in range(height):
                    tile_loc = tplsum(self.sc_loc, (65*x+33*y,24*y-11*z))
                    if z==height-1: gameDisplay.blit(self.tile_grass, tile_loc)
                    else:gameDisplay.blit(self.tile_dirt, tile_loc)
                    
    def draw_gridpts(self):
        cursorloc = self.nearest(tpldiff(pg.mouse.get_pos(), self.sc_loc))
        for y in range(self.shape[1]):
            for x in range(self.shape[0]):
               #z = self.grid_xy((x,y)).height()-1
               tile_loc = tplsum(self.sc_loc, self.grid_xy((x,y)).loc_px)
               if (x,y) == cursorloc:
                   gameDisplay.blit(self.marker_red, tpldiff(tile_loc, (6,1)))
               else:
                   gameDisplay.blit(self.marker_yellow, tpldiff(tile_loc, (6,1)))
                
   
#Subclass for individual tiles
class Hextile(Hexgrid):
    def __init__(self, stack, loc_xy):
        self.stack = stack
        self.loc_xy = loc_xy
        self.update_px()
    
    #Return list of all tile information
    def stack(self): return self.stack
    #return stack height
    def height(self): return len(self.stack)
    
    def add_layer(self, new):
        self.stack.append(new)
        self.update_px()
    def remove_layer(self):
        self.stack = self.stack[:-1]
        self.update_px()
    
    def update_px(self):
        x = self.loc_xy[0]
        y = self.loc_xy[1]
        z = self.height()
        self.loc_px = (65*x+33*y+33,24*y-11*(z-1)+12)
        
#    def loc_px(self):
#        
#        return loc_px

def tplsum(a,b): return tuple(a[i]+b[i] for i in range(len(a)))
def tpldiff(a,b): return tuple(a[i]-b[i] for i in range(len(a)))
def tplmult(a,b): return tuple(a[i]*b for i in range(len(a)))
def tpldist(a,b): return m.sqrt(sum(tuple((a[i]-b[i])**2 for i in range(len(a)))))
def tpldir(a,b): return tuple(tplmult(tpldiff(b,a),1/tpldist(a,b)))
def tplint(a): return tuple(int(a[i]) for i in range(len(a)))
def sign(x): return (x > 0) - (x < 0)
def mod8sub(a,b): return (a - b + 4) % 8 - 4

def scale_y(img, scale):
    return pg.transform.scale(img, (img.get_width(), int(img.get_height()*scale)))
    
def gameLoop():
    try:
        
        
        #tile.set_colorkey((94, 129, 162))
        
        hexgrid = Hexgrid((8,6))
        
        print()
        
        gameExit = False
        while not gameExit:
            
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == 27):
                    gameExit = True
                else: hexgrid.parse_input(event)
            
            hexgrid.draw_grid()
            hexgrid.draw_gridpts()
            
            #print(hexgrid.nearest(tpldiff(pg.mouse.get_pos(), hexgrid.sc_loc)))
            
            systext = sysfont.render('Mode: %s'%hexgrid.mode_list[hexgrid.mode_idx], False, (0,0,0))
            gameDisplay.blit(systext, (10,10))
            
            pg.display.update()
            
            clock.tick(30)
            
    except: traceback.print_exc()
            
e = gameLoop()
pg.quit()
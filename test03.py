# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 10:52:47 2018

@author: ic_admin
"""

import pygame as pg
import traceback
#import numpy as np
import math as m
from queue import Queue, PriorityQueue
#import sys
import tupleOps as tpl

pg.init()

W = 800
H = 600
gameDisplay = pg.display.set_mode((W,H))
pg.display.set_caption('Test Window')

clock = pg.time.Clock()

#pg.font.init()
#sysfont = pg.font.SysFont('Arial', 15)

class Hexgrid():
    def __init__(self, shape):
        self.shape = shape
        
        self.grid = [] #grid locs in x-y tile coordinates
        
        #Generate blank hexgrid
        for x in range(self.shape[0]):
            self.grid.append([])
            for y in range(self.shape[1]):
                self.grid[x].append(Hextile([1], (x,y)))
        
        self.sc_loc = (25,200)
        self.mouse_hold = set()
        self.mode_list = ["Test", "Edit"]
        self.mode_idx = 0
        
        self.tdim = (65,24,11)
        self.tile_grass = pg.image.load("Assets\\tileGrass.png")
        self.tile_dirt = scale_y(pg.image.load("Assets\\tileDirt.png"), 1/2)
        self.button = pg.image.load("Assets\\button.png")
        
        self.marker_red = pg.image.load("Hexset\\Tiles\\flowerRed.png")
        self.marker_yellow = pg.image.load("Hexset\\Tiles\\flowerYellow.png")
        
        self.highlight = {}
        self.highlight["blue"] = pg.image.load("Assets\\tileSelect.png")
        self.highlight["white"] = pg.image.load("Assets\\tileSelect2.png")
        self.cursor = pg.image.load("Assets\\tileCursor.png")
        self.cursor_mini = pg.transform.scale(self.cursor, tpl.tint(tpl.tmult(self.cursor.get_size(), 0.5)))
        
        self.path = []
        self.unitlist = []
        self.activeunit = []
        self.cursor_loc = []
        self.highlightlist = []
        
        self.buttonlist = []
        for i in range(2):
            self.buttonlist.append()
        self.hover = []

    def add_unit(self, unit):
        self.unitlist.append(unit)
        unit.hexgrid = self
        unit.eid = len(self.unitlist)

    def grid_xy(self, loc_xy):
        return self.grid[loc_xy[0]][loc_xy[1]]
    
    def parse_input(self, event):
        #print(event)
        if event.type == pg.MOUSEBUTTONDOWN:
            self.mouse_hold.add(event.button)
            if event.button == 1:
                if self.mode_idx == 1: #Test
                    cursorloc = self.nearest_mouse()
                    self.grid_xy(cursorloc).add_layer([1])
                if self.mode_idx == 0: #Edit
                    if self.activeunit:
                        nm = self.nearest_mouse()
                        if nm in self.highlightlist:
                            #self.activeunit.loc_xy = nm
                            self.activeunit.path = self.path
            if event.button == 3:
                if self.mode_idx == 1:
                    cursorloc = self.nearest_mouse()
                    self.grid_xy(cursorloc).remove_layer()
            if event.button in [4,5]:
                if self.mode_idx < len(self.mode_list)-1:
                    self.mode_idx += 1
                else: self.mode_idx = 0
                    
        if event.type == pg.MOUSEBUTTONUP:
            self.mouse_hold.remove(event.button)
        if event.type == pg.MOUSEMOTION:
            if 2 in self.mouse_hold:
                self.sc_loc = tpl.tsum(self.sc_loc, event.rel)
    
    def neighbors(self, loc_xy):
        adj_set = set(((1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)))
        neighbors = set()
        for step in adj_set:
            dest = tpl.tsum(loc_xy,step)
            if 0 <= dest[0] <= self.shape[0]-1 and 0 <= dest[1] <= self.shape[1]-1:
                if self.grid_xy(dest).height() > 0:
                    if True:# -3 <= (self.height_diff(loc_xy, dest)) <= 2:
                        if all(unit.loc_xy != dest for unit in self.unitlist):
                            neighbors.add(tpl.tsum(loc_xy,step))
        return neighbors
    
    def check_range(self, origin, max_rng):
        frontier = Queue()
        frontier.put(origin)
        cost_so_far = {}
        cost_so_far[origin] = 0
        rng = set()
        
        while not frontier.empty():
            current = frontier.get()
            for step in self.neighbors(current):
                new_cost = cost_so_far[current] + 1
                if step not in rng and new_cost <= max_rng:
                    cost_so_far[step] = new_cost
                    frontier.put(step)
                    rng.add(step)
        rng.discard(origin)
        return rng
    
    def pathfind_ast(self, origin, target):
        frontier = PriorityQueue()
        frontier.put((0, origin))
        came_from = {}
        cost_so_far = {}
        came_from[origin] = None
        cost_so_far[origin] = 0
        
        while not frontier.empty():
            current = frontier.get()[1]
            
            if current == target: break
            for next in self.neighbors(current):
                new_cost = cost_so_far[current] + 1 #self.move_cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    if next not in came_from:
                        cost_so_far[next] = new_cost
                        priority = new_cost + tpl.tdist(next, target)
                        frontier.put((priority, next))
                        came_from[next] = current
        
        current = target
        path = []
        while current != origin:
            path.append(current)
            try: current = came_from[current]
            except:
                traceback.print_exc()
                #print(came_from)
        path.reverse()
        
        return path
    
    def nearest_mouse(self):
        return self.nearest(tpl.tdiff(pg.mouse.get_pos(), self.sc_loc))
    
    def nearest(self, loc_px):
        nearest = []
        nearest_dist = m.inf
        for x in range(self.shape[0]):
            for y in range(self.shape[1]):
                dist = tpl.tdist(self.grid_xy((x,y)).loc_px, loc_px)
                if dist < nearest_dist:
                    nearest = (x,y)
                    nearest_dist = dist
        return nearest
    
    def height_diff(self, origin, target):
        return self.grid_xy(target).height() - self.grid_xy(origin).height()
    
    #Calculate parabolic jump trajectory
    def jump(self, origin, target):
        h = self.height_diff(origin, target)*11
        origin = self.grid_xy(origin).loc_px
        target = self.grid_xy(target).loc_px
        
        dist_so_far = 0
        tgt_dist = tpl.tdist((origin[0], origin[1]-h), target)
        tgt_dir = tpl.tdir((origin[0], origin[1]-h), target)
        
        g = -2.5 #pixels/frame^2
        vz = 5
        t = (-vz - m.sqrt(vz**2 - 4*(g/2)*(-h)))/(g)
        
        vxy = tgt_dist/t
        
        arc = [origin]
        for i in range(5): arc.append(origin)
        while dist_so_far < tgt_dist:
            step = tpl.tsum(arc[-1], tpl.tmult(tgt_dir, vxy))
            step = (step[0], step[1]-vz)
            arc.append(step)
            vz += g
            dist_so_far += vxy
            if dist_so_far > tgt_dist: arc[-1] = target
        for i in range(5): arc.append(arc[-1])
        return arc
    
    def draw_button(self, loc_px):
        gameDisplay.blit(self.button, loc_px)
    
    def draw_cursor(self, loc_xy):
        loc_px = tpl.tdiff(tpl.tsum(self.grid_xy(loc_xy).loc_px, self.sc_loc), (33, 10))
        gameDisplay.blit(self.cursor, loc_px)
        
    def draw_cursor_mini(self, loc_xy):
        loc_px = tpl.tdiff(tpl.tsum(self.grid_xy(loc_xy).loc_px, self.sc_loc), (16, 3))
        gameDisplay.blit(self.cursor_mini, loc_px)
    
    def draw_highlight(self, loc_xy, color):
        loc_px = tpl.tdiff(tpl.tsum(self.grid_xy(loc_xy).loc_px, self.sc_loc), (33, 10))
        gameDisplay.blit(self.highlight[color], loc_px)
    
    def check_hover(self):
        
    
    def draw_grid(self):
        cursor_loc = self.nearest_mouse()
        if self.activeunit:
            self.highlightlist = self.check_range(self.activeunit.loc_xy, 3)
            if cursor_loc in self.highlightlist:
                self.path = self.pathfind_ast(self.activeunit.loc_xy, cursor_loc)
            else: self.path = []
        gameDisplay.fill((200,230,255))
        for y in range(self.shape[1]):
            for x in range(self.shape[0]):
                height = self.grid_xy((x,y)).height()
                for z in range(height):
                    tile_loc = tpl.tsum(self.sc_loc, (65*x+33*y,24*y-11*z))
                    if z==height-1: gameDisplay.blit(self.tile_grass, tile_loc)
                    else:gameDisplay.blit(self.tile_dirt, tile_loc)
            for tile in self.highlightlist:
                if tile[1] == y: self.draw_highlight(tile, "blue")
            for tile in self.path:
                if tile[1] == y: self.draw_highlight(tile, "white")
            if cursor_loc[1] == y: self.draw_cursor(cursor_loc)
            for unit in self.unitlist:
                if unit.loc_xy[1] == y: unit.draw()
        
        for i in range(2):
            self.draw_button((625+75*i, 500))
                   
    def draw_gridpts(self):
        cursorloc = self.nearest(tpl.tdiff(pg.mouse.get_pos(), self.sc_loc))
        for y in range(self.shape[1]):
            for x in range(self.shape[0]):
               #z = self.grid_xy((x,y)).height()-1
               tile_loc = tpl.tsum(self.sc_loc, self.grid_xy((x,y)).loc_px)
               if (x,y) == cursorloc:
                   gameDisplay.blit(self.marker_red, tpl.tdiff(tile_loc, (6,1)))
               else:
                   gameDisplay.blit(self.marker_yellow, tpl.tdiff(tile_loc, (6,1)))
                
   
#Subclass for individual tiles
class Hextile():
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
        
class Unit():
    def __init__(self, loc_xy):
        self.hexgrid = None
        self. eid = None
        
        self.loc_xy = loc_xy
        #self.loc_px = self.hexgrid.grid_xy(self.loc_xy).loc_px
        
        #Define pawn animation set
        self.pawnfile = "Assets\\armor-merc-basicB.png"
        self.pawnsheet = pg.image.load(self.pawnfile)
        self.pawnsheet = pg.transform.scale(self.pawnsheet, tpl.tmult(self.pawnsheet.get_rect().size, 2))
        self.pawnsheet.set_colorkey((140, 172, 213))
        self.pawndim = (80,120)
        self.pawn = pg.Surface(self.pawndim, pg.SRCALPHA)
        
        self.animset = "stand"
        self.animsubframe = 0
        self.animframe = 0
        
        #self.animtile = (40,60)
        self.animattr = {} #index and duration of animation
        self.animattr["stand"] = (0,4)
        self.animattr["crouch"] = (1,1)
        
        self.path = []
        self.jump = []
        self.mvspd = 5
        
#        self.actionqueue = []
#        
#    def tick(self):
#        if self.path:
#            for element in self.path:
#                None
#        
    def draw(self):
        #Update current pixel position
        if not self.path: self.loc_px = self.hexgrid.grid_xy(self.loc_xy).loc_px
            
        #Update animation frames
        self.animsubframe += 1
        if self.animsubframe >= 6:
            self.animsubframe = 0
            self.animframe += 1
        if self.animframe >= self.animattr[self.animset][1]: self.animframe = 0
        
        #Update location (jump)
        if self.jump:
            if len(self.jump) > 1:
                if self.jump[0] == self.jump[1]:
                    self.animset = "crouch"
                    self.animframe = 0
                else: self.animset = "stand"
            if self.loc_xy != self.path[0] and self.jump[1][1] < self.jump[0][1]:
                self.loc_xy = self.path[0]
            self.loc_px = self.jump[0]
            self.jump = self.jump[1:]
            if not self.jump: self.path = self.path[1:]
            
        #Update location (walk/run)
        else:
            mvmt = self.mvspd
            while mvmt > 0 and self.path and not self.jump:
                dh = self.hexgrid.height_diff(self.loc_xy, self.path[0])
                if self.path and m.fabs(dh) >= 2:
                    if dh <= -2: self.jump = self.hexgrid.jump(self.loc_xy, self.path[0])
                    if dh >= 2:
                        self.jump = self.hexgrid.jump(self.path[0], self.loc_xy)[::-1]
                    break
                self.animset = "stand"
                self.loc_xy = self.path[0]
                #print(self.path)
                dist_wp = tpl.tdist(self.loc_px, self.hexgrid.grid_xy(self.path[0]).loc_px)
                if dist_wp <= mvmt:
                    self.loc_px = self.hexgrid.grid_xy(self.path[0]).loc_px
                    self.path = self.path[1:]
                    mvmt -= dist_wp
                else:
                    self.loc_px = tpl.tsum(self.loc_px, tpl.tmult(tpl.tdir(self.loc_px, self.hexgrid.grid_xy(self.path[0]).loc_px), self.mvspd))
                    mvmt = 0
        
        #If not moving, reset to stand anim
        if not self.path and not self.jump: self.animset = "stand"
        
        #Blit pawn to display
        self.pawn.fill(pg.Color(0,0,0,0))
        self.pawn.blit(self.pawnsheet, (0,0), (self.pawndim[0]*self.animframe, self.pawndim[1]*self.animattr[self.animset][0], self.pawndim[0], self.pawndim[1]))
        gameDisplay.blit(self.pawn,
                             tpl.tsum(tpl.tdiff(self.loc_px, (self.pawndim[0]/2+3,101)), self.hexgrid.sc_loc))


#def mod8sub(a,b): return (a - b + 4) % 8 - 4

def scale_y(img, scale):
    return pg.transform.scale(img, (img.get_width(), int(img.get_height()*scale)))
    
def gameLoop():
    try:
        
        hexgrid = Hexgrid((12,14))
        hexgrid.add_unit(Unit((3,2)))
        hexgrid.add_unit(Unit((5,5)))
        hexgrid.activeunit = hexgrid.unitlist[0]
        
        print()
        
        gameExit = False
        while not gameExit:
            
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == 27):
                    gameExit = True
                else: hexgrid.parse_input(event)
            
            hexgrid.draw_grid()
            
            pg.display.update()
            
            clock.tick(30)
            
    except: traceback.print_exc()
            
e = gameLoop()
pg.quit()
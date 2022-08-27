from re import X
from secrets import choice
import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos ,surf , groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos ,surf , groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil water']

class SoilLayer:
    def __init__(self,all_sprites):

        # Sprite Group
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()

        # Soil Graphic
        self.soil_surfs = import_folder_dict('./graphics/soil/')
        self.water_surfs = import_folder('./graphics/soil_water')
        self.create_soil_grid() 
        self.create_hit_rects()
    
    ## Position of the soil that can Farmable
    def create_soil_grid(self):
        ground = pygame.image.load('./graphics/world/ground.png')
        h_tiles,v_tiles = ground.get_width() // TILE_SIZE , ground.get_height() // TILE_SIZE
        
        self.grid = [[[]for col in range(h_tiles)] for row in range(v_tiles)]
        for x,y, _ in load_pygame('./data/map.tmx').get_layer_by_name('Farmable').tiles() :
            self.grid[y][x].append('F')
          
    def create_hit_rects(self):
        self.hit_rects = []
        for index_row,row in enumerate(self.grid):
            for index_col,cell in enumerate(row):
                if 'F' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x,y,TILE_SIZE,TILE_SIZE)
                    self.hit_rects.append(rect)
    
    ## Hit Soil
    def get_hit(self,point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                ## To Check Where in Map can Farmable
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
    
    ## Generate Soil Tiles
    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row,row in enumerate(self.grid):
            for index_col,cell in enumerate(row):
                if 'X' in cell:

                    # tile options
                    t = 'X' in self.grid[index_row - 1][index_col]
                    b = 'X' in self.grid[index_row + 1][index_col]
                    r = 'X' in row[index_col + 1]
                    l = 'X' in row[index_col - 1]

                    tile_type = 'o'

                    ## All Sides

                    if all((t,r,b,l)):
                        tile_type = 'x'
                    
                    ## Horizontal Tiles Only
                    if l and not any((t,r,b)):
                        tile_type = 'r'
                    elif r and not any((t,b,l)):
                        tile_type = 'l'
                    elif l and r and not any((t,b)):
                        tile_type = 'lr'

                    ## Vertical Tiles Only

                    if t and not any((l,r,b)):
                        tile_type = 'b'
                    elif b and not any((l,r,t)):
                        tile_type = 't'
                    elif t and b and not ((l,r)):
                        tile_type = 'tb'

                    ## Corners
                    if l and b and not any((r,t)):
                        tile_type = 'tr'
                    elif l and t and not any((r,b)):
                        tile_type = 'br'
                    elif r and b and not any((l,t)):
                        tile_type = 'tl'
                    elif r and t and not any((l,b)):
                        tile_type = 'bl' 

                    ## T Shapes
                    if all((t,b,r)) and not l :
                        tile_type = 'tbr'
                    elif all((t,b,l)) and not r:
                        tile_type = 'tbl'
                    elif all((l,r,t)) and not b:
                        tile_type = 'lrb'
                    elif all((l,r,b)) and not t:
                        tile_type = 'lrt'

                    SoilTile(
                        pos = (index_col * TILE_SIZE , index_row * TILE_SIZE),
                        surf = self.soil_surfs[tile_type],
                        groups = [self.all_sprites,self.soil_sprites]
                        )
    
    ## Water Method
    def water(self,target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE

                WaterTile(
                    pos = soil_sprite.rect.topleft,
                    surf = choice(self.water_surfs),
                    groups = [self.all_sprites,self.water_sprites]

                )
                self.grid[y][x].append('W')
    
    ## Reset Water Method
    def remove_water(self):

        ## Destory all water sprites
        for sprite in self.water_sprites.sprites():
            sprite.kill()
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')
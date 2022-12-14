import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic , Water , WildFlower , Tree , Interaction , Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain , Sky
from random import randint
from menu import Menu ,Inventory

class Level:
    def __init__(self):

        # get the display surface
        self.display_surface = pygame.display.get_surface() ## == self.screen

        # sprite group
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites,self.collision_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset,self.player)

        ## Sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0,10) > 7
        self.soil_layer.raining = self.raining
        self.sky = Sky()

        ## Shop
        self.menu = Menu(self.player,self.toggle_shop)
        self.inventory = Inventory(self.player,self.toggle_inventory)
        self.shop_active = False
        self.inventory_active = False

        ## Music
        self.success = pygame.mixer.Sound('./audio/success.wav')
        self.success.set_volume(0.3)
        

    def setup(self):
        
        ## Load map.tmx --> Tiled
        tmx_data = load_pygame('./data/map.tmx') 
        
        ## Load Elements

        ## house
        for layer in ['HouseFloor','HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE),surf,self.all_sprites,LAYERS['house bottom'])
        
        for layer in ['HouseWalls','HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE),surf,self.all_sprites) ## Don't have layers --> LAYERS['main'] == Default layer in Generic Class
        
        ## Fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE),surf,[self.all_sprites,self.collision_sprites])

        ## Water
        water_frames = import_folder('./graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
                Water((x * TILE_SIZE, y * TILE_SIZE),water_frames,self.all_sprites)

        ## Wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x,obj.y), obj.image , self.all_sprites)

        ## Trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(
                pos = (obj.x,obj.y),
                surf = obj.image,
                groups=[self.all_sprites,self.collision_sprites,self.tree_sprites],
                name = obj.name,
                player_add = self.player_add)

        ## Collsion Tiled
        for x,y,surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE,y * TILE_SIZE), pygame.Surface((TILE_SIZE,TILE_SIZE)),self.collision_sprites)

        Generic(
            pos = (0,0),
            surf = pygame.image.load('./graphics/world/ground.png').convert_alpha(),
            groups = self.all_sprites,
            z = LAYERS['ground'] ## Layer of ground
        )

        ## Player Class
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    pos = (obj.x,obj.y),
                    group = self.all_sprites,
                    collision_sprites = self.collision_sprites,
                    tree_sprites = self.tree_sprites,
                    interaction = self.interaction_sprites,
                    soil_layer = self.soil_layer, 
                    toggle_shop = self.toggle_shop,
                    toggle_inventory = self.toggle_inventory)
            if obj.name == 'Bed':
                Interaction(
                    pos = (obj.x,obj.y),
                    size= (obj.width,obj.height),
                    groups = self.interaction_sprites ,
                    name = obj.name)
                    
            if obj.name == 'Trader':
                Interaction(
                    pos = (obj.x,obj.y),
                    size= (obj.width,obj.height),
                    groups = self.interaction_sprites ,
                    name = obj.name)

    def player_add(self,item):
        self.player.item_inventory[item] += 1
        self.success.play()

    def toggle_shop(self):
        self.shop_active = not self.shop_active 

    def toggle_inventory(self):
        self.inventory_active = not self.inventory_active

    def reset(self):

        ## Plants
        self.soil_layer.update_plant()

        #apples on the tree
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        ## Soils
        self.soil_layer.remove_water()
        self.raining = randint(0,10) > 7
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        ## Sky
        self.sky.start_color = [255,255,255]

    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(
                        pos = plant.rect.topleft,
                        surf = plant.image,
                        groups = self.all_sprites,
                        z = LAYERS['main']
                    )
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

    def run(self,dt):

        ## Drawing Logic
        self.display_surface.fill('black')
        self.all_sprites.customize_draw(self.player)

        ## Updates
        if self.shop_active:
            self.menu.update()
        elif self.inventory_active:
            self.inventory.update()
        else:
            self.all_sprites.update(dt)
            self.plant_collision()
        
        self.overlay.display()
        ## Rain
        if self.raining and not self.shop_active:
            self.rain.update()

        ## Day Time
        self.sky.display(dt)

        ## Transition Overlay
        if self.player.sleep:
            self.transition.play()
        

## Camera Class Group
class CameraGroup(pygame.sprite.Group): ## --> All Background Item Group
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def customize_draw(self,player):

        ## Shif the Background To Follow The Player
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            ##For Player Behind the element --> sorted(self.sprites() , key = lambda sprite : sprite.rect.centery)
            for sprite in sorted(self.sprites() , key = lambda sprite : sprite.rect.centery):
                if layer == sprite.z:
                    offset_rect = sprite.rect.copy()  ## copy() --> return a same list
                    offset_rect.center -= self.offset ## Position of Player 
                    self.display_surface.blit(sprite.image,offset_rect)
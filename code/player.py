import pygame
from settings import *
from support import *

class Player(pygame.sprite.Sprite): ## pygame.spriteSprite --> Simple base class for visible game objects.
    def __init__ (self, pos , group):
        super().__init__(group)

        self.import_assets()
        self.status = 'down' ## Image --> Player Activity
        self.frame_index = 0

        ## general setup
        self.image = self.animations[self.status][self.frame_index]  ## Call The Animations
        self.rect = self.image.get_rect(center = pos) ## Position

        ## movement attributes
        self.direction = pygame.math.Vector2() ## 2-Dimensional Vector
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

    def import_assets(self):

        ## Animations
        self.animations = {'up': [],'down' : [] , 'left' : [] , 'right' : [] , ## Player Animation Movement
                            'right_idle' : [] , 'left_idle' : [] , 'up_idle' : [] , 'down_idle' : [], ## Idle Animation Movement
                            'right_hoe' : [] , 'left_hoe' : [] , 'up_hoe' : [] , 'down_hoe' : [], ## hoe Animation Movement
                            'right_axe' : [] , 'left_axe' : [] , 'up_axe' : [] , 'down_axe' : [], ## Axe Animation Movement
                            'right_water' : [] , 'left_water' : [] , 'up_water' : [] , 'down_water' : []} ## Water Animation Movement

        for animation in self.animations.keys() :
            full_path = './Graphics Folder/Graphic Folder 1/character/' + animation ## Import All Animations of Character in Graphics Folder
            self.animations[animation] = import_folder(full_path) ## Call import_folder function

    def input(self):

        ## input key
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]: ## up
            self.direction.y = -1
        elif keys[pygame.K_s]: ## down
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_d]: ## right
            self.direction.x = 1
        elif keys[pygame.K_a]: ## left
            self.direction.x = -1
        else :
            self.direction.x = 0

    def move(self,dt):

        ## normalizing vector
        if (self.direction.magnitude() > 0): ## Euclidean --> Euclic
            self.direction = self.direction.normalize() ##  vector with the same direction but length 1.
        
        ## horizontal movement (Left & Right)
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x
        ## vertical movement (Up & Down)
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y
    

    def update(self,dt):
        self.input()
        self.move(dt)
import pygame
from math import ceil
from sys import exit
from random import randint, choice

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_walk_1 = pygame.image.load('graphics/player/player_walk_1.png').convert_alpha()
        player_walk_2 = pygame.image.load('graphics/player/player_walk_2.png').convert_alpha()
        self.player_walk = [player_walk_1,player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load('graphics/player/jump.png').convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom = (SCREEN_WIDTH/10, 0))
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound('audio/jump.mp3')
        self.jump_sound.set_volume(0.3)
    
    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= sky_height:
            self.gravity = -20 #jump
            self.jump_sound.play()
        if keys[pygame.K_RIGHT] and self.rect.right <= (SCREEN_WIDTH-50):
            self.rect.x += 3
        if keys[pygame.K_LEFT] and self.rect.left >= 50:
            self.rect.x -= 3

    def apply_gravity (self):
            self.gravity +=1
            self.rect.y += self.gravity
            if self.rect.bottom >= sky_height: self.rect.bottom = sky_height

    def animation_state(self):
        if self.rect.bottom < sky_height :
            self.image = self.player_jump
        else:
            self.player_index += 0.1 #we are slowly increase the index so the animation is slower
            if self.player_index >= len(self.player_walk): self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]
   
    def update(self):
        self.apply_gravity()
        self.player_input()
        self.animation_state()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()

        if type == 'fly':
            fly_frame_1 = pygame.image.load('graphics/fly/fly1.png').convert_alpha()
            fly_frame_2 = pygame.image.load('graphics/fly/fly2.png').convert_alpha()
            self.frames = [fly_frame_1,fly_frame_2]
            y_pos = sky_height-randint(50,90)
        else:
            snail_frame_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
            snail_frame_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
            self.frames = [snail_frame_1,snail_frame_2]
            y_pos = sky_height
        
        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom = (randint(900,1100),y_pos))

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames): self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]
    
    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

    def update(self):
        self.animation_state()
        self.rect.x -= 6
        self.destroy()

def display_score():
    current_time = int(pygame.time.get_ticks() / 500) - start_time
    score_surf = test_font.render(f'Score: {current_time}',False,(64,64,64))
    score_rect = score_surf.get_rect(center =(SCREEN_WIDTH/2,50))
    screen.blit(score_surf,score_rect)
    return current_time

def collision_sprite():
    if pygame.sprite.spritecollide(player.sprite,obstacle_group,False):
        obstacle_group.empty()
        return False
    else: return True

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('cdt')
clock = pygame.time.Clock()
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
game_active = False
start_time = 0
score = 0
bg_music = pygame.mixer.Sound('audio/music.wav')
bg_music.play(loops=-1)

#background
sky_surf = pygame.image.load('graphics/Sky.png').convert()
sky_width = sky_surf.get_width()
sky_height = sky_surf.get_height()
ground_surf = pygame.image.load('graphics/ground.png').convert()
ground_width = ground_surf.get_width()

scroll = 0
tiles = ceil(SCREEN_WIDTH / ground_width)+1

#Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()
#we don't want to add obstacles if the timer is not running so obstacle_group.add(Obstacle(...)) will be used after

#Intro screen
player_stand = pygame.image.load('graphics/player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand,0,2)
player_stand_rect = player_stand.get_rect(center = (SCREEN_WIDTH/2,SCREEN_HEIGHT/2))

title_surf = test_font.render('Pixel Runner',False,(111,196,169))
title_rect = title_surf.get_rect(center =(SCREEN_WIDTH/2,SCREEN_HEIGHT/5))

caption_surf = test_font.render('Press space to start',False,(111,196,169))
caption_rect = caption_surf.get_rect(center =(SCREEN_WIDTH/2,SCREEN_HEIGHT/1.2))

#Timer
obstacle_timer = pygame.USEREVENT + 1 #we add +1 to avoid conflict with other pygame events
pygame.time.set_timer(obstacle_timer,1500)


while True:
    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(['fly','snail','snail','snail'])))
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                start_time=int(pygame.time.get_ticks()/500)
        

    #dislpay
    if game_active:
        #background
        for i in range(0, tiles):
            screen.blit(ground_surf, (i * ground_width + scroll, sky_height))
            screen.blit(sky_surf,(i * ground_width + scroll,0))
        scroll -= 5
        if abs(scroll) > ground_width : scroll = 0

        #score
        score = display_score()

        #player
        player.draw(screen)
        player.update()

        # obstacles
        obstacle_group.draw(screen)
        obstacle_group.update()

        # collisions
        game_active = collision_sprite()

    else:
        screen.fill((94,129,162))
        screen.blit(player_stand,player_stand_rect)

        score_message = test_font.render(f'Your score: {score}',False,(111,196,169))
        score_message_rect = score_message.get_rect(center = (SCREEN_WIDTH/2,SCREEN_HEIGHT/1.2))
        screen.blit(title_surf,title_rect)

        if score == 0 : screen.blit(caption_surf,caption_rect)
        else: screen.blit(score_message,score_message_rect)

    pygame.display.update()
    clock.tick(60)
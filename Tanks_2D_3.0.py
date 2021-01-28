# ========================================================================================================================
# Imports etc.
# ========================================================================================================================
import time
import random
import sys
import os
import pika
import uuid
import json
import kwargs
from threading import Thread
from math import *
import pygame
pygame.init()
print("Modules loaded")
# ========================================================================================================================
# HELP
# ========================================================================================================================

HELP = '''
Select/Continue in Menu- |F|
Move keys in Menu - |W| |A| |S| |D|

1P: Move Tank or Pointer in options - |W| |A| |S| |D|
1P: Fire or SelectSkin in options - |SPACE|

2P: Move Tank or Pointer in options - ARROWS
2P: Fire or SelectSkin in options- |RCTRL|

Back to menu etc... - |BACKSPACE| or |ESCAPE|



Если папка с игрой переносится, то иногда возникают проблемы с чтением mp3 файлов, это особенность пайгейма.
Если это произойдет, закомментируйте
pygame.mixer.music.load(f'sound/soundtrack/{tracks[r]}')
pygame.mixer.music.play(-1)
'''

# ========================================================================================================================
# Settings.
# ========================================================================================================================
IP = '34.254.177.17'
PORT = '5672'
VIRTUAL_HOST = 'dar-tanks'
USERNAME = 'dar-tanks'
PASSWORD = '5orPLExUYnyVYZg48caMpX'

winWidth = 800
winHeight = 600
winWidth2 = 1000  # additional space for UI
win = pygame.display.set_mode((winWidth2, winHeight))

UI = pygame.Surface((200, 600))  # width,height
UI.fill((31, 31, 31))  # color

FPS = 30
clock = pygame.time.Clock()

pygame.display.set_caption("Tanks 2D")
icon = pygame.image.load("anim/icon.png")
loading = pygame.image.load("anim/loading.png")
room_png = pygame.image.load("anim/room.png")
pygame.display.set_icon(icon)
win.blit(loading, (0, 0))
pygame.display.update()

print("Settings loaded")
# ========================================================================================================================
# Sounds.
# ========================================================================================================================

shootSnd = pygame.mixer.Sound('sound/piuHero.wav')
tankExplSnd = pygame.mixer.Sound('sound/death.wav')
hitSnd = pygame.mixer.Sound('sound/hitmarker.wav')
scrollSnd = pygame.mixer.Sound('sound/snd1.wav')
clickSnd = pygame.mixer.Sound('sound/snd2.wav')
tracks = os.listdir('sound/soundtrack')
pygame.mixer.music.set_volume(0.05)
# soundtrack_1 - Demon Slayer "Kimetsu no Yaiba" - Shinobu Theme
# soundtrack_2 - Demon Slayer "Kimetsu no Yaiba" - Giyuu Theme
# soundtrack_3 - AC3 - Main Theme

print("Sounds loaded")
# ========================================================================================================================
# Animations init.
# ========================================================================================================================

bulletExplSpr = []
tankExplSpr = []

anim_model_1 = []
anim_model_2 = []
anim_model_3 = []
anim_model_4 = []
anim_model_5 = []
anim_model_6 = []
anim_model_7 = []
anim_model_8 = []
anim_model_9 = []
anim_model_10 = []
anim_model_11 = []
anim_model_12 = []
anim_model_13 = []
anim_model_14 = []
anim_model_15 = []


for i in range(10):
    bulletExplSpr.append(pygame.image.load(
        f'anim/bulletExpl/explosion_{i}.png'))
    tankExplSpr.append(pygame.image.load(
        f'anim/tankExplosion/tank_expl_{i}.png'))
bonusSpr = pygame.image.load("anim/bonus.png")

for i in range(1, 4+1):
    anim_model_1.append(pygame.image.load(
        f'anim/models/model_4Fr (1)/sprite ({i}).png'))
    anim_model_2.append(pygame.image.load(
        f'anim/models/model_4Fr (2)/sprite ({i}).png'))
    anim_model_3.append(pygame.image.load(
        f'anim/models/model_4Fr (3)/sprite ({i}).png'))
    anim_model_4.append(pygame.image.load(
        f'anim/models/model_4Fr (4)/sprite ({i}).png'))

for i in range(1, 8+1):
    anim_model_5.append(pygame.image.load(
        f'anim/models/model_8Fr (1)/sprite ({i}).png'))
    anim_model_6.append(pygame.image.load(
        f'anim/models/model_8Fr (2)/sprite ({i}).png'))
    anim_model_7.append(pygame.image.load(
        f'anim/models/model_8Fr (3)/sprite ({i}).png'))
    anim_model_8.append(pygame.image.load(
        f'anim/models/model_8Fr (4)/sprite ({i}).png'))
    anim_model_9.append(pygame.image.load(
        f'anim/models/model_8Fr (5)/sprite ({i}).png'))
    anim_model_10.append(pygame.image.load(
        f'anim/models/model_8Fr (6)/sprite ({i}).png'))

for i in range(1, 9+1):
    anim_model_11.append(pygame.image.load(
        f'anim/models/model_9Fr (1)/sprite ({i}).png'))
    anim_model_12.append(pygame.image.load(
        f'anim/models/model_9Fr (2)/sprite ({i}).png'))
    anim_model_13.append(pygame.image.load(
        f'anim/models/model_9Fr (3)/sprite ({i}).png'))
    anim_model_14.append(pygame.image.load(
        f'anim/models/model_9Fr (4)/sprite ({i}).png'))
    anim_model_15.append(pygame.image.load(
        f'anim/models/model_9Fr (5)/sprite ({i}).png'))


skins = [anim_model_1, anim_model_2,
         anim_model_3, anim_model_4, anim_model_5, anim_model_6, anim_model_7, anim_model_8, anim_model_9, anim_model_10,
         anim_model_11, anim_model_12, anim_model_13, anim_model_14, anim_model_15]


print("Sprites loaded")
# ========================================================================================================================
# Main tank class.
# ========================================================================================================================


class Hero(object):
    def __init__(self, speed, hp, sprite, width=32, height=32):
        self.x = 32
        self.y = 32
        self.speed = 4
        self.baseSpeed = speed
        self.hp = hp
        self.width = width
        self.height = height
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

        self.up = True
        self.down = False
        self.left = False
        self.right = False

        self.shootTimer = 0
        self.alive = True
        self.bullets = []
        self.power = False
        self.pTimer = 0

        self.animFrame = 0
        self.animLimit = len(sprite)
        self.spriteU = sprite
        self.spriteR = []
        self.spriteD = []
        self.spriteL = []
        for i in self.spriteU:
            self.spriteR.append(pygame.transform.rotate(i, 270))
        for i in self.spriteR:
            self.spriteD.append(pygame.transform.rotate(i, 270))
        for i in self.spriteD:
            self.spriteL.append(pygame.transform.rotate(i, 270))

    def move(self, sec):
        self.speed = round(self.baseSpeed * sec)
        if self.up:
            self.hitbox = pygame.Rect(
                self.x, self.y-self.speed, self.width, self.height)
            for wall in walls:
                if self.hitbox.colliderect(wall.hitbox):
                    if wall.fire:
                        self.getDamage()
                        walls.remove(wall)
                    return
            for hero in heroes:
                if self is not hero:
                    if self.hitbox.colliderect(hero.hitbox):
                        return
            self.y -= self.speed
            self.animFrame += 1
            if self.y+self.height <= 0:
                self.y = winHeight
        elif self.down:
            self.hitbox = pygame.Rect(
                self.x, self.y+self.speed, self.width, self.height)
            for wall in walls:
                if self.hitbox.colliderect(wall.hitbox):
                    if wall.fire:
                        self.getDamage()
                        walls.remove(wall)
                    return
            for hero in heroes:
                if self is not hero:
                    if self.hitbox.colliderect(hero.hitbox):
                        return
            if self.y >= winHeight:
                self.y = 0-self.height
            self.y += self.speed
            self.animFrame += 1
        elif self.right:
            self.hitbox = pygame.Rect(
                self.x+self.speed, self.y, self.width, self.height)
            for wall in walls:
                if self.hitbox.colliderect(wall.hitbox):
                    if wall.fire:
                        self.getDamage()
                        walls.remove(wall)
                    return
            for hero in heroes:
                if self is not hero:
                    if self.hitbox.colliderect(hero.hitbox):
                        return
            self.x += self.speed
            self.animFrame += 1
            if self.x >= winWidth:
                self.x = 0-self.width
        elif self.left:
            self.hitbox = pygame.Rect(
                self.x-self.speed, self.y, self.width, self.height)
            for wall in walls:
                if self.hitbox.colliderect(wall.hitbox):
                    if wall.fire:
                        self.getDamage()
                        walls.remove(wall)
                    return
            for hero in heroes:
                if self is not hero:
                    if self.hitbox.colliderect(hero.hitbox):
                        return
            self.x -= self.speed
            self.animFrame += 1
            if self.x+self.width <= 0:
                self.x = winWidth

        if self.animFrame > self.animLimit-1:
            self.animFrame = 0

    def draw(self):
        if self.alive:
            # hitbox draw
            # pygame.draw.rect(
            #     win, [0, 255, 0], (self.x, self.y, self.width, self.height), 1)
            if self.up:
                win.blit(self.spriteU[self.animFrame], (self.x, self.y))
            elif self.down:
                win.blit(self.spriteD[self.animFrame], (self.x, self.y))
            elif self.right:
                win.blit(self.spriteR[self.animFrame], (self.x, self.y))
            elif self.left:
                win.blit(self.spriteL[self.animFrame], (self.x, self.y))

            if self.power and self.pTimer + 5000 > pygame.time.get_ticks():
                pygame.draw.circle(
                    win, [0, int(pygame.time.get_ticks()/2) % 255, 0], (self.x+16, self.y+16), 22, 1)
                self.power = True
                self.baseSpeed = tankSpeed*2
            else:
                self.baseSpeed = tankSpeed
                self.power = False

    def drawHP(self):
        bitHp = 30//hp
        pygame.draw.rect(win, [200, 0, 0], (self.x+1, self.y-4, bitHp*hp, 3))
        pygame.draw.rect(win, [0, 200, 0],
                         (self.x+1, self.y-4, bitHp*self.hp, 3))

    def shoot(self):
        if self.bullets == [] and self.shootTimer + gunReload < pygame.time.get_ticks():
            self.shootTimer = pygame.time.get_ticks()
            shootSnd.play()

            if self.up:
                self.bullets.append(Bullet(
                    self.x + self.width // 2, self.y-bulletR, bulletR, owner=self.bullets, up=True))

            elif self.down:
                self.bullets.append(Bullet(self.x + self.width // 2,
                                           self.y+self.height+bulletR, bulletR, owner=self.bullets, down=True))

            elif self.right:
                self.bullets.append(Bullet(
                    self.x + self.width+bulletR, self.y+self.height//2, bulletR, owner=self.bullets, right=True))

            elif self.left:
                self.bullets.append(Bullet(
                    self.x - bulletR, self.y+self.height//2, bulletR, owner=self.bullets, left=True))

    def direction(self, right=False, left=False, down=False, up=False):
        self.right = right
        self.left = left
        self.up = up
        self.down = down

    def respawn(self):
        if self.alive == False and singlePlayer == True:
            self.x = random.randrange(40, winWidth-80, 32)
            self.y = random.randrange(40, winHeight-80, 32)
            self.hp = hp
            self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)
            if 100-32 <= self.x <= winWidth-100 and 100-32 <= self.y <= winWidth-100:
                self.respawn()

            for hero in heroes:
                if hero != self:
                    if (hero.x-32 <= self.x <= hero.x+32 and hero.y-32 <= self.y <= hero.y+32):
                        self.respawn()

            for wall in walls:
                if (wall.x-32 <= self.x <= wall.x+52 and wall.y-32 <= self.y <= wall.y+52):
                    self.respawn()
        self.alive = True

    def getDamage(self):
        global gameOver
        hitSnd.play()
        for i in range(10):
            win.blit(bulletExplSpr[i], (self.x, self.y))
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False
            self.tankExpDraw()
            tankExplSnd.play()
            gameOver = True

    def tankExpDraw(self):
        for frame in tankExplSpr:
            win.blit(frame, (self.x, self.y))

# ========================================================================================================================
# Bullets.
# ========================================================================================================================


class Bullet(object):
    def __init__(self, x, y, bulletR, owner, bulletSpeed=250, down=False, up=False, right=False, left=False):
        self.x = x
        self.y = y
        self.radius = bulletR
        self.width = bulletR*2
        self.height = bulletR*2
        self.down = down
        self.up = up
        self.right = right
        self.left = left

        self.baseSpeed = bulletSpeed
        self.speed = 4
        self.owner = owner
        self.hitbox = pygame.Rect(
            self.x-self.radius, self.y-self.radius, self.width, self.height)

    def draw(self):
        pygame.draw.circle(win, [int((self.x+self.y)*0.4) %
                                 255, 0, 255], [self.x, self.y], self.radius)
        # hitbox draw
        # pygame.draw.rect(
        #     win, [0, 255, 0], (self.x-self.radius, self.y-self.radius, self.width, self.height), 1)

    def bulletExplDraw(self):
        for i in range(10):
            win.blit(bulletExplSpr[i], (self.x-12, self.y-12))

    def move(self, sec):
        self.speed = round(self.baseSpeed * sec)
        self.hitbox = pygame.Rect(
            self.x-self.radius, self.y-self.radius, self.width, self.height)
        if self.right:
            self.x += self.speed
        elif self.up:
            self.y -= self.speed
        elif self.left:
            self.x -= self.speed
        elif self.down:
            self.y += self.speed

        if self.x <= 0 or self.x >= winWidth or self.y <= 0 or self.y >= winHeight:
            if self.owner != []:
                self.owner.remove(self)

        for wall in walls:
            if wall.hitbox.colliderect(self.hitbox):
                if self.owner != []:
                    self.owner.remove(self)
                    self.bulletExplDraw()
                wall.getDamage()
        for hero in heroes:
            if hero.power:
                for bullet in hero.bullets:
                    bullet.baseSpeed = bulletSpeed*2
            else:
                for bullet in hero.bullets:
                    bullet.baseSpeed = bulletSpeed
            if hero.hitbox.colliderect(self.hitbox) and self.owner != hero.bullets:
                if self.owner != []:
                    self.owner.remove(self)
                    self.bulletExplDraw()
                hero.getDamage()

# ========================================================================================================================
# Walls.
# ========================================================================================================================


class Wall(object):
    def __init__(self, x, y, immortal=False, fire=False, width=20, height=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

        self.fire = fire
        self.alive = True
        self.immortal = immortal

    def draw(self):
        if self.immortal == False and self.fire == False:
            pygame.draw.rect(
                win, [int(self.x*2) % 255, int(self.y*2) % 255, 255], (self.x, self.y, self.width, self.height), 2)
        elif self.immortal:
            pygame.draw.rect(
                win, [255, 255, 255], (self.x, self.y, self.width, self.height), 2)
        elif self.fire:
            pygame.draw.rect(
                win, [200, 100, 50], (self.x, self.y, self.width, self.height), 1+int(pygame.time.get_ticks()/250) % 3)

    def getDamage(self):
        global gameOver
        if not self.immortal:
            self.alive = False


def map_creating():
    with open('data/map_1.txt', mode='r') as file:
        j = 0  # line number
        for line in file:
            for i in range(len(line)):
                if line[i] == 'x':
                    # x - immortal walls
                    walls.append(Wall(i*20, j*20, immortal=True))
                elif line[i] == '1':
                    walls.append(Wall(i*20, j*20))  # 1 - usual walls
                elif line[i] == '0':
                    r = random.randint(1, 100)  # 1% chance spawn fire wall
                    if r == 1:
                        walls.append(Wall(i*20, j*20, fire=True))
            j += 1
    print("Map created")

# ========================================================================================================================
# Lines in menu
# ========================================================================================================================


class Line(object):
    def __init__(self, x, y, width, height, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed

    def draw(self):
        pygame.draw.rect(
            win, [255, 255, 255], (self.x, self.y, self.width, self.height))

    def move(self):
        self.y += self.speed
        if self.y >= winHeight:
            lines.remove(self)

# ========================================================================================================================
# Food
# ========================================================================================================================


class Food(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)
        win.blit(bonusSpr, (self.x, self.y))
        pygame.draw.circle(
            win, [0, int(pygame.time.get_ticks()/2) % 255, 0], (self.x+self.height//2, self.y+self.width//2), 3+self.width//2, 3)

        for hero in heroes:
            if hero.hitbox.colliderect(self.hitbox):
                foods.clear()
                hero.pTimer = pygame.time.get_ticks()
                hero.power = True


foodTimer = pygame.time.get_ticks()


def foodSpawn(foods):
    global foodTimer, foodSpawnTime
    if foods == [] and foodTimer + foodSpawnTime < pygame.time.get_ticks():
        x = random.randrange(20, winWidth-40, 20)
        y = random.randrange(20, winHeight-40, 20)
        if 100-20 <= x <= winWidth-100 and 100-20 <= y <= winWidth-100:
            return
        for hero in heroes:
            if (hero.x-32 <= x <= hero.x+32 and hero.y-32 <= y <= hero.y+32):
                return
        foods.append(Food(x, y))
        foodTimer = pygame.time.get_ticks()


# ========================================================================================================================
# RPC Client
# ========================================================================================================================


class TankRpcClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=IP,
                port=PORT,
                virtual_host=VIRTUAL_HOST,
                credentials=pika.PlainCredentials(
                    username=USERNAME,
                    password=PASSWORD
                )
            )
        )
        self.channel = self.connection.channel()
        queue = self.channel.queue_declare(queue='',
                                           auto_delete=True,
                                           exclusive=True
                                           )
        self.callback_queue = queue.method.queue
        self.channel.queue_bind(
            exchange='X:routing.topic',
            queue=self.callback_queue
        )

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

        self.response = None
        self.corr_id = None
        self.token = None
        self.tank_id = None
        self.room_id = None

    def on_response(self, ch, method, props, body):  # Принимаем данные
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)
            # print(self.response)

    def call(self, key, message={}):  # Отправляем данные

        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='X:routing.topic',
            routing_key=key,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(message)
        )
        while self.response is None:
            self.connection.process_data_events()

    def check_server_status(self):
        self.call('tank.request.healthcheck')
        return self.response['status'] == '200'

    def obtain_token(self, room_id):
        message = {
            'roomId': room_id
        }
        self.call('tank.request.register', message)
        if 'token' in self.response:
            self.token = self.response['token']
            self.tank_id = self.response['tankId']
            self.room_id = self.response['roomId']
            return True
        return False

    def turn_tank(self, token, direction):
        message = {
            'token': token,
            'direction': direction
        }
        self.call('tank.request.turn', message)

    def fire(self, token):
        message = {
            'token': token
        }
        self.call('tank.request.fire', message)


class TankConsumerClient(Thread):
    def __init__(self, room_id):
        super().__init__()
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=IP,
                port=PORT,
                virtual_host=VIRTUAL_HOST,
                credentials=pika.PlainCredentials(
                    username=USERNAME,
                    password=PASSWORD
                )
            )
        )
        self.channel = self.connection.channel()
        queue = self.channel.queue_declare(queue='',
                                           auto_delete=True,
                                           exclusive=True
                                           )
        event_listener = queue.method.queue
        self.channel.queue_bind(
            exchange='X:routing.topic',
            queue=event_listener,
            routing_key='event.state.'+room_id
        )
        self.channel.basic_consume(
            queue=event_listener,
            on_message_callback=self.on_response,
            auto_ack=True
        )
        self.response = None
        self.connectionClosed = False

    def on_response(self, ch, method, props, body):  # Принимаем данные
        if self.connectionClosed:
            raise Exception('Connection Closed')
        self.response = json.loads(body)
        # print(self.response)

    def closeIt(self):
        self.connectionClosed = True

    def run(self):
        self.channel.start_consuming()


print("Classes loaded")
# ========================================================================================================================
# Variables etc
# ========================================================================================================================


with open("data/settings.txt", mode='r') as file:
    data = file.read()
settings = json.loads(data)

game_over_txt = "Game Over"

heroes = []
lines = []
walls = []
foods = []
gameOver = False
singlePlayer = False
multiPlayer = False
multiplayer_AI = False

gunReload = 250
foodSpawnTime = random.randrange(7000, 13000, 1000)

lineTimer = 0


hp = 3  # 1-30
tankSpeed = 125
bulletSpeed = 250
bulletR = 4  # Radius
p1SkinID = settings['p1SkinID']  # 0-14
p2SkinID = settings['p2SkinID']  # 0-14
myTank = Hero(tankSpeed, hp, skins[p1SkinID])
youTank = Hero(tankSpeed, hp, skins[p2SkinID])

chosenRoom = 'room-1'  # default room

enemy_ai_r = 300  # radius enemy detection
bullet_ai_r = 180  # radius bullets detection
shield_ai_r = 56  # radius close zone detection,to avoid suicide attack
changedir_ai_timer = 6000
AIChangeDirTime = 3000
directions = ['UP', 'DOWN', 'RIGHT', 'LEFT']

# ========================================================================================================================
#  Menu, interface
# ========================================================================================================================


def roomChoosing(menuDelay):
    global chosenRoom
    chooseroom = True
    font = pygame.font.SysFont('Arial', 40)
    rn = 1
    while chooseroom:
        win.blit(room_png, (0, 0))
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        if keys[pygame.K_f] and menuDelay+200 < pygame.time.get_ticks():
            menuDelay = pygame.time.get_ticks()
            clickSnd.play()
            chooseroom = False
        if (keys[pygame.K_d] or keys[pygame.K_a]) and menuDelay+200 < pygame.time.get_ticks():
            scrollSnd.play()
            menuDelay = pygame.time.get_ticks()
            if keys[pygame.K_a]:
                rn = (rn-1)
                if rn < 1:
                    rn = 30
            elif keys[pygame.K_d]:
                rn = (rn+1)
                if rn > 30:
                    rn = 1
        text = font.render(f'{rn}', 1, (255, 255, 255))
        win.blit(text, (winWidth2//2-text.get_rect()[2]//2, 295))
        chosenRoom = f'room-{rn}'
        pygame.display.update()


def mainMenu():
    r = random.randint(0, 2)  # play new music when MenuMode
    pygame.mixer.music.load(f'sound/soundtrack/{tracks[r]}')
    pygame.mixer.music.play(-1)

    global singlePlayer, multiplayer_AI, multiPlayer, lines, lineTimer, heroes, skins, p1SkinID, p2SkinID
    singlePlayer = False
    multiplayer_AI = False
    multiPlayer = False
    menuRun = True
    settingsMode = False

    choice = 0
    menuDelay = 0

    p1ChoiceX = 0
    p1ChoiceY = 0
    p2ChoiceX = 4
    p2ChoiceY = 0

    font = pygame.font.SysFont('comic sans ms', 25)
    font1 = pygame.font.SysFont('comic sans ms', 15)
    font2 = pygame.font.SysFont('comic sans ms', 40)
    gameName = font2.render('Tanks2D 3.0', 1, (255, 255, 255))
    button = font.render('Singleplayer', 1, (255, 174, 23))
    button1 = font.render('Multiplayer', 1, (255, 255, 255))
    button2 = font.render('MultiplayerAI', 1, (255, 255, 255))
    button3 = font.render('Settings', 1, (255, 255, 255))
    button4 = font.render('Quit', 1, (255, 255, 255))
    author = font1.render('by Koilybayev Daniil', 1, (255, 255, 255))

    help_0 = font1.render('Select/Continue - |F|', 1, (255, 255, 255))
    help_1 = font1.render(
        '1P: Move Tank/Pointer - |W| |A| |S| |D|', 1, (255, 255, 255))
    help_2 = font1.render('1P: Fire/Select - |SPACE|', 1, (255, 255, 255))
    help_3 = font1.render('2P: Move Tank/Pointer - ARROWS', 1, (255, 255, 255))
    help_4 = font1.render('2P: Fire/Select - |RCTRL|', 1, (255, 255, 255))
    help_5 = font1.render('Select your skin:', 1, (255, 255, 255))
    help_6 = font1.render('Back - |BACKSPACE|', 1, (255, 255, 255))
    print("Menu loaded")
    while menuRun:
        ms = clock.tick(60)
        win.fill((0, 0, 0))

        if settingsMode == False:
            # MAIN MENU UI
            win.blit(button, (winWidth-button.get_rect()[2]+190, 340))
            win.blit(button1, (winWidth-button1.get_rect()[2]+190, 380))
            win.blit(button2, (winWidth-button2.get_rect()[2]+190, 420))
            win.blit(button3, (winWidth-button3.get_rect()[2]+190, 460))
            win.blit(button4, (winWidth-button4.get_rect()[2]+190, 500))
            win.blit(gameName, (winWidth-gameName.get_rect()[2]+190, 240))
            win.blit(author, (winWidth-author.get_rect()[2]+190, 290))

        elif settingsMode:
            win.blit(help_0, (winWidth-help_0.get_rect()
                              [2]+190, 240-20))  # HELP INFORMATION
            win.blit(help_1, (winWidth-help_1.get_rect()[2]+190, 240+20*0))
            win.blit(help_2, (winWidth-help_2.get_rect()[2]+190, 240+20*1))
            win.blit(help_3, (winWidth-help_3.get_rect()[2]+190, 240+20*2))
            win.blit(help_4, (winWidth-help_4.get_rect()[2]+190, 240+20*3))
            win.blit(help_5, (winWidth-help_5.get_rect()[2]+190, 230+20*5))
            win.blit(help_6, (winWidth-help_6.get_rect()[2]+190, 240+20*13))

            for model in range(1, len(skins)//3+1):  # TANKS MODELS DRAW
                win.blit(skins[model-1][0], (winWidth2-model*40, 360))
            for model in range(1, len(skins)//3+1):
                win.blit(skins[5+model-1][0], (winWidth2-model*40, 360+40))
            for model in range(1, len(skins)//3+1):
                win.blit(skins[10+model-1][0], (winWidth2-model*40, 360+80))

            pygame.draw.rect(win, (100+int(pygame.time.get_ticks()/4) % 155, 0, 0),  # p1 selected model
                             (winWidth2-40-40*(p1SkinID % 5), 360+40*(p1SkinID//5), 33, 33), 4)
            pygame.draw.rect(win, (0, 0, 100+int(pygame.time.get_ticks()/4) % 155),
                             (winWidth2-40-40*(p2SkinID % 5), 360+40*(p2SkinID//5), 33, 33), 4)  # p2 selected model

            pygame.draw.rect(win, (38, 47, 222),
                             (winWidth2-40-40*p2ChoiceX, 360+40*p2ChoiceY, 33, 33), 2)  # p2 pointer
            pygame.draw.rect(win, (201, 30, 30),
                             (winWidth2-40-40*p1ChoiceX, 360+40*p1ChoiceY, 33, 33), 2)  # p1 pointer

        # ANIMATION LINES IN MENU
        if len(lines) < 30 and lineTimer + 100 < pygame.time.get_ticks() and menuRun:
            lineTimer = pygame.time.get_ticks()
            lineX = random.randint(20, 700)
            lineY = random.randint(-600, -500)
            lineWidth = random.randint(6, 25)
            lineHeight = random.randint(300, 700)
            lineSpeed = random.randint(60, 90)
            lines.append(Line(lineX, lineY, lineWidth, lineHeight, lineSpeed))
        for line in lines:
            line.move()
            line.draw()
        pygame.display.update()

        # Keys
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (choice == 4 and keys[pygame.K_f]):
                pygame.quit()
                quit()
        # Keys in MainMenu
        if (keys[pygame.K_s] or keys[pygame.K_w]) and settingsMode == False and menuDelay+200 < pygame.time.get_ticks():
            menuDelay = pygame.time.get_ticks()
            scrollSnd.play()
            if keys[pygame.K_s]:
                choice = (choice+1) % 5
            elif keys[pygame.K_w]:
                choice = (choice-1) % 5
                if choice < 0:
                    choice = 5
            button = font.render('Singleplayer', 1, (255, 255, 255))
            button1 = font.render('Multiplayer', 1, (255, 255, 255))
            button2 = font.render('MultiplayerAI', 1, (255, 255, 255))
            button3 = font.render('Settings', 1, (255, 255, 255))
            button4 = font.render('Quit', 1, (255, 255, 255))
            if choice == 0:
                button = font.render('Singleplayer', 1, (255, 174, 23))
            elif choice == 1:
                button1 = font.render('Multiplayer', 1, (255, 174, 23))
            elif choice == 2:
                button2 = font.render('MultiplayerAI', 1, (255, 174, 23))
            elif choice == 3:
                button3 = font.render('Settings', 1, (255, 174, 23))
            elif choice == 4:
                button4 = font.render('Quit', 1, (150, 0, 0))

        # Keys in OptionsMenu
        if (keys[pygame.K_s] or keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_DOWN] or keys[pygame.K_UP] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and settingsMode and menuDelay+200 < pygame.time.get_ticks():
            menuDelay = pygame.time.get_ticks()
            scrollSnd.play()
            if keys[pygame.K_s]:
                p1ChoiceY = (p1ChoiceY+1) % 3
            elif keys[pygame.K_w]:
                p1ChoiceY = (p1ChoiceY-1) % 3
                if p1ChoiceY < 0:
                    playerChoiceY = 3
            elif keys[pygame.K_a]:
                p1ChoiceX = (p1ChoiceX+1) % 5
            elif keys[pygame.K_d]:
                p1ChoiceX = (p1ChoiceX-1) % 5
                if p1ChoiceX < 0:
                    p1ChoiceX = 5
            elif keys[pygame.K_DOWN]:
                p2ChoiceY = (p2ChoiceY+1) % 3
            elif keys[pygame.K_UP]:
                p2ChoiceY = (p2ChoiceY-1) % 3
                if p2ChoiceY < 0:
                    playerChoiceY = 3
            elif keys[pygame.K_LEFT]:
                p2ChoiceX = (p2ChoiceX+1) % 5
            elif keys[pygame.K_RIGHT]:
                p2ChoiceX = (p2ChoiceX-1) % 5
                if p2ChoiceX < 0:
                    p2ChoiceX = 5
        # Space or CTRL to select skin
        if (keys[pygame.K_SPACE] or keys[pygame.K_RCTRL]) and settingsMode and menuDelay+200 < pygame.time.get_ticks():
            menuDelay = pygame.time.get_ticks()
            clickSnd.play()
            if keys[pygame.K_SPACE]:
                p1SkinID = p1ChoiceY*5+p1ChoiceX
            elif keys[pygame.K_RCTRL]:
                p2SkinID = p2ChoiceY*5+p2ChoiceX
        # Backspace - back in menu from SettingsMode
        if keys[pygame.K_BACKSPACE] and settingsMode:
            scrollSnd.play()
            settingsMode = False
        # F - select button in menu
        if keys[pygame.K_f] and menuDelay+200 < pygame.time.get_ticks():
            menuDelay = pygame.time.get_ticks()
            if settingsMode == False:
                clickSnd.play()
                if choice == 0:
                    print("Singleplayer mode activated")
                    singlePlayer = True
                    menuRun = False
                    lines.clear()
                elif choice == 1:
                    print("Multiplayer mode activated")
                    roomChoosing(menuDelay)
                    multiPlayer = True
                    menuRun = False
                    lines.clear()
                elif choice == 2:
                    print("AI mode activated")
                    roomChoosing(menuDelay)
                    multiplayer_AI = True
                    menuRun = False
                    lines.clear()
                elif choice == 3:
                    settingsMode = True


def game_over_window(game_over_txt):
    font = pygame.font.SysFont('comic sans ms', 30)
    backspaceTXT = font.render('Menu - [BackSpace]', 1, (255, 255, 255))
    text = font.render(game_over_txt, 1, (255, 255, 255))
    run = True
    print("Game Over screen loaded")
    while run:
        win.fill((0, 0, 0))
        win.blit(text, (winWidth2//2-text.get_rect()[2]//2, 280))
        win.blit(backspaceTXT, (winWidth -
                                backspaceTXT.get_rect()[2]+190, 550))
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_BACKSPACE]:
                run = False
        pygame.display.update()


# ========================================================================================================================
# Updating objects on display.
# ========================================================================================================================


def window_updating(sec):
    win.fill((0, 0, 0))
    for wall in walls:
        if wall.alive:
            wall.draw()
    for wall in walls:
        if not wall.alive:
            walls.remove(wall)
    for food in foods:
        food.draw()
    for hero in heroes:
        hero.draw()
        hero.move(sec)
        for bullet in hero.bullets:
            bullet.move(sec)
            bullet.draw()
    for hero in heroes:
        hero.drawHP()
    win.blit(UI, (winWidth, 0))
    pygame.display.update()


# ========================================================================================================================
# SinglePlayer game run
# ========================================================================================================================


def run_single():
    global myTank, youTank, heroes, walls, gameOver, bulletR, foods, game_over_txt
    win.blit(loading, (0, 0))
    pygame.display.update()
    single = True
    while single:
        ms = clock.tick(FPS)
        sec = ms/1000
        window_updating(sec)

        if myTank.power == False and youTank.power == False:
            foodSpawn(foods)

        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                single = False

        if myTank.alive:
            if keys[pygame.K_d]:
                myTank.direction(right=True)
            elif keys[pygame.K_a]:
                myTank.direction(left=True)
            elif keys[pygame.K_w]:
                myTank.direction(up=True)
            elif keys[pygame.K_s]:
                myTank.direction(down=True)

        if youTank.alive:
            if keys[pygame.K_RIGHT]:
                youTank.direction(right=True)
            elif keys[pygame.K_LEFT]:
                youTank.direction(left=True)
            elif keys[pygame.K_UP]:
                youTank.direction(up=True)
            elif keys[pygame.K_DOWN]:
                youTank.direction(down=True)

        if keys[pygame.K_SPACE] and myTank.alive:
            myTank.shoot()

        if keys[pygame.K_LSHIFT] and youTank.alive:
            youTank.shoot()

        if gameOver or keys[pygame.K_ESCAPE]:
            single = False
            if myTank.hp > 0 and youTank.hp <= 0:
                game_over_txt = '1 Player Win!'
            elif youTank.hp > 0 and myTank.hp <= 0:
                game_over_txt = '2 Player Win!'
            else:
                game_over_txt = 'SinglePlayer was closed'


# ========================================================================================================================
# MULTIPLAYER
# ========================================================================================================================


# костыль
vision_up = pygame.Rect(-100, -100, 1, 1)
vision_down = pygame.Rect(-100, -100, 1, 1)
vision_right = pygame.Rect(-100, -100, 1, 1)
vision_left = pygame.Rect(-100, -100, 1, 1)
vision_up_b = pygame.Rect(-100, -100, 1, 1)
vision_down_b = pygame.Rect(-100, -100, 1, 1)
vision_right_b = pygame.Rect(-100, -100, 1, 1)
vision_left_b = pygame.Rect(-100, -100, 1, 1)
vision_up_s = pygame.Rect(-100, -100, 1, 1)
vision_down_s = pygame.Rect(-100, -100, 1, 1)
vision_right_s = pygame.Rect(-100, -100, 1, 1)
vision_left_s = pygame.Rect(-100, -100, 1, 1)
enemy_hitbox = pygame.Rect(-300, -100, 1, 1)
enemy_bullet_hitbox = pygame.Rect(-300, -100, 1, 1)
enemy_bullet_rect = pygame.Rect(-300, -100, 1, 1)

checker_timer = 0
shootTimer = 0

ui_font = pygame.font.SysFont('comic sans ms', 15)

myDir = 'None'


def get_bullet_hitbox(client, myId, x, y, owner, width, height, **kwargs):
    global enemy_bullet_rect
    if myId != owner:
        enemy_bullet_rect = pygame.Rect(x, y, width, height)
    return enemy_bullet_rect


def ai_acting(enemy_bullet_hitbox, client, myId, x, y, id, width, height, direction, health, **kwargs):
    global vision_up, vision_down, vision_right, vision_left, enemy_hitbox, enemy_bullet_rect, checker_timer, changedir_ai_timer, vision_up_s, vision_down_s, vision_right_s, vision_left_s, vision_up_b, vision_down_b, vision_right_b, vision_left_b, myDir, shootTimer
    if myId == id:
        myDir = direction
        pygame.draw.rect(win, (255, 0, 0), (x+5, y-enemy_ai_r -
                                            shield_ai_r, width-10, enemy_ai_r), 2)  # UP tank
        pygame.draw.rect(win, (255, 0, 0), (x+5, y+height +
                                            shield_ai_r, width-10, enemy_ai_r), 2)  # DOWN tank
        pygame.draw.rect(win, (255, 0, 0), (x+height+shield_ai_r,
                                            y+5, enemy_ai_r, height-10), 2)  # RIGHT tank
        pygame.draw.rect(win, (255, 0, 0), (x-enemy_ai_r-shield_ai_r,
                                            y+5, enemy_ai_r, height-10), 2)  # LEFT tank

        pygame.draw.rect(win, (0, 255, 0), (x-15, y-bullet_ai_r,
                                            width+30, bullet_ai_r), 2)  # UP bullet
        pygame.draw.rect(win, (0, 255, 0), (x-15, y+height,
                                            width+30, bullet_ai_r), 2)  # DOWN bullet
        pygame.draw.rect(win, (0, 255, 0), (x+height,
                                            y-15, bullet_ai_r, height+30), 2)  # RIGHT bullet
        pygame.draw.rect(win, (0, 255, 0), (x-bullet_ai_r,
                                            y-15, bullet_ai_r, height+30), 2)  # LEFT bullet

        pygame.draw.rect(win, (0, 0, 255), (x-5, y-shield_ai_r,
                                            width+5, shield_ai_r), 2)  # UP bullet
        pygame.draw.rect(win, (0, 0, 255), (x-5, y +
                                            height, width+5, shield_ai_r), 2)  # DOWN bullet
        pygame.draw.rect(win, (0, 0, 255), (x+height,
                                            y-5, shield_ai_r, height+5), 2)  # RIGHT bullet
        pygame.draw.rect(win, (0, 0, 255), (x-shield_ai_r,
                                            y-5, shield_ai_r, height+5), 2)  # LEFT bullet
        vision_up = pygame.Rect(
            x+5, y-enemy_ai_r-shield_ai_r, width-10, enemy_ai_r)
        vision_down = pygame.Rect(
            x+5, y+height+shield_ai_r, width-10, enemy_ai_r)
        vision_right = pygame.Rect(
            x+height+shield_ai_r, y+5, enemy_ai_r, height-10)
        vision_left = pygame.Rect(
            x-enemy_ai_r-shield_ai_r, y+5, enemy_ai_r, height-10)

        vision_up_b = pygame.Rect(x-15, y-bullet_ai_r, width+30, bullet_ai_r)
        vision_down_b = pygame.Rect(x-15, y+height, width+30, bullet_ai_r)
        vision_right_b = pygame.Rect(x+height, y-15, bullet_ai_r, height+30)
        vision_left_b = pygame.Rect(
            x-bullet_ai_r, y-15, bullet_ai_r, height+30)

        vision_up_s = pygame.Rect(x-5, y-shield_ai_r, width+5, shield_ai_r)
        vision_down_s = pygame.Rect(x-5, y+height, width+5, shield_ai_r)
        vision_right_s = pygame.Rect(x+height, y-5, shield_ai_r, height+5)
        vision_left_s = pygame.Rect(x-shield_ai_r, y-5, shield_ai_r, height+5)
    else:
        enemy_hitbox = pygame.Rect(x, y, width, height)

    if checker_timer + 200 < pygame.time.get_ticks():  # timer for checking
        # check indicator, in the upper left corner
        pygame.draw.rect(win, (255, 0, 0), (4, 4, 4, 4))
        # enemy hitbox with shell intersection monitoring
        if enemy_hitbox.colliderect(vision_up_s):
            changedir_ai_timer = pygame.time.get_ticks()
            if myDir != directions[1] and myDir != directions[2] and myDir != directions[3]:
                checker_timer = pygame.time.get_ticks()
                return client.turn_tank(client.token, directions[1])
        elif enemy_hitbox.colliderect(vision_down_s):
            changedir_ai_timer = pygame.time.get_ticks()
            if myDir != directions[0] and myDir != directions[2] and myDir != directions[3]:
                checker_timer = pygame.time.get_ticks()
                return client.turn_tank(client.token, directions[0])
        elif enemy_hitbox.colliderect(vision_right_s):
            changedir_ai_timer = pygame.time.get_ticks()
            if myDir != directions[0] and myDir != directions[1] and myDir != directions[3]:
                checker_timer = pygame.time.get_ticks()
                return client.turn_tank(client.token, directions[3])
        elif enemy_hitbox.colliderect(vision_left_s):
            changedir_ai_timer = pygame.time.get_ticks()
            if myDir != directions[0] and myDir != directions[1] and myDir != directions[2]:
                checker_timer = pygame.time.get_ticks()
                return client.turn_tank(client.token, directions[2])
        # enemy hitbox with vision intersection monitoring
        elif enemy_hitbox.colliderect(vision_up):
            if myDir != directions[0]:
                checker_timer = pygame.time.get_ticks()
                changedir_ai_timer = pygame.time.get_ticks()
                return client.turn_tank(client.token, directions[0])
            if shootTimer + 2000 < pygame.time.get_ticks():
                shootTimer = pygame.time.get_ticks()
                client.fire(client.token)
                shootSnd.play()
        elif enemy_hitbox.colliderect(vision_down):
            if myDir != directions[1]:
                checker_timer = pygame.time.get_ticks()
                changedir_ai_timer = pygame.time.get_ticks()
                return client.turn_tank(client.token, directions[1])
            if shootTimer + 2000 < pygame.time.get_ticks():
                shootTimer = pygame.time.get_ticks()
                client.fire(client.token)
                shootSnd.play()
        elif enemy_hitbox.colliderect(vision_right):
            if myDir != directions[2]:
                checker_timer = pygame.time.get_ticks()
                changedir_ai_timer = pygame.time.get_ticks()
                return client.turn_tank(client.token, directions[2])
            if shootTimer + 2000 < pygame.time.get_ticks():
                shootTimer = pygame.time.get_ticks()
                client.fire(client.token)
                shootSnd.play()
        elif enemy_hitbox.colliderect(vision_left):
            if myDir != directions[3]:
                checker_timer = pygame.time.get_ticks()
                changedir_ai_timer = pygame.time.get_ticks()
                return client.turn_tank(client.token, directions[3])
            if shootTimer + 2000 < pygame.time.get_ticks():
                shootTimer = pygame.time.get_ticks()
                client.fire(client.token)
                shootSnd.play()

        elif enemy_bullet_hitbox != 'None':
            if enemy_bullet_hitbox.colliderect(vision_up_b) and myDir != directions[2] and myDir != directions[3]:
                checker_timer = pygame.time.get_ticks()
                changedir_ai_timer = pygame.time.get_ticks()
                return client.turn_tank(client.token, directions[random.randint(2, 3)])
            elif enemy_bullet_hitbox.colliderect(vision_down_b) and myDir != directions[2] and myDir != directions[3]:
                checker_timer = pygame.time.get_ticks()
                changedir_ai_timer = pygame.time.get_ticks()
                return client.turn_tank(client.token, directions[random.randint(2, 3)])
            elif enemy_bullet_hitbox.colliderect(vision_right_b) and myDir != directions[0] and myDir != directions[1]:
                checker_timer = pygame.time.get_ticks()
                changedir_ai_timer = pygame.time.get_ticks()
                return client.turn_tank(client.token, directions[random.randint(0, 1)])
            elif enemy_bullet_hitbox.colliderect(vision_left_b) and myDir != directions[0] and myDir != directions[1]:
                checker_timer = pygame.time.get_ticks()
                changedir_ai_timer = pygame.time.get_ticks()
                return client.turn_tank(client.token, directions[random.randint(0, 1)])


def draw_tanks_mp(myId, x, y, id, width, height, direction, health, **kwargs):
    global myDir
    # tank drawning
    if myId == id:
        myDir = direction
        tank_skin_mp = skins[p1SkinID][0]
    elif id[-1] == '0':
        tank_skin_mp = skins[3][0]
    elif id[-1] == '1':
        tank_skin_mp = skins[4][0]
    elif id[-1] == '2':
        tank_skin_mp = skins[5][0]
    elif id[-1] == '3':
        tank_skin_mp = skins[6][0]
    elif id[-1] == '4':
        tank_skin_mp = skins[7][0]
    elif id[-1] == '5':
        tank_skin_mp = skins[8][0]
    elif id[-1] == '6':
        tank_skin_mp = skins[9][0]
    elif id[-1] == '7':
        tank_skin_mp = skins[10][0]
    elif id[-1] == '8':
        tank_skin_mp = skins[11][0]
    elif id[-1] == '9':
        tank_skin_mp = skins[12][0]
    else:
        tank_skin_mp = skins[p2SkinID][0]

    if direction == 'UP':
        tank_skin_mp = pygame.transform.rotate(tank_skin_mp, 0)
    elif direction == 'DOWN':
        tank_skin_mp = pygame.transform.rotate(tank_skin_mp, 180)
    if direction == 'RIGHT':
        tank_skin_mp = pygame.transform.rotate(tank_skin_mp, -90)
    elif direction == 'LEFT':
        tank_skin_mp = pygame.transform.rotate(tank_skin_mp, 90)
    win.blit(tank_skin_mp, (x, y))
    # hp drawning
    pygame.draw.rect(win, [200, 0, 0], (x+1, y-4, 29, 4))
    pygame.draw.rect(win, [0, 200, 0], (x, y-4, 10*health, 4))

    # nick drawning
    font = pygame.font.SysFont('comic sans ms', 10)
    nick = font.render(f'You[{myId[5:]}]' if myId ==
                       id else f'[{id[5:]}]', 1, (255, 255, 255))
    win.blit(nick, (x + width // 2 - nick.get_size()[0] // 2, y-20))


def draw_bullets_mp(myId, x, y, owner, width, height, **kwargs):
    # bullet drawning
    if owner == myId:
        color = (100+int(pygame.time.get_ticks()/4) % 155, 0, 200)
    else:
        color = (200, 100+int(pygame.time.get_ticks()/4) % 155, 0)
    pygame.draw.rect(win, color, (x, y, width, height))


def draw_ui_mp(myId, myRoom, tanks):
    font = pygame.font.SysFont('comic sans ms', 13)
    tanks.sort(key=lambda x: x['score'], reverse=True)
    i = 1
    # area of UI, rectangle
    pygame.draw.rect(win, (255, 255, 255), (winWidth, 0, 199, 599), 2)
    # draw lines like tableon UI
    pygame.draw.rect(win, (255, 255, 255), (winWidth, 48, 200, 1))
    for tank in tanks:
        if tank['id'] == myId:
            nickname = 'my-tank'
        else:
            nickname = tank['id']
        table = font.render(
            f"{nickname}: |Points:{tank['score']}|HP:{tank['health']}|", 1, (255, 255, 255))
        win.blit(table, (winWidth+10, 30+i*17))
        pygame.draw.rect(win, (255, 255, 255),
                         (winWidth, 48+i*17, 200, 1))  # lines
        i += 1
    # draw room id
    room_n_txt = font.render(f"|ROOM - {myRoom[5:]}|", 1, (255, 255, 255))
    win.blit(room_n_txt, (winWidth+5, winHeight-20))


# main multiplayer function
def run_multi():
    global game_over_txt, AIChangeDirTime, changedir_ai_timer, shootTimer
    win.blit(loading, (0, 0))
    pygame.display.update()

    # rpc initializing
    client = TankRpcClient()
    client.check_server_status()
    client.obtain_token(chosenRoom)
    events = TankConsumerClient(chosenRoom)
    events.start()

    myRoom = client.room_id
    myId = client.tank_id
    client.turn_tank(client.token, 'UP')

    run = True
    while run:
        ms = clock.tick(FPS)
        sec = ms/1000
        win.fill((0, 0, 0))
        check = False

        tanks = events.response['gameField']['tanks']
        bullets = events.response['gameField']['bullets']
        losers = events.response['losers']
        kicked = events.response['kicked']

        for bullet in bullets:
            draw_bullets_mp(myId, **bullet)
        for tank in tanks:
            draw_tanks_mp(myId, **tank)

        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                run = False

        if not multiplayer_AI:
            # for control tank
            if keys[pygame.K_d]:
                client.turn_tank(client.token, 'RIGHT')
            elif keys[pygame.K_a]:
                client.turn_tank(client.token, 'LEFT')
            elif keys[pygame.K_w]:
                client.turn_tank(client.token, 'UP')
            elif keys[pygame.K_s]:
                client.turn_tank(client.token, 'DOWN')
            if keys[pygame.K_SPACE] and shootTimer + 2000 < pygame.time.get_ticks():
                shootTimer = pygame.time.get_ticks()
                client.fire(client.token)
                shootSnd.play()

        if multiplayer_AI:
            # change direction randomly, if AI didn't see anyone in time interval - AIChangeDirTime
            if changedir_ai_timer + AIChangeDirTime < pygame.time.get_ticks():  # AI Direction changing
                changedir_ai_timer = pygame.time.get_ticks()
                client.turn_tank(
                    client.token, directions[random.randint(0, 3)])
                # if shootTimer + 4000 < pygame.time.get_ticks():
                #     shootTimer = pygame.time.get_ticks()
                #     client.fire(client.token)
                #     shootSnd.play()

            # check tanks and bullet hitboxes, start analyze intersections
            for tank in tanks:
                if len(bullets) == 0:
                    enemy_bullet_hitbox = 'None'
                    ai_acting(enemy_bullet_hitbox, client,
                              myId, **tank)
                else:
                    for bullet in bullets:
                        enemy_bullet_hitbox = get_bullet_hitbox(
                            client, myId, **bullet)
                        ai_acting(enemy_bullet_hitbox, client,
                                  myId, **tank)

        round_time = events.response.get('remainingTime', 0)
        round_time_txt = ui_font.render(
            f'Time: {round_time}', True, (255, 255, 255))

        for tank in losers:
            if tank['tankId'] == myId:
                check = True
                game_over_txt = f'You({myId}) lose! Score: {tank["score"]}'
                run = False

        for tank in kicked:
            if tank['tankId'] == myId:
                check = True
                game_over_txt = f'You({myId}) were AFK!'
                run = False

        winners = events.response['winners']
        if len(winners) != 0:
            for tank in winners:
                if tank['tankId'] == myId:
                    check = True
                    game_over_txt = f'You({myId}) win! Score: {tank["score"]}'
                else:
                    check = True
                    game_over_txt = f'{tank["tankId"]} win! Score: {tank["score"]}'
            run = False

        for tank in tanks:
            if tank['id'] == myId:
                check = True

        if check == False:
            game_over_txt = f'Game Over!'
            run = False

        win.blit(UI, (winWidth, 0))
        win.blit(round_time_txt, (winWidth+10, 10))
        draw_ui_mp(myId, myRoom, tanks)
        pygame.display.update()

    win.blit(loading, (0, 0))
    pygame.display.update()

    client.connection.close()
    events.closeIt()
    print("Current session is closed")
    pygame.time.delay(1000)
    os.system("cls")


# ========================================================================================================================
# Main Cycle, renew gamestate, clear objects etc
# ========================================================================================================================

print("Game loaded")
run = True
while run:
    foods = []
    heroes = []
    walls = []
    game_over_txt = "Game Over"
    mainMenu()
    lines = []
    gameOver = False
    newSettings = json.dumps({"p1SkinID": p1SkinID, "p2SkinID": p2SkinID})
    with open("data/settings.txt", mode="w") as file:
        file.write(newSettings)
    if singlePlayer:
        del myTank
        del youTank
        myTank = Hero(tankSpeed, hp, skins[p1SkinID])
        youTank = Hero(tankSpeed, hp, skins[p2SkinID])
        heroes.append(myTank)
        heroes.append(youTank)
        for hero in heroes:
            hero.alive = False
            hero.hp = hp
            hero.bullets = []
            hero.power = False
        for hero in heroes:
            hero.respawn()
        map_creating()
        run_single()
    if multiPlayer or multiplayer_AI:
        run_multi()
    game_over_window(game_over_txt)
    os.system("cls")


pygame.quit()
quit()

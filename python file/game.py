import random
import pygame
import os
import sys
import sqlite3
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
import time
import math


def load_image(name):
    fullname = os.path.join(name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def menu():
    global screen, width, height, menu_flag, size
    width, height = 1000, 800
    size = (width, height)
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 0))


def update_menu():
    global menu_flag, screen
    screen.fill((0, 0, 0))
    x = width / 2 - 100
    y = height / 2 - 35
    if menu_flag == 0:
        pygame.draw.rect(screen, (0, 80, 140), (x, y, 200, 70))
    else:
        pygame.draw.rect(screen, (0, 135, 240), (x, y, 200, 70))
    font = pygame.font.Font(None, 50)
    text = font.render("START", True, (255, 255, 255))
    text_x = x + (200 - text.get_width()) / 2
    text_y = y + (70 - text.get_height()) / 2
    screen.blit(text, (text_x, text_y, text.get_width(), text.get_height()))


def check_menu(position):
    global width, height, menu_flag
    x_pos, y_pos = position
    if width / 2 - 100 < x_pos < width / 2 + 100 and height / 2 - 35 < y_pos < height / 2 + 35:
        menu_flag = 1
    else:
        menu_flag = 0


def new_game():
    global con, cur, screen,  size, width, height, v_villian, v_bullet, CLOCK, VILLIANS,\
        SCORE, boss_SCORE, prev_SCORE, FAILED,\
        all_sprites, all_villians, boss, shots, explodes,\
        tmr, boss_explosion, boss_int, tmr_int, boss_count,\
        font, text_x, text_y, text, menu_flag
    menu_flag = -1
    CLOCK = pygame.time.Clock()
    screen.fill((0, 0, 0))
    v_bullet = 100
    v_villian = 100
    boss_count = 0
    SCORE = 0
    prev_SCORE = -1
    boss_SCORE = 0
    VILLIANS = pygame.time.Clock()
    FAILED = 0
    tmr_int = 1000
    boss_int = 3900

    con = sqlite3.connect('results.db')
    cur = con.cursor()

    font = pygame.font.Font(None, 20)
    text = font.render(f"SCORE: {SCORE + boss_SCORE}", True, (100, 255, 100))
    text_x = 10
    text_y = 10

    explodes = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    boss = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(Player(all_sprites))
    all_villians = pygame.sprite.Group()
    all_sprites.update((width // 2, height // 2 - 32))

    tmr = QTimer()
    tmr.setInterval(tmr_int)
    tmr.timeout.connect(make_a_villian)
    tmr.start()

    boss_explosion = QTimer()
    boss_explosion.setInterval(700)
    boss_explosion.timeout.connect(boss_defeating)


def boss_defeating():
    global explodes, boom
    boom.play()
    explodes.add(Explosion(explodes))


def make_a_villian():
    global SCORE
    if SCORE > 200:
        a = random.randint(0, 2)
        if a == 0:
            all_villians.add(Villian(all_villians))
        else:
            all_villians.add(Villian_2(all_villians))
    else:
        all_villians.add(Villian(all_villians))


def pause():
    global cur, v_villian, v_bullet, SCORE, all_sprites, all_villians, screen, running, tmr, boss_SCORE
    tmr.stop()
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 50)
    font2 = pygame.font.Font(None, 35)
    text = font.render("GAME OVER", True, (100, 255, 100))
    text2 = font2.render(f"SCORE: {SCORE + boss_SCORE}", True, (100, 255, 100))
    text_x = width // 2 - text.get_width() // 2
    text_y = height // 2 - text.get_height() // 2
    text2_x = text_x + (text.get_width() - text2.get_width()) / 2
    text2_y = text_y + 15 + text.get_height()
    a = 0
    length = len(cur.execute(f'select * from result').fetchall())
    if length > 0:
        a = cur.execute(f'select score from result order by score desc').fetchone()[0]
    if length < 0 or SCORE + boss_SCORE > a:
        text3 = font2.render("NEW RECORD!!!", True, (255, 255, 100))
        text3_x = text2_x + (text2.get_width() - text3.get_width()) / 2
        text3_y = text_y - text3.get_height() - 15
        screen.blit(text3, (text3_x, text3_y))
    screen.blit(text, (text_x, text_y))
    screen.blit(text2, (text2_x, text2_y))

    cur.execute(f'insert into result(score) values({SCORE + boss_SCORE})')
    con.commit()
    pygame.display.flip()

    i = True
    while i:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                i = False
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                i = False
                new_game()
        pygame.display.flip()


def update_non_objects():
    global text, SCORE, v_villian, prev_SCORE, tmr, tmr_int, v_bullet, boss, boss_int, boss_SCORE, boss_count, BG, bg_count
    text = font.render(f"SCORE: {SCORE + boss_SCORE}", True, (100, 255, 100))
    if 500 <= (SCORE - 500 * boss_count) <= 540 and len(boss) == 0 and SCORE != prev_SCORE:
        boss_count += 2
        if boss_int - 300 > 500:
            boss_int -= 400
        tmr.stop()
        boss_appears()
    if (SCORE - prev_SCORE) >= 100 and len(boss) == 0:
        prev_SCORE = SCORE
        v_villian += 10
        v_bullet += 20
        if tmr_int - 50 > 250:
            tmr_int -= 50
            tmr.setInterval(tmr_int)
    if bg_count < 49:
        bg_count += 0.25
    if bg_count // 1 == 49:
        bg_count = 0
    BG.sprites()[0].image = load_image(fr'background\bg_{str(bg_count % 100).split(".")[0]}.jpg')


def boss_appears():
    global boss
    boss.add(Boss(boss))


class Explosion(pygame.sprite.Sprite):
    image = load_image('explode\ex_0.gif')

    def __init__(self, group):
        global boss
        super().__init__(group)
        global width, height, boss, boss_int
        self.image = Explosion.image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(boss.sprites()[0].rect.x + 100, boss.sprites()[0].rect.x + boss.sprites()[0].rect.width - 200)
        self.rect.y = random.randint(boss.sprites()[0].rect.y + 70, boss.sprites()[0].rect.y + boss.sprites()[0].rect.height - 70)
        self.count = 0

    def update(self):
        if self.count <= 8:
            self.count += 0.2
            self.image = load_image(f'explode\ex_{str(self.count).split(".")[0]}.gif')
        else:
            self.kill()


class Diamond(pygame.sprite.Sprite):
    image = load_image('diamond_blue.png')

    def __init__(self, group):
        super().__init__(group)
        global width, height, boss, boss_int
        self.image = Diamond.image
        self.rect = self.image.get_rect()
        self.rect.x = width / 2
        self.rect.y = height / 2 - 100
        self.state = 'STOP'
        self.fl = 0
        self.v = 80
        self.ability = False
        self.color = 'blue'
        self.count = 0

        self.mask = pygame.mask.from_surface(self.image)

        self.d_out_tmr = QTimer()
        self.d_out_tmr.setInterval(boss_int)
        self.d_out_tmr.timeout.connect(self.go_in)

        self.d_in_tmr = QTimer()
        self.d_in_tmr.setInterval(8000)
        self.d_in_tmr.timeout.connect(self.go_out)
        self.d_in_tmr.start()

    def update(self, msec):
        global boss, SCORE, boss_SCORE, prev_SCORE, boss_explosion
        if self.state == 'OUT':
            if self.rect.y < boss.sprites()[-1].rect.y + boss.sprites()[-1].rect.height - 50:
                self.rect.y += msec * self.v / 1000
                self.ability = True
        elif self.state == 'IN':
            if self.rect.y > 294:
                self.rect.y -= msec * self.v / 1000
                self.ability = True
        if self.rect.y == 294:
            self.fl += 1
        if self.fl == 1:
            self.ability = False
            if boss.sprites()[-1].HEALTH <= 0:
                boss_SCORE += boss.sprites()[-1].plus_score
                prev_SCORE = SCORE
                boss_explosion.start()
                self.kill()
            if self.state == 'OUT':
                self.d_out_tmr.start()
            else:
                self.d_in_tmr.start()
                boss.sprites()[-1].do_shots.start()
        if self.color == 'pink':
            if self.count == 2:
                self.color = 'blue'
            else:
                self.count += 0.5
        self.image = load_image(f'diamond_{self.color}.png')

    def go_out(self):
        global boss
        if len(boss) > 0:
            boss.sprites()[-1].do_shots.stop()
            self.d_in_tmr.stop()
            self.d_out_tmr.start()
            self.rect.x = random.randint(boss.sprites()[-1].rect.x + 150,
                                                   boss.sprites()[-1].rect.x + boss.sprites()[-1].rect.width - 300)
            self.state = 'OUT'
            self.fl = 0
            self.d_in_tmr.stop()

    def go_in(self):
        global boss
        self.state = 'IN'
        self.fl = 0
        self.d_out_tmr.stop()


class Boss_Shot(pygame.sprite.Sprite):
    image = load_image('boss_shot.png')

    def __init__(self, group):
        global boss, v_bullet, pew
        pew.play()
        super().__init__(group)
        self.image = Boss_Shot.image
        self.rect = self.image.get_rect()
        self.v = v_bullet / 20
        s = all_sprites.sprites()[0]
        if s.rect.x < width / 2:
            x = abs(width / 2 - s.rect.x) - s.rect.width / 2
        elif s.rect.x > width / 2:
            x = abs(width / 2 - s.rect.x) + s.rect.width / 2
        else:
            x = abs(width / 2 - s.rect.x)
        y = abs(height / 2 - s.rect.y)
        h = math.sqrt(y ** 2 + x ** 2)
        k = h / self.v
        x = x / k
        y = y / k
        self.cl = pygame.time.Clock()
        self.rect.x = width / 2
        self.rect.y = boss.sprites()[-1].rect.y + boss.sprites()[-1].rect.height
        self.fin_x = s.rect.x
        self.fin_y = s.rect.y
        self.plus_x = x
        self.plus_y = y
        self.sound = pygame.mixer.Sound('music\shot.mp3')

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        global v_bullet, height, width, all_sprites, SCORE
        if self.fin_x > width / 2:
            x_pos = self.rect.x + self.plus_x
        elif self.fin_x < width / 2:
            x_pos = self.rect.x - self.plus_x
        elif self.fin_x == width / 2:
            x_pos = self.rect.x
        y_pos = self.rect.y + self.plus_y
        self.rect.x = x_pos
        self.rect.y = y_pos

        s = all_sprites.sprites()[0]
        if pygame.sprite.collide_mask(self, s):
            s.explosion()
            self.kill()


class Boss(pygame.sprite.Sprite):
    image = load_image('m_boss.png')

    def __init__(self, group):
        super().__init__(group)
        global width, boss
        self.image = Boss.image
        self.rect = self.image.get_rect()
        self.rect.y = -1 * self.image.get_height()
        self.rect.x = (width - self.image.get_width()) / 2
        self.v = 10
        self.plus_score = 200
        self.msec = 30
        self.count = 0
        self.ex = 0
        self.ex_coords = (0, 0)
        self.state = 'MOVING'
        self.HEALTH = 15
        self.boom = pygame.mixer.Sound(r'music\boom.mp3')

        self.mask = pygame.mask.from_surface(self.image)

        self.explode = pygame.sprite.Sprite()
        self.explode.image = load_image(f'explode\ex_{self.ex}.gif')
        self.explode.rect = self.explode.image.get_rect()

        self.do_shots = QTimer()
        self.do_shots.setInterval(500)
        self.do_shots.timeout.connect(self.shoot)

    def update(self, msec):
        global FAILED, boss, tmr, SCORE, prev_SCORE, boss_explosion
        if self.rect.y >= 0:
            self.v = 40
        if self.rect.y < 30:
            self.rect.y = self.rect.y + msec * self.v / 1000
        if self.rect.y == 29 and self.state == 'MOVING':
            self.do_shots.start()
            b = boss.sprites()[0]
            b.kill()
            boss.add(Diamond(boss))
            boss.add(b)
            self.state = 'STOP'
        if self.ex_coords != (0, 0):
            if self.ex <= 8:
                self.ex += 0.2
                self.explode.image = load_image(f'explode\ex_{str(self.ex).split(".")[0]}.gif')
            else:
                self.explode.kill()
                FAILED = 1

        if self.HEALTH <= 0:
            if len(boss) == 2:
                boss.sprites()[0].go_in()
            if len(boss) == 1:
                self.do_shots.stop()
                self.rect.x = self.rect.x - msec * self.v * 2 / 1000
        if self.rect.x + self.rect.width < 0:
            boss_explosion.stop()
            self.kill()
            tmr.start()

    def hit(self, sender):
        global boss
        boss.sprites()[0].color = 'pink'
        boss.sprites()[0].count = 0
        self.HEALTH -= 1
        self.boom.play()
        sender.kill()

    def shoot(self):
        global shots
        shots.add(Boss_Shot(shots))

    def explosion(self):
        s = all_sprites.sprites()[0]
        a = s.rect.x - ((self.explode.rect.width - s.rect.width) / 2)
        b = s.rect.y - ((self.explode.rect.height - s.rect.height) / 2)
        self.ex_coords = (a, b)
        self.explode.rect.x, self.explode.rect.y = a, b
        all_sprites.sprites()[0].image = pygame.transform.scale(load_image('player.png'), (0, 0))
        all_sprites.sprites()[0].rect.x, all_sprites.sprites()[0].rect.y = 0, 0
        all_sprites.add(self.explode)
        self.do_shots.stop()


class Villian_2(pygame.sprite.Sprite):
    image = load_image('villian2.png')

    def __init__(self, group):
        global v_villian, width
        super().__init__(group)
        self.sender = ''
        self.image = Villian_2.image
        self.rect = self.image.get_rect()
        left = all_sprites.sprites()[0].rect.x - 150
        right = all_sprites.sprites()[0].rect.x + 180
        if left <= 0:
            left = 0
        if right >= width - self.rect.width:
            right = width - self.rect.width
        self.rect.x = random.randint(left + 10, right - 10)
        self.rect.y = -64
        self.ex = 0
        self.v = v_villian
        self.explode = pygame.sprite.Sprite()
        self.explode.image = load_image(f'explode\ex_{self.ex}.gif')
        self.explode.rect = self.explode.image.get_rect()
        self.plus_score = 50
        self.a = random.randint(0, 2)
        group.add(self)

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, msec):
        global FAILED, all_sprites, SCORE, boss, width
        self.rect.y = self.rect.y + msec * self.v / 1000

        if self.rect.y > height:
            self.kill()

        if self.explode in all_sprites.sprites():
            if self.ex <= 8:
                self.ex += 0.2
                self.explode.image = load_image(f'explode\ex_{str(self.ex).split(".")[0]}.gif')
            else:
                self.kill()
                self.explode.kill()
        if len(boss) > 0:
            if self.a == 0:
                self.rect.x += 3
            else:
                self.rect.x -= 3

    def explosion(self, sender):
        if sender == 'player':
            self.sender = sender
            all_sprites.sprites()[0].explosion()
        else:
            self.explode.rect.x = self.rect.x - (self.explode.rect.width - self.rect.width) / 2
            self.explode.rect.y = self.rect.y - (self.explode.rect.height - self.rect.height) / 2
            all_sprites.add(self.explode)
            self.image = pygame.transform.scale(load_image('villian.png'), (0, 0))
            self.rect.x, self.rect.y = 0, 0


class Villian(pygame.sprite.Sprite):
    image = load_image('villian.png')

    def __init__(self, group):
        global v_villian, all_sprites
        super().__init__(group)
        self.sender = ''
        self.image = Villian.image
        self.rect = self.image.get_rect()
        left = all_sprites.sprites()[0].rect.x - 150
        right = all_sprites.sprites()[0].rect.x + 180
        if left <= 0:
            left = 0
        if right >= width - self.rect.width:
            right = width - self.rect.width
        self.rect.x = random.randint(left + 10, right - 10)
        self.rect.y = -64
        self.ex = 0
        self.v = v_villian
        self.explode = pygame.sprite.Sprite()
        self.explode.image = load_image(f'explode\ex_{self.ex}.gif')
        self.explode.rect = self.explode.image.get_rect()
        self.plus_score = 10
        self.a = random.randint(0, 2)
        group.add(self)

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, msec):
        global FAILED, all_sprites, SCORE, width, boss
        self.rect.y = self.rect.y + msec * self.v / 1000

        if self.rect.y > height:
            self.kill()

        if self.explode in all_sprites.sprites():
            if self.ex <= 8:
                self.ex += 0.2
                self.explode.image = load_image(f'explode\ex_{str(self.ex).split(".")[0]}.gif')
            else:
                self.kill()
                self.explode.kill()

        if len(boss) > 0:
            if self.a == 0:
                self.rect.x += 3
            else:
                self.rect.x -= 3

    def explosion(self, sender):
        if sender == 'player':
            self.sender = sender
            all_sprites.sprites()[0].explosion()
        else:
            self.explode.rect.x = self.rect.x - (self.explode.rect.width - self.rect.width) / 2
            self.explode.rect.y = self.rect.y - (self.explode.rect.height - self.rect.height) / 2
            all_sprites.add(self.explode)
            self.image = pygame.transform.scale(load_image('villian.png'), (0, 0))
            self.rect.x, self.rect.y = 0, 0


class Shot(pygame.sprite.Sprite):
    image = load_image('shot.png')

    def __init__(self, group):
        global all_sprites, v_bullet
        super().__init__(group)
        self.image = Shot.image
        self.rect = self.image.get_rect()
        self.cl = pygame.time.Clock()
        self.rect.x = all_sprites.sprites()[0].rect.x + all_sprites.sprites()[0].rect.width / 2 - 3
        self.rect.y = all_sprites.sprites()[0].rect.y
        self.v = v_bullet
        self.boom = pygame.mixer.Sound(r'music\boom.mp3')

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        global SCORE, boss
        w = self.cl.tick()
        y_pos = self.rect.y - self.v * w / 1000
        self.rect.y = y_pos
        if y_pos < 0:
            self.kill()

        for s in all_villians.sprites():
            if pygame.sprite.collide_mask(self, s):
                s.explosion('shot')
                SCORE += s.plus_score
                self.kill()
                self.boom.play()
        if len(boss) > 0:
            if pygame.sprite.collide_mask(self, boss.sprites()[-1]):
                self.kill()
            if len(boss) == 2:
                if pygame.sprite.collide_mask(self, boss.sprites()[0]) and boss.sprites()[0].ability is True:
                    boss.sprites()[-1].hit(self)


class Player(pygame.sprite.Sprite):
    image = load_image('player.png')

    def __init__(self, group):
        super().__init__(group)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.count = 0
        self.ex = 0
        self.explode = pygame.sprite.Sprite()
        self.explode.image = load_image(f'explode\ex_{self.ex}.gif')
        self.explode.rect = self.explode.image.get_rect()
        self.boom = pygame.mixer.Sound(r'music\boom.mp3')

    def update(self, position):
        global FAILED, all_villians, SCORE
        if self.image.get_rect()[3] + position[0] < width:
            self.rect.x = position[0]
        self.rect.y = height - 10 - self.image.get_rect()[-1]

        if self.explode in all_sprites.sprites():
            if self.ex <= 8:
                self.ex += 0.2
                self.explode.image = load_image(f'explode\ex_{str(self.ex).split(".")[0]}.gif')
            else:
                self.explode.kill()
                if len(boss) > 0:
                    boss.sprites()[-1].do_shots.stop()
                FAILED = 1

        for i in all_villians.sprites():
            if pygame.sprite.collide_mask(self, i):
                i.explosion('player')

    def shot(self, position):
        global shots
        shots.add(Shot(shots))

    def explosion(self):
        self.explode.rect.x = self.rect.x - (self.explode.rect.width - self.rect.width) / 2
        self.explode.rect.y = self.rect.y - (self.explode.rect.height - self.rect.height) / 2
        all_sprites.sprites()[0].image = pygame.transform.scale(load_image('player.png'), (0, 0))
        all_sprites.sprites()[0].rect.x, all_sprites.sprites()[0].rect.y = 0, 0
        all_sprites.add(self.explode)
        self.boom.play()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pygame.init()
    FAILED = 2
    menu_flag = 0
    menu()
    bg_count = 1
    bg = pygame.sprite.Sprite()
    bg.image = load_image(r'background\bg_1.jpg')
    bg.rect = bg.image.get_rect()
    bg.rect.x, bg.rect.y = 0, 0
    BG = pygame.sprite.Group()
    BG.add(bg)
    sound = pygame.mixer.Sound('music\Aut In Scuto.mp3')
    boom = pygame.mixer.Sound(r'music\boom.mp3')
    pew = pygame.mixer.Sound('music\shot.mp3')
    sound.play(-1)

    running = True
    while running:
        if FAILED == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEMOTION:
                    all_sprites.update(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    all_sprites.sprites()[0].shot(event.pos)
            screen.fill((0, 0, 0))
            BG.draw(screen)
            all_villians.update(VILLIANS.tick(60))
            if len(boss) > 0:
                boss.update(boss.sprites()[-1].msec)
            update_non_objects()
            shots.update()
            explodes.update()
            all_sprites.update((all_sprites.sprites()[0].rect.x, all_sprites.sprites()[0].rect.y))
            shots.draw(screen)
            all_sprites.draw(screen)
            all_villians.draw(screen)
            boss.draw(screen)
            explodes.draw(screen)
            screen.blit(text, (text_x, text_y))
        elif FAILED == 1:
            pause()
        elif FAILED == 2:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEMOTION:
                        check_menu(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if menu_flag == 1:
                        new_game()
                update_menu()
        pygame.display.flip()
    pygame.quit()
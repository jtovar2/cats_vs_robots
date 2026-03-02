import pygame
pygame.init()

# Screen & Physics
WIDTH, HEIGHT = 1000, 600
FLOOR_Y = 500
GRAVITY = 0.8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Fonts
big_font = pygame.font.SysFont("arial", 90)
medium_font = pygame.font.SysFont("arial", 50)
small_font = pygame.font.SysFont("arial", 35)

# ==============================
# AVAILABLE CHARACTERS
# ==============================
characters = [
    {
        "name": "Fighter 1",
        "sprites": ["data/sprite_neutral_p1.png", "data/sprite_attack_p1.png",
                    "data/sprite_defend_p1.png", "data/sprite_injured_p1.png",
                    "data/sprite_defeated_p1.png", "data/sprite_jumping_p1.png"]
    },
    {
        "name": "Fighter 2",
        "sprites": ["data/sprite_neutral_p2.png", "data/sprite_attack_p2.png",
                    "data/sprite_defend_p2.png", "data/sprite_injured_p2.png",
                    "data/sprite_defeated_p2.png", "data/sprite_jumping_p2.png"]
    }
]

# ==============================
# FIGHTER CLASS
# ==============================
class Fighter:
    def __init__(self, x, y, controls, sprite_list):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, 80, 120)
        self.controls = controls
        self.vel_y = 0
        self.health = 100
        self.alive = True
        
        self.is_jumping = False
        self.attack_timer = 0
        self.is_defending = False
        self.hit_timer = 0
        self.facing_right = True
        
        self.sprites = {
            'neutral': pygame.image.load(sprite_list[0]).convert_alpha(),
            'attack':  pygame.image.load(sprite_list[1]).convert_alpha(),
            'defend':  pygame.image.load(sprite_list[2]).convert_alpha(),
            'injured': pygame.image.load(sprite_list[3]).convert_alpha(),
            'dead':    pygame.image.load(sprite_list[4]).convert_alpha(),
            'jump':    pygame.image.load(sprite_list[5]).convert_alpha()
        }

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.health = 100
        self.alive = True
        self.vel_y = 0
        self.attack_timer = 0
        self.hit_timer = 0
        self.is_jumping = False

    def update(self, target):
        if not self.alive:
            return
        
        keys = pygame.key.get_pressed()
        self.facing_right = self.rect.centerx < target.rect.centerx
        self.is_defending = False

        if self.attack_timer == 0 and self.hit_timer == 0:
            if keys[self.controls['left']]:
                self.rect.x -= 7
            if keys[self.controls['right']]:
                self.rect.x += 7
            if keys[self.controls['jump']] and not self.is_jumping:
                self.vel_y = -16
                self.is_jumping = True
            if keys[self.controls['attack']]:
                self.perform_attack(target)
            if keys[self.controls['defend']]:
                self.is_defending = True

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom > FLOOR_Y:
            self.rect.bottom = FLOOR_Y
            self.is_jumping = False

        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.hit_timer > 0:
            self.hit_timer -= 1

        if self.health <= 0:
            self.health = 0
            self.alive = False

    def perform_attack(self, target):
        self.attack_timer = 20
        offset = 50 if self.facing_right else -50
        hitbox = pygame.Rect(self.rect.centerx + offset - 25, self.rect.y, 60, 60)
        
        if hitbox.colliderect(target.rect):
            if target.is_defending:
                target.health -= 2
            else:
                target.health -= 10
                target.hit_timer = 15

    def draw(self, surface):
        if not self.alive:
            img = self.sprites['dead']
        elif self.hit_timer > 0:
            img = self.sprites['injured']
        elif self.is_defending:
            img = self.sprites['defend']
        elif self.attack_timer > 0:
            img = self.sprites['attack']
        elif self.is_jumping:
            img = self.sprites['jump']
        else:
            img = self.sprites['neutral']

        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
            
        surface.blit(img, (self.rect.x, self.rect.y))


# ==============================
# CHARACTER SELECT FUNCTION
# ==============================
def character_select():
    p1_choice = 0
    p2_choice = 1
    p1_locked = False
    p2_locked = False

    selecting = True
    while selecting:
        screen.fill((20, 20, 20))

        title = big_font.render("CHARACTER SELECT", True, (255,255,255))
        screen.blit(title, (WIDTH//2 - 250, 50))

        for i, char in enumerate(characters):
            x_pos = 300 + i * 300
            name = medium_font.render(char["name"], True, (255,255,255))
            screen.blit(name, (x_pos - 50, 250))

            if i == p1_choice:
                pygame.draw.rect(screen, (0,255,0), (x_pos-60,240,200,100), 3)
            if i == p2_choice:
                pygame.draw.rect(screen, (255,0,0), (x_pos-60,240,200,100), 3)

        instructions = small_font.render("P1: A/D + E to lock    P2: J/L + O to lock", True, (200,200,200))
        screen.blit(instructions, (WIDTH//2 - 300, 500))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if not p1_locked:
                    if event.key == pygame.K_a:
                        p1_choice = (p1_choice - 1) % len(characters)
                    if event.key == pygame.K_d:
                        p1_choice = (p1_choice + 1) % len(characters)
                    if event.key == pygame.K_e:
                        p1_locked = True

                if not p2_locked:
                    if event.key == pygame.K_j:
                        p2_choice = (p2_choice - 1) % len(characters)
                    if event.key == pygame.K_l:
                        p2_choice = (p2_choice + 1) % len(characters)
                    if event.key == pygame.K_o:
                        p2_locked = True

        if p1_locked and p2_locked:
            selecting = False

        pygame.display.update()
        clock.tick(60)

    return characters[p1_choice]["sprites"], characters[p2_choice]["sprites"]


# ==============================
# START GAME
# ==============================
p1_sprites, p2_sprites = character_select()

p1_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_f, 'attack': pygame.K_e, 'defend': pygame.K_r}
p2_controls = {'left': pygame.K_j, 'right': pygame.K_l, 'jump': pygame.K_SEMICOLON, 'attack': pygame.K_o, 'defend': pygame.K_p}

player1 = Fighter(200, 380, p1_controls, p1_sprites)
player2 = Fighter(700, 380, p2_controls, p2_sprites)

# Simple loop after select
run = True
while run:
    clock.tick(60)
    screen.fill((30,30,30))

    pygame.draw.line(screen, (255,255,255), (0,FLOOR_Y),(WIDTH,FLOOR_Y),2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    player1.update(player2)
    player2.update(player1)

    player1.draw(screen)
    player2.draw(screen)

    pygame.display.update()

pygame.quit()
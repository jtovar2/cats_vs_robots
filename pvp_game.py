import pygame

pygame.init()

# Screen & Physics
WIDTH, HEIGHT = 1000, 600
FLOOR_Y = 500
GRAVITY = 0.8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Fonts
big_font = pygame.font.SysFont("arial", 100)
small_font = pygame.font.SysFont("arial", 40)

# --- CHARACTER SELECT LOGIC ---
possible_characters = ['tingo', 'sushi', 'robot']

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def select_screen():
    selecting = True
    p1_index = 0
    p2_index = 1
    p1_ready = False
    p2_ready = False

    while selecting:
        screen.fill((20, 20, 20))
        draw_text("SELECT YOUR FIGHTER", small_font, (255, 255, 255), WIDTH//2 - 180, 50)

        # Player 1 Box
        p1_color = (0, 255, 0) if p1_ready else (255, 255, 255)
        pygame.draw.rect(screen, p1_color, (150, 150, 300, 300), 2)
        draw_text("PLAYER 1", small_font, p1_color, 220, 100)
        draw_text(possible_characters[p1_index].upper(), big_font, p1_color, 170, 250)
        draw_text("A / D to Change | E to Confirm", pygame.font.SysFont("arial", 20), (150, 150, 150), 180, 460)

        # Player 2 Box
        p2_color = (0, 255, 0) if p2_ready else (255, 255, 255)
        pygame.draw.rect(screen, p2_color, (550, 150, 300, 300), 2)
        draw_text("PLAYER 2", small_font, p2_color, 620, 100)
        draw_text(possible_characters[p2_index].upper(), big_font, p2_color, 570, 250)
        draw_text("J / L to Change | O to Confirm", pygame.font.SysFont("arial", 20), (150, 150, 150), 580, 460)

        # Error message if same character selected
        if possible_characters[p1_index] == possible_characters[p2_index]:
            draw_text("CANNOT SELECT SAME CHARACTER", small_font, (255, 0, 0), WIDTH//2 - 250, 520)
            p1_ready = p2_ready = False # Force unready if they match

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                # P1 Controls
                if not p1_ready:
                    if event.key == pygame.K_a: p1_index = (p1_index - 1) % len(possible_characters)
                    if event.key == pygame.K_d: p1_index = (p1_index + 1) % len(possible_characters)
                    if event.key == pygame.K_e and possible_characters[p1_index] != possible_characters[p2_index]:
                        p1_ready = True
                # P2 Controls
                if not p2_ready:
                    if event.key == pygame.K_j: p2_index = (p2_index - 1) % len(possible_characters)
                    if event.key == pygame.K_l: p2_index = (p2_index + 1) % len(possible_characters)
                    if event.key == pygame.K_o and possible_characters[p1_index] != possible_characters[p2_index]:
                        p2_ready = True
                
                # Undo Ready
                if event.key == pygame.K_r: p1_ready = False
                if event.key == pygame.K_p: p2_ready = False

        if p1_ready and p2_ready:
            return possible_characters[p1_index], possible_characters[p2_index]

        pygame.display.update()
        clock.tick(60)

# --- FIGHTER CLASS (UNCHANGED) ---
class Fighter:
    def __init__(self, x, y, p_id, controls, char_name):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, 80, 120)
        self.p_id = p_id
        self.controls = controls
        self.vel_y = 0
        self.health = 100
        self.alive = True
        self.is_jumping = False
        self.attack_timer = 0
        self.is_defending = False
        self.hit_timer = 0
        self.facing_right = True
        self.char_name = char_name
        
        # Load sprites based on selection
        self.sprites = {
            'neutral': pygame.image.load(f'data/{char_name}/sprite_neutral.png').convert_alpha(),
            'attack':  pygame.image.load(f'data/{char_name}/sprite_attack.png').convert_alpha(),
            'defend':  pygame.image.load(f'data/{char_name}/sprite_defend.png').convert_alpha(),
            'injured': pygame.image.load(f'data/{char_name}/sprite_injured.png').convert_alpha(),
            'dead':    pygame.image.load(f'data/{char_name}/sprite_defeated.png').convert_alpha(),
            'jump':    pygame.image.load(f'data/{char_name}/sprite_jumping.png').convert_alpha()
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
        if not self.alive: return
        keys = pygame.key.get_pressed()
        self.facing_right = self.rect.centerx < target.rect.centerx
        self.is_defending = False

        if self.attack_timer == 0 and self.hit_timer == 0:
            if keys[self.controls['left']]: self.rect.x -= 7
            if keys[self.controls['right']]: self.rect.x += 7
            if keys[self.controls['jump']] and not self.is_jumping:
                self.vel_y = -16
                self.is_jumping = True
            if keys[self.controls['attack']]: self.perform_attack(target)
            if keys[self.controls['defend']]: self.is_defending = True

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        if self.rect.bottom > FLOOR_Y:
            self.rect.bottom = FLOOR_Y
            self.is_jumping = False

        if self.attack_timer > 0: self.attack_timer -= 1
        if self.hit_timer > 0: self.hit_timer -= 1
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def perform_attack(self, target):
        self.attack_timer = 20
        offset = 50 if self.facing_right else -50
        hitbox = pygame.Rect(self.rect.centerx + offset - 25, self.rect.y, 60, 60)
        if hitbox.colliderect(target.rect):
            if target.is_defending: target.health -= 2
            else:
                target.health -= 10
                target.hit_timer = 15

    def draw(self, surface):
        if not self.alive: img = self.sprites['dead']
        elif self.hit_timer > 0: img = self.sprites['injured']
        elif self.is_defending: img = self.sprites['defend']
        elif self.attack_timer > 0: img = self.sprites['attack']
        elif self.is_jumping: img = self.sprites['jump']
        else: img = self.sprites['neutral']

        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        surface.blit(img, (self.rect.x, self.rect.y))

def draw_health_bar(surface, x, y, health, reverse=False):
    ratio = max(health, 0) / 100
    pygame.draw.rect(surface, (60, 60, 60), (x, y, 300, 25))
    color = (0, 200, 0) if ratio > 0.6 else (230, 200, 0) if ratio > 0.3 else (200, 0, 0)
    if reverse:
        pygame.draw.rect(surface, color, (x + 300 * (1 - ratio), y, 300 * ratio, 25))
    else:
        pygame.draw.rect(surface, color, (x, y, 300 * ratio, 25))
    pygame.draw.rect(surface, (255, 255, 255), (x, y, 300, 25), 3)

# --- INITIALIZATION ---
p1_choice, p2_choice = select_screen()

p1_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'attack': pygame.K_e, 'defend': pygame.K_r}
p2_controls = {'left': pygame.K_j, 'right': pygame.K_l, 'jump': pygame.K_i, 'attack': pygame.K_o, 'defend': pygame.K_p}

player1 = Fighter(200, 380, 1, p1_controls, p1_choice)
player2 = Fighter(700, 380, 2, p2_controls, p2_choice)

p1_wins = 0
p2_wins = 0
round_over = False
run = True

while run:
    clock.tick(60)
    screen.fill((30, 30, 30))
    pygame.draw.line(screen, (255, 255, 255), (0, FLOOR_Y), (WIDTH, FLOOR_Y), 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False

    if not round_over:
        player1.update(player2)
        player2.update(player1)

    draw_health_bar(screen, 50, 40, player1.health)
    draw_health_bar(screen, WIDTH - 350, 40, player2.health, reverse=True)
    player1.draw(screen)
    player2.draw(screen)

    if not player1.alive or not player2.alive:
        if not round_over:
            round_over = True
            round_timer = pygame.time.get_ticks()
            if player1.alive: p1_wins += 1
            else: p2_wins += 1

        if (pygame.time.get_ticks() // 300) % 2 == 0:
            draw_text("KO", big_font, (255, 0, 0), WIDTH//2 - 100, HEIGHT//2 - 100)

        if pygame.time.get_ticks() - round_timer > 3000:
            player1.reset()
            player2.reset()
            round_over = False

    pygame.display.update()

pygame.quit()
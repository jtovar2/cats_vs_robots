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
possible_characters = ['tingo', 'sushi', 'baby', 'robot']

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def select_screen():
    selecting = True
    p1_index = 0
    p2_index = 1
    p1_ready = False
    p2_ready = False

    # Load portraits
    portraits = {}
    for char in possible_characters:
        img = pygame.image.load(f"data/{char}/sprite_neutral.png").convert_alpha()
        portraits[char] = pygame.transform.scale(img, (220, 220))

    desc_font = pygame.font.SysFont("arial", 22)
    small_ui = pygame.font.SysFont("arial", 20)

    pulse_timer = 0

    while selecting:
        pulse_timer += 0.05
        screen.fill((15, 15, 25))

        # Title
        draw_text("SELECT YOUR FIGHTER", small_font, (255, 255, 255), WIDTH//2 - 180, 40)

        # VS Text
        vs_scale = 1 + 0.05 * pygame.math.Vector2(1,0).rotate(pulse_timer*50).x
        vs_font = pygame.font.SysFont("arial", int(80 * vs_scale))
        draw_text("VS", vs_font, (200, 50, 50), WIDTH//2 - 40, 250)

        # ---------------- PLAYER 1 ----------------
        p1_color = (0, 255, 0) if p1_ready else (255, 255, 255)
        p1_box = pygame.Rect(100, 130, 300, 350)
        pygame.draw.rect(screen, p1_color, p1_box, 3)

        draw_text("PLAYER 1", small_font, p1_color, 170, 90)

        char1 = possible_characters[p1_index]
        screen.blit(portraits[char1], (140, 160))
        draw_text(char1.upper(), big_font, p1_color, 120, 380)

        draw_text("A/D Change", small_ui, (150,150,150), 150, 430)
        draw_text("E Confirm", small_ui, (150,150,150), 160, 455)

        if p1_ready:
            overlay = pygame.Surface((300, 350), pygame.SRCALPHA)
            overlay.fill((0, 255, 0, 60))
            screen.blit(overlay, (100, 130))

        # ---------------- PLAYER 2 ----------------
        p2_color = (0, 255, 0) if p2_ready else (255, 255, 255)
        p2_box = pygame.Rect(600, 130, 300, 350)
        pygame.draw.rect(screen, p2_color, p2_box, 3)

        draw_text("PLAYER 2", small_font, p2_color, 670, 90)

        char2 = possible_characters[p2_index]
        screen.blit(portraits[char2], (640, 160))
        draw_text(char2.upper(), big_font, p2_color, 620, 380)

        draw_text("J/L Change", small_ui, (150,150,150), 660, 430)
        draw_text("O Confirm", small_ui, (150,150,150), 670, 455)

        if p2_ready:
            overlay = pygame.Surface((300, 350), pygame.SRCALPHA)
            overlay.fill((0, 255, 0, 60))
            screen.blit(overlay, (600, 130))

        # Prevent same character
        if char1 == char2:
            draw_text("CANNOT SELECT SAME CHARACTER", small_font, (255, 0, 0), WIDTH//2 - 250, 520)
            p1_ready = False
            p2_ready = False

        # ---------------- INPUT ----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if not p1_ready:
                    if event.key == pygame.K_a:
                        p1_index = (p1_index - 1) % len(possible_characters)
                    if event.key == pygame.K_d:
                        p1_index = (p1_index + 1) % len(possible_characters)
                    if event.key == pygame.K_e and char1 != char2:
                        p1_ready = True

                if not p2_ready:
                    if event.key == pygame.K_j:
                        p2_index = (p2_index - 1) % len(possible_characters)
                    if event.key == pygame.K_l:
                        p2_index = (p2_index + 1) % len(possible_characters)
                    if event.key == pygame.K_o and char1 != char2:
                        p2_ready = True

                if event.key == pygame.K_r:
                    p1_ready = False
                if event.key == pygame.K_p:
                    p2_ready = False

        if p1_ready and p2_ready:
            pygame.time.delay(800)
            return char1, char2

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

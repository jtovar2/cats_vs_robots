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

class Fighter:
    def __init__(self, x, y, p_id, controls,  char_name):
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
        
        neutral = f'data/{self.char_name}/sprite_neutral.png'
        attack = f'data/{self.char_name}/sprite_attack.png'
        defend = f'data/{self.char_name}/sprite_defend.png'
        injured = f'data/{self.char_name}/sprite_injured.png'
        dead = f'data/{self.char_name}/sprite_defeated.png'
        jump = f'data/{self.char_name}/sprite_jumping.png'
        self.sprites = {
            'neutral': pygame.image.load(neutral).convert_alpha(),
            'attack':  pygame.image.load(attack).convert_alpha(),
            'defend':  pygame.image.load(defend).convert_alpha(),
            'injured': pygame.image.load(injured).convert_alpha(),
            'dead':    pygame.image.load(dead).convert_alpha(),
            'jump':    pygame.image.load(jump).convert_alpha()
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


# Health Bar
def draw_health_bar(surface, x, y, health, max_health=100, width=300, height=25, reverse=False):
    ratio = max(health, 0) / max_health
    
    pygame.draw.rect(surface, (60, 60, 60), (x, y, width, height))

    if ratio > 0.6:
        color = (0, 200, 0)
    elif ratio > 0.3:
        color = (230, 200, 0)
    else:
        color = (200, 0, 0)

    if reverse:
        pygame.draw.rect(surface, color,
                         (x + width * (1 - ratio), y, width * ratio, height))
    else:
        pygame.draw.rect(surface, color,
                         (x, y, width * ratio, height))

    pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 3)

possible_characters = ['tabby', 'robot']
# Setup
p1_files = ["data/sprite_neutral_p1.png", "data/sprite_attack_p1.png", "data/sprite_defend_p1.png", 
            "data/sprite_injured_p1.png", "data/sprite_defeated_p1.png", "data/sprite_jumping_p1.png"]
p2_files = ["data/sprite_neutral_p2.png", "data/sprite_attack_p2.png", "data/sprite_defend_p2.png", 
            "data/sprite_injured_p2.png", "data/sprite_defeated_p2.png", "data/sprite_jumping_p2.png"]

p1_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_f, 'attack': pygame.K_e, 'defend': pygame.K_r}
p2_controls = {'left': pygame.K_j, 'right': pygame.K_l, 'jump': pygame.K_SEMICOLON, 'attack': pygame.K_o, 'defend': pygame.K_p}

player1 = Fighter(200, 380, 1, p1_controls, 'tabby')
player2 = Fighter(700, 380, 2, p2_controls, 'robot')

# Round System
p1_wins = 0
p2_wins = 0
round_over = False
round_timer = 0
ko_flash = True


# Main Loop
run = True
while run:
    clock.tick(60)
    screen.fill((30, 30, 30))
    pygame.draw.line(screen, (255, 255, 255), (0, FLOOR_Y), (WIDTH, FLOOR_Y), 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if not round_over:
        player1.update(player2)
        player2.update(player1)

    draw_health_bar(screen, 50, 40, player1.health)
    draw_health_bar(screen, WIDTH - 350, 40, player2.health, reverse=True)

    # Draw win counters
    p1_text = small_font.render(f"Wins: {p1_wins}", True, (255,255,255))
    p2_text = small_font.render(f"Wins: {p2_wins}", True, (255,255,255))
    screen.blit(p1_text, (50, 75))
    screen.blit(p2_text, (WIDTH - 200, 75))

    player1.draw(screen)
    player2.draw(screen)

    # KO + Round Logic
    if not player1.alive or not player2.alive:
        if not round_over:
            round_over = True
            round_timer = pygame.time.get_ticks()
            if player1.alive:
                p1_wins += 1
            else:
                p2_wins += 1

        # Flash KO text
        if (pygame.time.get_ticks() // 300) % 2 == 0:
            ko_text = big_font.render("KO", True, (255, 0, 0))
            screen.blit(ko_text, (WIDTH//2 - 100, HEIGHT//2 - 100))

        # Reset round after 3 seconds
        if pygame.time.get_ticks() - round_timer > 3000:
            if p1_wins == 2 or p2_wins == 2:
                # Match Over
                winner = "PLAYER 1 WINS!" if p1_wins == 2 else "PLAYER 2 WINS!"
                win_text = big_font.render(winner, True, (255,255,255))
                screen.blit(win_text, (WIDTH//2 - 300, HEIGHT//2))
            else:
                player1.reset()
                player2.reset()
                round_over = False

    pygame.display.update()

pygame.quit()

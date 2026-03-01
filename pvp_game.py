import pygame

# Initialize Pygame
pygame.init()
# Screen & Physics
WIDTH, HEIGHT = 1000, 600
FLOOR_Y = 500
GRAVITY = 0.8


class Fighter:
    def __init__(self, x, y, p_id, controls, sprite_list):
        self.rect = pygame.Rect(x, y, 80, 120) # Adjust size to fit your sprites
        self.p_id = p_id
        self.controls = controls
        self.vel_y = 0
        self.health = 100
        self.alive = True
        
        # State Management
        self.is_jumping = False
        self.attack_timer = 0
        self.is_defending = False
        self.hit_timer = 0
        self.facing_right = True
        
        # Load Sprites into a dictionary
        self.sprites = {
            'neutral': pygame.image.load(sprite_list[0]).convert_alpha(),
            'attack':  pygame.image.load(sprite_list[1]).convert_alpha(),
            'defend':  pygame.image.load(sprite_list[2]).convert_alpha(),
            'injured': pygame.image.load(sprite_list[3]).convert_alpha(),
            'dead':    pygame.image.load(sprite_list[4]).convert_alpha(),
            'jump':    pygame.image.load(sprite_list[5]).convert_alpha()
        }

    def update(self, target):
        if not self.alive: return
        
        keys = pygame.key.get_pressed()
        
        # 1. Direction Logic: Face the opponent
        if self.rect.centerx < target.rect.centerx:
            self.facing_right = True
        else:
            self.facing_right = False

        # 2. Movement & Input
        self.is_defending = False
        if self.attack_timer == 0 and self.hit_timer == 0:
            if keys[self.controls['left']]: self.rect.x -= 7
            if keys[self.controls['right']]: self.rect.x += 7
            if keys[self.controls['jump']] and not self.is_jumping:
                self.vel_y = -16
                self.is_jumping = True
            if keys[self.controls['attack']]:
                self.perform_attack(target)
            if keys[self.controls['defend']]:
                self.is_defending = True

        # 3. Physics
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        if self.rect.bottom > FLOOR_Y:
            self.rect.bottom = FLOOR_Y
            self.is_jumping = False

        # 4. Timers
        if self.attack_timer > 0: self.attack_timer -= 1
        if self.hit_timer > 0: self.hit_timer -= 1
        if self.health <= 0: self.alive = False

    def perform_attack(self, target):
        self.attack_timer = 20
        # Determine hitbox position based on direction
        offset = 50 if self.facing_right else -50
        hitbox = pygame.Rect(self.rect.centerx + offset - 25, self.rect.y, 60, 60)
        
        if hitbox.colliderect(target.rect):
            if target.is_defending:
                target.health -= 2 # Chip damage
            else:
                target.health -= 10
                target.hit_timer = 15 # Stun/Injured state

    def draw(self, surface):
        # Determine which sprite to use
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

        # Flip image if facing left
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
            
        surface.blit(img, (self.rect.x, self.rect.y))

# FIX 1: Set the video mode before creating objects that load images
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
# --- Main Setup ---
p1_files = ["data/sprite_neutral_p1.png", "data/sprite_attack_p1.png", "data/sprite_defend_p1.png", 
            "data/sprite_injured_p1.png", "data/sprite_defeated_p1.png", "data/sprite_jumping_p1.png"]
p2_files = ["data/sprite_neutral_p2.png", "data/sprite_attack_p2.png", "data/sprite_defend_p2.png", 
            "data/sprite_injured_p2.png", "data/sprite_defeated_p2.png", "data/sprite_jumping_p2.png"]

# ... (Insert p1_controls and p2_controls from previous snippet) ...

p1_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_f, 'attack': pygame.K_e, 'defend': pygame.K_r}
p2_controls = {'left': pygame.K_j, 'right': pygame.K_l, 'jump': pygame.K_SEMICOLON, 'attack': pygame.K_o, 'defend': pygame.K_p}

###build player objects
player1 = Fighter(200, 380, 1, p1_controls, p1_files)
player2 = Fighter(700, 380, 2, p2_controls, p2_files)


# Main Game Loop
run = True
while run:
    clock.tick(60)
    screen.fill((30, 30, 30)) # Dark background
    
    # Floor
    pygame.draw.line(screen, (255, 255, 255), (0, FLOOR_Y), (WIDTH, FLOOR_Y), 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    player1.update(player2)
    player2.update(player1)
    
    player1.draw(screen)
    player2.draw(screen)
    
    pygame.display.update()

pygame.quit()

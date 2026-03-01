import pygame

# Initialize Pygame
pygame.init()

# Screen Setup
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Physics Constants
GRAVITY = 0.8
FLOOR_Y = 500

class Fighter:
    def __init__(self, x, y, color, controls):
        self.rect = pygame.Rect(x, y, 50, 100)
        self.color = color
        self.vel_y = 0
        self.health = 100
        self.controls = controls
        self.is_jumping = False
        self.is_attacking = False
        self.is_defending = False
        self.attack_cooldown = 0
        
    def move(self, target):
        keys = pygame.key.get_pressed()
        
        # Reset defense state
        self.is_defending = False
        
        # Horizontal Movement
        if keys[self.controls['left']]:
            self.rect.x -= 7
        if keys[self.controls['right']]:
            self.rect.x += 7
            
        # Jump
        if keys[self.controls['jump']] and not self.is_jumping:
            self.vel_y = -15
            self.is_jumping = True
            
        # Attack
        if keys[self.controls['attack']] and self.attack_cooldown == 0:
            self.attack(target)
            self.attack_cooldown = 20
            
        # Defend
        if keys[self.controls['defend']]:
            self.is_defending = True

        # Apply Gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        # Floor Collision
        if self.rect.bottom > FLOOR_Y:
            self.rect.bottom = FLOOR_Y
            self.is_jumping = False
            
        # Screen Boundaries
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def attack(self, target):
        self.is_attacking = True
        # Create an attack hitbox slightly in front of the player
        hitbox = pygame.Rect(self.rect.centerx, self.rect.y, 60, 50)
        
        if hitbox.colliderect(target.rect):
            if not target.is_defending:
                target.health -= 10
                print(f"Hit! Target Health: {target.health}")
                if target.health <= 0:
                    print(f"{target.color} terminated")
            else:
                print("Blocked!")

    def draw(self, surface):
        # Draw the main body
        pygame.draw.rect(surface, self.color, self.rect)
        # Visual cue for defending
        if self.is_defending:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 5)

# Control Schemes
p1_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_f, 'attack': pygame.K_e, 'defend': pygame.K_r}
p2_controls = {'left': pygame.K_j, 'right': pygame.K_l, 'jump': pygame.K_SEMICOLON, 'attack': pygame.K_o, 'defend': pygame.K_p}

# Create Players
player1 = Fighter(200, 400, (255, 0, 0), p1_controls)
player2 = Fighter(700, 400, (0, 0, 255), p2_controls)

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

    player1.move(player2)
    player2.move(player1)
    
    player1.draw(screen)
    player2.draw(screen)
    
    pygame.display.update()

pygame.quit()

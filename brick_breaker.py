'''
Brick Breaker
'''

# Import the pygame libary.
import pygame

# Import the random library.
import random

# Initialize the pygame module.
pygame.init()

# Set the game display.
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 1000
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Brick Breaker')

# Set the FPS and clock.
FPS = 120
clock = pygame.time.Clock()

# Set the colors for the game.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 102, 255)
GREEN = (71, 209, 71)
RED = (230, 0, 0)
PINK = (255, 102, 153)

# Define classes.
class Game:
    ''' A class to control and update the gameplay'''
    def __init__(self, player, paddle, paddle_group, ball_group, brick_group, powerup_group):
        '''Initialize the game'''
        self.player = player
        self.paddle = paddle
        self.paddle_group = paddle_group
        self.ball_group = ball_group
        self.brick_group = brick_group
        self.powerup_group = powerup_group

        self.level_number = 1

        self.HUD_height = 40
        self.font = pygame.font.Font('assets/Mechanical-g5Y5.otf', 32)

        self.running = True

        self.level_timer = 0

        # Set the sounds for the game.
        self.brick_hit = pygame.mixer.Sound('assets/brick_hit.wav')
        self.brick_hit.set_volume(0.5)
        self.paddle_hit = pygame.mixer.Sound('assets/paddle_hit.wav')
        self.paddle_hit.set_volume(0.2)

        self.level_complete = pygame.mixer.Sound('assets/level_complete.wav')
        self.life_loss = pygame.mixer.Sound('assets/life_loss.wav')

    def update(self):
        '''Update the game'''
        self.check_collisions()
        self.check_fallen_ball()
        self.check_level_completion()
        self.check_fallen_powerup()

    def draw(self):
        '''Draw the HUD and other information to the display'''

        # Draw a line separating the HUD from the gameplay window.
        pygame.draw.line(display_surface, WHITE, (0, self.HUD_height), (WINDOW_WIDTH, self.HUD_height), 3)

        # Set text.
        score_text = self.font.render(f'Score: {self.player.score}', True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.left = 15
        score_rect.centery = self.HUD_height / 2

        time_text = self.font.render(f'{self.level_timer}', True, WHITE)
        time_rect = time_text.get_rect()
        time_rect.centerx = WINDOW_WIDTH / 2
        time_rect.centery = self.HUD_height / 2

        lives_text = self.font.render(f'Lives: {self.player.lives}', True, WHITE)
        lives_rect = lives_text.get_rect()
        lives_rect.right = WINDOW_WIDTH - 15
        lives_rect.centery = self.HUD_height / 2

        # Blit the text to the display.
        display_surface.blit(lives_text, lives_rect)
        display_surface.blit(score_text, score_rect)
        display_surface.blit(time_text, time_rect)

    def check_collisions(self):
        # Check collisions between the ball and the top, left, and right walls.
        for ball in self.ball_group:
            if (ball.rect.left <= 0) and (ball.dx < 0):
                ball.dx = (-1) * ball.dx
            if (ball.rect.right >= WINDOW_WIDTH) and (ball.dx > 0):
                ball.dx = (-1) * ball.dx
            if (ball.rect.top <= self.HUD_height) and (ball.dy < 0):
                ball.dy = (-1) * ball.dy

        # Check for collisions between the ball and the paddle.
        if pygame.sprite.spritecollide(self.paddle, self.ball_group, False):
            self.paddle_hit.play()
            for ball in pygame.sprite.groupcollide(self.ball_group, self.paddle_group, False, False):
                alpha = ball.rect.centerx - self.paddle.rect.centerx
                beta = self.paddle.width / 2
                ball.dx = alpha / beta
                ball.dy = - (2 - (ball.dx) ** 2) ** 0.5

        # Check for collision between the ball and bricks.
        for ball in self.ball_group:
            for brick in pygame.sprite.spritecollide(ball, self.brick_group, False):
                # Set the ball_brick_collision variable to False.
                ball_brick_collision = False

                # Set the hit zones within the brick that has been struck.
                hit_zone_buffer = ball.diameter / 2
                hit_zone_l = pygame.Rect(brick.rect.topleft, (hit_zone_buffer, brick.height))
                hit_zone_r = pygame.Rect((brick.rect.right - hit_zone_buffer, brick.rect.top), (hit_zone_buffer, brick.height))
                hit_zone_b = pygame.Rect((brick.rect.left, brick.rect.bottom - hit_zone_buffer), (brick.width, hit_zone_buffer))
                hit_zone_t = pygame.Rect(brick.rect.topleft,(brick.width, hit_zone_buffer))

                # Check which hit zone the ball has collided with.
                if hit_zone_l.collidepoint(ball.rect.right, ball.rect.centery):
                    ball_brick_collision = True
                    ball.dx = (-1) * ball.dx
                elif hit_zone_r.collidepoint(ball.rect.left, ball.rect.centery):
                    ball_brick_collision = True
                    ball.dx = (-1) * ball.dx
                elif hit_zone_b.collidepoint(ball.rect.centerx, ball.rect.top):
                    ball_brick_collision = True
                    ball.dy = (-1) * ball.dy
                elif hit_zone_t.collidepoint(ball.rect.centerx, ball.rect.bottom):
                    ball_brick_collision = True
                    ball.dy = (-1) * ball.dy

                if ball_brick_collision:
                    # Play the hit sound and kill the brick.
                    self.brick_hit.play()
                    brick.kill()

                    # Determine whether to generate a powerup.
                    if random.choice(list(range(5))) == random.choice(list(range(5))):
                        new_powerup = PowerUp(brick.rect.centerx, brick.rect.centery, random.choice(['AddBall']))
                        self.powerup_group.add(new_powerup)

                # Add to the player's score based on the level number and the level timer.
                if self.level_timer <= 60:
                    self.player.score += self.level_number * 10 + (60 - self.level_timer)
                else:
                    self.player.score += self.level_number * 10
        
        # Check for collisions between the paddle and a powerup.
        for powerup in self.powerup_group:
            if pygame.sprite.spritecollide(powerup, self.paddle_group, False):
                powerup.kill()
                if powerup.ptype == 'AddBall':
                    self.add_ball()

    def check_fallen_ball(self):
        '''Check if any of the player's balls has fallen off of the screen'''
        # If a ball has fallen off the screen, check whether it is the last ball the player has.
        # If the player has more balls, remove the ball from the ball group.
        # If the player has run out of lives, run the game over conditions and prompt the player to play again.
        for ball in self.ball_group:
            if ball.rect.top >= WINDOW_HEIGHT:
                # If the player has more balls available, simply kill the ball that has fallen off the screen.
                if len(self.ball_group) > 1:
                    ball.kill()
                else:
                    # Remove a life.
                    self.player.lives -= 1

                    # Play the life lost sound.
                    self.life_loss.play()

                    # Reset the position of the ball and paddle.
                    ball.reset()
                    self.paddle.reset()

                    # Remove all current powerups on the screen
                    self.powerup_group.empty()

                    # Update the display.
                    display_surface.fill(BLACK)
                    self.draw()
                    self.powerup_group.draw(display_surface)
                    self.paddle_group.draw(display_surface)
                    self.brick_group.draw(display_surface)
                    pygame.display.update()

                    # Check if the player has run out of lives.
                    if self.player.lives == 0:
                        self.pause_game('Game Over!', 'Press ENTER to Play Again')
                        self.reset_game()
                    else:
                        self.pause_game('Life Lost!', 'Press ENTER to Continue', False)

    def check_fallen_powerup(self):
        '''Check whether any existing powerups have fallen off the screen; if so, delete it'''
        for powerup in self.powerup_group:
            if powerup.rect.top >= WINDOW_HEIGHT:
                powerup.kill()

    def check_level_completion(self):
        '''Check whether the current level has been completed'''
        # Check whether there are no more bricks remaining.
        if len(self.brick_group) == 0:
            # Increment the level number.
            self.level_number += 1

            # Reset the paddle position.
            self.paddle.reset()

            # Remove all of the balls from the ball group.
            self.ball_group.empty()
            
            # Update the display.
            display_surface.fill(BLACK)
            self.ball_group.draw(display_surface)
            self.paddle_group.draw(display_surface)
            pygame.display.update()

            # Play the level complete jingle.
            self.level_complete.play()
            
            # Pause the game.
            self.pause_game('Level Complete', 'Press ENTER to Continue', True)

            # Start the next level.
            self.start_new_level()
        else:
            pass

    def add_ball(self):
        new_ball = Ball(self.paddle_group.sprites()[0].rect.centerx, self.paddle_group.sprites()[0].rect.top, self.level_number + 3)
        self.ball_group.add(new_ball)

    def start_new_level(self):
        '''Start a new level of the game'''
        self.level_timer = 0
        brick_horizontal_buffer = 5
        brick_vertical_buffer = 5
        brick_columns = 11
        brick_rows = 12
        brick_width = ((WINDOW_WIDTH) - (brick_columns + 1) * brick_horizontal_buffer) / brick_columns
        brick_height = ((WINDOW_HEIGHT) * (1/2) - (brick_rows + 1) * brick_vertical_buffer) / brick_rows

        if self.level_number == 1:
            self.level = Level(f'levels/level_{self.level_number}.txt', 'Heart')
            my_ball = Ball(self.paddle_group.sprites()[0].rect.centerx, self.paddle_group.sprites()[0].rect.top, self.level_number + 3)
            self.ball_group.add(my_ball)
        elif self.level_number == 2:
            self.level = Level(f'levels/level_{self.level_number}.txt', 'Box')
            my_ball = Ball(self.paddle_group.sprites()[0].rect.centerx, self.paddle_group.sprites()[0].rect.top, self.level_number + 3)
            self.ball_group.add(my_ball)
        elif self.level_number == 3:
            self.level = Level(f'levels/level_{self.level_number}.txt', 'Hourglass')
            my_ball = Ball(self.paddle_group.sprites()[0].rect.centerx, self.paddle_group.sprites()[0].rect.top, self.level_number + 3)
            self.ball_group.add(my_ball)
        else:
            self.pause_game('You Win!', 'Press ENTER to play again!', True)
            self.player.reset()
            self.level_number = 1
            my_ball = Ball(self.paddle_group.sprites()[0].rect.centerx, self.paddle_group.sprites()[0].rect.top, self.level_number + 3)
            self.ball_group.add(my_ball)
            self.level = Level(f'levels/level_{self.level_number}.txt', 'Heart')

        for i in range(1, brick_rows + 1):
            for j in range(1, brick_columns + 1):
                if self.level.mapping_dictionary[(i, j)]:
                        brick = Brick(brick_horizontal_buffer * (j) + brick_width * (j - 1), brick_vertical_buffer * (i) + brick_height * (i - 1) + self.HUD_height, brick_width, brick_height, self.level.mapping_dictionary[(i, j)])
                        self.brick_group.add(brick)
        
        # Draw all sprites and update the display.
        display_surface.fill(BLACK)
        self.draw()
        self.paddle_group.draw(display_surface)
        self.ball_group.draw(display_surface)
        self.brick_group.draw(display_surface)
        pygame.display.update()

        # Pause the game prior to gameplay.
        self.pause_game(f'Level: {self.level_number} - {self.level.name}', 'Press ENTER to continue')

    def pause_game(self, main_text, sub_text, hide_gameplay = False):
        '''Pause the game'''

        # Set a text offset to space out the pause text.
        text_offset = 45

        # Set text.
        main_text = self.font.render(main_text, True, WHITE)
        main_rect = main_text.get_rect()
        main_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT * (57/100) )

        sub_text = self.font.render(sub_text, True, WHITE)
        sub_rect = sub_text.get_rect()
        sub_rect.center = (WINDOW_WIDTH // 2, main_rect.centery + text_offset)

        # If the hide_gameplay option has been selected, hide the current gameplay.
        if hide_gameplay:
            display_surface.fill(BLACK)

        # Blit the pause screen text to the display.
        display_surface.blit(main_text, main_rect)
        display_surface.blit(sub_text, sub_rect)
        pygame.display.update()

        # Pause the game. Allow the player to either quit the program or press enter to continue.
        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                # Allow the user to quit the game.
                if event.type == pygame.QUIT:
                    is_paused = False
                    self.running = False
                # Allow the use to continue.
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        is_paused = False

    def reset_game(self):
        '''Reset the game and player attributes'''
        self.player.reset()
        self.brick_group.empty()
        self.ball_group.empty()
        self.powerup_group.empty()
        self.level_number = 1
        self.start_new_level()
    
class Player:
    '''A class to model the player'''
    def __init__(self):
        '''Initialize the player and define player attributes'''
        self.lives = 3
        self.score = 0
    
    def reset(self):
        '''Reset the player attributes'''
        self.lives = 3
        self.score = 0
    
class Paddle(pygame.sprite.Sprite):
    '''A class to model a paddle controlled by the player.'''
    def __init__(self):
        '''Initialize the paddle'''
        # Inherit the parent class's methods and attributes.
        super().__init__()

        # Define the paddle height, width, and buffer distance to the bottom of the display. 
        self.height = 15
        self.width = 150
        self.lower_buffer = 25

        # Define the paddle image as a surface and fill it with the color white.
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(WHITE)

        # Generate and locate the paddle rect.
        self.rect = self.image.get_rect() 
        self.rect.centerx = WINDOW_WIDTH / 2
        self.rect.bottom = WINDOW_HEIGHT - self.lower_buffer

        # Define the paddle velocity.
        self.velocity = 8

    def update(self):
        '''Allow the player to move the paddle across the screen'''
        # Generate an object containing the keys pressed.
        keys = pygame.key.get_pressed()

        # Move the player if the left or right arrow key has been pressed and they are within the screen bounds.
        if keys[pygame.K_a] and self.rect.left >= 0:
            self.rect.x -= self.velocity
        if keys[pygame.K_d] and self.rect.right <= WINDOW_WIDTH:
            self.rect.x += self.velocity
    
    def reset(self):
        self.rect.centerx = WINDOW_WIDTH / 2
        self.rect.bottom = WINDOW_HEIGHT - self.lower_buffer

class Ball(pygame.sprite.Sprite):
    '''A class to model the ball'''
    def __init__(self, x, y, velocity):
        '''Initialize the ball'''
        # Inherit the parent class's attributes and methods.
        super().__init__()

        # Define the kinematic attributes of the ball.
        self.starting_dx = random.choice([-1, 1])
        self.starting_dy = -1
        self.velocity = velocity
        self.dx = self.starting_dx
        self.dy = self.starting_dy

        # Define the ball diameter.
        self.diameter = 25
        
        # Define the ball image.
        self.image = pygame.Surface([self.diameter, self.diameter])
        pygame.draw.circle(self.image, WHITE, (self.diameter / 2, self.diameter / 2), self.diameter / 2)

        # Generate and locate the ball rect.
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        #self.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 55)
    
    def update(self):
        '''Move the ball'''
        self.rect.x += self.dx * self.velocity
        self.rect.y += self.dy * self.velocity
    
    def reset(self):
        '''Reset the ball to the center of the screen'''
        self.dx = random.choice([-1, 1])
        self.dy = -1
        self.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 55)

class Brick(pygame.sprite.Sprite):
    '''A class to model a brick'''
    def __init__(self, x, y, width, height, color):
        '''Initialize the brick'''
        # Inherit the parent class's attributes and methods.
        super().__init__()
        
        # Define the brick color, width, and height.
        self.color = color
        self.width = width
        self.height = height

        # Generate and fill the brick image with the brick color.
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(self.color)

        # Define and locate the brick rect.
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class PowerUp(pygame.sprite.Sprite):
    '''A powerup that the player can obtain'''
    def __init__(self, x, y, ptype):
        # Inherit the parent classes attributes and methods.
        super().__init__()

        # Set the width and height of the powerup block.
        self.height = 20
        self.width = 20

        # Define the powerup image as a pygame surface and fill it with the color white.
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(WHITE)

        # Generate and locate the power up rect.
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        # Define the powerup velocity.
        self.velocity = 2

        # Define the type of the power up.
        self.ptype = ptype
    
    def update(self):
        '''Move the powerup down the screen for the player to collect it'''
        self.rect.y += self.velocity

class Level:
    '''A class to map out a level'''
    def __init__(self, brick_map, name):
        '''Initialize the Level'''
        self.brick_map = brick_map
        self.color_dictionary = {'X':None, 'P':PINK, 'R':RED, 'G':GREEN, 'B':BLUE, 'W':WHITE}
        self.name = name
        
        # Open the input brick_map .txt file and store the text in a list attribute.
        with open(self.brick_map) as level_file:
            data_list = level_file.readlines()
            self.level_list = []
            for line in data_list:
                self.level_list.append(line.removesuffix('\n'))
        
        # Create a mapping dictionary which assigns a particular row, column tuple to a specific color.
        self.mapping_dictionary = {}
        for i, line in enumerate(self.level_list, 1):
            for j, char in enumerate(line, 1):
                self.mapping_dictionary[(i,j)] = self.color_dictionary[char]
    
    def check_format(self):
        '''Check whether the level .txt file is formatted correctly'''    
        for line in self.level_list:
            if len(line) != len(self.level_list[0]):
                return False
            else:
                return True

'''
Game Loop
'''

# Create the player.
my_player = Player()

# Create the paddle group and the Paddle object.
my_paddle_group = pygame.sprite.Group()
my_paddle = Paddle()
my_paddle_group.add(my_paddle)

# Create the ball group (we will add Ball objects via the game's start_new_level method)
my_ball_group = pygame.sprite.Group()

# Create the brick group (we will add Brick objects via the game's start_new_level method)
my_brick_group = pygame.sprite.Group()

# Create the powerup group (we will add PowerUp objects randomly when breaking bricks)
my_power_up_group = pygame.sprite.Group()

# Create a Game object.
my_game = Game(my_player, my_paddle, my_paddle_group, my_ball_group, my_brick_group, my_power_up_group)
my_game.start_new_level()

# Initialize a frame counter.
frame_counter = 0

while my_game.running:
    for event in pygame.event.get():
        # Check to see if they player wants to quit the game.
        if event.type == pygame.QUIT:
            my_game.running = False

        # For testing purposes, use '0' to delete all bricks on the screen.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_0:
                my_brick_group.empty()
    
    # Increment the frame counter and level timer.
    frame_counter += 1
    if frame_counter % 120 == 0:
        my_game.level_timer += 1

    # Fill the display.
    display_surface.fill(BLACK)

    # Update and draw all sprite groups.
    my_paddle_group.update()
    my_paddle_group.draw(display_surface)

    my_ball_group.update()
    my_ball_group.draw(display_surface)

    my_brick_group.update()
    my_brick_group.draw(display_surface)

    my_power_up_group.update()
    my_power_up_group.draw(display_surface)

    # Update and draw the Game object.
    my_game.update()
    my_game.draw()

    # Update the display and tick the clock.
    pygame.display.update()
    clock.tick(FPS)

# End of the game.
pygame.quit()

'''Development Tasks'''
# Create a paddle and allow the player to horizontally translate it accross the display. (COMPLETE)
# Restrict the movement of the paddle to within the bounds of the screen. (COMPLETE)
# Add a ball that will bounce within the display. (COMPLETE)
# Allow the ball to collide with the player's paddle. (COMPLETE)
# Tweak physics of the paddle contact with the ball. The ball's reversed x velocity should vary based on where the ball struck the paddle. (COMPLETE)
# Add bricks to the game at the start of a new level. (COMPLETE)
# Allow the player to destroy the bricks. Physics for the ball contact with the brick should be the same as the wall. (COMPLETE)
# Create a dictionary mapping system to create levels with specific brick placements and colors. (COMPLETE)
# Add a HUD to display the player score, lives, and current level. (COMPLETE)
# Add a pause screen that will display: at the start of a new level, when the player loses a life, when the player receives a game over. (COMPLETE)
# Add automatic level progression. i.e. the player will play level 1, then level 2, then level 3...if they play all of the levels then restart them to level 1. (COMPLETE)
# Increase the player's score each time they hit a brick. (COMPLETE)
# Increase the ball velocity at each level. (COMPLETE)
# Add music and sounds as required (paddle hit, brick hit, wall bounce, start new level, lose a life, etc.) (COMPLETE)
# Implement a level timer that impacts the player score increment when they hit a brick. (COMPLETE)
# Revise the UI to include the round timer. (COMPLETE)
# Add a power up that will randomly drop from a brick. (COMPLETE)
# The powers will spawn front he brick and move down the screen until the player picks it up. (COMPLETE)
# The powers will last a certain period of time (say 10 seconds).
# Powerup # 1: additional ball.
# Powerup # 2: missiles.
# Powerup # 3: increased paddle size.
# The powers will spawn from the brick and move down the screen until the player picks it up. The powers will last a certain period of time (say 10 seconds).
# Add a monkey power up that bounces across the screen and destroys all bricks in its path.
# Find a way to make the brick corners rounded...
# Add a boost mechanic that initiates at 100 and allows the player to increase their movement speed. This will recharge by destroying bricks.
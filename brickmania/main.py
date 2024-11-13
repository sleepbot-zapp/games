import pygame
import random
import sys
import time

pygame.init()

pygame.mixer.music.load("./brickmania/music.mp3")
track1 = pygame.mixer.Sound("./brickmania/music1.mp3")
track2 = pygame.mixer.Sound("./brickmania/music2.mp3")
track3 = pygame.mixer.Sound("./brickmania/music3.mp3")
pygame.mixer.music.play(-1)

WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BRICKMANIA")

WHITE = (255, 255, 255)
RED = (255, 30, 100)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

player_width = 100
player_height = 20
player_speed = 15

ball_radius = 10
ball_speed_x, ball_speed_y = 5, -5

brick_width = 60
brick_height = 20
brick_speed = 10
brick_rows = 6
brick_cols = WIDTH // brick_width

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

trail = []
trail_length = 10

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 20
        self.type = "extra_ball"
        self.color = GREEN
        self.fall_speed = 2

    def move(self):
        self.y += self.fall_speed

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Brick:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice([RED, BLUE, GREEN, YELLOW])

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, brick_width, brick_height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, brick_width, brick_height), 2)

def draw_player(x, y):
    pygame.draw.rect(screen, BLUE, (x, y, player_width, player_height), border_radius=10)

def draw_ball(x, y):
    trail.append((x, y))
    if len(trail) > trail_length:
        trail.pop(0)

    for i, (tx, ty) in enumerate(trail):
        alpha = 255 - int(255 * (i / trail_length))
        color = (YELLOW[0], YELLOW[1], YELLOW[2], alpha)
        trail_surface = pygame.Surface((ball_radius * 2, ball_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(trail_surface, color, (ball_radius, ball_radius), ball_radius)
        screen.blit(trail_surface, (tx - ball_radius, ty - ball_radius))

    pygame.draw.circle(screen, YELLOW, (x, y), ball_radius)

def draw_bricks(bricks):
    for brick in bricks:
        brick.draw()

def show_score(score):
    text = font.render(f"Score: {score}", True, RED)
    screen.blit(text, (WIDTH // 2 - 100, HEIGHT - 40))

def game_over(score):
    pygame.mixer.music.pause()
    track3.play()
    text = font.render("Game Over! Press SPACE to restart", True, WHITE)
    highscore = int(open("./brickmania/highscore.txt").read())
    text2 = font.render(f"High Score = {[score, highscore][highscore>score]}", True, WHITE)
    text3 = font.render(f"Your Score = {score}", True, WHITE)
    if highscore < score:
        ...
        # with open('./brickmania/highscore.txt', 'w') as f:
        #     f.write(str(score))
    screen.blit(text, (WIDTH // 2 - 220, HEIGHT // 2))
    screen.blit(text2, (WIDTH // 2 - 100, HEIGHT // 2 + 40))
    screen.blit(text3, (WIDTH // 2 - 100, HEIGHT // 2 + 80))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                track2.stop()
                pygame.mixer.music.unpause()
                return

def drop_powerup(brick_x, brick_y, powerups):
    if len(powerups) < 2 and random.random() < 0.2:
        return PowerUp(brick_x, brick_y)
    return None

def create_new_bricks():
    bricks = []
    for col in range(brick_cols):
        for row in range(brick_rows):
            bricks.append(Brick(col * brick_width, row * brick_height))
    return bricks

class SpecialBall:
    def __init__(self, x, y, dx, dy, expiration_time):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.expiration_time = expiration_time

    def move(self):
        self.x += self.dx
        self.y += self.dy

        if self.x <= ball_radius or self.x >= WIDTH - ball_radius:
            self.dx = -self.dx

        if self.y <= ball_radius:
            self.dy = -self.dy

    def draw(self):
        pygame.draw.circle(screen, RED, (self.x, self.y), ball_radius)

speed_increment = 1.0001

def main_game():
    paused = False
    player_x = (WIDTH - player_width) // 2
    player_y = HEIGHT - player_height - 70

    balls = [(random.randint(200, WIDTH // 2), random.randint(200, HEIGHT // 2), ball_speed_x, ball_speed_y)]
    balls_crossed_line = [False]

    score = 0
    bricks = create_new_bricks()
    powerups = []
    special_balls = []
    running = True

    last_move_time = time.time()
    inactivity_threshold = 2

    last_brick_move_time = time.time()
    brick_move_speed = 3

    last_special_ball_time = time.time()

    last_x_key_time = time.time()
    random_destruction_interval = 60

    while running:
        screen.fill(BLACK)
        clock.tick(60) / 1000
        current_time = time.time()

        if len(bricks) == 0:
            bricks = create_new_bricks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if current_time - last_move_time > inactivity_threshold:
            if player_x <= WIDTH // 2:
                player_x += 5 * player_speed
            elif player_x > WIDTH // 2:
                player_x -= 5 * player_speed
            last_move_time = current_time

        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player_x > 10:
            player_x -= player_speed
            last_move_time = current_time
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player_x < WIDTH - player_width - 10:
            player_x += player_speed
            last_move_time = current_time

        if (keys[pygame.K_w] or keys[pygame.K_UP]) and current_time - last_special_ball_time > 19:
            dx = random.choice([-8, 8]) 
            dy = random.randint(-5, -2)
            special_balls.append(SpecialBall(player_x + player_width // 2, player_y - ball_radius, dx, dy, current_time + 3))
            pygame.mixer.music.pause()
            track1.play()
            last_special_ball_time = current_time
            
        # Move all balls including special balls
        for i, (ball_x, ball_y, ball_dx, ball_dy) in enumerate(balls[:]):
            balls[i] = (ball_x, ball_y, ball_dx * speed_increment, ball_dy * speed_increment)

        # Update ball positions
        for i, (ball_x, ball_y, ball_dx, ball_dy) in enumerate(balls[:]):
            ball_x += ball_dx
            ball_y += ball_dy

            if ball_x <= ball_radius or ball_x >= WIDTH - ball_radius:
                ball_dx = -ball_dx

            if ball_y <= ball_radius:
                ball_dy = -ball_dy

            if ball_y >= HEIGHT - 60 - ball_radius and not balls_crossed_line[i]:
                balls_crossed_line[i] = True

            if player_x < ball_x < player_x + player_width and player_y < ball_y + ball_radius < player_y + player_height:
                center_x = player_x + player_width / 2
                hit_position = (ball_x - center_x) / (player_width / 2)
                ball_dx = ball_speed_x * hit_position
                ball_dy = -abs(ball_dy)
                ball_y = player_y - ball_radius

            balls[i] = (ball_x, ball_y, ball_dx, ball_dy)

        if all(balls_crossed_line):
            game_over(score)
            return

        # Update brick positions
        if current_time - last_brick_move_time > 1:
            for brick in bricks:
                brick.y += brick_move_speed
                if brick.y + brick_height >= HEIGHT:
                    game_over(score)
                    return
            last_brick_move_time = current_time

        bricks_to_remove = []
        for brick in bricks:
            for i, (ball_x, ball_y, ball_dx, ball_dy) in enumerate(balls[:]):
                if brick.x < ball_x < brick.x + brick_width and brick.y < ball_y < brick.y + brick_height:
                    bricks_to_remove.append(brick)
                    score += 10
                    powerup = drop_powerup(brick.x, brick.y, powerups)
                    if powerup:
                        powerups.append(powerup)
                    balls[i] = (ball_x, ball_y, ball_dx, -ball_dy)

            for special_ball in special_balls[:]:
                if brick.x < special_ball.x < brick.x + brick_width and brick.y < special_ball.y < brick.y + brick_height:
                    bricks_to_remove.append(brick)
                    score += 10
                    powerup = drop_powerup(brick.x, brick.y, powerups)
                    if powerup:
                        powerups.append(powerup)

        for brick in bricks_to_remove:
            if brick in bricks:
                bricks.remove(brick)

        if current_time - last_x_key_time > random_destruction_interval - 1:
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                pygame.mixer.music.pause()
                track2.play()
                for _ in range(5):
                    if bricks:
                        random_brick = random.choice(bricks)
                        bricks.remove(random_brick)
                        score += 20
                last_x_key_time = current_time


        # Handle power-ups
        for powerup in powerups[:]:
            powerup.move()
            powerup.draw()

            if player_x < powerup.x + powerup.width and player_x + player_width > powerup.x and player_y < powerup.y + powerup.height and player_y + player_height > powerup.y:
                powerups.remove(powerup)
                if powerup.type == "extra_ball":
                    balls.append((WIDTH // 2, HEIGHT // 2, ball_speed_x, ball_speed_y))
                    balls_crossed_line.append(False)

        for special_ball in special_balls[:]:
            special_ball.move()
            special_ball.draw()

            if special_ball.x < 0 or special_ball.x > WIDTH or special_ball.y < 0 or special_ball.y > HEIGHT:
                special_balls.remove(special_ball)

        draw_bricks(bricks)
        draw_player(player_x, player_y)
        for ball_x, ball_y, _, _ in balls:
            draw_ball(ball_x, ball_y)

        show_score(score)

        if current_time - last_special_ball_time > 19:
            special_ball_text = font.render("Special Ball Ready (UP)", True, GREEN)
        else:
            remaining_time = max(0, 20 - (current_time - last_special_ball_time))
            special_ball_text = font.render(f"Special Ball in {int(remaining_time)}s", True, WHITE)

        if current_time - last_x_key_time > random_destruction_interval - 1:
            countdown_text = font.render("Brick Destruction Ready (DOWN)", True, GREEN)
            screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2 + 250, HEIGHT - 40))
        else:
            time_until_destruction = max(0, random_destruction_interval - (current_time - last_x_key_time))
            countdown_text = font.render(f"Brick Destruction in {int(time_until_destruction)}s", True, WHITE)
            screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2 + 200, HEIGHT - 40))

        pygame.draw.line(screen, WHITE, (0, HEIGHT - 60), (WIDTH, HEIGHT - 60), 2)
        screen.blit(special_ball_text, (WIDTH // 2 - special_ball_text.get_width() // 2 - 250, HEIGHT - 40))

        pygame.display.flip()

        if not special_balls or current_time - last_special_ball_time >= 2:
            track1.stop()
            pygame.mixer.music.unpause()

        if current_time - last_x_key_time >= 5:
            track2.stop()
            pygame.mixer.music.unpause()

if __name__ == "__main__":
    while True:
        main_game()
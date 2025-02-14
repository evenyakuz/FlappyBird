import pygame
import sys
import random
from pygame.locals import *

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.5
JUMP = -10
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQ = 1500
MAX_SCORE = 999

# Цвета
SKY_BLUE = (135, 206, 235)
NIGHT_BLUE = (0, 51, 102)
YELLOW = (255, 255, 0)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (100, 100, 100)
MOON_YELLOW = (255, 255, 224)


class Bird:
    def __init__(self, color):
        self.x = WIDTH // 4
        self.y = HEIGHT // 2
        self.velocity = 0
        self.color = color
        self.size = 30

    def jump(self):
        self.velocity = JUMP

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.y = max(0, min(self.y, HEIGHT - self.size))


class Pipe:
    def __init__(self):
        self.gap_y = random.randint(100, HEIGHT - 100 - PIPE_GAP)
        self.width = 60
        self.x = WIDTH
        self.passed = False

    @property
    def rects(self):
        return [
            pygame.Rect(self.x, 0, self.width, self.gap_y),
            pygame.Rect(
                self.x,
                self.gap_y + PIPE_GAP,
                self.width,
                HEIGHT - self.gap_y - PIPE_GAP,
            ),
        ]

    def update(self):
        self.x -= PIPE_SPEED


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy Bird Pro")
        self.clock = pygame.time.Clock()
        self.bird_color = (255, 255, 0)
        self.is_night = False
        self.top_score = 0
        self.load_top_score()
        self.theme_button = pygame.Rect(WIDTH - 80, 10, 70, 30)
        self.stars = []
        self.color_picker_active = False
        self.sliders = [
            {"rect": pygame.Rect(100, 200, 200, 20), "value": 255},
            {"rect": pygame.Rect(100, 250, 200, 20), "value": 255},
            {"rect": pygame.Rect(100, 300, 200, 20), "value": 0},
        ]
        self.generate_stars()

    def load_top_score(self):
        try:
            with open("top_score.txt", "r") as f:
                self.top_score = min(int(f.read()), MAX_SCORE)
        except:
            self.top_score = 0

    def save_top_score(self):
        with open("top_score.txt", "w") as f:
            f.write(str(self.top_score))

    def generate_stars(self):
        self.stars = [
            (random.randint(0, WIDTH), random.randint(0, 300)) for _ in range(50)
        ]

    def draw_bird(self, bird):
        # Тело птицы
        body = pygame.Rect(bird.x - 15, bird.y - 10, 30, 20)
        pygame.draw.ellipse(self.screen, bird.color, body)

        # Крыло
        wing_points = [
            (bird.x - 10, bird.y),
            (bird.x - 20, bird.y - 10),
            (bird.x - 10, bird.y - 5),
        ]
        pygame.draw.polygon(self.screen, bird.color, wing_points)

        # Клюв
        pygame.draw.polygon(
            self.screen,
            YELLOW,
            [(bird.x + 15, bird.y), (bird.x + 25, bird.y), (bird.x + 15, bird.y + 5)],
        )

    def draw_pipes(self, pipes):
        for pipe in pipes:
            pygame.draw.rect(self.screen, DARK_GREEN, pipe.rects[0])
            pygame.draw.rect(self.screen, DARK_GREEN, pipe.rects[1])

            inner_offset = 5
            top_inner = pygame.Rect(
                pipe.rects[0].x + inner_offset,
                0,
                pipe.rects[0].width - 2 * inner_offset,
                pipe.rects[0].height - inner_offset,
            )
            bottom_inner = pygame.Rect(
                pipe.rects[1].x + inner_offset,
                pipe.rects[1].y + inner_offset,
                pipe.rects[1].width - 2 * inner_offset,
                pipe.rects[1].height - inner_offset,
            )
            pygame.draw.rect(self.screen, GREEN, top_inner)
            pygame.draw.rect(self.screen, GREEN, bottom_inner)

    def draw_score(self, score):
        text = pygame.font.Font(None, 36).render(f"Score: {score}", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, 50))
        self.screen.blit(text, text_rect)

        top_text = pygame.font.Font(None, 28).render(
            f"Top: {self.top_score}", True, WHITE
        )
        self.screen.blit(top_text, (10, 10))

    def draw_color_picker(self):
        pygame.draw.rect(self.screen, (40, 40, 40), (50, 150, 300, 200))
        for i, slider in enumerate(self.sliders):
            pygame.draw.rect(self.screen, (200, 200, 200), slider["rect"])
            handle_x = slider["rect"].x + int(slider["value"] / 255 * 200)
            pygame.draw.circle(
                self.screen, (0, 0, 0), (handle_x, slider["rect"].centery), 8
            )
            label = pygame.font.Font(None, 24).render(
                f"{['R','G','B'][i]}: {slider['value']}", True, WHITE
            )
            self.screen.blit(label, (slider["rect"].x, slider["rect"].y - 25))

    def update_bird_color(self):
        self.bird_color = tuple(s["value"] for s in self.sliders)

    def game_over_screen(self, score):
        if score > self.top_score:
            self.top_score = min(score, MAX_SCORE)
            self.save_top_score()

        while True:
            self.screen.fill(NIGHT_BLUE if self.is_night else SKY_BLUE)

            text = pygame.font.Font(None, 48).render("Game Over!", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            self.screen.blit(text, text_rect)

            restart_btn = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2, 140, 40)
            quit_btn = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 60, 140, 40)

            pygame.draw.rect(self.screen, BUTTON_COLOR, restart_btn)
            pygame.draw.rect(self.screen, BUTTON_COLOR, quit_btn)

            btn_font = pygame.font.Font(None, 28)
            self.screen.blit(
                btn_font.render("RESTART", True, WHITE),
                (restart_btn.x + 20, restart_btn.y + 10),
            )
            self.screen.blit(
                btn_font.render("QUIT", True, WHITE), (quit_btn.x + 40, quit_btn.y + 10)
            )

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if restart_btn.collidepoint(mouse_pos):
                        return True
                    elif quit_btn.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

    def run(self):
        while True:
            bird = Bird(self.bird_color)
            pipes = []
            score = 0
            last_pipe = pygame.time.get_ticks()
            game_started = False
            running = True

            while running:
                self.clock.tick(FPS)
                current_time = pygame.time.get_ticks()

                # Обработка событий
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            if not game_started:
                                game_started = True
                            bird.jump()
                    if event.type == MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if self.theme_button.collidepoint(mouse_pos):
                            self.is_night = not self.is_night
                            self.generate_stars()
                        elif pygame.Rect(10, HEIGHT - 50, 120, 40).collidepoint(
                            mouse_pos
                        ):
                            self.color_picker_active = not self.color_picker_active
                        elif self.color_picker_active:
                            for slider in self.sliders:
                                if slider["rect"].collidepoint(mouse_pos):
                                    slider["value"] = int(
                                        (mouse_pos[0] - slider["rect"].x) / 200 * 255
                                    )
                                    self.update_bird_color()
                                    bird.color = self.bird_color

                # Обновление игры
                if game_started:
                    bird.update()

                    if current_time - last_pipe > PIPE_FREQ:
                        pipes.append(Pipe())
                        last_pipe = current_time

                    for pipe in pipes:
                        pipe.update()

                    pipes = [p for p in pipes if p.x + p.width > 0]

                    for pipe in pipes:
                        for rect in pipe.rects:
                            if pygame.Rect(
                                bird.x - 15, bird.y - 10, 30, 20
                            ).colliderect(rect):
                                running = False
                        if not pipe.passed and pipe.x + pipe.width < bird.x:
                            pipe.passed = True
                            score += 1
                            if score >= MAX_SCORE:
                                running = False

                # Отрисовка
                self.screen.fill(NIGHT_BLUE if self.is_night else SKY_BLUE)

                if self.is_night:
                    for star in self.stars:
                        pygame.draw.circle(self.screen, WHITE, star, 1)
                    pygame.draw.circle(self.screen, MOON_YELLOW, (50, 50), 30)

                self.draw_pipes(pipes)
                self.draw_bird(bird)
                self.draw_score(score)

                # Кнопка темы
                pygame.draw.rect(self.screen, WHITE, self.theme_button, 2)
                theme_text = pygame.font.Font(None, 24).render(
                    "NIGHT" if not self.is_night else "DAY", True, WHITE
                )
                self.screen.blit(
                    theme_text, (self.theme_button.x + 10, self.theme_button.y + 5)
                )

                # Кнопка и палитра цветов
                if self.color_picker_active:
                    self.draw_color_picker()
                else:
                    color_btn = pygame.Rect(10, HEIGHT - 50, 120, 40)
                    pygame.draw.rect(self.screen, BUTTON_COLOR, color_btn)
                    self.screen.blit(
                        pygame.font.Font(None, 24).render("COLOR", True, WHITE),
                        (20, HEIGHT - 40),
                    )

                pygame.display.update()

            if self.game_over_screen(score):
                continue
            else:
                break


if __name__ == "__main__":
    game = Game()
    game.run()

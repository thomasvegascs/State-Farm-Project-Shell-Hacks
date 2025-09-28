import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 900, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Policy Hero - Start Screen")

# Colors
YELLOW = (250, 215, 0)
WHITE = (255, 255, 255)

# Fonts
title_font = pygame.font.Font("Pixel Emulator.otf", 52)
subtitle_font = pygame.font.Font("Pixel Emulator.otf", 18)
info_font = pygame.font.Font("Pixel Emulator.otf", 22, )
typewriter_font = pygame.font.Font("Pixel Emulator.otf", 14,)

# Clock
clock = pygame.time.Clock()
FPS = 120

# Jake's statement
jake_message = "Jake from State Farm says: Insurance has your back!"
typed_text = ""  # text being revealed
type_index = 0
type_delay = 4  # lower = faster typing

# Load pixel-art background (make sure background.png is in the same folder)
background = pygame.image.load("background.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))  # fit to screen


def start_screen():
    global typed_text, type_index
    running = True
    t = 0  # time counter for animations

    while running:
        # Draw background
        screen.blit(background, (0, 0))

        # --- Title Animation (bounce effect) ---
        y_offset = int(math.sin(t * 0.05) * 10)
        title_text = title_font.render("Policy Hero", True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4 + y_offset))
        screen.blit(title_text, title_rect)

        # --- Subtitle ---
        subtitle_text = subtitle_font.render(
            "Where we make insurance easier to understand", True, WHITE
        )
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        screen.blit(subtitle_text, subtitle_rect)

        subtitle_text2 = subtitle_font.render(
            "and prepare you for everyday risks!", True, WHITE
        )
        subtitle_rect2 = subtitle_text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        screen.blit(subtitle_text2, subtitle_rect2)

        # --- Info Text Animation (flashing) ---
        alpha = int((math.sin(t * 0.1) + 1) * 127)  # fades in/out
        info_surface = info_font.render("Press SPACE to Start", True, YELLOW)
        info_surface.set_alpha(alpha)
        info_rect = info_surface.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        screen.blit(info_surface, info_rect)

        # --- Jake from State Farm (Typewriter effect) ---
        if type_index < len(jake_message) and t % type_delay == 0:
            typed_text += jake_message[type_index]
            type_index += 1

        type_text_surface = typewriter_font.render(typed_text, True, WHITE)
        type_text_rect = type_text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        screen.blit(type_text_surface, type_text_rect)

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False  # exit start screen

        pygame.display.update()
        clock.tick(FPS)
        t += 1


# Run the start screen
start_screen()

pygame.quit()
sys.exit()

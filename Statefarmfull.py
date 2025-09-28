import pygame, sys, textwrap, math

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Policy Hero - Insurance Quiz")

clock = pygame.time.Clock()
FPS = 60

# --- Colors ---
YELLOW = (250, 215, 0)
WHITE = (255, 255, 255)

# --- Fonts ---
font_big = pygame.font.Font("Pixel Emulator.otf", 60)
font_small = pygame.font.Font("Pixel Emulator.otf", 22)
typewriter_font = pygame.font.Font("Pixel Emulator.otf", 18)

# --- Backgrounds ---
main_bg = pygame.image.load("main_bg.png").convert()
quiz_bg = pygame.image.load("quiz_bg.png").convert()
main_bg = pygame.transform.scale(main_bg, (WIDTH, HEIGHT))
quiz_bg = pygame.transform.scale(quiz_bg, (WIDTH, HEIGHT))

# --- Jake's statement ---
jake_message = "Jake from State Farm says: Insurance has your back!"
typed_text = ""
type_index = 0
type_delay = 4  # lower = faster typing

# --- Questions (with explanations) ---
questions = [
    ("A fire damages your kitchen. What covers the cost?",
     ["Car Insurance", "Home Insurance", "Health Insurance"], 1,
     "Home Insurance covers damage to your house and belongings after events like fire."),
    ("Your TV gets stolen. Coverage?",
     ["Home Insurance", "Health Insurance", "Car Insurance"], 0,
     "Home Insurance protects your personal property against theft."),
    ("A tree falls on your roof. Who helps?",
     ["Home Insurance", "Car Insurance", "Life Insurance"], 0,
     "Home Insurance pays for damages to your house caused by falling objects."),
    ("You crash into another car. Who pays?",
     ["Car Insurance", "Health Insurance", "Home Insurance"], 0,
     "Car Insurance covers accidents involving your vehicle and others."),
    ("Your windshield cracks. Coverage?",
     ["Home Insurance", "Car Insurance", "Health Insurance"], 1,
     "Car Insurance usually includes glass repair or replacement."),
    ("A thief steals your car. Which insurance helps?",
     ["Car Insurance", "Home Insurance", "Health Insurance"], 0,
     "Car Insurance can include comprehensive coverage for theft."),
    ("You break your arm. Coverage?",
     ["Car Insurance", "Health Insurance", "Home Insurance"], 1,
     "Health Insurance pays medical costs like broken bones and treatment."),
    ("You need prescription medicine. What pays?",
     ["Health Insurance", "Home Insurance", "Car Insurance"], 0,
     "Health Insurance helps cover prescriptions and medications."),
    ("You have surgery. Who helps?",
     ["Life Insurance", "Car Insurance", "Health Insurance"], 2,
     "Health Insurance pays for medical operations and hospital stays."),
    ("You go for a routine checkup. Which insurance?",
     ["Health Insurance", "Car Insurance", "Life Insurance"], 0,
     "Health Insurance covers preventative care like doctor visits."),
]

# --- Layout constants ---
QUESTION_Y = 160
ANSWER_START_Y = 300
ANSWER_SPACING = 70
LINE_WIDTH = 50

# --- Game state ---
state = "start"
question_index = 0
score = 0
feedback_text = ""
explanation_text = ""
time_counter = 0

# --- Animation variables for title ---
title_surface = font_big.render("Policy Hero", True, YELLOW)
title_x = -title_surface.get_width()
title_y = HEIGHT // 3
title_speed = 12
bounce_offset = 0
bounce_direction = 1

# --- Helpers ---
def render_wrapped_text_with_shadow(text, font, color, shadow_color, max_width, y_start, shadow_offset=3):
    wrapped = textwrap.wrap(text, width=max_width)
    surfaces = [font.render(line, True, color) for line in wrapped]
    shadow_surfaces = [font.render(line, True, shadow_color) for line in wrapped]
    total_height = len(surfaces) * font.get_height()
    y = y_start - total_height // 2
    for surf, shadow in zip(surfaces, shadow_surfaces):
        screen.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + shadow_offset, y + shadow_offset))
        screen.blit(surf, (WIDTH//2 - surf.get_width()//2, y))
        y += font.get_height() + 5

def render_question_and_answers(q_index):
    q, options, correct, explanation = questions[q_index]
    return q, options, correct, explanation

# --- Initialize first question ---
current_question, current_options, correct_answer, explanation_text = render_question_and_answers(question_index)

running = True
t = 0
while running:
    t += 1
    time_counter += 1
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
            pygame.quit(); sys.exit()

        if state == "start":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                state = "quiz"

        elif state == "quiz":
            if e.type == pygame.KEYDOWN and e.unicode in ["1", "2", "3"]:
                chosen = int(e.unicode) - 1
                if chosen == correct_answer:
                    score += 1
                    feedback_text = "Correct!"
                else:
                    feedback_text = "Oops!"
                explanation_text = questions[question_index][3]

                # Draw feedback + explanation
                screen.blit(quiz_bg, (0, 0))
                fb_shadow = font_big.render(feedback_text, True, (0, 0, 0))
                fb_surface = font_big.render(feedback_text, True, (255, 255, 0))
                fb_x = WIDTH//2 - fb_surface.get_width()//2
                fb_y = HEIGHT//2 - 150
                screen.blit(fb_shadow, (fb_x + 3, fb_y + 3))
                screen.blit(fb_surface, (fb_x, fb_y))
                render_wrapped_text_with_shadow(
                    explanation_text, font_small, (255, 255, 255), (0, 0, 0),
                    LINE_WIDTH, HEIGHT//2 + 150
                )
                pygame.display.flip()
                pygame.time.delay(3000)

                # Next question
                feedback_text = ""
                explanation_text = ""
                question_index += 1
                if question_index >= len(questions):
                    state = "end"
                else:
                    current_question, current_options, correct_answer, explanation_text = render_question_and_answers(question_index)

        elif state == "end":
            if e.type == pygame.KEYDOWN:
                running = False

    # --- Draw ---
    if state == "start":
        screen.blit(main_bg, (0, 0))
        # Animated title
        if title_x < WIDTH // 2 - title_surface.get_width() // 2:
            title_x += title_speed
        else:
            bounce_offset += bounce_direction
            if bounce_offset > 10 or bounce_offset < -10:
                bounce_direction *= -1
        screen.blit(title_surface, (title_x, title_y + bounce_offset))
        # Subtitle
        subtitle = font_small.render("Where we make insurance easier to understand", True, WHITE)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 - 20))
        subtitle2 = font_small.render("and prepare you for everyday risks!", True, WHITE)
        screen.blit(subtitle2, (WIDTH//2 - subtitle2.get_width()//2, HEIGHT//2 + 10))
        # Flashing "Press SPACE"
        alpha = int((math.sin(t * 0.1) + 1) * 127)
        info_surface = font_small.render("Press SPACE to Start", True, YELLOW)
        info_surface.set_alpha(alpha)
        screen.blit(info_surface, (WIDTH//2 - info_surface.get_width()//2, HEIGHT - 60))
        # Jake's typewriter message
        if type_index < len(jake_message) and t % type_delay == 0:
            typed_text += jake_message[type_index]
            type_index += 1
        type_text_surface = typewriter_font.render(typed_text, True, WHITE)
        screen.blit(type_text_surface, (WIDTH//2 - type_text_surface.get_width()//2, HEIGHT//2 + 80))

    elif state == "quiz":
        screen.blit(quiz_bg, (0, 0))
        render_wrapped_text_with_shadow(current_question, font_small, (255, 255, 0), (0, 0, 0), LINE_WIDTH, QUESTION_Y)
        for i, opt in enumerate(current_options):
            scale = 1.0 + 0.05 * math.sin(time_counter * 0.2 + i)
            dynamic_font = pygame.font.Font("Pixel Emulator.otf", int(32 * scale))
            shadow = dynamic_font.render(f"{i+1}. {opt}", True, (0, 0, 0))
            screen.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + 3, ANSWER_START_Y + i*ANSWER_SPACING + 3))
            surf = dynamic_font.render(f"{i+1}. {opt}", True, (0, 255, 255))
            screen.blit(surf, (WIDTH//2 - surf.get_width()//2, ANSWER_START_Y + i*ANSWER_SPACING))

    elif state == "end":
        screen.fill((0, 0, 50))
        end_title = font_big.render("Quiz Complete!", True, (255, 255, 0))
        screen.blit(end_title, (WIDTH//2 - end_title.get_width()//2, HEIGHT//2 - 60))
        score_text = font_big.render(f"Your Score: {score} / {len(questions)}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        if score >= 8:
            msg = "You're an Insurance Hero!"
        elif score >= 5:
            msg = "Great job! You’re learning!"
        else:
            msg = "Keep practicing insurance!"
        result_text = font_small.render(msg, True, WHITE)
        screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 + 80))
        end_msg = font_small.render("Press any key to exit", True, (200, 200, 200))
        screen.blit(end_msg, (WIDTH//2 - end_msg.get_width()//2, HEIGHT//2 + 140))

    pygame.display.flip()
    clock.tick(FPS)

import sys, math, random
import pygame

# -----------------------------
# Basic setup
# -----------------------------
pygame.init()
WIDTH, HEIGHT = 900, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Policy Hero - Level 1 (Home Insurance)")
clock = pygame.time.Clock()
FPS = 60

# -----------------------------
# Colors & fonts
# -----------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 215, 0)
RED = (200, 60, 60)
GREEN = (60, 180, 90)
BLUE = (70, 130, 180)
ORANGE = (255, 140, 0)
GREY = (60, 60, 60)
LIGHT_GREY = (110, 110, 110)

FONT = pygame.font.Font("Pixel Emulator.otf", 18)
FONT_BOLD = pygame.font.Font("Pixel Emulator.otf", 22,)
FONT_BIG = pygame.font.Font("Pixel Emulator.otf", 28)

# -----------------------------
# House layout (simple 2D cutaway)
# -----------------------------
FLOOR_Y = {  # standing y positions for floors
    1: HEIGHT - 90,
    2: HEIGHT - 220,
}
FLOOR_TOP = {  # top of each floor box for drawing
    1: HEIGHT - 160,
    2: HEIGHT - 350,
}
HOUSE_LEFT_WALL_X = 150
HOUSE_RIGHT_WALL_X = WIDTH - 150
WINDOW_WIDTH = 40
WINDOW_HEIGHT = 40

# Interactables (coarse positions)
DOOR_X = HOUSE_LEFT_WALL_X + 10
WINDOW_RIGHT_X = HOUSE_RIGHT_WALL_X  - 10 - WINDOW_WIDTH  # 1F right window
STOVE_X = (HOUSE_LEFT_WALL_X + HOUSE_RIGHT_WALL_X) // 2 - 20  # 1F stove center-ish
GUN_X = (HOUSE_LEFT_WALL_X + HOUSE_RIGHT_WALL_X) // 2 - 10    # 2F mystery gun
INTERACT_DIST = 40

# Combat: where thieves stop to damage the wall (just outside the house walls)
THIEF_TARGET_LEFT = HOUSE_LEFT_WALL_X - 8
THIEF_TARGET_RIGHT = HOUSE_RIGHT_WALL_X + 8

# -----------------------------
# Game states
# -----------------------------
STATE_START = "start"
STATE_PREP = "prep"
STATE_COMBAT = "combat"
STATE_FAIL = "fail"            # failed prep (stove left on)
STATE_INSURANCE_BLAST = "blast"
STATE_WIN = "win"              # after blast showcase; demo end

# -----------------------------
# Player
# -----------------------------
class Player:
    def __init__(self):
        self.floor = 1
        self.x = (HOUSE_LEFT_WALL_X + HOUSE_RIGHT_WALL_X) // 2
        self.speed = 3.0
        self.width = 18
        self.height = 28
        self.facing = "right"
        self.has_gun = False

    @property
    def y(self):
        return FLOOR_Y[self.floor]

    def rect(self):
        return pygame.Rect(int(self.x - self.width/2), int(self.y - self.height), self.width, self.height)

    def move_left(self):
        self.x -= self.speed
        self.facing = "left"
        self._clamp()

    def move_right(self):
        self.x += self.speed
        self.facing = "right"
        self._clamp()

    def move_up(self):
        self.floor = 2

    def move_down(self):
        self.floor = 1

    def _clamp(self):
        # stay within house interior horizontal bounds
        left = HOUSE_LEFT_WALL_X + 10
        right = HOUSE_RIGHT_WALL_X - 10
        self.x = max(left, min(right, self.x))

    def draw(self, surf):
        # simple little person
        pygame.draw.rect(surf, YELLOW, self.rect())
        # face indicator
        eye_x = self.rect().centerx + (-4 if self.facing == "left" else 4)
        eye_y = self.rect().top + 8
        pygame.draw.circle(surf, BLACK, (eye_x, eye_y), 2)
        if self.has_gun and self.floor == 2:
            txt = FONT.render("🔫", True, WHITE)
            surf.blit(txt, (self.rect().centerx - 8, self.rect().top - 18))

# -----------------------------
# Interactables
# -----------------------------
class Door:
    def __init__(self):
        self.locked = False
        self.x = DOOR_X
        self.floor = 1

    def interact(self, player):
        if player.floor == 1 and abs(player.x - self.x) <= INTERACT_DIST:
            self.locked = True
            return "Door locked."
        return None

    def draw(self, surf):
        rect = pygame.Rect(self.x, FLOOR_Y[1]-60, 34, 60)
        pygame.draw.rect(surf, LIGHT_GREY if self.locked else GREY, rect)
        pygame.draw.rect(surf, BLACK, rect, 2)

class Window1FRight:
    def __init__(self):
        self.locked = False
        self.x = WINDOW_RIGHT_X
        self.floor = 1

    def interact(self, player):
        if player.floor == 1 and abs(player.x - (self.x+WINDOW_WIDTH/2)) <= INTERACT_DIST:
            self.locked = True
            return "Window locked."
        return None

    def draw(self, surf):
        rect = pygame.Rect(self.x, FLOOR_Y[1]-120, WINDOW_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(surf, BLUE if self.locked else (120, 180, 220), rect)
        pygame.draw.rect(surf, BLACK, rect, 2)

class Stove:
    def __init__(self):
        self.on = True
        self.x = STOVE_X
        self.floor = 1

    def interact(self, player):
        if player.floor == 1 and abs(player.x - (self.x+20)) <= INTERACT_DIST:
            self.on = False
            return "Stove turned off."
        return None

    def draw(self, surf):
        rect = pygame.Rect(self.x, FLOOR_Y[1]-30, 40, 30)
        pygame.draw.rect(surf, (100,100,100), rect)
        pygame.draw.rect(surf, BLACK, rect, 2)
        # flame indicator
        if self.on:
            pygame.draw.polygon(surf, ORANGE, [
                (self.x+8, rect.top), (self.x+20, rect.top-14), (self.x+32, rect.top)
            ])

class GunPickup:
    def __init__(self):
        self.taken = False
        self.x = GUN_X
        self.floor = 2

    def interact(self, player):
        if not self.taken and player.floor == 2 and abs(player.x - self.x) <= INTERACT_DIST:
            self.taken = True
            player.has_gun = True
            return "Mystery gun equipped."
        return None

    def draw(self, surf):
        if not self.taken:
            rect = pygame.Rect(self.x-8, FLOOR_Y[2]-18, 16, 8)
            pygame.draw.rect(surf, (80,80,80), rect)
            pygame.draw.rect(surf, BLACK, rect, 1)

# -----------------------------
# Combat entities
# -----------------------------
class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.vx = -7 if direction == "left" else 7
        self.radius = 3
        self.alive = True

    def update(self):
        self.x += self.vx
        if self.x < -20 or self.x > WIDTH + 20:
            self.alive = False

    def rect(self):
        return pygame.Rect(int(self.x-self.radius), int(self.y-self.radius), self.radius*2, self.radius*2)

    def draw(self, surf):
        pygame.draw.circle(surf, YELLOW, (int(self.x), int(self.y)), self.radius)

class Thief:
    def __init__(self, side, speed=1.2, hp=1):
        self.side = side  # "left" or "right"
        self.hp = hp
        self.speed = speed
        self.width = 16
        self.height = 26
        self.damage_timer = 0.0
        self.damage_interval = 0.5  # seconds per tick of damage
        self.alive = True

        if side == "left":
            self.x = -30
            self.target_x = THIEF_TARGET_LEFT
            self.vx = abs(speed)
        else:
            self.x = WIDTH + 30
            self.target_x = THIEF_TARGET_RIGHT
            self.vx = -abs(speed)

        # thieves run along ground outside (1F level, just a little lower than house floor)
        self.y = FLOOR_Y[1] + 5

    def rect(self):
        return pygame.Rect(int(self.x-self.width/2), int(self.y-self.height), self.width, self.height)

    def update(self, dt, house):
        if not self.alive: return
        # move until reaching wall, then damage over time
        if (self.side == "left" and self.x + self.vx*dt*60 < self.target_x) or \
           (self.side == "right" and self.x + self.vx*dt*60 > self.target_x):
            self.x += self.vx
        else:
            # at wall: damage house over time
            self.damage_timer += dt
            if self.damage_timer >= self.damage_interval:
                self.damage_timer = 0.0
                house.take_damage(2)

    def hit(self, dmg=1):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

    def draw(self, surf):
        c = (160, 50, 50) if self.side == "left" else (50, 50, 160)
        pygame.draw.rect(surf, c, self.rect())
        pygame.draw.rect(surf, BLACK, self.rect(), 1)

# -----------------------------
# House health + insurance meter
# -----------------------------
class House:
    def __init__(self):
        self.max_hp = 100
        self.hp = self.max_hp

    def take_damage(self, amt):
        self.hp = max(0, self.hp - amt)

    @property
    def insurance_pct(self):
        # Mirrors damage taken so both hit 0%/100% together
        return int((1 - (self.hp / self.max_hp)) * 100)

    def heal_full(self):
        self.hp = self.max_hp

# -----------------------------
# Wave manager
# -----------------------------
class WaveManager:
    def __init__(self):
        self.wave = 0
        self.spawn_timer = 0.0
        self.spawn_interval = 0.9
        self.to_spawn = 0
        self.active = False

    def start_next_wave(self):
        self.wave += 1
        # scales up: count, speed, hp variety
        self.to_spawn = min(1 + self.wave, 8)
        self.spawn_interval = max(0.45, 0.9 - self.wave*0.07)
        self.spawn_timer = 0.0
        self.active = True

    def update(self, dt, thieves):
        if not self.active: return
        if self.to_spawn <= 0:
            # wave is over when all thieves are dead
            if all(not t.alive for t in thieves):
                self.active = False
            return
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            side = random.choice(["left", "right"])
            spd = 1.0 + min(1.8, self.wave * 0.15) + random.uniform(-0.1, 0.2)
            hp = 1 + (1 if random.random() < min(0.15 + self.wave*0.05, 0.6) else 0)
            thieves.append(Thief(side, speed=spd, hp=hp))
            self.to_spawn -= 1

# -----------------------------
# Utility: draw bars & UI
# -----------------------------
def draw_bar(surf, x, y, w, h, pct, fg_color, bg_color):
    pygame.draw.rect(surf, bg_color, (x, y, w, h))
    inner_w = int(w * max(0, min(1, pct)))
    pygame.draw.rect(surf, fg_color, (x, y, inner_w, h))
    pygame.draw.rect(surf, BLACK, (x, y, w, h), 2)

def draw_house_shell(surf):
    # yard background
    surf.fill((15, 25, 35))
    # grass
    pygame.draw.rect(surf, (30, 80, 40), (0, FLOOR_Y[1]+6, WIDTH, HEIGHT - (FLOOR_Y[1]+6)))
    # house body
    body = pygame.Rect(HOUSE_LEFT_WALL_X, FLOOR_TOP[2], HOUSE_RIGHT_WALL_X - HOUSE_LEFT_WALL_X, FLOOR_Y[1] - FLOOR_TOP[2] + 20)
    pygame.draw.rect(surf, (180, 170, 150), body)
    pygame.draw.rect(surf, BLACK, body, 3)
    # floor separators
    pygame.draw.line(surf, BLACK, (HOUSE_LEFT_WALL_X, FLOOR_TOP[1]), (HOUSE_RIGHT_WALL_X, FLOOR_TOP[1]), 3)
    # windows (2F)
    left_win_rect = pygame.Rect(HOUSE_LEFT_WALL_X+8, FLOOR_Y[2]-120, WINDOW_WIDTH, WINDOW_HEIGHT)
    right_win_rect = pygame.Rect(HOUSE_RIGHT_WALL_X-8-WINDOW_WIDTH, FLOOR_Y[2]-120, WINDOW_WIDTH, WINDOW_HEIGHT)
    for wr in [left_win_rect, right_win_rect]:
        pygame.draw.rect(surf, (150, 200, 240), wr)
        pygame.draw.rect(surf, BLACK, wr, 2)

# -----------------------------
# Main game class
# -----------------------------
class Game:
    def __init__(self):
        self.reset_all()

    def reset_all(self):
        self.state = STATE_START
        self.player = Player()
        self.door = Door()
        self.window_r = Window1FRight()
        self.stove = Stove()
        self.gun = GunPickup()
        self.house = House()
        self.bullets = []
        self.thieves = []
        self.waves = WaveManager()
        self.prep_timer = 30.0   # seconds
        self.msg = ""
        self.flash_timer = 0.0
        self.blast_timer = 0.0

    # ------------- state transitions -------------
    def start_prep(self):
        self.state = STATE_PREP
        self.prep_timer = 30.0
        self.msg = "Preparation started! Do the 4 tasks."

    def start_combat(self):
        self.state = STATE_COMBAT
        self.waves.start_next_wave()
        self.msg = "Wave 1 begins!"

    def fail_prep(self):
        self.state = STATE_FAIL
        self.msg = "House caught fire! (Stove left on). Press R to retry."

    def trigger_insurance_blast(self):
        self.state = STATE_INSURANCE_BLAST
        self.blast_timer = 2.5  # show message & effect for 2.5s
        # wipe all enemies
        for t in self.thieves:
            t.alive = False
        self.house.heal_full()
        self.msg = "Don't worry, Insurance has you covered!"

    def finish_with_win(self):
        self.state = STATE_WIN
        self.msg = "Level Complete! Insurance covered your losses."

    # ------------- input handling -------------
    def handle_input(self, events, keys, dt):
        # global navigation
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if self.state == STATE_START and e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                self.start_prep()
            if self.state in (STATE_FAIL, STATE_WIN) and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r or e.key == pygame.K_RETURN or e.key == pygame.K_SPACE:
                    self.reset_all()

        # movement in interactive states
        if self.state in (STATE_PREP, STATE_COMBAT):
            if keys[pygame.K_LEFT]:
                self.player.move_left()
            if keys[pygame.K_RIGHT]:
                self.player.move_right()
            if keys[pygame.K_UP]:
                self.player.move_up()
            if keys[pygame.K_DOWN]:
                self.player.move_down()

            # interact / shoot (A)
            if keys[pygame.K_a]:
                if self.state == STATE_PREP:
                    self._try_prep_interactions()
                elif self.state == STATE_COMBAT:
                    self._try_shoot()

    def _try_prep_interactions(self):
        # try each interactable; show the first message we get
        msg = self.door.interact(self.player)
        if not msg:
            msg = self.window_r.interact(self.player)
        if not msg:
            msg = self.stove.interact(self.player)
        if not msg:
            msg = self.gun.interact(self.player)
        if msg:
            self.msg = msg
            self.flash_timer = 1.2

    def _try_shoot(self):
        # can only shoot from 2F windows, and only if gun equipped
        if not self.player.has_gun or self.player.floor != 2:
            return
        # determine which window the player is nearest to
        left_win_center = HOUSE_LEFT_WALL_X + 8 + WINDOW_WIDTH/2
        right_win_center = HOUSE_RIGHT_WALL_X - 8 - WINDOW_WIDTH/2
        if abs(self.player.x - left_win_center) <= INTERACT_DIST:
            self.bullets.append(Bullet(left_win_center, FLOOR_Y[2]-110, "left"))
        elif abs(self.player.x - right_win_center) <= INTERACT_DIST:
            self.bullets.append(Bullet(right_win_center, FLOOR_Y[2]-110, "right"))

    # ------------- game updates -------------
    def update(self, dt):
        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.state == STATE_PREP:
            self.prep_timer -= dt
            if self.prep_timer <= 0:
                # check stove
                if self.stove.on:
                    self.fail_prep()
                else:
                    # must have completed all tasks to proceed (door/window/gun)
                    all_done = self.door.locked and self.window_r.locked and self.player.has_gun
                    if not all_done:
                        # allow but warn: you can still proceed; thieves harder since you forgot something
                        self.msg = "You forgot a task! Proceeding..."
                    self.start_combat()

        elif self.state == STATE_COMBAT:
            # fire waves and update enemies
            self.waves.update(dt, self.thieves)
            for t in self.thieves:
                t.update(dt, self.house)

            # bullets & collisions
            for b in self.bullets:
                b.update()
                for t in self.thieves:
                    if t.alive and b.alive and b.rect().colliderect(t.rect()):
                        t.hit(1)
                        b.alive = False

            # prune
            self.thieves = [t for t in self.thieves if t.alive]
            self.bullets = [b for b in self.bullets if b.alive]

            # start next wave if cleared
            if not self.waves.active and len(self.thieves) == 0:
                if self.waves.wave >= 3:
                    # For demo: after 3 waves, we force difficulty to push health to 0
                    # Spawn a heavy wave right away
                    self.waves.start_next_wave()
                    self.waves.to_spawn += 4
                else:
                    self.waves.start_next_wave()
                    self.msg = f"Wave {self.waves.wave} begins!"

            # Insurance linkage: when HP hits 0, insurance is 100 -> trigger blast
            if self.house.hp <= 0:
                self.trigger_insurance_blast()

        elif self.state == STATE_INSURANCE_BLAST:
            self.blast_timer -= dt
            if self.blast_timer <= 0:
                self.finish_with_win()

    # ------------- drawing -------------
    def draw(self, surf):
        draw_house_shell(surf)

        # draw interactables
        self.door.draw(surf)
        self.window_r.draw(surf)
        self.stove.draw(surf)
        self.gun.draw(surf)

        # player
        self.player.draw(surf)

        # bullets & thieves
        for b in self.bullets:
            b.draw(surf)
        for t in self.thieves:
            t.draw(surf)

        # UI top bars
        # Health bar (green)
        draw_bar(surf, 20, 15, 260, 16, self.house.hp / self.house.max_hp, GREEN, (40, 60, 40))
        health_label = FONT.render(f"House Health {self.house.hp}%", True, WHITE)
        surf.blit(health_label, (22, 34))

        # Insurance meter (mirrors damage)
        ins_pct = self.house.insurance_pct / 100.0
        draw_bar(surf, WIDTH-280, 15, 260, 16, ins_pct, ORANGE, (60, 50, 40))
        ins_label = FONT.render(f"Insurance Meter {self.house.insurance_pct}%", True, WHITE)
        surf.blit(ins_label, (WIDTH-278, 34))

        # floor labels
        lvl1 = FONT.render("1F", True, WHITE)
        lvl2 = FONT.render("2F", True, WHITE)
        surf.blit(lvl2, (HOUSE_LEFT_WALL_X-30, FLOOR_Y[2]-10))
        surf.blit(lvl1, (HOUSE_LEFT_WALL_X-30, FLOOR_Y[1]-10))

        # state overlays
        if self.state == STATE_START:
            title = FONT_BIG.render("Welcome to Policy Hero!", True, YELLOW)
            subtitle = FONT_BOLD.render("Press SPACE to begin Level 1 (Home Insurance)", True, WHITE)
            surf.blit(title, (WIDTH//2 - title.get_width()//2, 90))
            surf.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 130))
            help_txt = FONT.render("Move: ← →  • Floors: ↑ ↓  • Action/Shoot: A", True, WHITE)
            surf.blit(help_txt, (WIDTH//2 - help_txt.get_width()//2, 165))

        if self.state == STATE_PREP:
            # tasks checklist
            header = FONT_BOLD.render("Preparation (30s) - Complete these 4 tasks:", True, WHITE)
            surf.blit(header, (20, 60))
            items = [
                ("Lock left door (1F)", self.door.locked),
                ("Lock right window (1F)", self.window_r.locked),
                ("Turn off the stove (1F)", not self.stove.on),
                ("Grab the mystery gun (2F)", self.player.has_gun),
            ]
            y = 84
            for text, done in items:
                dot = "✔" if done else "•"
                col = GREEN if done else WHITE
                line = FONT.render(f"{dot} {text}", True, col)
                surf.blit(line, (28, y)); y += 20

            # countdown
            t = max(0, int(math.ceil(self.prep_timer)))
            timer_txt = FONT_BIG.render(f"{t}", True, ORANGE if t <= 10 else YELLOW)
            surf.blit(timer_txt, (WIDTH//2 - timer_txt.get_width()//2, 12))

        if self.state == STATE_COMBAT:
            wave_txt = FONT_BOLD.render(f"Wave {self.waves.wave}", True, WHITE)
            surf.blit(wave_txt, (WIDTH//2 - wave_txt.get_width()//2, 60))
            hint = FONT.render("Shoot from 2F windows using A. Protect the walls!", True, WHITE)
            surf.blit(hint, (WIDTH//2 - hint.get_width()//2, 84))

        if self.state == STATE_FAIL:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,170))
            surf.blit(overlay, (0,0))
            msg1 = FONT_BIG.render("House caught fire!", True, ORANGE)
            msg2 = FONT_BOLD.render("You left the stove on.", True, WHITE)
            msg3 = FONT.render("Press R / ENTER / SPACE to retry", True, WHITE)
            for i, m in enumerate([msg1, msg2, msg3]):
                surf.blit(m, (WIDTH//2 - m.get_width()//2, 130 + i*36))

        if self.state == STATE_INSURANCE_BLAST:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 190, 40, 70))
            surf.blit(overlay, (0,0))
            line1 = FONT_BIG.render("Don't worry,", True, BLACK)
            line2 = FONT_BIG.render("Insurance has you covered!", True, BLACK)
            surf.blit(line1, (WIDTH//2 - line1.get_width()//2, 110))
            surf.blit(line2, (WIDTH//2 - line2.get_width()//2, 145))

        if self.state == STATE_WIN:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            surf.blit(overlay, (0,0))
            line1 = FONT_BIG.render("All damages repaired.", True, YELLOW)
            line2 = FONT_BOLD.render("Level Complete! Insurance covered your losses.", True, WHITE)
            line3 = FONT.render("Press R / ENTER / SPACE to play again", True, WHITE)
            for i, m in enumerate([line1, line2, line3]):
                surf.blit(m, (WIDTH//2 - m.get_width()//2, 120 + i*34))

        # floating message
        if self.msg and self.flash_timer > 0:
            msg = FONT.render(self.msg, True, WHITE)
            surf.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT - 36))

# -----------------------------
# Main loop
# -----------------------------
def main():
    game = Game()
    # auto jump to start screen
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        game.handle_input(events, keys, dt)
        game.update(dt)
        game.draw(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main()

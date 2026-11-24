import pygame
import random
import sys
import os
import json

# Starta Pygame
pygame.init()

# Fönstrets storlek
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hugos Rymdspel")

# Klocka
clock = pygame.time.Clock()

# Färger
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 220, 100)
RED = (230, 50, 50)
BLUE = (70, 150, 255)
YELLOW = (255, 230, 50)
ORANGE = (255, 140, 0)
GRAY = (140, 140, 140)

# Textinställningar
font = pygame.font.SysFont("Arial", 30)
small_font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 55)

# Spelarens inställningar
player_width = 50
player_height = 40
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - 70
player_speed = 7

# Inställningar för svårighetsgrad
ENEMY_SPAWN_DELAY = 70       # Högre tal = färre fiender
ENEMY_START_SPEED = 1        # Fiendernas startfart
ENEMY_SPEED_STEP = 15        # Poäng som krävs för att farten ska öka med 1
SHOOT_BACK_SCORE = 10        # Vid så här många poäng börjar fienderna skjuta
ENEMY_SHOOT_CHANCE = 300     # Högre tal = fienderna skjuter mer sällan
ENEMY_BULLET_SPEED = 4       # Fiendeskottens fart (långsamma)

# Inställningar för namn och highscore
MAX_NAME_LENGTH = 12         # Max antal tecken i namnet
LEADERBOARD_SHOWN = 10       # Hur många som visas på leaderboarden
LEADERBOARD_SAVED = 100      # Hur många resultat som sparas i filen

# Highscore sparas i en fil bredvid spelet, så den finns kvar när spelet stängs
HIGHSCORE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "highscores.json"
)

# Poäng
score = 0

# Spelarens namn
player_name = ""

# Skott och fiender
bullets = []
enemy_bullets = []
enemies = []

# Skapa stjärnor
stars = []

for i in range(100):
    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 3)
    ])


# ---------- Highscore ----------

# Läs in highscores från filen
def load_highscores():
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        scores = []

        for item in data:
            scores.append({
                "name": str(item["name"]),
                "score": int(item["score"])
            })

        scores.sort(key=lambda s: s["score"], reverse=True)
        return scores

    except (OSError, ValueError, KeyError, TypeError):
        # Filen saknas eller är trasig, börja med en tom lista
        return []


# Spara highscores till filen
def save_highscores(scores):
    try:
        temp_file = HIGHSCORE_FILE + ".tmp"

        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)

        # Byt ut den gamla filen först när den nya är helt skriven
        os.replace(temp_file, HIGHSCORE_FILE)

    except OSError:
        print("Kunde inte spara highscore-filen.")


# Lägg till ett nytt resultat och spara listan
def add_score(name, new_score):
    scores = load_highscores()

    # Resultat med 0 poäng sparas inte
    if new_score <= 0:
        return None, scores

    entry = {"name": name, "score": new_score}
    scores.append(entry)

    # Sortera högst poäng först (äldre resultat står kvar före nyare vid lika poäng)
    scores.sort(key=lambda s: s["score"], reverse=True)
    scores = scores[:LEADERBOARD_SAVED]

    save_highscores(scores)

    return entry, scores


# ---------- Ritfunktioner ----------

# Rita bakgrunden
def draw_background():
    screen.fill(BLACK)

    for star in stars:
        pygame.draw.circle(
            screen,
            WHITE,
            (star[0], star[1]),
            star[2] // 2 + 1
        )


# Skapa en fiende
def create_enemy():
    x = random.randint(20, WIDTH - 50)

    enemy = pygame.Rect(x, -40, 40, 40)

    enemies.append(enemy)


# Rita spelaren
def draw_player():
    points = [
        (player_x + player_width // 2, player_y),
        (player_x, player_y + player_height),
        (player_x + player_width, player_y + player_height)
    ]

    pygame.draw.polygon(screen, GREEN, points)

    # Cockpit
    pygame.draw.circle(
        screen,
        BLUE,
        (player_x + player_width // 2, player_y + 25),
        6
    )


# Rita fiender
def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)


# Rita spelarens skott
def draw_bullets():
    for bullet in bullets:
        pygame.draw.rect(screen, YELLOW, bullet)


# Rita fiendernas skott
def draw_enemy_bullets():
    for bullet in enemy_bullets:
        pygame.draw.rect(screen, ORANGE, bullet)


# Visa text
def draw_text(text, font_type, color, x, y):
    image = font_type.render(text, True, color)
    screen.blit(image, (x, y))


# Visa text centrerad i sidled
def draw_text_centered(text, font_type, color, y):
    image = font_type.render(text, True, color)
    screen.blit(image, (WIDTH // 2 - image.get_width() // 2, y))


# Rita leaderboarden
def draw_leaderboard(scores, y_start, highlight=None):
    draw_text_centered("LEADERBOARD", font, YELLOW, y_start)

    y = y_start + 45

    if not scores:
        draw_text_centered("Inga resultat än", small_font, GRAY, y)
        return

    for i, entry in enumerate(scores[:LEADERBOARD_SHOWN]):

        # Markera spelarens eget nya resultat
        if entry is highlight:
            color = GREEN
        else:
            color = WHITE

        draw_text(str(i + 1) + ".", small_font, color, 250, y)
        draw_text(entry["name"], small_font, color, 300, y)

        score_image = small_font.render(str(entry["score"]), True, color)
        screen.blit(score_image, (550 - score_image.get_width(), y))

        y += 27


# ---------- Menyer och skärmar ----------

# Startmeny
def start_menu():

    while True:
        draw_background()

        title = big_font.render(
            "Hugos Rymdspel",
            True,
            GREEN
        )

        screen.blit(
            title,
            (WIDTH // 2 - title.get_width() // 2, 150)
        )

        draw_text_centered(
            "Tryck ENTER för att starta",
            font,
            YELLOW,
            300
        )

        draw_text_centered(
            "Tryck L för att se leaderboarden",
            font,
            BLUE,
            350
        )

        draw_text_centered(
            "Pilar = Flytta | SPACE = Skjut",
            font,
            WHITE,
            430
        )

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    return

                if event.key == pygame.K_l:
                    show_leaderboard()

        pygame.display.update()
        clock.tick(60)


# Visa bara leaderboarden (från startmenyn)
def show_leaderboard():
    scores = load_highscores()

    while True:
        draw_background()

        draw_leaderboard(scores, 60)

        draw_text_centered(
            "Tryck ESC eller ENTER för att gå tillbaka",
            small_font,
            WHITE,
            520
        )

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    return

        pygame.display.update()
        clock.tick(60)


# Skriv in sitt namn
def name_input():
    global player_name

    # Börja med det förra namnet, så man slipper skriva om det
    name = player_name

    while True:
        draw_background()

        draw_text_centered("Skriv ditt namn", big_font, GREEN, 150)

        # Ruta för namnet
        box = pygame.Rect(WIDTH // 2 - 200, 280, 400, 60)
        pygame.draw.rect(screen, WHITE, box, 3)

        # Blinkande markör
        cursor = ""

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor = "|"

        name_image = font.render(name + cursor, True, YELLOW)
        screen.blit(
            name_image,
            (box.x + 15, box.y + 30 - name_image.get_height() // 2)
        )

        draw_text_centered(
            "Tryck ENTER när du är klar",
            small_font,
            WHITE,
            380
        )

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:

                    # Namnet får inte vara tomt
                    if name.strip() != "":
                        player_name = name.strip()
                        return

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]

                else:
                    # Lägg till tecknet (fungerar även med å, ä och ö)
                    if (
                        event.unicode
                        and event.unicode.isprintable()
                        and len(name) < MAX_NAME_LENGTH
                    ):
                        name += event.unicode

        pygame.display.update()
        clock.tick(60)


# Starta om spelet
def reset_game():
    global player_x, score, bullets, enemy_bullets, enemies

    player_x = WIDTH // 2 - player_width // 2
    score = 0
    bullets = []
    enemy_bullets = []
    enemies = []


# Game Over
def game_over():

    # Spara resultatet en gång, direkt när spelet är slut
    entry, scores = add_score(player_name, score)

    new_record = entry is not None and scores[0] is entry

    while True:
        draw_background()

        draw_text_centered("GAME OVER", big_font, RED, 20)

        draw_text_centered(
            player_name + " fick " + str(score) + " poäng!",
            font,
            WHITE,
            90
        )

        if new_record:
            draw_text_centered("NYTT REKORD!", font, YELLOW, 130)

        draw_leaderboard(scores, 175, entry)

        draw_text_centered(
            "R = Spela igen  |  N = Byt namn  |  ESC = Avsluta",
            small_font,
            GREEN,
            545
        )

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    return "again"

                if event.key == pygame.K_n:
                    return "newname"

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(60)


# ---------- Huvudspel ----------

def game():

    global player_x, score

    reset_game()

    enemy_timer = 0
    running = True

    while running:

        clock.tick(60)

        # Händelser
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                # Skjut laser
                if event.key == pygame.K_SPACE:

                    bullet = pygame.Rect(
                        player_x + player_width // 2 - 3,
                        player_y,
                        6,
                        15
                    )

                    bullets.append(bullet)

        # Spelarens rörelse
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            player_x -= player_speed

        if keys[pygame.K_RIGHT]:
            player_x += player_speed

        # Håll spelaren i fönstret
        player_x = max(
            0,
            min(WIDTH - player_width, player_x)
        )

        # Skapa fiender
        enemy_timer += 1

        if enemy_timer >= ENEMY_SPAWN_DELAY:
            create_enemy()
            enemy_timer = 0

        # Flytta fiender (långsamt)
        enemy_speed = ENEMY_START_SPEED + score // ENEMY_SPEED_STEP

        for enemy in enemies[:]:
            enemy.y += enemy_speed

            # Om en fiende når nedre kanten har man förlorat
            if enemy.bottom >= HEIGHT:
                running = False

        # Fienderna skjuter tillbaka när man kommit förbi 10 poäng
        if score >= SHOOT_BACK_SCORE:
            for enemy in enemies:

                # Skjut bara när fienden syns på skärmen
                if enemy.top > 0 and random.randint(1, ENEMY_SHOOT_CHANCE) == 1:

                    enemy_bullet = pygame.Rect(
                        enemy.centerx - 3,
                        enemy.bottom,
                        6,
                        15
                    )

                    enemy_bullets.append(enemy_bullet)

        # Flytta spelarens skott
        for bullet in bullets[:]:
            bullet.y -= 10

            if bullet.bottom < 0:
                bullets.remove(bullet)

        # Flytta fiendernas skott
        for bullet in enemy_bullets[:]:
            bullet.y += ENEMY_BULLET_SPEED

            if bullet.top > HEIGHT:
                enemy_bullets.remove(bullet)

        # Kontrollera träffar på fiender
        for bullet in bullets[:]:
            for enemy in enemies[:]:

                if bullet.colliderect(enemy):

                    if bullet in bullets:
                        bullets.remove(bullet)

                    if enemy in enemies:
                        enemies.remove(enemy)

                    score += 1
                    break

        # Kontrollera kollision med spelaren
        player_rect = pygame.Rect(
            player_x,
            player_y,
            player_width,
            player_height
        )

        for enemy in enemies:

            if player_rect.colliderect(enemy):
                running = False

        # Kontrollera om fiendeskott träffar spelaren
        for bullet in enemy_bullets:

            if player_rect.colliderect(bullet):
                running = False

        # Rita allt
        draw_background()
        draw_player()
        draw_enemies()
        draw_bullets()
        draw_enemy_bullets()

        draw_text(
            "Poäng: " + str(score),
            font,
            WHITE,
            20,
            20
        )

        draw_text(
            "Spelare: " + player_name,
            font,
            WHITE,
            570,
            20
        )

        pygame.display.update()


# ---------- Programmets huvudloop ----------

start_menu()

name_input()

while True:

    game()

    choice = game_over()

    # Vill man byta namn visas namnskärmen igen
    if choice == "newname":
        name_input()

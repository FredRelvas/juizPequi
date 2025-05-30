import pygame
from field import SSLRenderField
from ball import Ball
from robot import SSLRobot
from utils import COLORS
from game_logic import get_ball_possession, check_ball_direction_change, update_last_touch # Atualize esta linha
#import time

# Inicialização do pygame
pygame.init()

# Criação do campo e da janela
field = SSLRenderField()
screen = pygame.display.set_mode(field.window_size)
pygame.display.set_caption("Simulação Futebol de Robôs")
clock = pygame.time.Clock()

# Escala usada
scale = field.scale

# Definir limites do campo para os robôs
min_x = scale * SSLRenderField.margin  # LINHAS DE FUNDO
max_x = field.screen_width - scale * SSLRenderField.margin # LINHAS DE FUNDO
min_y = scale * SSLRenderField.margin  # LATERAIS
max_y = field.screen_height - scale * SSLRenderField.margin# LATERAIS
robot_bounds = (min_x-25, max_x+25, min_y-25, max_y+25)

# Limites bola
ball_bounds = (min_x+10, max_x-10, min_y, max_y)

# Inicializa bola
ball = Ball(x=field.center_x, y=field.center_y, scale=scale)

# Inicializa robôs
robots = []
# Time azul
robots += [
    SSLRobot(x=field.center_x - 1.5 * scale, y=field.center_y - scale, direction=0, scale=scale, id=0, team_color=COLORS["BLUE"]),
    SSLRobot(x=field.center_x - 1.5 * scale, y=field.center_y,         direction=0, scale=scale, id=1, team_color=COLORS["BLUE"]),
    SSLRobot(x=field.center_x - 1.5 * scale, y=field.center_y + scale, direction=0, scale=scale, id=2, team_color=COLORS["BLUE"]),
]
# Time vermelho
robots += [
    SSLRobot(x=field.center_x + 1.5 * scale, y=field.center_y - scale, direction=180, scale=scale, id=0, team_color=COLORS["RED"]),
    SSLRobot(x=field.center_x + 1.5 * scale, y=field.center_y,         direction=180, scale=scale, id=1, team_color=COLORS["RED"]),
    SSLRobot(x=field.center_x + 1.5 * scale, y=field.center_y + scale, direction=180, scale=scale, id=2, team_color=COLORS["RED"]),
]
controlled_robot = robots[1]  # Robô azul que será controlado com o teclado
# Velocidades de movimento
speed = 1.5
rotation_speed = 2

def is_goal(ball, field):
    # Medidas já escaladas
    goal_top = (field.screen_height - field.goal_width) / 2
    goal_bottom = goal_top + field.goal_width

    # Gol à esquerda
    if field.margin - field.goal_depth <= ball.x <= field.margin:
        if goal_top <= ball.y <= goal_bottom:
            return "LEFT"

    # Gol à direita
    right_goal_x = field.screen_width - field.margin
    if right_goal_x <= ball.x <= right_goal_x + field.goal_depth:
        if goal_top <= ball.y <= goal_bottom:
            return "RIGHT"

    return None


# Quem tocou por último
last_touch_info = (None, None) 

goal_posts_info = {
    "LEFT": {
        "x_min": field.margin - field.goal_depth,
        "x_max": field.margin,
        "y_min": (field.screen_height - field.goal_width) / 2,
        "y_max": (field.screen_height - field.goal_width) / 2 + field.goal_width
    },
    "RIGHT": {
        "x_min": field.screen_width - field.margin,
        "x_max": field.screen_width - field.margin + field.goal_depth,
        "y_min": (field.screen_height - field.goal_width) / 2,
        "y_max": (field.screen_height - field.goal_width) / 2 + field.goal_width
    }
}

# Loop principal
running = True
while running:
    clock.tick(60)  # 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Leitura de teclas pressionadas
    keys = pygame.key.get_pressed()
    vx = vy = vtheta = 0

    if keys[pygame.K_w]:
        vy -= speed
    if keys[pygame.K_s]:
        vy += speed
    if keys[pygame.K_a]:
        vx -= speed
    if keys[pygame.K_d]:
        vx += speed
    if keys[pygame.K_q]:
        vtheta -= rotation_speed
    if keys[pygame.K_e]:
        vtheta += rotation_speed

# Aplica movimento ao robô controlado
    controlled_robot.move(vx, vy, vtheta, bounds=robot_bounds)
    
    # Verifica se a bola saiu pelas laterais (parte superior ou inferior do campo)
    if ball.y < min_y or ball.y > max_y:
        print("Lateral!")

    # Reposiciona a bola na linha lateral (mantém y)
        ball.y = min_y if ball.y < min_y else max_y

    
    # Verifica se a bola saiu pelas linhas de fundo (parte direita ou esquerda do campo)
    if ball.x < min_x or ball.x > max_x:
        print("Linha de Fundo!")

    # Define se saiu pela esquerda ou direita
        saiu_pela_esquerda = ball.x < min_x

    # Define posição de recuo dentro da área de pênalti
        if saiu_pela_esquerda:
            ball.x = field.margin + field.penalty_length / 2
        else:
            ball.x = field.screen_width - field.margin - field.penalty_length / 2

    # Centraliza verticalmente a bola dentro da área de pênalti
        ball.y = field.screen_height / 2

    # Para a bola
        ball.vx = 0
        ball.vy = 0

    current_possession_id, current_possession_team_color = get_ball_possession(ball, robots)

    if current_possession_id is not None:
        if current_possession_team_color == COLORS["BLUE"]:
            print(f"Posse da bola: Time Azul, Robô ID: {current_possession_id}")
        elif current_possession_team_color == COLORS["RED"]:
            print(f"Posse da bola: Time Vermelho, Robô ID: {current_possession_id}")
    else:
        print("Posse da bola: Livre")
        #time.sleep(1)
    

    # Limpa tela e desenha campo
    field.draw(screen)

    # Atualiza e desenha robôs
    for robo in robots:
        robo.draw(screen)
        # Exemplo de movimento para testar
        robo.move(vx=0, vy=0, vtheta=0.5)  # rotacionando devagar

        # Colisão com a bola
        if ball.check_collision(robo):
            ball.bounce_off(robo)#, bounds=ball_bounds)
        
        ball.update()

        last_touch_info = update_last_touch(ball, robots, last_touch_info, goal_posts_info)

        current_possession_id, current_possession_team_color = get_ball_possession(ball, robots)

        if current_possession_id is not None:
            if current_possession_team_color == COLORS["BLUE"]:
                print(f"Posse da bola: Time Azul, Robô ID: {current_possession_id}")
            elif current_possession_team_color == COLORS["RED"]:
                print(f"Posse da bola: Time Vermelho, Robô ID: {current_possession_id}")
        else:
            print("Posse da bola: Livre")
    
        if last_touch_info[0] is not None:
            if last_touch_info[1] == COLORS["BLUE"]:
                print(f"Último toque: Time Azul, Robô ID: {last_touch_info[0]}")
            elif last_touch_info[1] == COLORS["RED"]:
                print(f"Último toque: Time Vermelho, Robô ID: {last_touch_info[0]}")
        else:
            print("Último toque: Nenhum (ou Trave)")

    goal_side = is_goal(ball, field)
    if goal_side:
        print(f"Gol do lado {goal_side}!")

    # Reposiciona a bola no centro
        ball.x = field.center_x
        ball.y = field.center_y
        ball.vx = 0
        ball.vy = 0



    # Desenha bola
    ball.draw(screen)

    pygame.display.flip()

pygame.quit()

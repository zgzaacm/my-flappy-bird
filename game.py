import pygame, sys, random

# 在初始化前，将mixer质量调低，避免声音出现延迟
pygame.mixer.pre_init(channels=1, buffer=256)
# 初始化游戏
pygame.init()
# 设置屏幕大小
x, y = 345, 612
screen = pygame.display.set_mode((x, y))
# 控制每秒最多的帧数
clock = pygame.time.Clock()
# 载入游戏字体
game_font = pygame.font.Font('04B_19.ttf', 25)

# 游戏内置变量
gravity = 0.25 # 小鸟下降的每帧加速度
bird_movement = 0 # 初始速度
game_active = False # 初始游戏状态
score = 0 # 初始得分
high_score = 0 # 初始最高分数
first_time = True # 是否第一次开始游戏
last_over = [] # 记录小鸟上一次超过的柱子

# 1. 背景图片
# 载入图片 convert会让pygame更快处理 减少延迟
bg_surface = pygame.image.load('assets/background-day.png').convert()
# 放缩图片到合适的大小
bg_surface = pygame.transform.scale(bg_surface,(x, y))

def scale_size(t, x=2):
    return (int(t[0] // 5 * 3 * x), int(t[1] // 5 * 3 * x))

# 2.地板图片载入 与之前同理
floor_surface = pygame.image.load('assets/base.png').convert()
floor_size = floor_surface.get_size()
floor_surface = pygame.transform.scale(floor_surface, (402, 132))
floor_x_pos = 0 # 为了做成动画效果 地板位置不断后退 两块地板循环后退

# 3.管道载入
pipe_surface = pygame.image.load('assets/pipe-green.png').convert()
pipe_surface = pygame.transform.scale(pipe_surface, (60, 576))
pipe_size = pipe_surface.get_size()
# 管道列表 每隔一段时间出现新的管道
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pipe_generate_time = 1300
pygame.time.set_timer(SPAWNPIPE, pipe_generate_time)
# 随机从这里抽出管道高度
pipe_height = [240, 360, 400, 300, 200]

# 4.小鸟图片载入
def create_bird(path):
    # 得到鸟的一张图片 因为要做成动画 需要连续播放三张图片
    bird_surface = pygame.image.load('assets/bluebird-'+path+'flap.png').convert_alpha()
    bird_surface = pygame.transform.scale(bird_surface, (36, 24))
    return bird_surface
bird_frames = [create_bird(path) for path in ['down', 'mid', 'up']]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center=(60, y//2-50))
# 创建用户event的标志
BIRDFLAP = pygame.USEREVENT + 1
# 设置该事件每200毫秒触发一次
pygame.time.set_timer(BIRDFLAP, 200)


# 5.gameover界面载入
game_over_surface = pygame.image.load('assets/message.png').convert_alpha()
game_over_size = game_over_surface.get_size()
game_over_surface = pygame.transform.scale(game_over_surface, (205, 302))
game_over_rect = game_over_surface.get_rect(center = (x // 2, y // 2 - 30))

# sound载入
flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
hit_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
death_sound = pygame.mixer.Sound('sound/sfx_die.wav')
score_sound = pygame.mixer.Sound('sound/sfx_point.wav')
swo_soung = pygame.mixer.Sound('sound/sfx_swooshing.wav')

# 绘制地板
def draw_floor():
    global floor_x_pos
    floor_x_pos -= 1
    # 绘制两块地板 造成连续的假象
    screen.blit(floor_surface, (floor_x_pos, y - floor_size[1]))
    screen.blit(floor_surface, (floor_x_pos + floor_size[0], y - floor_size[1]))
    if floor_x_pos <= - floor_size[0]:
        floor_x_pos = 0

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop = (x + pipe_size[0], random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom = (x + pipe_size[0], random_pipe_pos - 190))
    return bottom_pipe, top_pipe

def move_pipes():
    global pipe_list
    for pipe in pipe_list:
        pipe.centerx -= 2
    pipe_list = list(filter(lambda pipe: 
    pipe.centerx > -pipe_size[0], pipe_list))

def draw_pipes():
    global pipe_list
    for pipe in pipe_list:
        if pipe.bottom >= y:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)

def check_collision():
    global pipe_list
    for pipe in pipe_list:
        if bird_rect.colliderect(pipe):
            hit_sound.play()
            death_sound.play()
            return False
    if bird_rect.top <= -100 or bird_rect.bottom >= y - floor_size[1]:
        hit_sound.play()
        death_sound.play()
        return False
    return True

def draw_bird():
    global bird_movement
    bird_movement += gravity
    new_bird = pygame.transform.rotozoom(bird_surface,  - bird_movement * 3, 1)
    bird_rect.centery += bird_movement
    screen.blit(new_bird, bird_rect)

def bird_animation():
    new_bird_surface = bird_frames[bird_index]
    new_bird_rect = bird_surface.get_rect(center=(60, bird_rect.centery))
    return new_bird_surface, new_bird_rect

def score_display(game_state):
    global high_score, score
    if game_state == 'main_game':
        score_surface = game_font.render(f'Score: {int(score)}', False, (255, 255, 255))
        score_rect = score_surface.get_rect(center = (x // 2, 60))
        screen.blit(score_surface, score_rect)
    else:
        screen.blit(game_over_surface, game_over_rect)
        score_surface = game_font.render(f'Score: {score}', False, (255, 0, 0))
        score_rect = score_surface.get_rect(center = (x // 2, 60))
        screen.blit(score_surface, score_rect)
        
        if score > high_score:
            high_score = score

        high_score_surface = game_font.render(f'High score : {high_score}', False, (0, 0, 255))
        high_score_rect = high_score_surface.get_rect(center = (x // 2, 470))
        screen.blit(high_score_surface, high_score_rect)

def calculate_score():
    global score, pipe_list, bird_rect, last_over
    if len(pipe_list) > 0 and pipe_list[0] not in last_over and bird_rect.centerx > pipe_list[0].centerx:
        last_over = (pipe_list[0], pipe_list[1])
        score += 1
        score_sound.play()

while True: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = -8
                flap_sound.play()
            if event.key == pygame.K_SPACE and not game_active:
                swo_soung.play()
                first_time = False
                game_active = True
                last_over = []
                score = 0
                bird_index = 0
                pipe_list.clear()
                bird_movement = 0
                bird_rect.center = (60, y//2-50)
        if event.type == SPAWNPIPE and game_active:
            pipe_list.extend(create_pipe())
        if event.type == BIRDFLAP and game_active:
            bird_index += 1
            bird_index %= 3
            bird_surface, bird_rect = bird_animation()

    screen.blit(bg_surface, (0, 0))

    if game_active:
        # bird
        draw_bird()

        # Pipes
        move_pipes()
        draw_pipes()

        # score
        calculate_score()
        score_display('main_game')
    else:
        score_display('game_over')
    
    # 游戏进行时检测碰撞
    if not first_time and game_active:
        game_active = check_collision()

    draw_floor()

    # 每帧更新
    pygame.display.update()

    # fps
    clock.tick(120)
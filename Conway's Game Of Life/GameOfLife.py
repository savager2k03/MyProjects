import pygame
import random

'''An implementation of Conway's Game of Life using pygame'''
#TODO: implement using numpy
#TODO: show realtime fps
#TODO: do some proper commenting
#TODO: a way to zoom in & zoom out 
#TODO: an option for loading preset patterns
#TODO: portal thing,preset loader,auto expand
#TODO: REDUCE THE USE OF GLOBALS (8)
#TODO: auto expand
#TODO: replace toggle portal with something else,maybe 'kill out of bounds' button
#TODO: fix selection overlay when resizing cell width/grid

print('the icons used in this program are from https://www.flaticon.com/.')
pygame.init()

cell_width = 7
cell_margin = 1
grid_size = 20
grid_res = (grid_size*(cell_margin+cell_width))


min_res_x = grid_res + 60 + 2
min_res_y = 240 + 2

resolution = (min_res_x,min_res_y)
screen = pygame.display.set_mode(resolution)

pygame.display.set_caption("GAME OF LIFE")

clock = pygame.time.Clock()

font = pygame.font.Font('freesansbold.ttf',12)

pause_icon      = pygame.transform.scale(pygame.image.load('pause.png'     ),(30, 30)) 
resume_icon     = pygame.transform.scale(pygame.image.load('resume.png'    ),(30, 30)) #x0
clear_icon      = pygame.transform.scale(pygame.image.load('clear.png'     ),(30, 30))

fps_incr_icon   = pygame.transform.scale(pygame.image.load('fast.png'      ),(30, 30)) #x1
fps_decr_icon   = pygame.transform.scale(pygame.image.load('slow.png'      ),(30, 30))

next_gen_icon   = pygame.transform.scale(pygame.image.load('next.png'      ),(30, 30)) #x2
prev_gen_icon   = pygame.transform.scale(pygame.image.load('prev.png'      ),(30, 30))

random_icon     = pygame.transform.scale(pygame.image.load('random.png'    ),(30, 30)) #x3
preset_icon     = pygame.transform.scale(pygame.image.load('preset.png'    ),(30, 30))

settings_icon   = pygame.transform.scale(pygame.image.load('settings.png'  ),(30, 30)) #x4
defaults_icon   = pygame.transform.scale(pygame.image.load('defaults.png'  ),(30, 30)) 

fps_icon        = pygame.transform.scale(pygame.image.load('fps.png'       ),(30, 30)) #x5
generation_icon = pygame.transform.scale(pygame.image.load('generation.png'),(30, 30)) 

portal_icon     = pygame.transform.scale(pygame.image.load('portal.png'    ),(30, 30)) #x6
expand_icon     = pygame.transform.scale(pygame.image.load('expand.png'    ),(30, 30))

info_icon       = pygame.transform.scale(pygame.image.load('info.png'      ),(30, 30)) #x7
exit_icon       = pygame.transform.scale(pygame.image.load('exit.png'      ),(30, 30))

plus_icon       = pygame.transform.scale(pygame.image.load('plus.png'      ),(10, 10)) 
minus_icon       = pygame.transform.scale(pygame.image.load('minus.png'    ),(10, 10))



colors = (
    '#2f2f2f',
    '#dd0531',
    '#65dc98',
    '#5f5f5f',
    '#ffffff',
    '#ff89ff',
    '#fdd890',
    '#6289f8',
    '#a0ffe3',
    '#007fff')

background_color = colors[0]
living_cell_color = colors[1]
dead_cell_color = colors[9]

cell_size_text = font.render("CELLWIDTH",True,colors[0])
grid_size_text = font.render("GRIDSIZE",True,colors[0])
 
def make_grid():
    global grid
    grid = []
    for i in range(grid_size):
        grid.append([])
        for j in range(grid_size):
            grid[i].append(0)
def algorithm():
    global generation,grid_size
    generation += 1  
    new_children = []
    dead_parents = []

    for i in range(grid_size):
        for j in range(grid_size): 

            #fixme:gotta fix it anyways
            # if auto_expand_state == True:
            #     if grid[i][j] == 1 and (i>=len(grid)-2 or j>=len(grid)-2): #just in case a live cell is near SE ↘️, 
            #         grid_size += 1

            #     if grid[i][j] == 1 and (i<=1 or j<=1):#just in case a live cell is near NW ↖️, 
            #         grid_size += 1
            #     expand_grid()
            #     update_dimensions()


            living_neighbors = get_living_neighbors(i,j)
            if len(living_neighbors) <= 1 or len(living_neighbors) >= 4:
                dead_parents.append([i,j])
            elif len(living_neighbors) == 3 :
                new_children.append([i,j])
    take_birth(new_children)                
    rest_in_peace(dead_parents)
def get_living_neighbors(cell_x,cell_y):
    neighbors = [
            [cell_x-1,cell_y-1],
            [cell_x+1,cell_y+1],
            [cell_x+1,cell_y],
            [cell_x-1,cell_y],
            [cell_x,cell_y+1],
            [cell_x,cell_y-1],
            [cell_x+1,cell_y-1],
            [cell_x-1,cell_y+1],
            ]
    living_neighbors = []
    for i in neighbors:
        if portal_state:
            if i[0] < 0:
                i[0] = grid_size-1
            elif i[0] >= grid_size:
                i[0] = 0
            if i[1] < 0:
                i[1] = grid_size-1
            elif i[1] >= grid_size:
                i[1] = 0
        
        elif i[0] < 0 or i[1] < 0 or i[0] >= grid_size or i[1] >= grid_size:
            continue

        if grid[i[0]][i[1]] == 1:
            living_neighbors.append(i)
    return living_neighbors
def take_birth(children):
    for new_child in children:
        grid[new_child[0]][new_child[1]] = 1
def rest_in_peace(parents):
    for dead_parent in parents:
        grid[dead_parent[0]][dead_parent[1]] = 0
def draw_the_grid():
    for row in range(grid_size):
        for column in range(grid_size):
            if grid[row][column] == 1:
                color = living_cell_color
            else:
                color = dead_cell_color
            pygame.draw.rect(screen,color,((row*(cell_width+cell_margin)),(column*(cell_width+cell_margin)),cell_width,cell_width))
def get_clicked_cell(raw_position):
    global grid
    row = (raw_position[0]//(cell_width+cell_margin))
    column = (raw_position[1]//(cell_width+cell_margin))

    if row >= grid_size or column >= grid_size:
        return 0

    if grid[row][column] == 1:
        grid[row][column] = 0
    elif grid[row][column] == 0:
        grid[row][column] = 1



def update_dimensions(skip=0):
    global selection_overlay,overlay,grid_res,min_res_x,min_res_y,resolution,screen
    if grid_size*(cell_margin+cell_width) <= 160 and skip == 0:
        return 0
    selection_overlay = [(grid_size/2)*(cell_width+1),(grid_size/2)*(cell_width+1)]
    overlay = pygame.Surface((cell_width,cell_width))
    grid_res = (grid_size*(cell_margin+cell_width))
    min_res_x = grid_res + 60 + 2
    min_res_y = grid_res + 80 + 2 
    resolution = (min_res_x,min_res_y)
    screen = pygame.display.set_mode(resolution)


    item_dict['icon'][0][1] = [grid_res-55,  grid_res+20+5]
    item_dict['icon'][1][1] = [grid_res-15, grid_res+20+5]
    item_dict['icon'][2][1] = [grid_res-55,  grid_res+40+5]
    item_dict['icon'][3][1] = [grid_res-15, grid_res+40+5]

    offset = min_res_y-32
    for i in item_dict['icon'][-1:3:-2]:
        i[1] = [grid_res+30,offset]
        offset-=30

    offset = min_res_y-32
    for i in item_dict['icon'][-2:3:-2]:
        i[1] = [grid_res,offset]
        offset-=30

    item_dict['surface'][0][2] = [grid_res,0,60,min_res_y]
    item_dict['surface'][1][2] = [0,grid_res,grid_res,80]
            
    item_dict['text'][0][1][1] = grid_res+5
    item_dict['text'][1][1][0] = grid_res-50
    item_dict['text'][1][1][1] = grid_res+5
    item_dict['text'][2][1][1] = grid_res+20+5
    item_dict['text'][3][1][0] = grid_res-32
    item_dict['text'][3][1][1] = grid_res+20+5
    item_dict['text'][4][1][1] = grid_res+40+5
    item_dict['text'][5][1][0] = grid_res-32
    item_dict['text'][5][1][1] = grid_res+40+5
    item_dict['text'][6][1][1] = grid_res+60+5


    offset = 0
    for i in item_dict['line'][0:4]:
        i[2] = [grid_res+offset,0,2,min_res_y]  #icon vertical
        offset += 30
    
    offset = min_res_y-2
    for i in item_dict['line'][3:12]:            #icon horizontal
        i[2] = [grid_res,offset,60,2]
        offset -= 30

    offset = 0
    for i in item_dict['line'][12:18]:            #display horizontal
        i[2] = [0,grid_res+offset,grid_res,2]
        offset += 20


    item_dict['line'][17][2] = [0,grid_res,2,80]   #display vertical
    item_dict['line'][18][2] = [80,grid_res,2,60]
def decr_cell_width():
    global cell_width,paused_state
    paused_state = True
    # print(min_res_x,min_res_y)
    if cell_width == 1:
        return
    cell_width -= 1
    if update_dimensions() == 0:
        cell_width += 1
def incr_cell_width():
    global cell_width,paused_state
    paused_state = True
    cell_width += 1
    update_dimensions()
def decr_grid_size():
    global grid_size,paused_state
    paused_state = True
    if grid_size<=10:
        return
    grid_size-=1
    if not update_dimensions() == 0:
        shrink_grid()
    else:
        grid_size+=1
def incr_grid_size():
    global grid_size,paused_state
    paused_state = True
    grid_size+=1
    expand_grid()
    shift_alive()
    update_dimensions()
def expand_grid():
    for i in grid:
        i.append(0)
    new_row = []
    for i in range(grid_size):
        new_row.append(0)
    grid.append(new_row)
def shrink_grid():
    for i in grid:
        i.pop()
    grid.pop()
def shift_alive():
    global grid
    for i in range(-1,-(grid_size+1), -1):
        for j in range(-1,-(len(grid[i])+1),-1):
            if grid[i][j] == 1:
                grid[i][j] = 0
                grid[i+1][j+1] = 1
def toggle_pause():
    global paused_state
    if paused_state == True:
        paused_state = False
    else:
        paused_state = True
def clear_grid():
    global paused_state,generation
    generation = 0
    paused_state = True
    make_grid()
def incr_fps():
    global fps
    if fps < 60:
        fps+=5
def decr_fps():
    global fps
    if fps > 5:
       fps-=5
def prev_gen():
    print('THIS OPTION IS TO BE REMOVED')
    #TODO: removethis button
    # print('Its Impossible to do this coz,COGL is an irreversible cellular automata,\
    #        \neach generation have one and only successor but could be evolved from multiple predecessors')
def next_gen():
    global paused_state
    paused_state = True
    algorithm()
def set_rand():
    global paused_state
    paused_state = True
    clear_grid()
    for i in range(grid_size):
        for j in range(grid_size):
            grid[i][j] = random.randint(0,1)
def load_presets():
    pass
def toggle_settings():
    global settings_state,paused_state
    paused_state = True
    if settings_state == True:
        settings_state = False
    else:
        settings_state = True
def set_defaults():
    global grid_size,cell_width,cell_margin,paused_state
    paused_state = True
    grid_size = 20
    make_grid()
    cell_width = 7
    cell_margin = 1
    update_dimensions(skip=1)
def toggle_fps():
    global fps_state
    if fps_state:
        fps_state = False
        item_dict['text'][1][0] = font.render("",True,colors[0])
        print('Not any useful feature,this option will be removed later')
    else:
        fps_state = True
def toggle_generation():
    global generation_state
    if generation_state:
        generation_state = False
        item_dict['text'][0][0] = font.render("",True,colors[0])
        print('Not any useful feature,this option will be removed later')
    else:
        generation_state = True
def toggle_portal():
    print('not any useful feature :(')
    global portal_state
    if portal_state == True:
        portal_state = False
    else:
        portal_state = True
def auto_expand_grid():
    global auto_expand_state,paused_state
    paused_state = True
    if auto_expand_state == True:
        auto_expand_state = False
        #todo: gotta do something here
    else:
        auto_expand_state = True
def toggle_info():
    global info_state,paused_state,background_color
    if info_state:
        info_state = False
        background_color = colors[0]
        screen = pygame.display.set_mode((min_res_x,min_res_y))
        
    else:
        paused_state = True
        info_state = True
        screen = pygame.display.set_mode((500,200))
        background_color = colors[4]
def exit_program():
    global exit_state
    exit_state = True
def toggle_grid():
    global cell_margin
    if cell_margin == 0:
        cell_margin = 1
    else:
        cell_margin = 0
    update_dimensions()
def change_background_color():
    global background_color
    index = colors.index(background_color)
    index += 1
    if index >= len(colors):
        index = 0
    background_color = colors[index]
def change_living_cell_color():
    global living_cell_color
    index = colors.index(living_cell_color)
    index += 1
    if index >= len(colors):
        index = 0
    if colors[index] == dead_cell_color:
        print('try a better color combination')
    living_cell_color = colors[index]
def change_dead_cell_color():
    global dead_cell_color
    index = colors.index(dead_cell_color)
    index += 1
    if index >= len(colors):
        index = 0
    if colors[index] == living_cell_color:
        print('try a better color combination')
    dead_cell_color = colors[index]
def toggle_big_grid():
    global grid_size,cell_width,fps
    grid_size = 100
    make_grid()
    fps = 60
    cell_width = 2
    update_dimensions()
    

info_list = [
    "John Conway's \"Game Of Life\" Simulation",
    "Implemented using python's Pygame Library",
    "",
    "The Simulation have 4 simple Rules as follows ",
    " > Any live cell with fewer than two live neighbors dies, as if by underpopulation.",
    " > Any live cell with two or three live neighbors lives on to the next generation.",
    " > Any live cell with more than three live neighbors dies, as if by overpopulation.",
    " > Any dead cell with exactly three live neighbors becomes a live cell, as if by reproduction.",
    "",
    "This implementation is not that fast but works at considerate speed for small grids :) ",
]

settings_list = [
    "SHOW GRID",
    "BACKGROUND_COLOR ",
    "LIVING_CELL_COLOR ",
    "DEAD_CELL_COLOR ",
    "GIMME A BIG GRID",
    "PORTAL LIKE BOUNDS"

]




make_grid()
grid[0][1] = 1
grid[1][2] = 1
grid[2][0] = 1
grid[2][1] = 1
grid[2][2] = 1


fps = 60
generation = 1
preset = 'click on shuffle for presets'
x_overlay_change = 0
y_overlay_change = 0


selection_overlay = [(grid_size/2)*(cell_width+1),(grid_size/2)*(cell_width+1)]

overlay = pygame.Surface((cell_width,cell_width))
overlay.fill('#ff0000')
overlay.set_alpha(140)

black_background = pygame.Surface((150,16))
black_background.fill('#1f1f1f')
black_background.set_alpha(230)

info_screen = pygame.Surface((50,50))

fps_counter_display = font.render(str(fps)+" FPS",True,colors[0])
generation_counter_display = font.render("GEN "+str(generation),True,colors[0])
cell_size_display = font.render(str(cell_width),True,colors[0])
grid_size_display = font.render(str(grid_size),True,colors[0])
preset_name = font.render(preset,True,colors[0])


item_dict = {
'icon'    : [
            [minus_icon,     [grid_res-55,  grid_res+20+5], decr_cell_width],
            [plus_icon,      [grid_res-15, grid_res+20+5], incr_cell_width],
            [minus_icon,     [grid_res-55,  grid_res+40+5], decr_grid_size ],
            [plus_icon,      [grid_res-15, grid_res+40+5], incr_grid_size ],
            [resume_icon,          [grid_res,0], toggle_pause     ],   
            [clear_icon,        [grid_res+30,0], clear_grid       ], 
            [fps_incr_icon,       [grid_res,30], incr_fps         ],
            [fps_decr_icon,    [grid_res+30,30], decr_fps         ],
            [prev_gen_icon,       [grid_res,60], prev_gen         ],
            [next_gen_icon,    [grid_res+30,60], next_gen         ],
            [random_icon,         [grid_res,90], set_rand         ],
            [preset_icon,      [grid_res+30,90], load_presets     ],
            [settings_icon,      [grid_res,120], toggle_settings  ],
            [defaults_icon,   [grid_res+30,120], set_defaults     ],
            [fps_icon,           [grid_res,150], toggle_fps       ],
            [generation_icon, [grid_res+30,150], toggle_generation],
            [portal_icon,        [grid_res,180], toggle_portal    ],
            [expand_icon,     [grid_res+30,180], auto_expand_grid ],
            [info_icon,          [grid_res,210], toggle_info      ],
            [exit_icon,       [grid_res+30,210], exit_program     ]
            ]
            ,
'text'    : [
            [generation_counter_display,[5,                        grid_res+5]],
            [fps_counter_display,       [grid_res-50,              grid_res+5]],
            [cell_size_text,            [5,                     grid_res+20+5]],
            [cell_size_display,         [int(grid_res/2)+40+5,  grid_res+20+5]],
            [grid_size_text,            [5,                     grid_res+40+5]],
            [grid_size_display,         [int(grid_res/2)+40+5,  grid_res+40+5]],
            [preset_name,               [5,                     grid_res+60+5]] 
            ]
            ,
'line'    : [
            [screen,colors[0],[grid_res+0  ,0,    2,min_res_y]],  #icon vertical
            [screen,colors[0],[grid_res+30 ,0,    2,min_res_y]],
            [screen,colors[0],[grid_res+60 ,0,    2,min_res_y]],

            [screen,colors[0],[grid_res,0,    60,2]],  #icon horizontal
            [screen,colors[0],[grid_res,30,   60,2]],
            [screen,colors[0],[grid_res,60,   60,2]],
            [screen,colors[0],[grid_res,90,   60,2]],
            [screen,colors[0],[grid_res,120,  60,2]],
            [screen,colors[0],[grid_res,150,  60,2]],
            [screen,colors[0],[grid_res,180,  60,2]],
            [screen,colors[0],[grid_res,210,  60,2]],
            [screen,colors[0],[grid_res,240,  60,2]],

            [screen,colors[0],[0,grid_res+0,  grid_res,2]], #display horizontal
            [screen,colors[0],[0,grid_res+20, grid_res,2]],
            [screen,colors[0],[0,grid_res+40, grid_res,2]],
            [screen,colors[0],[0,grid_res+60, grid_res,2]],
            [screen,colors[0],[0,grid_res+80, grid_res,2]],

            [screen,colors[0],[0,grid_res,2,80]],               #display vertical
            [screen,colors[0],[80,grid_res,2,60]] 
            ]
            ,
'surface' : [
            [screen,colors[2],[grid_res,0,60,min_res_y]],
            [screen,colors[2],[0,grid_res,grid_res,80]] 
            ]
            ,
'settings': (
            (black_background,(0, 0),               toggle_grid),  #show grid
            (black_background,(0,17),   change_background_color),  #change background_color
            (black_background,(0,34),  change_living_cell_color),  #change living cell color
            (black_background,(0,51),    change_dead_cell_color),  #change dead cell color
            (black_background,(0,68),           toggle_big_grid),  #toggle big/small grid
            (black_background,(0,85),             toggle_portal),  #toggle portal like bounds
            )
}   



paused_state = True
info_state = False
settings_state = False
exit_state = False
fps_state = True
generation_state = True
portal_state = False
auto_expand_state = False


# -------- Main Program Loop -----------
while not exit_state:

    #text to render 
    if generation_state:
        item_dict['text'][0][0] = font.render("GEN "+str(generation),True,colors[0])
    if fps_state:
        item_dict['text'][1][0] = font.render(str(fps)+" FPS",True,colors[0])

    item_dict['text'][3][0] = font.render(str(cell_width),True,colors[0])
    item_dict['text'][5][0] = font.render(str(grid_size),True,colors[0])

    #check events 
    event_list = pygame.event.get()
    for event in event_list: 
        if event.type == pygame.QUIT:  
            exit_state = True  

        #check for keypress 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if info_state:
                    toggle_info()
                    continue
                elif settings_state:
                    toggle_settings()
                    continue

                get_clicked_cell((int(selection_overlay[0]),int(selection_overlay[1])))
            if event.key == pygame.K_LEFT:
                x_overlay_change = -(cell_margin+cell_width)
            elif event.key == pygame.K_RIGHT:
                x_overlay_change = (cell_margin+cell_width)
            elif event.key == pygame.K_UP:
                y_overlay_change = -(cell_margin+cell_width)
            elif event.key == pygame.K_DOWN:
                y_overlay_change = (cell_margin+cell_width)
            
        #check for keyrelease 
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                x_overlay_change = 0
                y_overlay_change = 0
        

        #check for mouse click 
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_position = pygame.mouse.get_pos()
            #if it is a left click 
            if event.button == 1:
                if info_state:
                    toggle_info()
                    continue
                elif settings_state:
                    for each_option in item_dict['settings']:
                        position = each_option[1]
                        action = each_option[2]
                        if mouse_position[0] >= position[0] and mouse_position[0] <= position[0]+150 and mouse_position[1] >= position[1] and mouse_position[1] <= position[1]+16:
                            action()
                if get_clicked_cell(mouse_position) == 0: #incase functions returns 0,(in other words, when no match for cell)
                    for button in item_dict['icon'][4:]: # main buttons on the right
                        position = button[1]
                        action = button[2]
                        if mouse_position[0] >= position[0] and mouse_position[0] <= position[0]+30 and mouse_position[1] >= position[1] and mouse_position[1] <= position[1]+30:
                            action()
                    for button in item_dict['icon'][:4]: # some buttons at bottom
                        position = button[1]
                        action = button[2]
                        if mouse_position[0] >= position[0] and mouse_position[0] <= position[0]+10 and mouse_position[1] >= position[1] and mouse_position[1] <= position[1]+10:
                            action()                            

    
    screen.fill(background_color) # fill background_color 

    if info_state:
        for i in range(len(info_list)):
            info_screen = font.render(info_list[i],True,colors[0])
            screen.blit(info_screen,(0,i*10))
        pygame.display.update()
        continue


    
    #blit/draw stuff to the screen -
    for i in item_dict['surface']:
        pygame.draw.rect(*i)
    for i in item_dict['icon']:
        screen.blit(i[0],i[1])
    for i in item_dict['text']:
        screen.blit(*i)
    for i in item_dict['line']:
        pygame.draw.rect(*i)



    #if not paused,then run the Simulation 
    if not paused_state:
        screen.blit(pause_icon,item_dict['icon'][4][1]) 
        algorithm()

    draw_the_grid() #draw the grid/simulation to the screen 

    #whether to draw setting screen 
    if settings_state:
        for i in item_dict['settings']:
            screen.blit(i[0],i[1])
        for i in range(len(settings_list)):
            option = pygame.font.Font('freesansbold.ttf',10).render(settings_list[i],True,colors[2])
            screen.blit(option,(0,i*18))
        pygame.display.update()
        continue


    #for the selection thing 
    tempx = selection_overlay[0]
    tempy = selection_overlay[1]
    selection_overlay[1] += y_overlay_change 
    selection_overlay[0] += x_overlay_change
    if selection_overlay[0] < 0 or selection_overlay[0] >= grid_res or selection_overlay[1] < 0 or selection_overlay[1] >= grid_res:
        selection_overlay[0] = tempx
        selection_overlay[1] = tempy
    screen.blit(overlay,(selection_overlay[0],selection_overlay[1]))

 
    clock.tick(fps)
    pygame.display.update()

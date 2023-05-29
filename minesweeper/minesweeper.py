#BUG: there seems to be a bug where if all neighbours of a cell have hints ,it doesnt reveal its hinted neighbours when clicked
#FIXME: First click shouldnt be on a Mine/Hint
#TODO: A Better Mine distribution
import pygame
import random

pygame.init()
font = pygame.font.Font('freesansbold.ttf',12)

cell_width = 16     
cell_margin = 0

#SET GRID SIZE HERE
grid_size = 15
grid_res = (grid_size*(cell_margin+cell_width))

screen = pygame.display.set_mode((grid_res,grid_res))

pygame.display.set_caption("MINESWEEPER")
clock = pygame.time.Clock()

#windows minesweeper images from https://www.spriters-resource.com/
img_mine_cell = pygame.image.load('./img_mine_cell.png') 
img_exploded_mine_cell = pygame.image.load('./img_exploded_mine_cell.png') 
img_flagged_cell = pygame.image.load('./img_flagged_cell.png') 
img_clicked_cell = pygame.image.load('./img_clicked_cell.png') 
img_unclicked_cell = pygame.image.load('./img_unclicked_cell.png') 
hint_images = {1:pygame.image.load('./img_no1.png'), 
               2:pygame.image.load('./img_no2.png'),
               3:pygame.image.load('./img_no3.png'), 
               4:pygame.image.load('./img_no4.png'), 
               5:pygame.image.load('./img_no5.png'), 
               6:pygame.image.load('./img_no6.png'), 
               7:pygame.image.load('./img_no7.png'), 
               8:pygame.image.load('./img_no8.png')}


grid = []
mine_weight = 25

def set_random_mine():
    # return random.choices((0,1),weights=(100-mine_weight, mine_weight),k=2)
    x = random.randint(0,6)
    if x != 0:
        return 0
    return 1    
    

def make_grid():
    global grid
    row = []
    for row_id in range(grid_size):
        for column_id in range(grid_size):
            row.append([0,set_random_mine(),0,0])
        grid.append(row)
        row = []
    for row in range(grid_size):
        for column in range(grid_size):
            mines=0
            neighbours = get_neighbours(row, column)
            for neighbour in neighbours:
                if neighbour[0] < 0 or neighbour[1] < 0 or neighbour[0] > grid_size-1 or neighbour[1] > grid_size-1:
                    continue
                if grid[neighbour[0]][neighbour[1]][1] == 1:
                    mines+=1

            grid[row][column][3] = mines


def draw_grid(game_status):
    global game_over
    for row in range(grid_size):
        for column in range(grid_size):
            cell = grid[row][column]
            #unclicked
            if cell[0] == 0:
                cell_img = img_unclicked_cell
                if cell[2] == 1:
                    cell_img = img_flagged_cell

            #clicked
            if cell[0] == 1:
                cell_img = img_clicked_cell
                if cell[3] != 0:
                    cell_img = hint_images[cell[3]]
            
            if cell[0] == 1 and cell[1] == 1:
                cell_img = img_mine_cell
            if game_over == 1:
                if cell[1] == 1:
                    cell_img = img_mine_cell
                if cell[2] == 2:
                    cell_img = img_exploded_mine_cell
            screen.blit(cell_img,(row*(cell_width+cell_margin),column*(cell_width+cell_margin)))
    

def on_game_over(row,column):
    global grid,game_over
    print("GAME OVER")
    grid[row][column][2] = 2 #just a way of storing position of exploded mine
    game_over = 1
    # for row in range(grid_size):
    #     for column in range(grid_size):
    #         cell = grid[row][column]
    #         cell[0] = 1


def check_win():
    won = 1
    for i in grid:
        for j in i:
            if j[0] == 0 and j[1] != 1 and j[3] == 0:
                won=0
            if j[2] == 2:
                won=0
    return won


def get_clicked_cell(raw_mouse_position,mouse_state):
    row = (raw_mouse_position[0]//(cell_width+cell_margin))
    column = (raw_mouse_position[1]//(cell_width+cell_margin))
    if True in mouse_state:
        mode = mouse_state.index(True)
        modify_on_click(row,column,mode)


def get_neighbours(row,column):
    return [(row,column+1),(row+1,column+1),(row+1,column),(row+1,column-1),(row,column-1),(row-1,column-1),(row-1,column),(row-1,column+1)]


def reveal(row,column):
    workable = False
    for x in get_neighbours(row, column):
        if x[0] < 0 or x[0] > grid_size-1 or x[1] < 0 or x[1] > grid_size-1:
            continue
        testcell = grid[x[0]][x[1]]
        if testcell[0] == 0 and testcell[3] ==0 and testcell[1] != 1:
            workable = True
    if workable == False:
        return
    for i in get_neighbours(row,column):
        if i[0] < 0 or i[0] > grid_size-1 or i[1] < 0 or i[1] > grid_size-1:
            continue
        cell = grid[i[0]][i[1]]
        if cell[0] == 0 and cell[1] != 1:
            cell[0] = 1
            reveal(i[0],i[1])
            

def modify_on_click(row,column,mode):
    if check_win() == 1:
        print('YOU WON')
       
    global grid
    cell = grid[row][column]
    if cell[0] == 1:
        return
    if mode == 0:
        if cell[1] != 1: #if not a bomb
            cell[0] = 1 #click it
            if cell[3] == 0: #if no hints 
                reveal(row, column) #expand all continuous
        elif cell[1] == 1: #otherwise if a bomb, game over
            on_game_over(row,column)
            
    elif mode == 2:
        if cell[2] == 1:
            cell[2] = 0
        elif cell[2] == 0:
            cell[2] = 1

make_grid()
game_over = 0

dec_weight_icon = pygame.transform.scale(pygame.image.load('./minus.png'),(30,30))
mine_weight_icon= pygame.transform.scale(pygame.image.load('./probability.png'),(30,30))
inc_weight_icon = pygame.transform.scale(pygame.image.load('./plus.png'),(30,30))
dec_size_icon   = pygame.transform.scale(pygame.image.load('./minus.png'),(30,30))
grid_size_icon  = pygame.transform.scale(pygame.image.load('./grid.png'),(30,30))
inc_size_icon   = pygame.transform.scale(pygame.image.load('./plus.png'),(30,30))
gui_items = {
            'icons':
                {
                dec_weight_icon  : (10,grid_res+10),
                mine_weight_icon : (50,grid_res+10),
                inc_weight_icon  : (90,grid_res+10),

                dec_size_icon    : (10,grid_res+50),
                grid_size_icon   : (50,grid_res+50),
                inc_size_icon    : (90,grid_res+50),
                },
            }

exit_state = False
while not exit_state:

    event_list = pygame.event.get()
    for event in event_list: 
        if event.type == pygame.QUIT:  
            exit_state = True  
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                exit_state = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            raw_mouse_position = pygame.mouse.get_pos()
            x,y = raw_mouse_position[0],raw_mouse_position[1]
            # print(x,y)            
            if raw_mouse_position[0] <= grid_res and raw_mouse_position[1] <= grid_res:
                mouse_state = pygame.mouse.get_pressed()
                get_clicked_cell(raw_mouse_position,mouse_state)
    
    screen.fill('#c0c0c0')

    draw_grid(0)
    #TODO: enable user interaction
    # for icon in gui_items['icons']:
    #     screen.blit(icon,gui_items['icons'][icon])
    pygame.display.update()

    if game_over:
        pygame.time.wait(2000)
        exit_state = True
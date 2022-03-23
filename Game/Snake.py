import random, math
import pygame
import tkinter as tk


class cube(object):
    rows = 20
    w = 500
    def __init__(self, start, dirnx = 1, dirny = 0, color = (255, 0, 0)):
        self.pos = start
        self.dirnx = dirnx
        self.dirny = dirny
        self.color = color
    
    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)
    
    def draw(self, surface, eyes = False):
        dis = self.w // self.rows
        i = self.pos[0]
        j = self.pos[1]
        pygame.draw.rect(surface, self.color, (i*dis + 1, j*dis + 1, dis - 2, dis - 2))
        if eyes:
            centre = dis // 2
            radius = 3
            circleMiddle = (i * dis + centre - radius,  j*dis + 8)
            circleMiddl2 = (i * dis + dis - 2*radius,   j*dis + 8)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle, radius)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddl2, radius)
             
         

#=============================================================================    
class snake(object):
    body = []
    turns = {}
    def __init__(self, color, pos):
        self.color = color
        self.head = cube(pos)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1
    
    def reset(self, pos):
        self.head = cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1
    
    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            # Button pressed by user
            keys = pygame.key.get_pressed()
            for key in keys:
                if keys[pygame.K_LEFT]:
                    self.dirnx = -1
                    self.dirny = 0
                elif keys[pygame.K_RIGHT]:
                    self.dirnx = 1
                    self.dirny = 0
                elif keys[pygame.K_UP]:
                    self.dirnx = 0
                    self.dirny = -1
                elif keys[pygame.K_DOWN]:
                    self.dirnx = 0
                    self.dirny = 1
                # SAVE IT IN DICO FOR SNAKE TO MOVE AFTER HEAD
                self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        #
        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                # WHEN ARRIVE AT TAILS, we remove the turn {position: direction}
                if i == len(self.body) - 1:  
                    self.turns.pop(p)
            else:
                if c.dirnx == -1    and c.pos[0] <= 0:              c.pos = (c.rows - 1, c.pos[1])
                elif c.dirnx == 1   and c.pos[0] >= c.rows - 1:     c.pos = (0, c.pos[1])
                elif c.dirny == 1   and c.pos[1] >= c.rows - 1:     c.pos = (c.pos[0], 0)
                elif c.dirny == -1  and c.pos[1] <= 0:              c.pos = (c.pos[0], c.rows - 1)
                else:
                    c.move(c.dirnx, c.dirny)
                
                
    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny
        # Add Tail after Tail
        if dx == 1 and dy == 0:
            self.body.append(cube((tail.pos[0] - 1, tail. pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(cube((tail.pos[0] + 1, tail. pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(cube((tail.pos[0], tail. pos[1] - 1)))
        elif dx == 0 and dy == - 1:
            self.body.append(cube((tail.pos[0], tail. pos[1] + 1)))
        # Place right the Tail
        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy
        
    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:  c.draw(surface, True)
            else:       c.draw(surface)
              
            
#=============================================================================            
def drawGrid(w, rows, surface):
    sizeBtwn = w // rows
    x = 0
    y = 0
    for l in range(rows):
        x = x + sizeBtwn
        y = y + sizeBtwn
        pygame.draw.line(surface, (255,255,255), (x, 0), (x, w))
        pygame.draw.line(surface, (255,255,255), (0, y), (w, y))
        
def redrawWindow(surface):
    global width, rows, s, snack
    surface.fill((0, 0, 0))
    s.draw(surface)
    snack.draw(surface)
    drawGrid(width, rows, surface)
    pygame.display.update()
    
    
def randomSnack(rows, item):
    position = item.body
    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)
        if len(list(filter(lambda z:z.pos == (x, y), position))) > 0:
            continue
        else: break
    return (x,y)
    
def message_box(subject, content):
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    tk.messagebox.showinfo(subject, content)
    try:
        root.destroy()
    except: pass
    
def main():
    global width, rows, s, snack
    width = 500
    rows = 20
    win = pygame.display.set_mode((width, width))
    s = snake ((255, 0, 0), (10, 10))
    snack = cube(randomSnack(rows, s), color = (0,255,0))
    flag = True
    clock = pygame.time.Clock()
    
    while flag:
        # WAIT
        pygame.time.delay(50)
        clock.tick(10)
        # MOVE
        s.move()
        # IF HEAD GOT SNACK
        if s.body[0].pos == snack.pos:
            s.addCube()
            snack = cube(randomSnack(rows, s), color = (0,255,0))
        # IF HEAD BITE BODY
        for x in range(len(s.body)):
            if s.body[x].pos in list(map(lambda z:z.pos, s.body[x+1:])):
                print('Score: ', len(s.body))
                message_box('You lost','Try Again ?')
                s.reset((10, 10))
                break        
        
        redrawWindow(win)
        
    
main()






print(20 // 3)


import pygame
import sys
from settings import *
from buttonClass import *
import requests
from bs4 import BeautifulSoup

class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Sudoku -B Nayak")
        #===== Initialize a window
        self.window=pygame.display.set_mode((WIDTH,HEIGHT))
        self.exit_game = False
        self.running=True
        self.selected=None
        self.mousePos=None
        self.state='playing'
        self.finished=False
        self.cellChanged=False
        self.grid=[]
        self.playingButtons=[]
        self.incorrectCells=[]
        self.menuButtons=[]
        self.endButtons=[]
        self.lockcells=[]
        self.font=pygame.font.SysFont('arial',CELLSIZE//2)
        self.getPuzzle('2')
        self.load()

    def welcome(self):
        img = pygame.image.load("c:\\Users\\Acer\\Desktop\\VS Studio Python\\Sudoku [project 13]\\Welcome-page-001.jpg")
        img = pygame.transform.scale(img,(600,600)).convert_alpha()
        self.exit_game = False
        while not self.exit_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.exit_game = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return
            
            self.window.blit(img,(0,0))
            pygame.display.update()
            pygame.time.Clock().tick(60)

    def run(self):
        self.welcome()
        while self.running:
            if self.state == 'playing':
                self.playing_events()
                self.playing_update()
                self.playing_draw()

        pygame.quit()
        sys.exit()

    def playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running=False
            #===== User click
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.selected=self.mouseOnGrid()
                if self.selected:
                    self.pos=self.selected
                else:
                    self.pos=None
                    for button in self.playingButtons:
                        if button.highlighted:
                            button.click()

            #===== User type a key
            if event.type == pygame.KEYDOWN:
                if self.selected != None and self.selected not in self.lockcells:
                    if str(event.unicode).isnumeric:
                        self.grid[self.selected[1]][self.selected[0]]=int(event.unicode)
                        self.cellChanged=True

    def mouseOnGrid(self):
        """ It's return indexes if you click inside the board otherwise it's return False """
        #====== check mouse click on board or not
        if self.mousePos[0] < gridPos[0] or self.mousePos[1] < gridPos[1]:
            return False
        if self.mousePos[0] > gridPos[0]+gridsize or self.mousePos[1] > gridPos[1]+gridsize:
            return False
        #====== if click on board then return indexes
        return ((self.mousePos[0]-gridPos[0])//CELLSIZE,(self.mousePos[1]-gridPos[1])//CELLSIZE)


    def playing_update(self):
        self.mousePos=pygame.mouse.get_pos()
        for button in self.playingButtons:
            button.update(self.mousePos)

        if self.cellChanged:
            self.incorrectCells=[]
            #print(self.incorrectCells)
            if self.allCelldone():
                self.checkAllCells()
                if len(self.incorrectCells) == 0:
                    finish = False
                    img = pygame.image.load("c:\\Users\\Acer\\Desktop\\VS Studio Python\\Sudoku [project 13]\\You Win_page-0001.jpg")
                    img = pygame.transform.scale(img,(600,600)).convert_alpha()
                    while not finish:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                finish = True
                                self.running=False
                                self.finished = True
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_RETURN:
                                    finish = True
                                    self.getPuzzle(2)
                        self.window.blit(img,(0,0))
                        pygame.display.update()
                        pygame.time.Clock().tick(60)

    def playing_draw(self):
        self.window.fill(WHITE)

        for button in self.playingButtons:
            button.draw(self.window)

        self.shade_incorrect_cells()

        if self.selected:
            self.drawSelection(self.window,self.selected)
        
        self.shade_locked_cells()

        self.drawNumbers(self.window)
        self.drawGrid(self.window)
        self.cellChanged=False
        pygame.display.update()

    def drawGrid(self,window):
        pygame.draw.rect(window,BLACK,(gridPos[0],gridPos[1],WIDTH-150,HEIGHT-150),2)
        for x in range(9):
            pygame.draw.line(window,BLACK, (gridPos[0]+(x*CELLSIZE),gridPos[1]), (gridPos[0]+(x*CELLSIZE),gridPos[1]+450), 2 if x % 3 == 0 else 1)
            pygame.draw.line(window,BLACK, (gridPos[0],gridPos[1]+(x*CELLSIZE)), (gridPos[0]+450,(x*CELLSIZE)+gridPos[1]), 2 if x % 3 == 0 else 1)
            
    def drawSelection(self,window,pos):
        pygame.draw.rect(window,LIGHTBLUE,((self.pos[0]*CELLSIZE)+gridPos[0],(self.pos[1]*CELLSIZE)+gridPos[1],CELLSIZE,CELLSIZE))

    def loadButtons(self):
        self.playingButtons.append(Button(  20,40,WIDTH//7,40,
                                            function=self.checkAllCells,
                                            colour=(27,142,207),
                                            text="Check"))
        
        self.playingButtons.append(Button(  140,40,WIDTH//7,40,
                                            function=self.getPuzzle,
                                            params="1",
                                            colour=(117,172,112),
                                            text="Easy"))
        
        self.playingButtons.append(Button(  WIDTH//2-(WIDTH//7)//2,40,WIDTH//7,40,
                                            function=self.getPuzzle,
                                            params="2",
                                            colour=(204,197,110),
                                            text="Medium"))
        
        self.playingButtons.append(Button(  380,40,WIDTH//7,40,
                                            function=self.getPuzzle,
                                            params="3",
                                            colour=(199,129,48),
                                            text="Hard"))
        
        self.playingButtons.append(Button(  500,40,WIDTH//7,40,
                                            function=self.getPuzzle,
                                            params="4",
                                            colour=(207,68,68),
                                            text="Evil"))
        

    def textToscreen(self,window,text,pos):
        font=self.font.render(text,False,BLACK)
        fontwidth=font.get_width()
        fontheight=font.get_height()
        pos[0] += (CELLSIZE-fontwidth)//2
        pos[1] += (CELLSIZE-fontheight)//2
        window.blit(font,pos)

    def drawNumbers(self,window):
        #===== enumarate use to get a index list
        for yidx,row in enumerate(self.grid):
            for xidx,num in enumerate(row):
                if num != 0:
                    pos = [(xidx*CELLSIZE)+gridPos[0],(yidx*CELLSIZE)+gridPos[1]]
                    self.textToscreen(window,str(num),pos)

    def load(self):
        self.playingButtons = []
        self.loadButtons()
        self.lockcells = []
        self.incorrectCells = []
        self.finished=False
        
        #===== Setting lockedcells from original board 
        for yidx,row in enumerate(self.grid):
            for xidx,num in enumerate(row):
                if num != 0:
                    self.lockcells.append([xidx,yidx])
    
    def shade_locked_cells(self):
        for cell in self.lockcells:
            pygame.draw.rect(self.window,LOCKEDCELLCOLOUR,((cell[0]*CELLSIZE)+gridPos[0],(cell[1]*CELLSIZE)+gridPos[1],CELLSIZE,CELLSIZE))

    def shade_incorrect_cells(self):
        for cell in self.incorrectCells:
            pygame.draw.rect(self.window,INCORRECTCELLCOLOUR,((cell[1]*CELLSIZE)+gridPos[0],(cell[0]*CELLSIZE)+gridPos[1],CELLSIZE,CELLSIZE))

###### Board cheacking Functions #######
    def allCelldone(self):
        for row in self.grid:
            for number in row:
                if number == 0:
                    return False
        return True

    def checkAllCells(self):
        #====== check rows
        for yidx,row in enumerate(self.grid):
            for xidx,num in enumerate(row):
                k=xidx+1
                for j in range(k,len(row)):
                    if self.grid[yidx][j] == num and self.grid[yidx][j] != 0:
                        if [j,yidx] in self.lockcells:
                            self.incorrectCells.append([yidx,xidx])
                        else:
                            self.incorrectCells.append([yidx,j])
        #====== check columns
        for i in range(9):
            for j in range(8):
                num=self.grid[j][i]
                for k in range(j+1,9):
                    if num == self.grid[k][i] and self.grid[j][i] != 0:
                        if [i,k] in self.lockcells:
                            self.incorrectCells.append([j,i])
                        else:
                            self.incorrectCells.append([k,i])
        #====== check smaller grid
        for i in range(3):
            for j in range(3):
                check={}
                index=0
                for m in range((j*3),(j*3)+3):
                    for n in range((i*3),(i*3)+3):
                        check[f'{index}']=[m,n,self.grid[m][n]]
                        index+=1

                list1=list(check.values())
                for k in range(9):
                    num=list1[k]
                    for l in range(k+1,9):
                        if num[2] == list1[l][2] and int(num[2]) != 0:
                            index=[list1[l][1],list1[l][0]]
                            if index in self.lockcells:
                                self.incorrectCells.append([num[0],num[1]])
                            else:
                                self.incorrectCells.append([list1[l][0],list1[l][1]])
##### web scraping #####
    def getPuzzle(self,difficulty):
        #Difficulty passed as string with one digit .1-4
        url=f"https://nine.websudoku.com/?level={difficulty}"
        html=requests.get(url).content
        soup=BeautifulSoup(html,'html.parser')
        ids=[]
        list1=[]
        grid=[]
        data=[]

        for i in range(9):
            for j in range(9):
                ids.append('f'+str(i)+str(j))
        
        for one_id in ids:
            list1.append(str(soup.find(id=one_id)).split(" "))
            
        for item in list1:
            sp=item[7].split('=')
            if sp[0]=='value':
                data.append(int(sp[1].split('"')[1]))
            else:
                data.append(0)

            if len(data) == 9:
                grid.append(data)
                data=[]

        self.grid=grid
        self.load()
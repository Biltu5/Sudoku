import pygame

class Button:
    def __init__(self,x,y,width,height,text=None,colour=(73,73,73),highlightcolour=(189,189,189),
    function=None,params=None):
        self.image=pygame.Surface((width,height))
        self.pos=(x,y)
        self.rect=self.image.get_rect()
        self.rect.topleft=self.pos
        self.width=width
        self.height=height
        self.text=text
        self.colour=colour
        self.function=function
        self.params=params
        self.highlightcolour=highlightcolour
        self.highlighted=False

    def update(self,mouse):
        if self.rect.collidepoint(mouse):
            self.highlighted=True
        else:
            self.highlighted=False

    def draw(self,window):
        self.image.fill(self.highlightcolour if self.highlighted else self.colour)
        if self.text:
            self.drawText()

        window.blit(self.image,self.pos)

    def click(self):
        if self.params:
            self.function(self.params)
        else:
            self.function()

    def drawText(self):
        font = pygame.font.SysFont("arial",20,bold=1)
        text = font.render(self.text,False,(0,0,0))
        width,height = text.get_size()
        x = (self.width - width)//2
        y = (self.height - height)//2
        self.image.blit(text,(x,y))
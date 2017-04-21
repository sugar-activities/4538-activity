# pic_menu.py

import pygame,os,g,utils,math

layouts=[(6,2,3),(12,3,4),(16,4,4),(20,4,5),(30,5,6)]

class Item():
    def __init__(self,img,x,y,r,c,pic_file,ind):
        self.img=img; self.x=x; self.y=y; self.pic_file=pic_file; self.ind=ind
        self.r=r; self.c=c

class Menu(): # edge is the size of the selector box 
    def __init__(self,gutter_x,gutter_y,edge):
        self.edge=edge; self.gutter_x=gutter_x; self.gutter_y=gutter_y
        self.path=os.path.join('data','pics')
        count=0
        self.items=[]
        for filename in os.listdir(self.path):
            item=Item(None,None,None,None,None,filename,count)
            self.items.append(item)
            if count==0:
                img=pygame.image.load(os.path.join(self.path,filename))
                w=img.get_width(); h=img.get_height()
            count+=1
        for layout in layouts:
            if count<=layout[0]: nr=layout[1]; nc=layout[2]; break
        self.pic_w=(g.sy(32)-((nc+1)*gutter_x))/nc; self.pic_h=h*self.pic_w/w
        self.nr=nr; self.nc=nc
        x0=gutter_x+g.offset; y0=gutter_x
        y=y0; ind=0; smooth=True
        for r in range(nr):
            x=x0
            for c in range(nc):
                item=self.items[ind]
                path_file=os.path.join(self.path,item.pic_file)
                img=pygame.image.load(path_file)
                if ind==0:
                    try:
                        img=pygame.transform.smoothscale(\
                            img,(self.pic_w,self.pic_h))
                    except:
                        smooth=False
                if smooth:
                    img=pygame.transform.smoothscale(img,(self.pic_w,self.pic_h))
                else:
                    img=pygame.transform.scale(img,(self.pic_w,self.pic_h))
                item.img=img; item.x=x; item.y=y; item.r=r; item.c=c
                x+=self.pic_w+gutter_x; ind+=1
                if ind==count: break
            if ind==count: break
            y+=self.pic_h+gutter_y
        self.count=count
        self.green=self.items[0]; self.green_set()
            
    def draw(self):
        ind=0
        for item in self.items:
            g.screen.blit(item.img,(item.x,item.y))
            if item==self.green:
                pygame.draw.rect(g.screen,utils.GREEN,\
                        (item.x,item.y,self.pic_w,self.pic_h),self.edge)
            ind+=1
        
    def which(self):
        for item in self.items:
            x,y=item.x,item.y
            if utils.mouse_in(x,y,x+self.pic_w,y+self.pic_h):
                return item
        return None

    def click(self):
        item=self.which()
        if item==None: return None
        self.green=item; return item.pic_file
        
    def set_mouse(self):
        item=self.which()
        if item!=None: self.green=item; self.green_set()

    def enter(self):
        return self.green.pic_file

    def locn(self,r0,c0):
        ind=0
        for r in range(self.nr):
            for c in range(self.nc):
                if r==r0 and c==c0: return self.items[ind]
                ind+=1
        return self.items[0]

    def green_set(self):
        x=self.green.x+self.pic_w/2; y=self.green.y+self.pic_h/2
        pygame.mouse.set_pos((x,y)); g.pos=(x,y)
        
    def right(self):
        r=self.green.r; c=self.green.c
        c+=1
        if c==self.nc: c=0
        self.green=self.locn(r,c); self.green_set()
                
    def left(self):
        r=self.green.r; c=self.green.c
        c-=1
        if c<0: c=self.nc-1
        self.green=self.locn(r,c); self.green_set()
                
    def down(self):
        r=self.green.r; c=self.green.c
        r+=1
        if r==self.nr: r=0
        self.green=self.locn(r,c); self.green_set()
                
    def up(self):
        r=self.green.r; c=self.green.c
        r-=1
        if r<0: r=self.nr-1
        self.green=self.locn(r,c); self.green_set()
                





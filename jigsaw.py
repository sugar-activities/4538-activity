# jigsaw.py
import g,pygame,math,utils,random,os

class Piece:
    def __init__(self,ind):
        self.ind=ind
        self.img=None; self.x0=None; self.y0=None
        self.x=None; self.y=None; self.group=0; self.mates=[]
        self.fixed=False; self.shape=None

class Jigsaw:
    def __init__(self):
        self.pic_file=None
        self.load_shape_imgs(); self.load_shadow_imgs(); self.load_red_imgs()
        mates=[[18,12,27],[18,12,28,13,19],[19,13,29,14,20],[20,14,30],\
               [27,12,21,15,31],[12,28,13,22,16,32,15,21],[13,29,14,23,17,33,16,22],\
               [14,30,34,17,23],\
               [31,15,24],[15,32,16,25,24],[25,16,33,17,26],[26,17,34],\
               [27,0,18,1,28,5,21,4],[1,19,2,29,6,22,5,28],[2,20,3,30,7,23,6,29],\
               [4,21,5,32,9,24,8,31],[5,22,6,33,10,25,9,32],[6,23,7,34,11,26,10,33]]
        # these are worked out from the above
        # eg 0:[18,12,27] -> 18,0 and 27,0 cos >17 is a square
        sq_mates=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        ind=0
        for m in mates:
            for n in m:
                if n>17:
                    if ind not in sq_mates[n-18]:
                        sq_mates[n-18].append(ind)
            ind+=1
        mates+=sq_mates
        self.pieces=[]
        for ind in range(35): pce=Piece(ind); self.pieces.append(pce)
        for ind in range(35):
            pce=self.pieces[ind]
            for i in mates[ind]: pce.mates.append(self.pieces[i])
            pce.shape=8 # square; since 17 of the 35 are squares :o)
            if ind==0: pce.shape=0 # top left
            elif ind==3: pce.shape=2 # top right
            elif ind==8: pce.shape=5 # bottom left
            elif ind==11: pce.shape=7 # bottom right
            elif ind==4: pce.shape=3 # left
            elif ind==7: pce.shape=4 # right
            elif ind in (1,2): pce.shape=1 # 2 top
            elif ind in (9,10): pce.shape=6 # 2 bottom
            elif ind in (12,13,14,5,6,15,16,17): pce.shape=9 # 8 octagons
        self.margin=g.sy(.8); self.next_group=0; self.final=False
        self.glow=False; self.red=False

    def set_piece(self,img,x0,y0,ind):
        for ind0 in range(35):
            if self.pieces[ind0].ind==ind: break;
        pce=self.pieces[ind0]
        pce.img=img; pce.x0=x0+g.offset; pce.y0=y0
        
    def setup(self,pic_file):
        self.pic_file=pic_file
        self.load(pic_file) # fetch image, g.img - will always be fullscreen
        # square side=106.74 works for 1200 pixel wide image
        w=g.img.get_width(); h=g.img.get_height(); g.rect=pygame.Rect(g.offset,0,w,h)
        s=106.74*w/1200.0 # square side ( DON'T USE square image get_width() )
        t=s/math.sqrt(2.0)
        width=s+2.0*t # octagon width
        # octagons or part octagons
        y=-t; ind=0
        for r in range(3):
            x=-t
            for c in range(4):
                img,x1,y1=self.octagon(s,width,x,y)
                self.set_piece(img,x1,y1,ind)
                x+=width+s; ind+=1
            y+=width+s
        y=s
        for r in range(2):
            x=s
            for c in range(3):
                img,x1,y1=self.octagon(s,width,x,y)
                self.set_piece(img,x1,y1,ind)
                x+=width+s; ind+=1
            y+=width+s
        # squares
        y=0
        for r in range(3):
            x=s+t
            for c in range(3):
                x1=x-1; y1=y-1
                if r==0: y1=y
                if r==2: y1=y-2
                img=self.square(s+2,x1,y1)
                self.set_piece(img,x1,y1,ind)
                x+=width+s; ind+=1
            y+=width+s
        y=s+t
        for r in range(2):
            x=0
            for c in range(4):
                x1=x-1; y1=y-1
                if c==0: x1=x
                if c==3: x1=x-2
                img=self.square(s+2,x1,y1)
                self.set_piece(img,x1,y1,ind)
                x+=width+s; ind+=1
            y+=width+s
        self.shuffle()
        

    def shuffle(self):
        imgw=g.img.get_width()
        for pce in self.pieces:
            w=pce.img.get_width(); h=pce.img.get_height()
            pce.x=random.randint(0,imgw-w)+g.offset
            pce.y=random.randint(0,g.h-h)
            pce.group=0; pce.fixed=False
        random.shuffle(self.pieces)
        self.carry=None; self.final=None; self.glow=False

    def draw(self):
        if self.complete(): g.screen.blit(g.img,(g.offset,0)); return
        carry_gp=None
        if self.carry!=None:
            mx,my=g.pos
            self.carry.x=mx+self.dx; self.carry.y=my+self.dy
            if self.carry.group>0:
                self.align(self.carry); carry_gp=self.carry.group
        for pce in self.pieces:
            if pce.fixed: g.screen.blit(pce.img,(pce.x0,pce.y0))
        if not self.glow:
            for pce in self.pieces:
                if not pce.fixed:
                    if pce.group!=carry_gp:
                        g.screen.blit(pce.img,(pce.x,pce.y))
        if self.carry!=None:
            if self.carry.group>0:
                for pce in self.pieces:
                    if not pce.fixed:
                        if pce.group==self.carry.group:
                            shadow=self.shadow_imgs[pce.shape]
                            if self.red: shadow=self.red_imgs[pce.shape]
                            x=pce.x-self.shadow_offset
                            y=pce.y-self.shadow_offset
                            g.screen.blit(shadow,(x,y))
                for pce in self.pieces:
                    if not pce.fixed:
                        if pce.group==self.carry.group:
                            g.screen.blit(pce.img,(pce.x,pce.y))
            else:
                shadow=self.shadow_imgs[self.carry.shape]
                if self.red: shadow=self.red_imgs[pce.shape]
                x=self.carry.x-self.shadow_offset
                y=self.carry.y-self.shadow_offset
                g.screen.blit(shadow,(x,y))
                g.screen.blit(self.carry.img,(self.carry.x,self.carry.y))

    # returns an octagonal piece from g.img, top left x1,y1
    # designed to fit 4 across the 1200 screen - controlled by s value
    def octagon(self,s,width,x,y):
        x1=x; y1=y; surf=None; xlim=g.img.get_width(); ylim=g.img.get_height()
        if x<0 and y<0: x1=0; y1=0; surf=self.shape_imgs[0].copy()
        elif (x+width)>xlim and y<0:
            y1=0; surf=self.shape_imgs[2].copy()
        elif x<0 and (y+width)>ylim:
            x1=0; surf=self.shape_imgs[5].copy()
            y1=ylim-surf.get_height()
        elif (x+width)>xlim and (y+width)>ylim:
            surf=self.shape_imgs[7].copy()
            y1=ylim-surf.get_height()
        elif y<0: y1=0; surf=self.shape_imgs[1].copy()
        elif (y+width)>ylim:
            surf=self.shape_imgs[6].copy(); y1=ylim-surf.get_height()
        elif x<0:
            x1=0; surf=self.shape_imgs[3].copy()
        elif (x+width)>xlim:
            surf=self.shape_imgs[4].copy()
        if surf==None: surf=self.shape_imgs[9].copy()
        w=surf.get_width(); h=surf.get_height()
        surf.blit(g.img,(0,0),(x1,y1,w,h),pygame.BLEND_MIN)
        return surf,x1,y1

    # returns a square piece side s from g.img, top left x,y
    def square(self,s,x,y):
        surf=pygame.Surface((s,s))
        surf.blit(g.img,(0,0),(x,y,s,s))
        return surf

    def solve(self): # for testing only
        for pce in self.pieces: pce.x=pce.x0; pce.y=pce.y0

    def load(self,pic_file):
        req_ratio=1200.0/835.0
        fname=os.path.join('data','pics',pic_file)
        img=pygame.image.load(fname)
        w=img.get_width(); h=img.get_height()
        if w==1200 and h==835:
            g.img=utils.load_image(pic_file,False,'pics')
        else:
            surf=pygame.Surface((1200,835))
            ratio=float(w)/float(h)
            if abs(req_ratio-ratio)>.1:
                if ratio>req_ratio: w=h*req_ratio
                else: h=w/req_ratio
                surf=pygame.Surface((int(w),int(h))); surf.blit(img,(0,0))
                w=1200; h=835
                try:
                    img=pygame.transform.smoothscale(surf,(int(g.imgf*w),int(g.imgf*h)))
                except:
                    img=pygame.transform.scale(surf,(int(g.imgf*w),int(g.imgf*h)))
                g.img=img
            else: # ratio ok - scale to right size
                w=1200; h=835
                try:
                    img=pygame.transform.smoothscale(img,(int(g.imgf*w),int(g.imgf*h)))
                except:
                    img=pygame.transform.scale(img,(int(g.imgf*w),int(g.imgf*h)))
                g.img=img

    def top(self,pce):
        self.pieces.remove(pce)
        self.pieces.append(pce)

    def top_gp(self,gp):
        lst=utils.copy_list(self.pieces)
        for pce in lst:
            if pce.group==gp: self.top(pce)

    def which(self):
        l=utils.copy_list(self.pieces)
        for i in range(35):
            pce=l.pop()
            img=pce.img
            if utils.mouse_on_img(img,(pce.x,pce.y)):
                if not pce.fixed:
                    if pce.group>0:
                        self.top_gp(pce.group)
                    else:
                        self.top(pce)
                    return pce
        return None

    def click(self):
        if self.final: return False #****
        if self.carry:
            pce=self.carry
            self.carry=None # put down
            if pce.group==0:
                self.check(pce)
            else: # check all members of group
                self.check(pce)
                looking=True
                for i in range(100): # no infinite loop possibility
                    looking=False
                    for pce1 in self.pieces:
                        if pce1.group==pce.group:
                            if self.check(pce1): looking=True
                    if not looking:break
                if looking: print '>>>> avoided loop'
            if pce.group>0: self.top_gp(pce.group)
            self.align(pce)
            self.fix()
            if self.glow:
                if not pce.fixed: self.carry=pce; self.red=True
            self.complete()
            return True
        pce=self.which()
        if pce==None: return False
        # pick up
        mx,my=g.pos
        self.carry=pce; self.dx=pce.x-mx; self.dy=pce.y-my
        return True

    def check(self,piece):
        if piece.fixed: return False
        tf=False
        for pce in piece.mates:
            if (piece.group==pce.group) and pce.group>0: #already in same group
                pass
            else:
                dx0=piece.x0-pce.x0; dy0=piece.y0-pce.y0
                dx=piece.x-pce.x; dy=piece.y-pce.y
                if abs(dx-dx0)<self.margin:
                    if abs(dy-dy0)<self.margin:
                        tf=True
                        if pce.group==0:
                            if piece.group==0:
                                self.next_group+=1
                                pce.group=self.next_group
                                piece.group=self.next_group
                            else:
                                pce.group=piece.group
                        else:
                            if piece.group==0:
                                piece.group=pce.group
                            else: # two separate groups
                                for pce1 in self.pieces:
                                    if pce1.group==piece.group:
                                        pce1.group=pce.group
        return tf

    def align(self,pce0):
        gp0=pce0.group
        if gp0>0:
            dddx=pce0.x-pce0.x0; dddy=pce0.y-pce0.y0
            for pce in self.pieces:
                if pce.group==gp0 and (pce<>pce0):
                    ddx=pce.x0-pce0.x0; ddy=pce.y0-pce0.y0
                    dx=ddx; dy=ddy
                    pce.x=pce0.x0+dx+dddx
                    pce.y=pce0.y0+dy+dddy

    def fix(self): #  fix pieces which are in final position or near enough
        for pce in self.pieces:
            if not pce.fixed:
                if abs(pce.x-pce.x0)<self.margin:
                    if abs(pce.y-pce.y0)<self.margin:
                        pce.x=pce.x0; pce.y=pce.y0
                        pce.fixed=True

    def load_shape_imgs(self):
        self.shape_imgs=[0]*10
        self.shape_imgs[5]=utils.load_image('bl.png',True,'shapes')
        self.shape_imgs[7]=pygame.transform.flip(self.shape_imgs[5],True,False)
        self.shape_imgs[0]=pygame.transform.flip(self.shape_imgs[5],False,True)
        self.shape_imgs[2]=pygame.transform.flip(self.shape_imgs[5],True,True)
        self.shape_imgs[3]=utils.load_image('l.png',True,'shapes')
        self.shape_imgs[4]=pygame.transform.flip(self.shape_imgs[3],True,False)
        self.shape_imgs[1]=pygame.transform.rotate(self.shape_imgs[3],-90)
        self.shape_imgs[6]=pygame.transform.rotate(self.shape_imgs[3],90)
        self.shape_imgs[8]=utils.load_image('s.png',True,'shapes') # not used
        self.shape_imgs[9]=utils.load_image('o.png',True,'shapes')

    def load_shadow_imgs(self):
        self.shadow_offset=g.sy(.53)
        self.shadow_imgs=[0]*10
        self.shadow_imgs[5]=utils.load_image('bl.png',True,'shadows')
        self.shadow_imgs[7]=pygame.transform.flip(self.shadow_imgs[5],True,False)
        self.shadow_imgs[0]=pygame.transform.flip(self.shadow_imgs[5],False,True)
        self.shadow_imgs[2]=pygame.transform.flip(self.shadow_imgs[5],True,True)
        self.shadow_imgs[3]=utils.load_image('l.png',True,'shadows')
        self.shadow_imgs[4]=pygame.transform.flip(self.shadow_imgs[3],True,False)
        self.shadow_imgs[1]=pygame.transform.rotate(self.shadow_imgs[3],-90)
        self.shadow_imgs[6]=pygame.transform.rotate(self.shadow_imgs[3],90)
        self.shadow_imgs[8]=utils.load_image('s.png',True,'shadows')
        self.shadow_imgs[9]=utils.load_image('o.png',True,'shadows')

    def load_red_imgs(self):
        self.red_imgs=[0]*10
        self.red_imgs[5]=utils.load_image('bl.png',True,'reds')
        self.red_imgs[7]=pygame.transform.flip(self.red_imgs[5],True,False)
        self.red_imgs[0]=pygame.transform.flip(self.red_imgs[5],False,True)
        self.red_imgs[2]=pygame.transform.flip(self.red_imgs[5],True,True)
        self.red_imgs[3]=utils.load_image('l.png',True,'reds')
        self.red_imgs[4]=pygame.transform.flip(self.red_imgs[3],True,False)
        self.red_imgs[1]=pygame.transform.rotate(self.red_imgs[3],-90)
        self.red_imgs[6]=pygame.transform.rotate(self.red_imgs[3],90)
        self.red_imgs[8]=utils.load_image('s.png',True,'reds')
        self.red_imgs[9]=utils.load_image('o.png',True,'reds')

    def complete(self):
        if self.final: return True
        for pce in self.pieces:
            if not pce.fixed: return False
        self.final=True
        g.ms=pygame.time.get_ticks()
        return True


        

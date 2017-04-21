#!/usr/bin/python
# Oct.py
"""
    Copyright (C) 2011  Peter Hewitt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

"""
# ideal pic size: 1200x835
import g,pygame,utils,sys,load_save,jigsaw,pic_menu,buttons
try:
    import gtk
except:
    pass

class Oct:

    def __init__(self):
        self.journal=True # set to False if we come in via main()
        self.canvas=None # set to the pygame canvas if we come in via activity.py

    def display(self):
        if g.state==1:
            g.screen.fill(utils.CREAM)
            self.menu.draw()
        else:
            g.screen.fill((255,192,192))
            pygame.draw.rect(g.screen,utils.BLACK,g.rect,1)
            self.jigsaw.draw()
            if g.ms!=None: utils.centre_blit(g.screen,g.smiley,g.cxy)
        if g.state==2:
            if self.jigsaw.final: buttons.on('new') 
        buttons.draw()

    def do_click(self):
        if g.state==1:
            pic_file=self.menu.click()
            if pic_file!=None:
                self.jig_click(pic_file)
                g.state=2
            return True
        else:   
            return self.jigsaw.click()

    def jig_click(self,pic_file):
        if pic_file==None: return False
        if pic_file!=self.jigsaw.pic_file:
           self.jigsaw.setup(pic_file) 
        elif self.jigsaw.final: self.jigsaw.setup(pic_file)

    def do_button(self,bu):
        if bu=='new':
            g.state=1; buttons.off('new'); g.ms=None; self.menu.green_set()

    def do_key(self,key):
        if key==pygame.K_v: g.version_display=not g.version_display; return
        if g.state==1:
            if key in g.RIGHT: self.menu.right(); return
            if key in g.LEFT: self.menu.left(); return
            if key in g.DOWN: self.menu.down(); return
            if key in g.UP: self.menu.up(); return
            if key in g.CROSS: self.menu.set_mouse(); self.do_click(); return
            if key in g.TICK:
                pic_file=self.menu.enter()
                self.jig_click(pic_file)
                g.state=2
        elif g.state==2:
            if key in g.SQUARE: self.do_button('new')
            #if key==pygame.K_1: self.jigsaw.solve() ###

    def buttons_setup(self):
        buttons.Button('new',(g.sx(16),g.sy(20.8)))
        buttons.off('new')

    def update(self):
        if g.ms<>None:
            d=pygame.time.get_ticks()-g.ms
            if d>4000: # delay in ms
                g.ms=None # turn smiley off
                g.redraw=True
                
    def flush_queue(self):
        flushing=True
        while flushing:
            flushing=False
            if self.journal:
                while gtk.events_pending(): gtk.main_iteration()
            for event in pygame.event.get(): flushing=True

    def run(self):
        g.init()
        if not self.journal: utils.load()
        self.menu=pic_menu.Menu(g.sy(.2),g.sy(.2),g.sy(.2))
        self.jigsaw=jigsaw.Jigsaw()
        load_save.retrieve()
        self.buttons_setup()
        if self.canvas<>None: self.canvas.grab_focus()
        ctrl=False
        pygame.key.set_repeat(600,120); key_ms=pygame.time.get_ticks()
        going=True
        while going:
            if self.journal:
                # Pump GTK messages.
                while gtk.events_pending(): gtk.main_iteration()

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    if not self.journal: utils.save()
                    going=False
                elif event.type == pygame.MOUSEMOTION:
                    g.pos=event.pos
                    g.redraw=True
                    if self.canvas<>None: self.canvas.grab_focus()
                    self.jigsaw.red=False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.redraw=True
                    if event.button==1:
                        if self.do_click():
                            pass
                        else:
                            bu=buttons.check()
                            if bu!='': self.do_button(bu); self.flush_queue()
                    elif event.button==3:
                        self.jigsaw.glow=not self.jigsaw.glow
                elif event.type == pygame.KEYDOWN:
                    # throttle keyboard repeat
                    if pygame.time.get_ticks()-key_ms>110:
                        key_ms=pygame.time.get_ticks()
                        if ctrl:
                            if event.key==pygame.K_q:
                                if not self.journal: utils.save()
                                going=False; break
                            else:
                                ctrl=False
                        if event.key in (pygame.K_LCTRL,pygame.K_RCTRL):
                            ctrl=True; break
                        self.do_key(event.key); g.redraw=True
                        self.flush_queue()
                elif event.type == pygame.KEYUP:
                    ctrl=False
            if not going: break
            self.update()
            if g.redraw:
                self.display()
                if g.version_display: utils.version_display()
                g.screen.blit(g.pointer,g.pos)
                pygame.display.flip()
                g.redraw=False
            g.clock.tick(40)

if __name__=="__main__":
    pygame.init()
    pygame.display.set_mode()
    game=Oct()
    game.journal=False
    game.run()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)

#load_save.py
import g,utils,jigsaw

loaded=[] # list of strings

def load(f):
    global loaded
    try:
        for line in f.readlines():
            loaded.append(line)
    except:
        pass

def save(f):
    return
    f.write(str(g.v)+'\n')

# note need for rstrip() on strings
def retrieve():
    global loaded
    return
    if len(loaded)>0:
        g.v=int(loaded[0])


    

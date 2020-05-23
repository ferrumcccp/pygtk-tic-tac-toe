import sys
class MemSolver:
    """
    Memorized BFS Solver
    dp: dp array
    In index, two its represent a cell. 0=empty 1=opponent 2=me(the computer)
    -2147483647: Uncalculated
    -10000: I Lose
    0: Draw
    10000: I Win
    next: the best next operation
    -1: Uncalculated
    -2: Final
    0~8 Selection
    """
    dp=[]
    next=[]
    def __init__(self):
        for i in range(0,4**9):
            self.dp.append(-(1<<31)+1)
            self.next.append(-1)
    def revert(self,x):
        for i in range(0,9):
            if x&(3<<(i<<1)):
                x^=(3<<(i<<1))
        return x
    def check_final(self,x):
        """
        Check if the game comes to an end.
        0=Not final.
        1=I lose.
        2=Draw.
        3=I win.
        """
        y=self.revert(x)
        mask={0x30C3:0x2082,0xC30C:0x8208,0x30C30:0x20820,0x3F:0x2A,
        0xFC0:0xA80,0x3F000:0x2A000,0x30303:0x20202,0x3330:0x2220} # 2-2-2 Mask

        for i,j in mask.items():
            if x&i==j:
                return 3
            if y&i==j:
                return 1
        if x^y==(1<<18)-1:
            return 2
        return 0
    def dfs(self,x,dbg=False):
        """
        Memorized DFS on x
        """
        #print("x=%x"%x)
        if self.next[x]!=-1:
            return
        chk=self.check_final(x)
        if chk>0:
            if chk==1:
                self.dp[x]=-10000
            if chk==2:
                self.dp[x]=0
            if chk==3:
                self.dp[x]=10000
            return
        for i in range(0,9):
            if not x&(3<<(i<<1)):
                # Available
                xpie=self.revert(x^(2<<(i<<1)))
                self.dfs(xpie)
                zy=self.dp[xpie]*(-0.9)-5
                if dbg:
                    print("===DG:%d = %d ===",i,zy)
                    for p in range(0,3):
                        for j in range(0,3):
                            print("-XOE"[(xpie>>(p*6+j*2))&3],end="")
                        print("#")
                if zy>self.dp[x]:
                    self.dp[x]=zy
                    self.next[x]=i

class GameMan:
    """
    Game Manager
    """
    def __init__(self):
        self.ms=MemSolver()
        self.curstate=0
        self.turn=0
    def query(self,x,y):
        """
        Query point (x,y)
        """
        if x<0 or x>2 or y<0 or y>2:
            raise Exception("Out of bound:(%d,%d)"%(x,y))
        return (self.curstate>>((x*3+y)<<1))&3
    def set(self,x,y):
        """
        Place a piece at (x,y)
        """
        if self.ms.check_final(self.curstate)>0:
            raise Exception("The game is over.")
        if self.query(x,y)>0:
            raise Exception("Position occupied: (%d,%d)"%(x,y))
        #color=1+self.turn%2
        #print("LSH=%d"%((x*3+y)<<1))
        #print("COLOR=%d"%self.get_color())
        self.curstate|=(self.get_color()<<((x*3+y)<<1))
        self.turn+=1
    def get_color(self):
        return 1+self.turn%2
    def response(self):
        """
        The computer places a piece
        """
        if self.ms.check_final(self.curstate)>0:
            raise Exception("The game is over.")
        #color=1+self.turn%2
        state=self.curstate
        if self.get_color()==1:
            state=self.ms.revert(state) # in white's view
        self.ms.dfs(state)
        pos=self.ms.next[state]
        #print("COLOR=%d"%self.get_color())
        self.curstate|=self.get_color()<<(pos<<1)
        self.turn+=1
    def is_end(self):
        end=self.ms.check_final(self.curstate)
        if end==0:
            return ""
        if end==1:
            return "X wins"
        if end==2:
            return "Draw"
        if end==3:
            return "O wins"

class CLIFe:
    """
    CLI Frontend
    """
    def __init__(self):
        self.gm=GameMan()
    def work(self):
        while True:
            for i in range(0,3):
                for j in range(0,3):
                    print("-XOE"[self.gm.query(i,j)],end="")
                print("")
            if self.gm.is_end()!="":
                break
            #print("CURSTATE=%x %x"%(self.gm.curstate,self.gm.\
            #ms.revert(self.gm.curstate)))
            if self.gm.get_color()==2:
                self.gm.response()
            else:
                x=input()
                if len(x)!=2 or(not ord('0')<=ord(x[0])<ord('3'))or(not ord('0')\
                <=ord(x[1])<ord('3')):
                    print("Bad input.")
                else:
                    xcor=ord(x[0])-ord('0')
                    ycor=ord(x[1])-ord('0')
                    #print("(%d,%d)"%(xcor,ycor))
                    if self.gm.query(xcor,ycor)>0:
                        print("Occupied.")
                    else:
                        self.gm.set(xcor,ycor)
        print(self.gm.is_end())
try:
    import gi
except Exception:
    print("No PyGTK Found. Have fun in the terminal!")
    x=CLIFe()
    x.work()
    import sys
    sys.exit()

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
class GiWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="井字棋")
        self.gm=GameMan()
        self.btab=[[],[],[]]
        gri=Gtk.Grid()
        self.add(gri)
        for i in range(0,3):
            for j in range(0,3):
                self.btab[i].append(Gtk.Button(label="-"))
        for i in range(0,3):
            for j in range(0,3):
                gri.attach(self.btab[i][j],i,j,1,1)
                self.btab[i][j].connect("clicked",self.on_button_click,\
                "%d%d"%(i,j))
    def check_final(self):
        cf=self.gm.is_end()
        if cf=="":
            return
        #dialog=Gtk.MessageDialog(self,0,Gtk.MessageType.INFO,\
        #Gtk.ButtonsType.OK,cf,)
        #dialog=Gtk.MessageDialog()
        #dialog.text=cf
        #dialog.message_type=Gtk.MessageType.INFO
        #dialog.buttons=Gtk.ButtonsType.OK
        dialog=Gtk.MessageDialog(self,0,Gtk.MessageType.INFO,\
        Gtk.ButtonsType.OK,cf,)
        dialog.run()
        dialog.destroy()
        self.destroy()
        sys.exit()
    def updbtn(self):
        for i in range(0,3):
            for j in range(0,3):
                self.btab[i][j].set_label("-XOE"[self.gm.query(i,j)])
    def on_button_click(self,wid,name):
        xcor=ord(name[0])-ord('0')
        ycor=ord(name[1])-ord('0')
        self.gm.set(xcor,ycor)
        self.updbtn()
        self.check_final()
        self.gm.response()
        self.updbtn()
        self.check_final()

win = GiWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

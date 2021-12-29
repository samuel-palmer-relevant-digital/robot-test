import microbit as mb
y=0
s=1
r=2
z=1
w=2
class Inställningar:
 def __init__(a):
  a.riktning=y
  a.sväng=y
 def sätt(a,I,E):
  a.riktning=I
  a.sväng=E
 def sätt_från_annan(a,A):
  a.sätt(A.riktning,A.sväng)
 def är_samma(a,A):
  return a.riktning==A.riktning and a.sväng==A.sväng
 def bild(a):
  if a.sväng==z:
   return mb.Image.ARROW_W
  if a.sväng==w:
   return mb.Image.ARROW_E
  return mb.Image.HEART
def sp(m,d):
 if m.read_digital()!=d:
  m.write_digital(d)
def motsatt_sida(E):
 return w if E==z else w
K=Inställningar()
def flytta(ins):
 K.sätt_från_annan(ins)
 if ins.riktning==s:
  sp(mb.pin13,1)
  sp(mb.pin14,0)
 elif ins.riktning==r:
  sp(mb.pin13,0)
  sp(mb.pin14,1)
 else:
  sp(mb.pin13,0)
  sp(mb.pin14,0)
 if ins.sväng==z:
  sp(mb.pin15,0)
  sp(mb.pin16,1)
 elif ins.sväng==w:
  sp(mb.pin15,1)
  sp(mb.pin16,0)
 else:
  sp(mb.pin15,0)
  sp(mb.pin16,0)
class Öga:
 def __init__(a,m,u):
  a.pin=m
  a.sida=u
  a.minst=1023
  a.senast=0
  a.dold_multi=1
  a.uppdatera()
 def uppdatera(a):
  a.senast=max(a.pin.read_analog(),1)
  a.minst=min(a.minst,a.senast)
  a.dold_multi=a.senast/a.minst
R=Öga(mb.pin1,z)
b=Öga(mb.pin2,w)
O=0.05
U=3 
c=1.2 
e=1000
x=1.2
o=300
C=2000
def hitta_mest_dolda():
 T=max(R.dold_multi,b.dold_multi)
 F=max(R.senast,b.senast)
 N=min(R.senast,b.senast)
 if max(F,1)/max(N,1)<c and T<U:
  return None
 return R if R.senast>b.senast else b
class KraschHanterare:
 def __init__(a):
  a.arr=[]
  a.in_slot=0
  a.minimum=-1
  a.kraschar=False
 def reset(a):
  a.arr.clear()
  a.in_slot=0
  a.minimum=-1
  a.kraschar=False
 def uppdatera(a,tid):
  if K.riktning!=s or K.sväng!=y: 
   a.reset()
   return
  d=abs(mb.accelerometer.get_z())
  if len(a.arr)!=0 and a.arr[-1][1]//100==tid//100:
   a.arr[-1]=((a.arr[-1][0]*a.in_slot+d)/(a.in_slot+1),tid)
   return
  a.arr.append((d,tid))
  a.in_slot=1
  i=False
  while tid-a.arr[0][1]>e:
   a.arr.pop(0)
   i=True
  if not i:
   return
  nu=a.genomsnitt()
  a.minimum=nu if a.minimum==-1 else min(nu,a.minimum)
  if nu/max(a.minimum,1)>x:
   a.kraschar=True
 def genomsnitt(a):
  t=0
  for _,S in enumerate(a.arr):
   t+=S[0]
  return t/len(a.arr)
def hummux():
 h=False
 mb.pin12.write_digital(1)
 l=0
 L=Inställningar()
 W=Inställningar()
 P=False
 X=o
 Y=w
 G=KraschHanterare()
 while True:
  if mb.button_a.was_pressed():
   h=not h
   P=False
  if mb.button_b.was_pressed():
   h=not h
   P=True
  if not h:
   mb.display.show(mb.Image.SAD)
   L.sätt(y,y)
   flytta(L)
   l=0
   X=o
   G.reset()
   continue
  g=mb.running_time()
  R.uppdatera()
  b.uppdatera()
  W.sätt(s,y)
  j=hitta_mest_dolda()
  G.uppdatera(g)
  if j is not None:
   W.sväng=motsatt_sida(j.sida)
  if G.kraschar:
   W.sätt(r,Y)
   L.sätt_från_annan(W)
   l=0
   X=C
   Y=motsatt_sida(Y) 
  if W.är_samma(L):
   if g-l>X:
    if not P:
     flytta(W)
    mb.display.show(W.bild())
  else:
   l=g
   L.sätt_från_annan(W)
hummux()

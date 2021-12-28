import microbit as mb
p=0
g=1
P=2
r=1
U=2
def set_pin(O,e):
 if O.read_digital()!=e:
  O.write_digital(e)
def flytta(i,m):
 if i==g or i==P:
  if mb.pin8.read_digital():
   if i==g:
    set_pin(mb.pin13,1)
    set_pin(mb.pin14,0)
   else:
    set_pin(mb.pin13,0)
    set_pin(mb.pin14,1)
 else:
  set_pin(mb.pin13,0)
  set_pin(mb.pin14,0)
 if m==r:
  set_pin(mb.pin15,0)
  set_pin(mb.pin16,1)
 elif m==U:
  set_pin(mb.pin15,1)
  set_pin(mb.pin16,0)
 else:
  set_pin(mb.pin15,0)
  set_pin(mb.pin16,0)
v=[]
class Öga:
 def __init__(X,O,Y):
  X.pin=O
  X.sida=Y
  X.mest=0
  X.minst=1023
  X.senast=0
  X.förändring=0
  X.boost=0
  X.dold_ökning=0
  X.dold_multi=1
  if Y==r:
   X.andra_sidan=U
  else:
   X.andra_sidan=r
  X.uppdatera_värde()
 def andra_ögat(X):
  return v[1]if X.sida==r else v[0]
 def uppdatera_värde(X):
  X.senast=max(X.pin.read_analog(),1)
  X.mest=max(X.mest,X.senast)
  X.minst=min(X.minst,X.senast)
  X.boost=X.senast-X.minst
  X.dold_multi=X.senast/X.minst
 def uppdatera(X):
  D=X.senast
  X.uppdatera_värde()
  X.förändring=X.senast-D
  if X.förändring>0:
   X.dold_ökning=X.förändring/D
  else:
   X.dold_ökning=0
o=Öga(mb.pin1,r)
x=Öga(mb.pin2,U)
v=[o,x]
d=0.05
k=3 
S=1.2 
W=1000
def hitta_mest_dolda():
 N=max(o.dold_multi,x.dold_multi)
 t=max(o.senast,x.senast)
 j=min(o.senast,x.senast)
 if max(t,1)/max(j,1)<S and N<k:
  return None
 return o if o.senast>x.senast else x
class Inställningar:
 def __init__(X):
  X.riktning=p
  X.sväng=p
 def sätt(X,i,m):
  X.riktning=i
  X.sväng=m
 def sätt_från_annan(X,b):
  X.sätt(b.riktning,b.sväng)
 def är_samma(X,b):
  return X.riktning==b.riktning and X.sväng==b.sväng
 def bild(X):
  if X.sväng==r:
   return mb.Image.ARROW_W
  if X.sväng==U:
   return mb.Image.ARROW_E
  return mb.Image.HEART
class KraschHanterare:
 def __init__(X):
  X.arr=[]
  X.in_slot=0;
 def uppdatera(X,tid):
  e=mb.accelerometer.get_y()
  if len(X.arr)!=0 and X.arr[-1][1]//100==tid//100:
   X.arr[-1]=((X.arr[-1][0]*X.in_slot+e)/(X.in_slot+1),tid)
   return
  X.arr.append((e,tid))
  while tid-X.arr[0][1]>W:
   X.arr.pop(0)
 def genomsnitt(X):
  q=0
  for _,G in enumerate(X.arr):
   q+=G[0]
  return q/len(X.arr)
 def krashar(X):
  return False
def sätt_pixlar(hur_många):
 for n in range(25):
  mb.display.set_pixel(n%5,n//5,9 if n<hur_många else 0)
def hummux():
 w=False
 mb.pin12.write_digital(1)
 u=0
 Q=Inställningar()
 f=Inställningar()
 H=False
 V=KraschHanterare()
 while True:
  if mb.button_a.was_pressed():
   w=not w
   H=False
  if mb.button_b.was_pressed():
   w=not w
   H=True
  if not w:
   mb.display.show(mb.Image.SAD)
   flytta(p,p)
   u=0
   continue
  C=mb.running_time()
  o.uppdatera()
  x.uppdatera()
  m=p
  i=g
  n=hitta_mest_dolda()
  V.uppdatera(C)
  if n is not None:
   m=n.andra_sidan
  f.sätt(i,m)
  if f.är_samma(Q):
   if C-u>300:
    if not H:
     flytta(f.riktning,f.sväng)
  else:
   u=C
   Q.sätt_från_annan(f)
hummux()
# Created by pyminifier (https://github.com/liftoff/pyminifier)

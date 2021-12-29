import microbit as mb
T=0
r=mb.pin13
y=mb.pin14
l=mb.pin16
V=mb.pin15
IM=mb.Image
class Inst:
 def __init__(K):
  K.sätt(T,T)
 def sätt(K,C,S):
  K.rik=C
  K.sväng=S
 def sätt_från_annan(K,N):
  K.sätt(N.rik,N.sväng)
 def är_samma(K,N):
  return K.rik==N.rik and K.sväng==N.sväng
 def bild(K):
  if K.rik==y:
   return IM.NO
  if K.sväng==l:
   return IM.ARROW_W
  if K.sväng==V:
   return IM.ARROW_E
  return IM.HEART
def sp(B,A):
 A.write_digital(1 if B==A else 0)
def motsatt_sida(S):
 return V if S==l else l
a=Inst()
def flytta(ins):
 a.sätt_från_annan(ins)
 sp(ins.rik,r)
 sp(ins.rik,y)
 sp(ins.sväng,l)
 sp(ins.sväng,V)
class Öga:
 def __init__(K,A,h):
  K.pin=A
  K.sida=h
  K.minst=1023
  K.up()
 def up(K):
  K.senast=max(K.pin.read_analog(),1)
  K.minst=min(K.minst,K.senast)
  K.dold_multi=K.senast/K.minst
s=Öga(mb.pin1,l)
u=Öga(mb.pin2,V)
q=0.05
m=3 
w=1.2 
i=2000
f=1.8
O=300
P=500
def hitta_mest_dolda():
 D=max(s.dold_multi,u.dold_multi)
 M=max(s.senast,u.senast)
 I=min(s.senast,u.senast)
 if max(M,1)/max(I,1)<w and D<m:
  return None
 return s if s.senast>u.senast else u
class KraschHanterare:
 def __init__(K):
  K.arr=[]
  K.reset()
 def reset(K):
  K.arr.clear()
  K.in_slot=0
  K.minimum=-1
  K.faktor=0
 def up(K,tid):
  if a.rik!=r or a.sväng!=T: 
   K.reset()
   return
  B=abs(mb.accelerometer.get_z())
  if len(K.arr)!=0 and K.arr[-1][1]//200==tid//200:
   K.arr[-1]=((K.arr[-1][0]*K.in_slot+B)/(K.in_slot+1),tid)
   return
  K.arr.append((B,tid))
  K.in_slot=1
  X=False
  while tid-K.arr[0][1]>i:
   K.arr.pop(0)
   X=True
  if not X:
   return
  nu=K.genomsnitt()
  K.minimum=nu if K.minimum==-1 else min(nu,K.minimum)
  K.faktor=nu/max(K.minimum,1)
  return K.faktor>f
 def genomsnitt(K):
  o=0
  for _,n in enumerate(K.arr):
   o+=n[0]
  return o/len(K.arr)
def sätt_pixlar(hur_många):
 for n in range(25):
  mb.display.set_pixel(n%5,n//5,9 if n<hur_många else 0)
def hummux():
 v=False
 mb.pin12.write_digital(1)
 k=0
 b=Inst()
 p=Inst()
 t=False
 e=O
 d=V
 j=KraschHanterare()
 while True:
  if mb.button_a.was_pressed():
   v=not v
   t=False
  if mb.button_b.was_pressed():
   v=not v
   t=True
  if not v:
   mb.display.show(IM.SAD)
   b.sätt(T,T)
   flytta(b)
   k=0
   e=O
   j.reset()
   continue
  W=mb.running_time()
  s.up()
  u.up()
  p.sätt(r,T)
  Y=hitta_mest_dolda()
  J=j.up(W)
  if J:
   p.sätt(y,d)
   b.sätt_från_annan(p)
   k=0
   e=P
   d=motsatt_sida(d) 
  if p.är_samma(b):
   if W-k>e:
    if not t:
     flytta(p)
    if not J:
     e=O
  else:
   k=W
   b.sätt_från_annan(p)
  sätt_pixlar(j.faktor*10)
hummux()

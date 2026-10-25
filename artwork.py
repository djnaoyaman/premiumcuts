"""Original, geometric record-shelf illustrations in the site's blue/cream palette."""
def record_art(index):
 b='currentColor';p='var(--paper)'
 def rect(x,y,w,h,fill=b):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'
 def circle(x,y,r,fill=b):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>'
 def path(d,fill=b):return f'<path d="{d}" fill="{fill}"/>'
 def line(x1,y1,x2,y2,width=3):return f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{b}" stroke-width="{width}"/>'
 def ring(x,y,r,w=16):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{b}" stroke-width="{w}"/>'
 designs=[
  circle(240,150,105)+circle(240,150,65,p)+rect(30,45,40,210)+rect(85,45,15,210)+line(120,45,120,255)+circle(240,150,10),
  path('M45 180a135 135 0 0 1 270 0Z')+path('M75 180a105 105 0 0 1 210 0Z',p)+path('M105 180a75 75 0 0 1 150 0Z')+rect(45,205,270,12)+rect(45,240,180,12)+circle(300,246,12),
  rect(30,30,150,120)+path('M180 30a120 120 0 0 1 120 120H180Z')+path('M30 150h150v120A150 120 0 0 1 30 150Z')+circle(255,225,45),
  path('M30 270V210H90V150H150V90H210V30H270V270Z')+circle(290,65,28)+line(30,285,330,285),
  ''.join(rect(30+x*60,30+y*60,60,60) for x in range(5) for y in range(4) if (x+y)%2==0)+circle(180,150,68,p)+ring(180,150,43,18),
  rect(30,105,300,35)+rect(30,160,300,12)+rect(30,190,300,6)+circle(180,150,98,p)+rect(160,30,40,240)+ring(180,150,88,9),
  path('M30 270L180 30L330 270Z')+path('M30 270H330L180 180Z',p)+circle(180,150,35,p)+line(30,285,330,285),
  ''.join(path(f'M{x} 40V{260-i*35}H{320-i*35}V40',fill='none').replace('fill="none"',f'fill="none" stroke="{b}" stroke-width="14"') for i,x in enumerate([40,75,110,145])),
  path('M30 30H330L30 270Z')+path('M150 270L330 90V270Z')+circle(90,90,30,p)+line(210,30,330,150,12),
  ring(180,150,110,28)+rect(160,20,40,260)+rect(50,130,260,40)+circle(180,150,45,p)+circle(180,150,12),
  rect(30,30,300,240)+circle(245,150,115,p)+circle(245,150,70)+rect(30,60,100,12,p)+rect(30,85,100,12,p)+rect(30,110,100,12,p),
  ''.join(path(f'M{40+i*40} 265V145a{120-i*20} {120-i*20} 0 0 1 {240-i*40} 0v120h-18V145a{102-i*20} {102-i*20} 0 0 0 -{204-i*40} 0v120Z') for i in range(4)),
  path('M45 270V150a135 135 0 0 1 270 0v120H265V150a85 85 0 0 0 -170 0v120Z')+rect(135,150,90,120)+circle(180,150,45),
  circle(115,145,75)+ring(240,145,75,10)+line(35,245,325,245,6)+''.join(circle(45+i*30,275,5) for i in range(10)),
  ''.join(path(f'M{x} {y}a60 60 0 0 1 120 0v40a60 60 0 0 0 -120 0Z') for x,y in [(30,90),(150,90),(90,210),(210,210)]),
  ''.join(rect(30+x*75,30+y*80,75,80) if (x+y)%2==0 else circle(67.5+x*75,70+y*80,24) for y in range(3) for x in range(4)),
  rect(30,30,300,240)+rect(55,55,250,190,p)+rect(80,80,200,140)+rect(105,105,150,90,p)+rect(130,130,100,40),
  circle(90,100,65)+circle(180,150,65)+circle(270,200,65)+circle(90,100,30,p)+circle(180,150,30,p)+circle(270,200,30,p)+line(30,270,330,30,2),
  rect(30,30,120,240)+path('M180 30h30a120 120 0 0 1 0 240h-30Z')+rect(60,60,60,180,p)+circle(210,150,55,p),
  circle(105,105,75)+path('M210 30L330 180H210Z')+rect(30,210,300,60)+line(180,30,180,180,6),
  path('M30 150a75 75 0 0 1 150 0Z')+path('M180 150a75 75 0 0 0 150 0Z')+''.join(circle(45+i*30,245,8) for i in range(10))+line(30,55,330,55,8),
  path('M180 20L310 150L180 280L50 150Z')+path('M180 70L260 150L180 230L100 150Z',p)+circle(180,150,28)+rect(25,30,20,240)+rect(315,30,20,240),
 ]
 n=(int(index)-1)%len(designs)
 return '<svg viewBox="0 0 360 300" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">'+designs[n]+'</svg>'

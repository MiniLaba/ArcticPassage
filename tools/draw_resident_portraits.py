"""Three original vector portraits, authored in code from existing character palettes.
Keeps the retained Ada/Mira/Roan masters; no generated imagery or enlarged sprites.
"""
from pathlib import Path
from random import Random
import argparse
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=(R/'art/source/code-portraits' if R.name=='ArcticPassage' else R/'public/assets/experience'));A=parser.parse_args().output
A.mkdir(exist_ok=True)

def portrait(name,skin,light,shadow,coat,dark,hat,expression=0):
 p=[]
 def path(d,fill,stroke=None,w=1):p.append(f'<path d="{d}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"' if stroke else '')+'/>')
 def ellipse(x,y,rx,ry,fill):p.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}"/>')
 def line(d,col,w=1):path(d,'none',col,w)
 p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="768" height="768" viewBox="0 0 512 512"><title>{name.title()} · Frosthavn</title><defs><linearGradient id="paper" x2="0.8" y2="1"><stop stop-color="#f5e8cc"/><stop offset="1" stop-color="#e1d1ad"/></linearGradient><linearGradient id="skin" x2=".8" y2=".6"><stop stop-color="{light}"/><stop offset=".5" stop-color="{skin}"/><stop offset="1" stop-color="{shadow}"/></linearGradient><linearGradient id="coat" x2="1" y2=".5"><stop stop-color="{coat}"/><stop offset="1" stop-color="{dark}"/></linearGradient><pattern id="weave" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M0 1h8M1 0v8" stroke="#fff2cf" stroke-width=".4" opacity=".13"/></pattern></defs>')
 path('M0 0H512V512H0z','url(#paper)')
 # Quiet landscape / chart details behind the bust.
 for off in [0,22,47]:line(f'M-40 {385+off}Q90 {290+off} 170 {340+off}T350 {325+off}T550 {360+off}','#a7b0a1',.7)
 p.append('<circle cx="393" cy="111" r="60" fill="none" stroke="#9da99b" stroke-width=".7" opacity=".5"/><path d="M393 34v154m-77-77h154" stroke="#9da99b" stroke-width=".6" opacity=".4"/>')
 path('M17 512q10-93 79-120l90-34 135 2 103 38q57 24 73 114Z',dark,'#3c3b32',3)
 path('M25 512q12-90 82-114l87-35 128 4 94 36q59 20 74 109Z','url(#coat)')
 path('M90 410q-13 46-7 102H39q5-67 51-102m334-2q34 34 46 104h-48q9-55 2-104',dark)
 path('M195 321l-3 55 66 47 67-49-15-65Z',shadow,'#694d3a',2)
 path('M204 322l3 40 52 39 45-38-3-47Z',skin)
 # Ears and side hair.
 ellipse(172,237,19,33,shadow);ellipse(346,231,19,31,shadow)
 path('M180 143q8-59 83-64 94 0 95 92l-10 98-176 5Z','#3f3027')
 if name=='amma':
  # A roomy cream hood and soft fleece edge.
  path('M124 329q-43-101-18-173Q136 54 247 49q117-1 157 106 22 63-9 174l-53 40-177-8Z','#d1c4a2','#9e8c68',3)
  path('M145 318q-25-87-12-143 24-91 118-95 91-3 119 84 18 54-8 149l-37 37-148 3Z','#eee3c6')
  for i in range(31):
   import math
   a=math.pi*.1+i/30*math.pi*.8
   x=256+132*math.cos(a);y=191-119*math.sin(a)
   line(f'M{x-5:.1f} {y+8:.1f}l-2-12 7 7','#bfaf8d',1.2)
 # Face, planes of light, neck and forehead.
 face={'nora':'M178 179q6-66 79-67 75-1 85 67l-1 73q-4 62-36 88-24 19-49 18-28 0-52-25-26-25-28-76Z','levin':'M178 179q9-62 79-67 77-1 85 67l-7 90-28 61-46 28-48-22-30-69Z','amma':'M173 183q8-66 84-71 78 0 90 69l-4 76q-1 56-37 85-23 17-50 16-32-1-57-26-28-29-29-78Z'}[name]
 path(face,'url(#skin)','#694b38',2)
 path('M184 208q0-58 48-75-29 32-27 91l8 50-19 7q-17-24-10-73',light)
 path('M323 177q19 37 10 90-6 31-23 57l-28 23q42-8 56-60 12-40-1-87Z',shadow)
 path('M208 309q33 32 73 14l20-12q-4 28-43 34-30 1-50-36',skin)
 # Hairline variations.
 if name=='nora':
  path('M170 230q-21-72 8-113 29-44 93-40 70 2 86 55 14 47-9 99l-13-62q-29-8-51-43-14 31-91 43l-10 64Z','#47342d','#322a26',3)
  for d in ['M188 166q40-37 78-53','M195 151q28-38 64-47','M280 108q20 38 54 53','M286 97q39 25 51 58']:line(d,'#78523b',3)
 elif name=='levin':
  path('M170 238q-10-62 13-94l20-2-13 75-7 41Z','#574135')
  path('M326 147l20 15 3 93-16 5Z','#574135')
 else:
  path('M177 220q-12-64 29-87 31-23 56-22 57-2 79 47l-4 76-15-45q-33-26-59-48-24 36-70 41l-5 45Z','#55463b','#3f352e',2)
  for d in ['M193 173q34-21 58-47','M202 179q32-22 54-48','M268 125q23 35 57 48']:line(d,'#c0b99f',2.2)
 # Eyebrows / eyes. Slight asymmetry keeps a quiet, human expression.
 for x,y in ([(211,222),(288,219)] if name=='nora' else [(211,224),(290,222)] if name=='levin' else [(209,228),(289,226)]):
  brow=-6 if expression==2 else -22 if expression==3 else -16
  path(f'M{x-17} {y+brow}q17-9 33-1l-1 6q-16-6-31 0Z','#594033')
  path(f'M{x-16} {y}q15-13 31-1-15 13-31 1Z','#eee1c8','#79503a',1)
  ellipse(x+2,y,6.5,7,'#534234');ellipse(x+3,y,3.5,5.5,'#272e2b');ellipse(x+1,y-3,1.6,1.7,'#fff8dc')
  line(f'M{x-16} {y}q15-12 31-1','#503a2e',2)
  line(f'M{x-13} {y+14}q13 5 26 0',shadow,1.5)
  if expression==1:
   path(f'M{x-17} {y-7}h34v16h-34Z',skin);line(f'M{x-16} {y+2}q16-13 32-1','#593e31',2.2)
  if expression==5:line(f'M{x-17} {y-4}l31 2','#5b3e2e',2)
 # Nose, cheek planes and a restrained smile.
 path('M256 223l-8 48q8 7 18 3l8-5-12-6Z',shadow)
 line('M249 269q10 7 21-1','#875237',1.4)
 path('M218 267q5-7 15-4l-4 8Z','#c58361')
 path('M286 264l18-6-3 11Z','#a8674a')
 path('M231 302q25-11 49-3-24 16-49 3Z','#965c44')
 line('M230 301q24 6 50-2','#734934',1.8)
 line('M243 312q13 4 24-1',light,1.6)
 if expression==1:
  path('M229 299q25 5 52-3-13 33-31 22Z','#7b4b39');path('M233 300q24 4 43-2l-5 8-32 2Z','#f1dfbf')
 elif expression==2:
  path('M224 294h62v23h-62Z',skin);line('M232 309q23-13 44-2','#80523f',2)
 elif expression==3:
  path('M224 293h62v27h-62Z',skin);ellipse(257,308,9,13,'#80523f')
 elif expression==4:
  ellipse(210,269,15,6,'#cc866e');ellipse(301,267,14,6,'#bc775f');line('M235 303q21 8 41-2','#80523f',2)
 if name=='amma':
  for d in ['M196 210l-10 5','M316 207l14 3','M194 241l-8 5','M310 237l15 4','M224 284l-7 10','M291 280l9 9','M246 320q13 5 26-1']:line(d,'#97694e',1)
  # A long braid tucked over one shoulder.
  path('M336 239q35 31 12 67 32 24 7 51 29 24 2 49 17 29-7 51l-32 6q-12-30 4-50-19-27-3-49-23-24-1-50-23-27 4-57Z','#4a3d33','#352f29',2)
  for y in [281,321,359,396,431]:line(f'M325 {y}q28 9 21 24m-14-17 20 10','#aa9b7d',3)
  path('M323 445l32-4 3 10-34 6Z','#bd9b54');line('M332 455l-5 22m18-23 6 22','#534333',4)
 if name=='levin':
  path('M182 263l20 13 14 14q19 0 31-8l20 1 16 6 24-9 27-18-1 43q-13 58-72 65-56-13-71-59Z','#584033','#46372d',2)
  path('M201 291q19 8 40-2 26-7 43 4l24-4-13 24q-37 31-80-1Z','#805c40')
  path('M230 301q25 8 50-2l-9 9-30 2Z','#ad7c58')
  if expression==1:path('M235 302q20 4 41-1-6 17-23 15Z','#e5d3b3')
  elif expression==2:line('M234 309q21-14 42-3','#3a3029',3)
  elif expression==3:ellipse(256,310,8,12,'#382d28')
  for x in range(198,326,10):
   y=312+abs(x-260)//5;line(f'M{x} {y}l3 18','#ab825a',1.4)
  for x in [212,228,295,311]:line(f'M{x} 284l2 9','#c2a17b',1)
  # Real glass, a thin brass bridge and metal temples.
  for x in [187,272]:p.append(f'<rect x="{x}" y="204" width="65" height="40" rx="9" fill="#dce2ca" fill-opacity=".1" stroke="#c7ab65" stroke-width="5"/><path d="M{x+9} 211h18l-18 22z" fill="#fff5dc" opacity=".2"/>')
  line('M252 217q10-7 20 0m-87-1-14-4m165 2 11-4','#b59653',4)
 # Collars, winter layers and textile details.
 if name=='nora':
  path('M188 341l67 45 62-48 25 33-71 75-86-47Z','#ede5d0','#c6b994',2)
  path('M178 347l-57 42 53 123h53l-26-113-24-17 27-11Z','#497185','#294b5c',3)
  path('M320 341l62 47-55 124h-54l38-115 30-17-37-10Z','#41667a','#294b5c',3)
  path('M230 409h51v103h-51z','#c6d0bf');line('M255 418v94','#7c8b81',2)
  path('M181 77q63-50 133-2l29 49-10 58q-72-24-150 3l-13-51Z',hat,'#263f4d',3)
  path('M180 113q69-34 153-3l10 24q-72-27-170 10Z','#55788a')
  path('M171 141l-23 34 1 99 28 5 9-80Z','#2d4d60','#243d49',3)
  path('M341 139l18 30 2 98-23 4-8-72Z','#29495a','#243d49',3)
  path('M155 183l10-4 6 80-15-3Z','#bfd0cd');path('M345 179l8 3 1 73-9 2Z','#b6c8c7')
  for x in [192,276]:
   p.append(f'<rect x="{x}" y="116" width="56" height="33" rx="9" fill="#d5ceb0" stroke="#253f4c" stroke-width="7"/><rect x="{x+6}" y="122" width="44" height="21" rx="5" fill="#a1bbbf"/>')
   path(f'M{x+10} 124h14l-12 17h-5Z','#e1e5d0')
  line('M248 132q13-9 28 0','#b1baa5',6)
  path('M351 417h49v38h-49Z','#1c394c','#8ba1a1',1);line('M362 427h25m-25 8h16','#a6b6a8',2)
  path('M115 432l41-13 5 13-42 12Z','#d8bd78');path('m117 449 40-12 4 12-40 12Z','#bd9765')
 elif name=='levin':
  path('M190 348q54 34 128-3l22 43-38 46-107-20-22-34Z','#c5af72','#9b8858',2)
  path('M197 369q57 38 124-2l-8 31q-48 32-110-5Z','#dac48b')
  path('M210 396l40 21-10 95h-45Z','#b8a269');line('M214 410l21 10m-22 4 20 9m-22 4 20 9m-21 4 18 10','#d9c58d',2)
  path('M179 100q72-40 145-2l17 65-9 19-162-2-8-22Z',hat,'#3d4b38',3)
  path('M165 151q91-18 175 2l-2 33q-89-19-173 0Z','#66745a','#4a5c45',2)
  for x in range(174,336,9):line(f'M{x} 156v21','#8a9573',1.2)
  path('M220 112h70v26h-70Z','#bea86e','#9f8d5e',1);line('M233 123h44','#e2d1a0',2)
  path('M321 429l73-5 10 88h-86Z','#b59b66','#5d644d',4);line('M333 444l48-3m-46 13 39-3m-37 13 42-3','#736d4c',2)
  path('M398 411l7-1 13 84-7 2Z','#e3bc7e');path('M398 411l2-12 5 11Z','#3d4f42')
 else:
  path('M180 346q25 38 70 44 47-2 77-41l11 32q-26 62-82 73-59-11-92-68Z','#dfd3af','#baaa84',2)
  path('M209 382l43 29 47-32-14 65-58-2Z','#b49a63')
  for y in range(397,440,10):line(f'M232 {y}h42','#d7c38d',2)
  path('M167 384l-36 12 30 116h66l-29-87Z','#ad6750','#7f4939',2)
  path('M334 382l35 16-37 114h-58l27-81Z','#a25e49','#7f4939',2)
  for y in [425,444,463,482]:
   ellipse(266,y,3.5,3.5,'#d4bd80');line(f'M274 {y}h6','#85533f',1)
  path('M99 443l51-14 3 9-51 14Z','#c5a473');line('M111 459l30-7m-27 15 30-7','#7b4c3f',2)
 # Coat seams and understated embroidered / woven edges.
 line('M92 430q-8 40-1 82m322-82q10 46 4 82',light,1)
 for x in [103,403]:
  for y in range(436,507,8):line(f'M{x} {y}l2 3', '#dbc49a',.9)
 # Screen-print texture: deterministic tiny strokes, low opacity.
 rng=Random(name)
 p.append('<g opacity=".13" stroke="#7d6548" stroke-width=".55">')
 for _ in range(480):
  x=rng.randrange(512);y=rng.randrange(512)
  p.append(f'<path d="M{x} {y}h{rng.randrange(1,3)}"/>')
 p.append('</g></svg>')
 (A/(f'portrait-{name}.svg' if expression==0 else f'portrait-{name}-{expression}.svg')).write_text(''.join(p))

for expression in range(6):
 portrait('nora','#ca936e','#e0b18a','#ac7354','#456e80','#294d61','#325266',expression)
 portrait('levin','#bb8864','#d9ab82','#96694c','#687c57','#435b42','#52684a',expression)
 portrait('amma','#b78160','#d5a77e','#946349','#ac6850','#7c493d','#d9ccaa',expression)
print('Drew Nora, Levin and Amma, with six expressions each; character clothing and colours retained.')

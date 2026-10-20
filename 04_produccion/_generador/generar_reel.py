# -*- coding: utf-8 -*-
import os, subprocess, shutil, sys
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
OUT=os.path.join(ROOT,"04_produccion","_reels")
W,H=1080,1920
MAUVE=(154,125,145); PLUM=(74,52,86); PEACH=(244,190,150); TEAL=(205,233,232); LIGHT=(243,248,247); WHITE=(255,255,255); CREAM=(255,244,236); CHAR=(51,51,51)
F="/usr/share/fonts/truetype/"
def sans(s): return ImageFont.truetype(F+"dejavu/DejaVuSans-Bold.ttf",s)
def serb(s): return ImageFont.truetype(F+"liberation/LiberationSerif-Bold.ttf",s)
def ser(s): return ImageFont.truetype(F+"liberation/LiberationSerif-Regular.ttf",s)
M=110; MW=W-2*M
def wrap(d,t,f,mw):
    L=[];c=""
    for w in t.split():
        x=(c+" "+w).strip()
        if d.textlength(x,font=f)<=mw: c=x
        else:
            if c: L.append(c)
            c=w
    L.append(c); return L
def fit(d,t,mk,start,mn,maxh,lh=1.25):
    s=start
    while s>=mn:
        f=mk(s); L=wrap(d,t,f,MW)
        if len(L)*s*lh<=maxh: return f,L,s
        s-=2
    f=mk(mn); return f,wrap(d,t,f,MW),mn
STYLE={"hook":(MAUVE,WHITE,sans,86),"body":(TEAL,PLUM,serb,76),"q":(LIGHT,PLUM,serb,78),"quote":(MAUVE,WHITE,serb,72),"close":(PLUM,WHITE,serb,66)}
def card(kind,text,sub,path):
    bg,fg,mk,st=STYLE[kind]
    im=Image.new("RGB",(W,H),bg); d=ImageDraw.Draw(im)
    f,L,s=fit(d,text,mk,st,40,760,1.28)
    h=int(len(L)*s*1.28); y=(H-h)//2-60
    for l in L:
        d.text((M,y),l,font=f,fill=fg); y+=int(s*1.28)
    d.rectangle([M,y+24,M+180,y+36],fill=PEACH)
    if sub:
        f2,L2,s2=fit(d,sub,ser,40,26,300,1.35); y2=y+80
        for l in L2:
            d.text((M,y2),l,font=f2,fill=(CREAM if kind in("hook","quote","close") else CHAR)); y2+=int(s2*1.35)
    d.text((M,H-420),"Karina Alvarado",font=sans(34),fill=(CREAM if kind in("hook","quote","close") else PLUM))
    im.save(path)
def build(name,cards,dur=3.5):
    d=os.path.join(OUT,name); shutil.rmtree(d,ignore_errors=True); os.makedirs(d+"/_tmp")
    clips=[]
    for i,(k,t,sub) in enumerate(cards,1):
        p=f"{d}/_tmp/c{i}.png"; card(k,t,sub,p)
        if i==1: shutil.copy(p,f"{d}/portada.png")
        c=f"{d}/_tmp/c{i}.mp4"
        subprocess.run(["ffmpeg","-y","-loglevel","error","-loop","1","-t",str(dur),"-i",p,"-vf",f"fade=t=in:st=0:d=0.35,fade=t=out:st={dur-0.35}:d=0.35,format=yuv420p","-r","30","-c:v","libx264","-pix_fmt","yuv420p",c],check=True)
        clips.append(c)
    open(f"{d}/_tmp/list.txt","w").write("".join(f"file '{c}'\n" for c in clips))
    total=dur*len(cards)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",f"{d}/_tmp/list.txt","-f","lavfi","-t",str(total),"-i","anullsrc=r=44100:cl=stereo","-c:v","copy","-c:a","aac","-shortest",f"{d}/reel.mp4"],check=True)
    shutil.rmtree(d+"/_tmp"); return d,total
REELS={
"2026-10-24_Reel_ingresos-vs-patrimonio":[("hook","¿Lo que ganás se queda a tu nombre?",""),("body","Generar ingresos es lo que entra cada mes.",""),("body","Consolidar un patrimonio es lo que queda: a tu nombre y protegido.",""),("quote","Se puede trabajar toda una vida y aun así no lograr un patrimonio propio, si nadie nos explicó cómo hacerlo.",""),("q","Esa explicación es lo que faltaba. Empecemos por ahí.",""),("close","Más en mi newsletter: enlace en el perfil.","Karina Alvarado, asesora")],
"2026-10-31_Reel_revisa-lo-que-figura-a-tu-nombre":[("hook","Un secreto, amigas.",""),("body","En mi experiencia, quienes ya consolidaron su patrimonio revisan periódicamente sus bienes en los registros públicos.",""),("q","¿A nombre de quién figura cada bien?",""),("q","¿Hay anotaciones o gravámenes?",""),("q","¿Tus estructuras legales están al día?",""),("quote","No es desconfianza. Es mantenimiento.",""),("close","Información general sobre Costa Rica. No sustituye asesoría jurídica.","Más en mi newsletter: enlace en el perfil.")],
"2026-11-07_Reel_antes-de-aceptar-un-cargo":[("hook","Antes de aceptar ser presidenta de una sociedad:",""),("q","¿Para qué existe y qué papel tendría yo?",""),("q","¿Quién gestiona el negocio y quién maneja el dinero?",""),("q","¿Están los libros y las actas al día?",""),("q","¿Por qué me lo piden a mí y no a otra persona?",""),("close","Información general sobre Costa Rica. No sustituye asesoría jurídica.","Más en mi newsletter: enlace en el perfil.")],
}
if __name__=="__main__":
    os.makedirs(OUT,exist_ok=True)
    for n,c in REELS.items():
        d,t=build(n,c); print(n,t,"s")

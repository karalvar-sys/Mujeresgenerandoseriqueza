# -*- coding: utf-8 -*-
import os, sys, shutil, csv
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from contenido import PIECES
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROD = os.path.join(ROOT, "04_produccion")
COVER = os.path.join(ROOT, "05_activos_marca", "portada_ebook-01.png")
W, H = 1080, 1350
MAUVE=(154,125,145); PLUM=(74,52,86); PEACH=(244,190,150); TEAL=(205,233,232); LIGHT=(243,248,247); CHAR=(51,51,51); WHITE=(255,255,255); CREAM=(255,244,236)
F="/usr/share/fonts/truetype/"
def sans(s): return ImageFont.truetype(F+"dejavu/DejaVuSans-Bold.ttf",s)
def serb(s): return ImageFont.truetype(F+"liberation/LiberationSerif-Bold.ttf",s)
def ser(s): return ImageFont.truetype(F+"liberation/LiberationSerif-Regular.ttf",s)
def seri(s): return ImageFont.truetype(F+"liberation/LiberationSerif-Italic.ttf",s)
M=90; MW=W-2*M
def wrap(d,t,f,mw):
    lines=[];cur=""
    for w in t.split():
        x=(cur+" "+w).strip()
        if d.textlength(x,font=f)<=mw: cur=x
        else:
            if cur: lines.append(cur)
            cur=w
    lines.append(cur); return lines
def fit(d,t,mk,start,minimum,mw,maxh,lh=1.28):
    s=start
    while s>=minimum:
        f=mk(s); ls=wrap(d,t,f,mw)
        if len(ls)*s*lh<=maxh: return f,ls,s
        s-=2
    f=mk(minimum); return f,wrap(d,t,f,mw),minimum
def para(d,x,y,t,mk,start,minimum,fill,maxh,lh=1.28,mw=MW):
    if not t: return y
    f,ls,s=fit(d,t,mk,start,minimum,mw,maxh,lh)
    for l in ls:
        d.text((x,y),l,font=f,fill=fill); y+=int(s*lh)
    return y

def meas(d,t,mk,start,minimum,maxh,lh,mw=MW):
    if not t: return None,[],0,0
    f,ls,s=fit(d,t,mk,start,minimum,mw,maxh,lh)
    return f,ls,s,int(len(ls)*s*lh)
def put(d,x,y,m,fill,lh):
    f,ls,s,h=m
    for l in ls:
        d.text((x,y),l,font=f,fill=fill); y+=int(s*lh)
    return y
AREA_T=120; AREA_B=H-170
def foot(d,i,n,col,brand=True):
    if brand: d.text((M,H-95),"Karina Alvarado",font=sans(28),fill=col)
    if n>1: d.text((W-M-70,H-95),f"{i}/{n}",font=sans(28),fill=col)
def render(slide,i,n):
    kind=slide[0]
    if kind=="cover":
        im=Image.new("RGB",(W,H),MAUVE);d=ImageDraw.Draw(im)
        y=para(d,M,240,slide[1],sans,84,52,WHITE,560,1.22)
        d.rectangle([M,y+30,M+180,y+42],fill=PEACH)
        para(d,M,y+90,slide[2],seri,48,32,CREAM,300,1.3)
        if n>1: d.text((M,H-170),"Deslizá  →",font=sans(36),fill=PEACH)
        foot(d,i,n,CREAM)
    elif kind=="statement":
        im=Image.new("RGB",(W,H),TEAL);d=ImageDraw.Draw(im)
        m1=meas(d,slide[1],serb,76,44,760,1.25); m2=meas(d,slide[2],ser,40,28,260,1.35)
        tot=m1[3]+60+(m2[3]+40 if m2[3] else 0)
        y=AREA_T+max(0,(AREA_B-AREA_T-tot)//2)
        y=put(d,M,y,m1,PLUM,1.25)
        d.rectangle([M,y+24,M+180,y+36],fill=PEACH)
        if m2[3]: put(d,M,y+76,m2,CHAR,1.35)
        foot(d,i,n,PLUM)
    elif kind=="question":
        im=Image.new("RGB",(W,H),LIGHT);d=ImageDraw.Draw(im)
        d.rectangle([0,0,W,22],fill=MAUVE)
        n_b=slide[3] if len(slide)>3 else None
        m1=meas(d,slide[1],serb,66,40,520,1.3); m2=meas(d,slide[2],ser,40,28,330,1.35)
        badge=230 if n_b else 0
        tot=badge+m1[3]+(30+m2[3] if m2[3] else 0)
        y=AREA_T+max(0,(AREA_B-AREA_T-tot)//2)
        if n_b:
            d.ellipse([M,y,M+190,y+190],fill=PEACH)
            nf=sans(120); tw=d.textlength(n_b,font=nf); d.text((M+95-tw/2,y+22),n_b,font=nf,fill=PLUM)
            y+=230
        y=put(d,M,y,m1,PLUM,1.3)
        if m2[3]: put(d,M,y+30,m2,CHAR,1.35)
        foot(d,i,n,MAUVE)
    elif kind=="list":
        im=Image.new("RGB",(W,H),LIGHT);d=ImageDraw.Draw(im)
        d.rectangle([0,0,W,22],fill=MAUVE)
        mt=meas(d,slide[1],sans,54,36,200,1.25)
        its=[meas(d,it,serb,46,32,200,1.25,MW-60) for it in slide[2]]
        tot=mt[3]+66+sum(m[3]+34 for m in its)
        y=AREA_T+max(0,(AREA_B-AREA_T-tot)//2)
        y=put(d,M,y,mt,PLUM,1.25)
        d.rectangle([M,y+14,M+180,y+26],fill=PEACH); y+=80
        for m in its:
            d.ellipse([M,y+14,M+22,y+36],fill=PEACH)
            y=put(d,M+50,y,m,PLUM,1.25)+34
        foot(d,i,n,MAUVE)
    elif kind in("quote","close","book"):
        im=Image.new("RGB",(W,H),MAUVE);d=ImageDraw.Draw(im)
        mk=seri if kind=="quote" else serb
        sub=slide[2] if len(slide)>2 else ""
        m1=meas(d,slide[1],mk,72 if kind!="close" else 64,40,620,1.28)
        if kind=="book":
            y=200
            y=put(d,M,y,m1,WHITE,1.28)
            d.rectangle([M,y+26,M+180,y+38],fill=PEACH)
            cov=Image.open(COVER).convert("RGB"); ch=520; cw=int(cov.width*ch/cov.height); cov=cov.resize((cw,ch))
            cy=y+80
            d.rectangle([M-6,cy-6,M+cw+5,cy+ch+5],fill=PEACH); im.paste(cov,(M,cy))
            d.text((M+cw+34,cy+110),"Mujeres generándose",font=sans(34),fill=WHITE)
            d.text((M+cw+34,cy+155),"riqueza: Manual para",font=sans(34),fill=WHITE)
            d.text((M+cw+34,cy+200),"emprendedoras",font=sans(34),fill=WHITE)
            d.text((M+cw+34,cy+265),"eBook en Amazon",font=sans(30),fill=PEACH)
            d.text((M+cw+34,cy+310),"Enlace en el perfil",font=sans(26),fill=CREAM)
        else:
            m2=meas(d,sub,ser,38,26,330,1.35)
            tot=m1[3]+64+(m2[3] if m2[3] else 0)
            y=AREA_T+max(0,(AREA_B-AREA_T-tot)//2)
            y=put(d,M,y,m1,WHITE,1.28)
            d.rectangle([M,y+26,M+180,y+38],fill=PEACH)
            if m2[3]: put(d,M,y+80,m2,CREAM,1.35)
        foot(d,i,n,CREAM)
    return im
def save_set(slides,folder,pdf=None):
    os.makedirs(folder,exist_ok=True)
    n=len(slides); ims=[]
    for i,s in enumerate(slides,1):
        im=render(s,i,n); im.save(os.path.join(folder,f"slide_{i:02d}.png")); ims.append(im)
    if pdf: ims[0].save(pdf,"PDF",resolution=100.0,save_all=True,append_images=ims[1:])
def write_copy(path,title,rows):
    open(path,"w",encoding="utf-8").write(f"# {title}\n\n**Estado: BORRADOR para tu aprobación** · no publicado · no programado\n\n"+rows)
control=[]
def add(fecha,canal,formato,pieza,carpeta,flags,verificar,hora):
    control.append([fecha,hora,canal,formato,pieza,carpeta,"Borrador - pendiente de aprobacion","; ".join(flags+verificar) if (flags or verificar) else "","No"])
for p in PIECES:
    # --- carrusel IG/FB
    fc=p["fecha_c"]; slug=p["slug"]
    cf=f"{fc}_IG-FB_carrusel_{slug}"; cpath=os.path.join(PROD,cf)
    if p.get("reuse"):
        src=os.path.join(PROD,p["reuse"])
        if os.path.exists(src) and not os.path.exists(cpath): shutil.copytree(src,cpath)
        elif not os.path.exists(cpath): os.makedirs(cpath)
        n=len([f for f in os.listdir(cpath) if f.startswith("slide_")])
        # eliminar ficha previa para reemplazarla
        for old in ("copy_y_ficha.md",):
            pp=os.path.join(cpath,old)
            if os.path.exists(pp): os.remove(pp)
    else:
        save_set(p["c_slides"],cpath); n=len(p["c_slides"])
    rows=(f"**Fecha sugerida:** {fc} · **Hora provisoria:** 19:00 (hora de Costa Rica; ajustar con Insights)\n**Archivos:** slide_01.png … slide_{n:02d}.png (1080×1350)\n**Tema:** {p['tema']}\n**Llamada a la acción:** {p['c_cta']}\n\n"
          f"## Copy Instagram\n{p['c_ig']}\n\n{p['c_h']}\n\n## Copy Facebook\n{p['c_fb']}\n\n## Texto alternativo\n{p['c_alt']}\n\n"
          "## Control de calidad\n"+"".join(f"- [ ] {x}\n" for x in p["flags"])+"".join(f"- [ ] **Verificar:** {x}\n" for x in p["verificar"])
          +"- [x] Sin promesas de resultado ni cifras sin fuente.\n- [x] Hashtags: máximo 5.\n- [ ] Tu revisión de tono: ¿suena a vos?\n")
    write_copy(os.path.join(cpath,"copy.md"),f"Carrusel: {p['tema']}",rows)
    add(fc,"IG+FB","carrusel",p["tema"],cf,p["flags"],p["verificar"],"19:00")
    # --- estático IG/FB
    if p.get("s"):
        fs=p["fecha_s"]; sf=f"{fs}_IG-FB_estatico_{slug}"; spath=os.path.join(PROD,sf)
        s=p["s"]; slide=(s[0],s[1],s[2] if len(s)>2 else "")
        os.makedirs(spath,exist_ok=True)
        render(slide,1,1).save(os.path.join(spath,"imagen.png"))
        rows=(f"**Fecha sugerida:** {fs} · **Hora provisoria:** 12:00 (Costa Rica)\n**Archivo:** imagen.png (1080×1350)\n**Llamada a la acción:** {p['s_cta']}\n\n"
              f"## Copy Instagram\n{p['s_ig']}\n\n{p['s_h']}\n\n## Copy Facebook\n{p['s_fb']}\n\n## Texto alternativo\n{p['s_alt']}\n\n"
              "## Control de calidad\n"+"".join(f"- [ ] {x}\n" for x in p["flags"][:1])+"- [ ] Tu revisión de tono\n")
        write_copy(os.path.join(spath,"copy.md"),f"Estático: {p['tema']}",rows)
        add(fs,"IG+FB","estatico",p["tema"],sf,p["flags"][:1],p["verificar"],"12:00")
    # --- LinkedIn
    fl=p["fecha_li"]; lf=f"{fl}_LinkedIn_texto_{slug}"; lpath=os.path.join(PROD,lf); os.makedirs(lpath,exist_ok=True)
    extra=""
    if p["id"] in ("W03","W07","W10"):
        pdf=os.path.join(lpath,"documento_carrusel.pdf")
        slides=p["c_slides"] if p["c_slides"] else []
        if slides: save_set(slides,os.path.join(lpath,"_tmp"),pdf=pdf); shutil.rmtree(os.path.join(lpath,"_tmp"))
        extra="**Adjunto opcional:** `documento_carrusel.pdf` (publicación tipo documento de LinkedIn).\n"
    rows=(f"**Fecha sugerida:** {fl} · **Hora provisoria:** 08:00 (Costa Rica)\n{extra}\n## Texto de la publicación\n{p['li']}\n\n{p['li_h']}\n\n## Control de calidad\n"
          +"".join(f"- [ ] {x}\n" for x in p["flags"][:2])+"".join(f"- [ ] **Verificar:** {x}\n" for x in p["verificar"])+"- [ ] Tu revisión de tono\n")
    write_copy(os.path.join(lpath,"post.md"),f"LinkedIn: {p['tema']}",rows)
    add(fl,"LinkedIn","texto"+(" + documento PDF" if extra else ""),p["tema"],lf,p["flags"][:2],p["verificar"],"08:00")
control.sort(key=lambda r:(r[0],r[1]))
with open(os.path.join(PROD,"hoja_de_control_oct_dic.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["fecha","hora_provisoria","canal","formato","pieza","carpeta","estado","requiere","programada"]); w.writerows(control)
print(len(control),"piezas")

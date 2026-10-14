import cv2, numpy as np, sys, json
S,U=sys.argv[1],sys.argv[2]
views={ # crop (x0,y0,x1,y1) in true photo px, grabcut rect inside crop, output width
 'front':('da505fdb-image.jpg',(450,500,1070,1340),(80,70,560,800),448),
 'left': ('bc0b73e7-image.jpg',(420,420,1440,1520),(60,40,980,1060),512),
 'right':('5881d0e3-image.jpg',(440,560,1440,1620),(40,40,980,1040),512),
 'back': ('b3d62ba2-image.jpg',(380,380,1180,1360),(40,40,780,960),448)}
meta={}
for k,(f,(x0,y0,x1,y1),(rx0,ry0,rx1,ry1),ow) in views.items():
    im=cv2.imread(f'{U}/{f}')[y0:y1,x0:x1].copy()
    m=np.zeros(im.shape[:2],np.uint8); bg=np.zeros((1,65),np.float64); fg=np.zeros((1,65),np.float64)
    cv2.grabCut(im,m,(rx0,ry0,rx1-rx0,ry1-ry0),bg,fg,6,cv2.GC_INIT_WITH_RECT)
    mask=((m==1)|(m==3)).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(mask)
    if n>1: big=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); mask=(lab==big).astype(np.uint8)
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    mask=cv2.erode(mask,np.ones((7,7),np.uint8))
    # fill the background by spreading edge colours outward (normalized convolution)
    f32=im.astype(np.float32); mf=mask.astype(np.float32)
    out=f32*mf[...,None]; filled=mf.copy(); acc=out.copy()
    for s in (4,8,16,32,64,128):
        num=cv2.GaussianBlur(f32*mf[...,None],(0,0),s); den=cv2.GaussianBlur(mf,(0,0),s)[...,None]+1e-6
        est=num/den; need=(filled<0.5)&(den[...,0]>0.02)
        acc[need]=est[need]; filled[need]=1
    acc[filled<0.5]=np.mean(f32[mask>0],axis=0)
    soft=cv2.GaussianBlur(mf,(0,0),2)[...,None]
    res=f32*soft+acc*(1-soft)
    h=int(round(ow*(y1-y0)/(x1-x0)))
    res=cv2.resize(np.clip(res,0,255).astype(np.uint8),(ow,h),interpolation=cv2.INTER_AREA)
    cv2.imwrite(f'{S}/home/face_{k}.jpg',res,[cv2.IMWRITE_JPEG_QUALITY,88])
    cv2.imwrite(f'{S}/face/mask_{k}.png',mask*255)
    meta[k]=dict(x0=x0,y0=y0,w=x1-x0,h=y1-y0)
print(json.dumps(meta))

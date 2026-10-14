import cv2, numpy as np, sys
S=sys.argv[1]
src=cv2.imread(f'{S}/home/plate.jpg'); im=src.astype(np.float32)
B,G,Rr=im[...,0],im[...,1],im[...,2]
H,W=B.shape
lum=Rr*.3+G*.59+B*.11
# fit a smooth sky model (quadratic in x,y) on clean sky pixels around the cage
ys,xs=np.mgrid[0:H,0:W]
fit=np.zeros((H,W),bool); fit[0:190,700:1200]=True; fit[190:260,700:820]=True
fit&=(Rr-B)<-8
X=np.stack([np.ones(fit.sum()),xs[fit],ys[fit],xs[fit]**2,ys[fit]**2,xs[fit]*ys[fit]],1)/np.array([1,1e3,1e3,1e6,1e6,1e6])
A=np.stack([np.ones(H*W),xs.ravel(),ys.ravel(),xs.ravel()**2,ys.ravel()**2,(xs*ys).ravel()],1)/np.array([1,1e3,1e3,1e6,1e6,1e6])
sky=np.zeros_like(im)
for c in range(3):
    coef,*_=np.linalg.lstsq(X,im[...,c][fit],rcond=None); sky[...,c]=(A@coef).reshape(H,W)
skyl=sky[...,2]*.3+sky[...,1]*.59+sky[...,0]*.11
m=np.zeros((H,W),np.float32)
for (x0,x1,y0,y1) in [(826,884,165,258),(952,1015,200,295)]:
    box=np.zeros((H,W),bool); box[y0:y1,x0:x1]=True
    m[box&((Rr-B)<2)&(lum>skyl+3)]=1
hole=cv2.dilate(cv2.imread(f'{S}/out/mask.png',0),np.ones((25,25),np.uint8))>0
hole[260:]=False
m[hole&((Rr-B)<-2)]=1
m=cv2.GaussianBlur(cv2.dilate(m,np.ones((3,3),np.uint8)),(0,0),2.0)
grain=np.random.normal(0,1.6,im.shape).astype(np.float32)
out=im*(1-m[...,None])+(sky+grain)*m[...,None]
out=np.clip(out,0,255).astype(np.uint8)
cv2.imwrite(f'{S}/home/plate_fixed.jpg',out,[cv2.IMWRITE_JPEG_QUALITY,92])
cv2.imwrite(f'{S}/out/halo3.png',cv2.resize(out[140:320,800:1060],(780,540)))

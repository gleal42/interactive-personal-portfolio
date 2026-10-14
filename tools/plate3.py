import cv2, numpy as np, sys
S=sys.argv[1]; P=12
im=cv2.imread(f'{S}/out/f0.png'); m=cv2.imread(f'{S}/out/mask.png',0)
m=cv2.dilate(m,np.ones((9,9),np.uint8))
imp=cv2.copyMakeBorder(im,P,P,P,P,cv2.BORDER_REFLECT); mp=cv2.copyMakeBorder(m,P,P,P,P,cv2.BORDER_CONSTANT,0)
# extend mask into top padding where chain touches edge
mp[:P+2,:][:, (mp[P+2]>0)]=255
src=np.roll(imp,-160,axis=1)
ys,xs=np.where(mp>0); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
patch=src[y0:y1+1,x0:x1+1]; pm=mp[y0:y1+1,x0:x1+1]
o=cv2.seamlessClone(patch,imp,pm,(x0+(x1-x0+1)//2,y0+(y1-y0+1)//2),cv2.NORMAL_CLONE)[P:-P,P:-P]
# soften the bright halo at the cloud-top boundary: blend toward telea result in the sky zone
o=cv2.GaussianBlur(o,(0,0),0.6); o=cv2.addWeighted(o,1.5,cv2.GaussianBlur(o,(0,0),2),-0.5,0)
cv2.imwrite(f'{S}/home/plate.jpg',o,[cv2.IMWRITE_JPEG_QUALITY,92])
cv2.imwrite(f'{S}/out/platecrop.png',o[0:400,760:1100])

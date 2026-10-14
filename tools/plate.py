import cv2, numpy as np, sys
S=sys.argv[1]
im=cv2.imread(f'{S}/out/f0.png')
m=np.zeros(im.shape[:2],np.uint8)
cv2.rectangle(m,(906,0),(929,78),255,-1)          # chain
cv2.circle(m,(920,86),20,255,-1)                  # ring
cv2.ellipse(m,(919,170),(76,80),0,180,360,255,-1) # dome
cv2.rectangle(m,(843,165),(995,375),255,-1)       # body + base
cv2.rectangle(m,(896,368),(938,720),255,-1)       # ladder
m=cv2.dilate(m,np.ones((5,5),np.uint8))
cv2.imwrite(f'{S}/out/mask.png',m)
valid=(m==0).astype(np.uint8)*255
out=np.zeros_like(im)
# FSR works per channel set; use FAST on full image in Lab
cv2.xphoto.inpaint(im,valid,out,cv2.xphoto.INPAINT_FSR_FAST)
cv2.imwrite(f'{S}/out/plate_fsr.png',out)
t=cv2.inpaint(im,m,5,cv2.INPAINT_TELEA)
cv2.imwrite(f'{S}/out/plate_telea.png',t)

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','Liberation Serif','DejaVu Serif']})
fig,ax=plt.subplots(figsize=(6.4,10.4)); ax.set_xlim(-0.6,10.2); ax.set_ylim(0.6,17.2); ax.axis('off')
def box(cx,cy,w,h,title,lines,fs=11.5):
    ax.add_patch(FancyBboxPatch((cx-w/2,cy-h/2),w,h,boxstyle='round,pad=0.02,rounding_size=0.25',fc='white',ec='black',lw=1.3))
    lh=0.42; top=cy+(len(lines)*lh)/2
    ax.text(cx,top,title,ha='center',va='center',fontsize=fs+0.5,fontweight='bold')
    for i,l in enumerate(lines): ax.text(cx,top-(i+1)*lh,l,ha='center',va='center',fontsize=fs)
def arr(x1,y1,x2,y2):
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='-|>',color='black',lw=1.2,mutation_scale=12,shrinkA=0,shrinkB=0))
def line(xs,ys): ax.plot(xs,ys,color='black',lw=1.2)
box(2.55,16.2,4.7,1.5,'Airborne LiDAR',['2020 point cloud','~30 million classified points'])
box(7.45,16.2,4.7,1.5,'NAIP Orthophoto',['11 Oct 2020','R, G, B, NIR · 0.6 m'])
box(2.55,13.55,4.7,2.25,'LiDAR Processing',['DTM (ground returns)','DSM (first returns)','nDSM = DSM − DTM (0.5 m)'])
box(7.45,13.55,4.7,2.25,'Image Preparation',['Resample to 0.5 m','Snap to LiDAR grid','Extract R, G, B, NIR bands'])
arr(2.55,15.45,2.55,14.68); arr(7.45,15.45,7.45,14.68)
box(5,10.55,9.6,2.25,'Three SAM Inputs (3-band, 8-bit)',['A: Photo (R, G, B)','B: LiDAR image (height, hillshade, flatness)','C: Fusion image (NIR, Red, DSM)'])
arr(2.55,12.42,2.55,11.68); arr(7.45,12.42,7.45,11.68)
box(5,7.6,9.6,2.25,'Text-Prompted SAM (Google Colab)',['Grounding DINO + SAM ViT-H','Prompt "building" · thresholds 0.2','Size filter: drop boxes > 20% of tile'])
arr(5,9.42,5,8.73)
box(5,4.95,9.6,1.85,'LiDAR Check (Decision-Level Fusion)',['Keep elevated, non-vegetated detections','Automatic Otsu thresholds on elevation and NDVI'])
arr(5,6.47,5,5.88)
box(3.6,2.2,6.8,2.25,'Accuracy Assessment',['Precision · Recall · F1 · IoU','Detection rate by building','size and height'])
box(8.65,2.2,2.3,2.25,'Ground Truth',['LiDAR','building','class 6'],fs=11)
arr(3.6,4.02,3.6,3.33); arr(7.5,2.2,7.0,2.2)
# ground truth connector: from LiDAR Processing left side, down the left margin, to Ground Truth bottom
line([0.2,-0.3,-0.3],[13.55,13.55,0.8]); line([-0.3,8.65],[0.8,0.8]); arr(8.65,0.8,8.65,1.07)
plt.savefig('flowchart_bw_times.png',dpi=300,bbox_inches='tight',facecolor='white'); print('ok')

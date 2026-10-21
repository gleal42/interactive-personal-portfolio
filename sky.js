/* Where the cage and the cloud go, shared by the CSS preview (runs at once) and the 3D scene.
   Units: px of a 1280x720 layout frame, fitted to the screen like the old background photo. */
const SKY={PW:1280,PH:720,ANCHOR:{x:1007,y:148},   // ANCHOR: where the cage base sits in the frame
  CW:988,CH:643,                     // assets/clouds.webp, px
  ROW0:764,                          // photo row of the cut-out's first row (for the sky gradient)
  PEAK:{x:438,y:9},                  // the very top of the cloud, centred under the cage (cut-out px)
  GAP:44};                           // frame px between the cage base and the peak
function skyLayout(W,H){             // H = height of the first screen
  const portrait=W/H<=1, shortWide=!portrait&&H<560, cl=(v,a,b)=>Math.min(b,Math.max(a,v));
  let k,sx,sy,w,m=1;
  if(portrait){
    const by=H*.38,bh=H*.62; k=Math.max(W/SKY.PW,bh/SKY.PH);
    const y0=by+bh-SKY.PH*k;
    sx=W*.72; sy=y0+(SKY.ANCHOR.y+140)*k; w=W*1.6;   // on phones it hangs below the text
  }else{
    // Wide screens: the wider the screen, the bigger the cage and cloud and the further they move in from the
    // right edge, so they fill the middle instead of leaving an empty band between the words and the cloud.
    const a=W/H, g=cl(1+.42*(a-1.6),1,1.5);
    k=Math.max(H/SKY.PH*g,a<=2?W/SKY.PW:0);
    m=cl(1.2+.6*(a-1.6),1.2,1.55);                      // the man, cage, ladder and balloon (and the cloud with them), scaled together
    // centred in the open sky between the end of the words and the right edge of the screen
    const right=sel=>{let x=0; for(const el of document.querySelectorAll(sel)){
      const rg=document.createRange(); rg.selectNodeContents(el);
      for(const r of rg.getClientRects()) if(r.width) x=Math.max(x,r.right);} return x;};
    const textR=right(".intro p")||W*.4, lineR=right(".reveal h1");   // the intro, and "The door was never locked." after the jump
    sx=(Math.min(textR,W*.6)+W)/2;
    sx=Math.max(sx,lineR+110*k*m);                    // and never under the closing line
    // the chain runs up through the menu row: if it would cut through a word, slide it into the nearest gap
    const words=[...document.querySelectorAll("nav .links a")].map(a=>a.getBoundingClientRect()).filter(r=>r.width);
    for(const r of words) if(sx>r.left-8&&sx<r.right+8){
      const i=words.indexOf(r), prevR=i>0?words[i-1].right:-1e9, nextL=i<words.length-1?words[i+1].left:1e9;
      const toL=(Math.max(prevR,r.left-60)+r.left)/2, toR=(r.right+Math.min(nextL,r.right+60))/2;
      sx=Math.abs(toL-sx)<Math.abs(toR-sx)?toL:toR; break;}
    const navB=shortWide?52:82;                       // the cage, chain ring and balloon stay below the menu
    m=Math.max(1,Math.min(m,(H*.55-navB-18)/(145*k)));   // short screens: keep the cage base above the middle, so the cloud still shows
    sy=Math.max(H*.365,navB+18+145*k*m);
    w=Math.max(H*1.5*g*m,(W-sx)/.42);
  }
  // the cloud's peak sits right under the cage; the cloud is big and may run off the right edge and below
  // the fold (scrolling reveals the rest of it)
  const s=w/SKY.CW;
  return {portrait,shortWide,k,m,sx,sy,cloud:{x:sx-SKY.PEAK.x*s,y:sy+SKY.GAP*k*m-SKY.PEAK.y*s,w,h:SKY.CH*s}};
}
function placeCloudCSS(el,L,fold){const c=L.cloud,p=(n,v)=>el.style.setProperty(n,v.toFixed(1)+"px");
  p("--cx",c.x); p("--cy",c.y); p("--cw",c.w); p("--fold",fold);}
{const sky=document.getElementById("sky"), st=document.getElementById("stage"), work=document.getElementById("work"),
  f=()=>{const H=st.clientHeight, L=skyLayout(st.clientWidth,H); placeCloudCSS(sky,L,H);
    // the work section starts a little below the bottom of the cloud, whatever the screen
    work.style.paddingTop=Math.max(64,Math.round(L.cloud.y+L.cloud.h*.93-H+56))+"px";};
  f(); addEventListener("resize",f);
  document.fonts&&document.fonts.ready.then(()=>dispatchEvent(new Event("resize")));}   // the words set where the cage goes: re-place once the font has loaded

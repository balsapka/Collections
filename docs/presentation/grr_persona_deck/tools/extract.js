<script>
window.addEventListener('load',()=>setTimeout(()=>{
const px=v=>parseFloat(v)||0;
const col=c=>{if(!c)return null;const m=c.match(/rgba?\(([^)]+)\)/);if(!m)return null;const a=m[1].split(',').map(s=>parseFloat(s));if(a.length===4&&a[3]===0)return null;return a.slice(0,3).map(v=>Math.round(v)).concat([a.length===4?a[3]:1]);};
const isInline=el=>{const d=getComputedStyle(el).display;return d==='inline'||el.tagName==='BR';};
const out=[];
document.querySelectorAll('section').forEach(sec=>{
  const R0=sec.getBoundingClientRect();
  const ss=getComputedStyle(sec);
  const S={id:sec.id,bg:col(ss.backgroundColor),bgimg:ss.backgroundImage,items:[]};
  const rel=r=>({x:r.left-R0.left,y:r.top-R0.top,w:r.width,h:r.height});
  sec.querySelectorAll('*').forEach(el=>{
    if(el.closest('aside')||el.closest('svg')&&el.tagName.toLowerCase()!=='svg')return;
    const st=getComputedStyle(el);
    if(st.display==='none'||st.visibility==='hidden')return;
    const r=el.getBoundingClientRect(); if(!r.width||!r.height)return;
    const g=rel(r);
    if(el.tagName.toLowerCase()==='svg'){S.items.push(Object.assign({k:'svg',wedge:!!el.closest('[data-pg]')},g));return;}
    // box
    const bg=col(st.backgroundColor);
    const sides=['Top','Right','Bottom','Left'].map(s=>[px(st['border'+s+'Width']),st['border'+s+'Style'],col(st['border'+s+'Color'])]);
    const vis=sides.filter(s=>s[0]>0&&s[1]!=='none'&&s[2]);
    if(bg||vis.length) S.items.push(Object.assign({k:'box',bg,rad:px(st.borderTopLeftRadius),sides},g));
    // text block
    if(isInline(el))return;
    let hasText=false,hasBlock=false;
    el.querySelectorAll('*').forEach(c=>{if(!isInline(c))hasBlock=true;});
    for(const n of el.childNodes){}
    const tw=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let t;while((t=tw.nextNode())){if(t.textContent.trim())hasText=true;}
    if(!hasText||hasBlock)return;
    const runs=[];
    const w2=document.createTreeWalker(el,NodeFilter.SHOW_TEXT|NodeFilter.SHOW_ELEMENT);let n;
    while((n=w2.nextNode())){
      if(n.nodeType===1){if(n.tagName==='BR')runs.push({br:1});continue;}
      const p=getComputedStyle(n.parentElement);
      let txt=n.textContent.replace(/\s+/g,' ');
      if(p.textTransform==='uppercase')txt=txt.toUpperCase();
      runs.push({t:txt,size:px(p.fontSize),color:col(p.color),wt:parseInt(p.fontWeight),it:p.fontStyle==='italic',strike:p.textDecorationLine.includes('line-through'),ls:px(p.letterSpacing),fam:p.fontFamily});
    }
    const pl=px(st.paddingLeft)+px(st.borderLeftWidth),pr=px(st.paddingRight)+px(st.borderRightWidth),pt=px(st.paddingTop)+px(st.borderTopWidth),pb=px(st.paddingBottom)+px(st.borderBottomWidth);
    const fs=px(st.fontSize);let lh=st.lineHeight==='normal'?fs*1.26:px(st.lineHeight);
    const range=document.createRange();range.selectNodeContents(el);const rects=[...range.getClientRects()].filter(q=>q.width>0);
    const lines=new Set(rects.map(q=>Math.round(q.top))).size;
    let tr=null;if(rects.length){const L=Math.min(...rects.map(q=>q.left)),T=Math.min(...rects.map(q=>q.top)),Rr=Math.max(...rects.map(q=>q.right)),B=Math.max(...rects.map(q=>q.bottom));tr={x:L-R0.left,y:T-R0.top,w:Rr-L,h:B-T};}
    S.items.push({k:'text',x:g.x+pl,y:g.y+pt,w:g.w-pl-pr,h:g.h-pt-pb,tr,align:st.textAlign,lh,fs,lines,nowrap:st.whiteSpace==='nowrap',runs});
  });
  out.push(S);
});
const pre=document.createElement('pre');pre.id='out';pre.textContent=JSON.stringify(out);document.body.appendChild(pre);
},2500));
</script>

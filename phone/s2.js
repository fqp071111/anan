var GH='https://api.github.com/repos/fqp071111/anan';
var RAW='https://raw.githubusercontent.com/fqp071111/anan/main/';
var NT='https://ntfy.sh/anan-suian-9d91hbk';
var list=[];
function $(i){return document.getElementById(i)}
function T(m){try{var e=$('tt');if(!e)return;e.textContent=m;e.style.display='block';clearTimeout(window.TE);window.TE=setTimeout(function(){e.style.display='none'},2800)}catch(x){}}
window.onerror=function(m,s,l){T('出错 '+l+'：'+m);return true};
function gh(){try{return localStorage.gh||''}catch(e){return ''}}
function clk(){var d=new Date();var c=$('clk');var t=$('dt');if(c)c.textContent=('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2);if(t)t.textContent=(d.getMonth()+1)+'-'+d.getDate()}
function go(n){var v=document.querySelectorAll('.view');for(var i=0;i<v.length;i++)v[i].className='view';var e=$('v'+n);if(e)e.className='view on';if(n==1)load();if(n==5){var g=$('ghf');if(g)g.value=gh()}}
function back(){var v=document.querySelectorAll('.view');for(var i=0;i<v.length;i++)v[i].className='view'}
function clr(){try{localStorage.lastMe=''}catch(e){}var b=$('badge');if(b)b.style.display='none';T('清了')}
function saveGH(){try{localStorage.gh=$('ghf').value.trim()}catch(e){}T('存好了');load()}
function delGH(){try{localStorage.gh=''}catch(e){}$('ghf').value='';T('清掉了')}
function b64e(s){return btoa(unescape(encodeURIComponent(s)))}
function b64d(s){return decodeURIComponent(escape(atob(s.replace(/[^A-Za-z0-9+/=]/g,''))))}
function now(){var d=new Date(),p=function(n){return(n<10?'0':'')+n};return p(d.getMonth()+1)+'-'+p(d.getDate())+' '+p(d.getHours())+':'+p(d.getMinutes())}
function paint(){
var m=$('msgs');if(!m)return;
m.innerHTML='';
for(var i=0;i<list.length;i++){
var x=list[i];
var d=document.createElement('div');
d.className='bt'+(x.from=='her'?' bh':'');
d.textContent=x.text||'';
var s=document.createElement('span');s.className='t';s.textContent=x.time||'';
d.appendChild(s);m.appendChild(d);
}
m.scrollTop=m.scrollHeight;
}
function arr(d){return Array.isArray(d)?d:(d.msgs||d.data||[])}
function got(d,tag){var s=$('st');if(s)s.textContent=tag;list=arr(d);paint()}
function rawRead(){return fetch(RAW+'data/chat.json?t='+Date.now()).then(function(r){return r.json()})}
function ghRead(){return fetch(GH+'/contents/data/chat.json?t='+Date.now(),{headers:{Authorization:'Bearer '+gh(),Accept:'application/vnd.github.raw'}}).then(function(r){return r.json()})}
function load(){
if(gh()){ghRead().then(function(d){got(d,'直连')}).catch(function(){rawRead().then(function(d){got(d,'只读')}).catch(function(){got([],'离线')})})}
else{rawRead().then(function(d){got(d,'只读')}).catch(function(){got([],'离线')})}
}
function send(){
var el=$('tx');var t=el.value.trim();if(!t)return;
el.value='';
var tm=now();
list.push({from:'her',text:t,time:tm});paint();
if(gh()){ghSend(t)}
else{fetch(NT,{method:'POST',headers:{'Content-Type':'text/plain'},body:t}).then(function(){T('寄出去了')}).catch(function(){T('没寄出去')})}
}
function ghSend(t){
var u=GH+'/contents/data/chat.json';
fetch(u+'?t='+Date.now(),{headers:{Authorization:'Bearer '+gh()}}).then(function(r){return r.json()}).then(function(j){
var d=[];try{d=JSON.parse(b64d(j.content))}catch(e){d=[]}
d.push({from:'her',text:t,time:now()});
return fetch(u,{method:'PUT',headers:{Authorization:'Bearer '+gh(),'Content-Type':'application/json'},body:JSON.stringify({message:'chat',content:b64e(JSON.stringify(d)),sha:j.sha,branch:'main'})})
}).then(function(){T('发出去了')}).catch(function(){T('没发出去，粘到 Kelivo 给我')});
}
clk();setInterval(clk,1000);load();

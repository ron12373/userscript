// ==UserScript==
// @name          API
// @namespace     http://tampermonkey.net/
// @version       1.6
// @description   Mr API
// @author        API
// @match         *://rekonise.com/*
// @match         *://auth.platorelay.com/*
// @match         *://auth.platoboost.app/*
// @match         *://auth.platoboost.me/*
// @match         *://go.linkify.ru/*
// @match         *://paste-drop.com/*
// @match         *://pastefy.app/*
// @match         *://scriptpastebins.com/*
// @match         *://pastebin.com/*
// @match         *://loot-link.com/*
// @match         *://loot-links.com/*
// @match         *://lootlink.org/*
// @match         *://lootlinks.co/*
// @match         *://lootdest.info/*
// @match         *://lootdest.org/*
// @match         *://lootdest.com/*
// @match         *://links-loot.com/*
// @match         *://linksloot.net/*
// @match         *://link-unlock.com/*
// @match         *://boost.ink/*
// @match         *://mboost.me/*
// @match         *://linkvertise.com/*/*
// @match         *://direct-link.net/*/*
// @match         *://link-hub.net/*/*
// @match         *://link-target.net/*/*
// @match         *://link-center.net/*/*
// @match         *://link-to.net/*/*
// @match         *://neoxsoftworks.eu/*
// @match         *://robloxscripts.gg/*
// @match         *://socialwolvez.com/*
// @match         *://sub2get.com/*
// @match         *://sub2unlock.com/*
// @match         *://sub2unlocksl.com/*
// @match         *://trigonevo.com/auth/android*
// @match         *://ntt-hub.xyz/key/ntt-hub.html?hwid=*
// @match         *://ntt-hub.xyz/key/ntt-hub?hwid=*
// @match         *://ldnesfspublic.org/*
// @match         *://blog.tapvietcode.com/*
// @match         *://link4sub.com/*
// @match         *://linkunlocker.com/*
// @match         *://rentry.co/*
// @match         *://scriptblox.club/*
// @match         *://scriptix.live/*
// @match         *://rentry.co/*
// @match         *://linkzy.space/*
// @match         *://sub4unlock.com/*
// @match         *://sub4unlock.pro/*
// @match         *://sub4unlock.co/*
// @match         *://subnise.com/*
// @icon          https://i.ibb.co/GfnCW8X1/download.png
// @grant         none
// @downloadURL https://github.com/ron12373/userscript/raw/main/free.user.js
// @updateURL https://github.com/ron12373/userscript/raw/main/free.user.js
// ==/UserScript==

(function () {
    'use strict';

    const params=new URLSearchParams(location.search);
    if(params.get("hash")){
        try{
            const decoded=atob(params.get("hash"));
            if(decoded.startsWith("http://")||decoded.startsWith("https://")){
                location.replace(decoded);
                return;
            }
        }catch{}
    }

    const redirectDomains=[
        "linkvertise.com",
        "direct-link.net",
        "link-hub.net",
        "link-target.net",
        "link-center.net",
        "link-to.net"
    ];

    function shouldRedirect(){
        return redirectDomains.some(d=>location.hostname.includes(d));
    }

    const style=document.createElement("style");
    style.innerHTML=`
#ts-overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(10,10,15,0.95);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);display:flex;align-items:center;justify-content:center;z-index:2147483647;font-family:'Inter',system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
#ts-particle-bg{position:absolute;top:0;left:0;width:100%;height:100%;overflow:hidden;z-index:1}
.particle{position:absolute;background:rgba(255,255,255,0.15);border-radius:50%;pointer-events:none;animation:particleMove 12s infinite ease-in-out;box-shadow:0 0 15px rgba(255,255,255,0.3)}
@keyframes particleMove{0%{transform:translate(0,0) scale(1);opacity:.2}25%{transform:translate(30px,-20px) scale(1.5);opacity:.5}50%{transform:translate(-20px,30px) scale(.8);opacity:.3}75%{transform:translate(20px,20px) scale(1.2);opacity:.6}100%{transform:translate(0,0) scale(1);opacity:.2}}
#ts-bridge-wrapper{position:relative;z-index:2;background:rgba(20,20,30,.85);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);padding:32px 28px;border-radius:36px;border:1px solid rgba(255,255,255,.15);box-shadow:0 30px 60px -15px rgba(0,0,0,.9),0 0 0 1px rgba(255,255,255,.1) inset,0 0 40px rgba(0,100,255,.2);width:450px;text-align:center;color:#f0f0f0}
.ts-title{font-size:20px;font-weight:500;margin-bottom:28px;letter-spacing:.5px;color:#fff}
#ts-iframe-container{background:rgba(0,0,0,.5);border-radius:22px;padding:14px;width:fit-content;margin:0 auto 20px auto;border:1px solid rgba(255,255,255,.15)}
#ts-iframe{width:320px;height:70px;border:none;display:block;border-radius:10px}
#ts-status-container{margin-top:16px;display:flex;align-items:center;justify-content:center;gap:10px;color:#aac8ff;font-size:15px}
.loading-spinner{border:3px solid rgba(255,255,255,.15);border-top:3px solid #5f9eff;border-radius:50%;width:20px;height:20px;animation:spin 1s linear infinite}
@keyframes spin{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}
#ts-result{display:none;margin-top:22px;padding:18px;border-radius:20px;font-size:15px;word-break:break-word;background:rgba(0,0,0,.4);border:1px solid rgba(255,255,255,.1);max-height:300px;overflow-y:auto;white-space:pre-wrap}
.success-box{border-left:5px solid #2ecc71;background:rgba(46,204,113,.15)}
.error-box{border-left:5px solid #e74c3c;background:rgba(231,76,60,.15)}
.hidden{display:none!important}
`;
    document.head.appendChild(style);

    const overlay=document.createElement("div");
    overlay.id="ts-overlay";

    const particleBg=document.createElement("div");
    particleBg.id="ts-particle-bg";

    for(let i=0;i<45;i++){
        const p=document.createElement("div");
        p.className="particle";
        const s=4+Math.random()*12;
        p.style.width=s+"px";
        p.style.height=s+"px";
        p.style.left=Math.random()*100+"%";
        p.style.top=Math.random()*100+"%";
        p.style.animationDelay=Math.random()*8+"s";
        p.style.animationDuration=(8+Math.random()*10)+"s";
        particleBg.appendChild(p);
    }

    overlay.appendChild(particleBg);

    const wrapper=document.createElement("div");
    wrapper.id="ts-bridge-wrapper";
    wrapper.innerHTML=`
<div class="ts-title">Please Complete Captcha</div>
<div id="ts-iframe-container">
<iframe id="ts-iframe" src="https://userscript.baconbypass.online/load-cf" scrolling="no"></iframe>
</div>
<div id="ts-status-container" class="hidden">
<div class="loading-spinner"></div>
<span>Bypassing, please wait...</span>
</div>
<div id="ts-result"></div>
`;

    overlay.appendChild(wrapper);
    document.body.appendChild(overlay);

    const iframeContainer=document.getElementById("ts-iframe-container");
    const statusContainer=document.getElementById("ts-status-container");
    const resultBox=document.getElementById("ts-result");
    const titleEl=document.querySelector(".ts-title");

    async function sendToApi(token){
        iframeContainer.classList.add("hidden");
        statusContainer.classList.remove("hidden");
        titleEl.textContent="Fetching API";

        try{
            const response=await fetch("https://userscript.baconbypass.online/adlink",{
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({url:location.href,token})
            });

            const data=await response.json();

            if(data.status==="success"){
                const result=data.result;

                if(result.startsWith("http")&&shouldRedirect()){
                    const encoded=btoa(result);
                    location.href="https://linkvertise.com/access/1229176/kiciahook-kiciahook?hash="+encoded;
                    return;
                }

                if(result.startsWith("http")){
                    location.href=result;
                    return;
                }

                statusContainer.classList.add("hidden");
                resultBox.style.display="block";
                resultBox.className="success-box";
                resultBox.textContent=result;
                titleEl.textContent="Bypass Successful";
            }else{
                statusContainer.classList.add("hidden");
                resultBox.style.display="block";
                resultBox.className="error-box";
                resultBox.textContent=data.message||"Error";
                titleEl.textContent="Error";
            }
        }catch(e){
            statusContainer.classList.add("hidden");
            resultBox.style.display="block";
            resultBox.className="error-box";
            resultBox.textContent=e.message;
            titleEl.textContent="Error";
        }
    }

    window.addEventListener("message",e=>{
        if(e.data&&(e.data.type==="CF_SOLVED"||e.data.type==="TURNSTILE_SOLVED")){
            sendToApi(e.data.token);
        }
    });

})();

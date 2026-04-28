// ==UserScript==
// @name         API
// @namespace    http://tampermonkey.net/
// @version      1.9
// @description  API Huh?
// @author       API
// @match        *://rekonise.com/*
// @match        *://auth.platorelay.com/*
// @match        *://auth.platoboost.app/*
// @match        *://auth.platoboost.me/*
// @match        *://go.linkify.ru/*
// @match        *://paste-drop.com/*
// @match        *://pastefy.app/*
// @match        *://scriptpastebins.com/*
// @match        *://pastebin.com/*
// @match        *://loot-link.com/*
// @match        *://loot-links.com/*
// @match        *://lootlink.org/*
// @match        *://lootlinks.co/*
// @match        *://lootdest.info/*
// @match        *://lootdest.org/*
// @match        *://lootdest.com/*
// @match        *://links-loot.com/*
// @match        *://linksloot.net/*
// @match        *://links.lootlabs.gg/*
// @match        *://link-unlock.com/*
// @match        *://boost.ink/*
// @match        *://mboost.me/*
// @match        *://linkvertise.com/*/*
// @match        *://direct-link.net/*/*
// @match        *://link-hub.net/*/*
// @match        *://link-target.net/*/*
// @match        *://link-center.net/*/*
// @match        *://link-to.net/*/*
// @match        *://neoxsoftworks.eu/*
// @match        *://robloxscripts.gg/*
// @match        *://socialwolvez.com/*
// @match        *://sub2get.com/*
// @match        *://sub2unlock.com/*
// @match        *://sub2unlocksl.com/*
// @match        *://trigonevo.com/auth/android*
// @match        *://ntt-hub.xyz/key/main?hwid=*
// @match        *://ntt-hub.xyz/key/ntt-hub?hwid=*
// @match        *://ldnesfspublic.org/*
// @match        *://blog.tapvietcode.com/*
// @match        *://link4sub.com/*
// @match        *://linkunlocker.com/*
// @match        *://rentry.co/*
// @match        *://scriptblox.club/*
// @match        *://scriptix.live/*
// @match        *://linkzy.space/*
// @match        *://sub4unlock.com/*
// @match        *://sub4unlock.pro/*
// @match        *://sub4unlock.co/*
// @match        *://subnise.com/*
// @icon         https://i.ibb.co/GfnCW8X1/download.png
// @require      https://github.com/ron12373/userscript/raw/main/mommy.js
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    const params = new URLSearchParams(location.search);
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    if (params.get("hash")) {
        try {
            const decoded = atob(params.get("hash"));
            if (decoded.startsWith("http://") || decoded.startsWith("https://")) {
                location.replace(decoded);
                return;
            }
        } catch (e) {}
    }

    const redirectDomains = ["linkvertise.com", "direct-link.net", "link-hub.net", "link-target.net", "link-center.net", "link-to.net"];
    function shouldRedirect() { return redirectDomains.some(d => location.hostname.includes(d)); }

    const style = document.createElement("style");
    style.innerHTML = `
        #cmd-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7); z-index: 2147483647;
            font-family: 'Consolas', 'Lucida Console', monospace;
            display: flex; align-items: center; justify-content: center;
        }
        #cmd-window {
            width: 700px; height: 400px; background: #0c0c0c;
            border: 1px solid #777; box-shadow: 0 15px 40px rgba(0,0,0,0.9);
            display: flex; flex-direction: column; border-radius: 4px; overflow: hidden;
        }
        #cmd-header {
            background: #ffffff; color: #000; padding: 0 0 0 10px; font-size: 12px;
            display: flex; justify-content: space-between; align-items: center;
            height: 28px; border-bottom: 1px solid #555; user-select: none;
        }
        .header-title { display: flex; align-items: center; gap: 8px; }
        .header-icon { width: 16px; height: 16px; }
        .header-controls { display: flex; height: 100%; }
        .control-btn { width: 45px; text-align: center; line-height: 28px; font-size: 14px; transition: 0.1s; cursor: pointer; }
        .control-btn:hover { background: #e5e5e5; }
        .btn-close:hover { background: #e81123 !important; color: #fff; }
        #cmd-body { padding: 12px; flex-grow: 1; overflow-y: auto; line-height: 1.4; font-size: 14px; color: #cccccc; }
        .cmd-line { margin-bottom: 4px; word-break: break-all; }
        .cmd-prompt { color: #ffffff; margin-right: 5px; }
        .cmd-text-cyan { color: #00ffff; }
        .cmd-text-red { color: #ff5555; }
        .cmd-text-green { color: #00ff00; }
        .cmd-text-yellow { color: #ffff00; }
        #ts-iframe-container { margin: 10px 0; border: 1px solid #333; padding: 10px; background: #1a1a1a; width: fit-content; }
        #ts-iframe { width: 300px; height: 75px; border: none; filter: invert(0.9); }
        .copy-btn { display: inline-block; margin-top: 10px; padding: 5px 10px; background: #333; color: #00ff00; border: 1px solid #555; cursor: pointer; font-size: 12px; transition: 0.2s; }
        .copy-btn:hover { background: #444; border-color: #00ff00; }
        .copy-btn:active { background: #222; }
        .loading-text::after { content: ''; animation: dots 1.5s steps(4, end) infinite; }
        @keyframes dots { 0%,20%{content:''} 40%{content:'.'} 60%{content:'..'} 80%{content:'...'} }
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: #0c0c0c; }
        ::-webkit-scrollbar-thumb { background: #333; }
        .hidden { display: none !important; }
    `;
    document.head.appendChild(style);

    const overlay = document.createElement("div");
    overlay.id = "cmd-overlay";
    overlay.innerHTML = `
        <div id="cmd-window">
            <div id="cmd-header">
                <div class="header-title">
                    <img class="header-icon" src="https://i.ibb.co/GfnCW8X1/download.png">
                    <span>C:\\Windows\\system32\\cmd.exe - baconbypass.exe</span>
                </div>
                <div class="header-controls">
                    <div class="control-btn">─</div>
                    <div class="control-btn">❏</div>
                    <div id="close-cmd" class="control-btn btn-close">✕</div>
                </div>
            </div>
            <div id="cmd-body">
                <div class="cmd-line">Microsoft Windows [Version 10.0.19045.4291]</div>
                <div class="cmd-line">(c) Microsoft Corporation. All rights reserved.</div>
                <br>
                <div class="cmd-line"><span class="cmd-prompt">C:\\Users\\Bacon></span>baconbypass.exe --target=${location.hostname}</div>
                <div id="cmd-log">
                    <div class="cmd-line">[*] Initializing...</div>
                </div>
                <div id="ts-iframe-container" class="hidden">
                    <iframe id="ts-iframe" src="https://userscript.baconbypass.online/load-cf" scrolling="no"></iframe>
                </div>
                <div id="cmd-status" class="hidden">
    <div id="status-text" class="cmd-line cmd-text-cyan loading-text">[*] Fetching Bacon Bypass Bot</div>
</div>
                <div id="cmd-result" class="cmd-line hidden"></div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);

    document.getElementById("close-cmd").onclick = () => { overlay.remove(); };

    const logBox = document.getElementById("cmd-log");
    const statusBox = document.getElementById("cmd-status");
    const iframeContainer = document.getElementById("ts-iframe-container");
    const resultBox = document.getElementById("cmd-result");

    function addLog(text, colorClass = "") {
        const div = document.createElement("div");
        div.className = "cmd-line " + colorClass;
        div.innerHTML = `<span class="cmd-prompt">[*]</span> ${text}`;
        logBox.appendChild(div);
        document.getElementById("cmd-body").scrollTop = 9999;
    }

    async function getVerifyToken() {
        try {
            const res = await fetch("https://userscript.baconbypass.online/verify");
            const data = await res.json();
            if (!data.s || !data.p) throw new Error();
            return await new Promise((resolve, reject) => {
                if (typeof window.ppp !== 'function') return reject(new Error("lib not ready"));
                window.ppp(data.p, async (result) => {
                    try {
                        const encoded = btoa(result);
                        const vRes = await fetch("https://userscript.baconbypass.online/verify", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ session: data.s, result: encoded })
                        });
                        const vData = await vRes.json();
                        if (vData.status === "success" && vData.token2) resolve(vData.token2);
                        else reject(new Error("verification failed"));
                    } catch (e) { reject(e); }
                });
            });
        } catch (e) {
            return null;
        }
    }

    async function runBypass(cfToken) {
        iframeContainer.classList.add("hidden");
        statusBox.classList.remove("hidden");

        const statusText = document.getElementById("status-text");

        try {
            statusText.innerText = "[*] Verifying security challenge";
            statusText.className = "cmd-line cmd-text-yellow loading-text";

            const token2 = await getVerifyToken();

            if (!token2) {
                resultBox.classList.remove("hidden");
                resultBox.className = "cmd-line cmd-text-red";
                resultBox.innerHTML = `<br>[SYSTEM ERROR] Challenge failed. Please try again.`;
                statusBox.classList.add("hidden");
                return;
            }

            addLog("Challenge Passed Successfully!", "cmd-text-green");

            statusText.innerText = "[*] Fetching Bacon Bypass Bot";
            statusText.className = "cmd-line cmd-text-cyan loading-text";

            const response = await fetch("https://userscript.baconbypass.online/adlink", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: location.href, token: cfToken, token2 })
            });

            const data = await response.json();

            if (data.status === "success") {
                const result = data.result;

                addLog("Done!", "cmd-text-green");
                statusBox.classList.add("hidden");

                if (result.startsWith("http") && shouldRedirect()) {
                    location.href = "https://linkvertise.com/access/1229176/kiciahook-kiciahook?hash=" + btoa(result);
                    return;
                }

                if (result.startsWith("http")) {
                    location.href = result;
                    return;
                }

                resultBox.classList.remove("hidden");
                resultBox.innerHTML = `
                <br><span class="cmd-text-cyan">>> DATA RETRIEVED:</span><br>
                <span id="raw-data" style="color:#fff;background:#222;padding:2px 5px;">${result}</span><br>
                <div id="copy-trigger" class="copy-btn">Click to Copy</div>
            `;
                document.getElementById("copy-trigger").onclick = function () {
                    navigator.clipboard.writeText(result).then(() => {
                        this.innerText = "COPIED!";
                        this.style.color = "#fff";
                        setTimeout(() => { this.innerText = "Click to Copy"; this.style.color = "#00ff00"; }, 2000);
                    });
                };
            } else {
                throw new Error(data.message || "Bypass Failed");
            }
        } catch (e) {
            statusBox.classList.add("hidden");
            resultBox.classList.remove("hidden");
            resultBox.className = "cmd-line cmd-text-red";
            resultBox.innerHTML = `<br>[SYSTEM ERROR] ${e.message}`;
        }
    }

    async function init() {
        addLog("Challenge required. Complete verification below.", "cmd-text-yellow");
        iframeContainer.classList.remove("hidden");
    }

    init();

    window.addEventListener("message", async (e) => {
        if (e.data && (e.data.type === "CF_SOLVED" || e.data.type === "TURNSTILE_SOLVED")) {
            await runBypass(e.data.token);
        }
    });
})();

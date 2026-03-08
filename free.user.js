// ==UserScript==
// @name          API
// @namespace     http://tampermonkey.net/
// @version       2.4
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
// @match         *://linkvertise.com/*
// @match         *://direct-link.net/*
// @match         *://link-hub.net/*
// @match         *://link-target.net/*
// @match         *://link-center.net/*
// @match         *://link-to.net/*
// @match         *://neoxsoftworks.eu/*
// @match         *://robloxscripts.gg/*
// @match         *://socialwolvez.com/*
// @match         *://sub2get.com/*
// @match         *://sub2unlock.com/*
// @match         *://sub2unlocksl.com/*
// @match         *://trigonevo.com/auth/android*
// @match         *://ntt-hub.xyz/*
// @match         *://ldnesfspublic.org/*
// @icon          https://i.ibb.co/GfnCW8X1/download.png
// @grant         none
// ==/UserScript==

(function() {
    'use strict';

    const style = document.createElement('style');
    style.innerHTML = `
        #ts-particle-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 9999;
            pointer-events: none;
            overflow: hidden;
            background: #0a0a0a;
        }
        .particle {
            position: absolute;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 50%;
            pointer-events: none;
            animation: particleMove 12s infinite ease-in-out;
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
        }
        @keyframes particleMove {
            0% {
                transform: translate(0, 0) scale(1);
                opacity: 0.2;
            }
            25% {
                transform: translate(30px, -20px) scale(1.5);
                opacity: 0.5;
            }
            50% {
                transform: translate(-20px, 30px) scale(0.8);
                opacity: 0.3;
            }
            75% {
                transform: translate(20px, 20px) scale(1.2);
                opacity: 0.6;
            }
            100% {
                transform: translate(0, 0) scale(1);
                opacity: 0.2;
            }
        }

        #ts-bridge-wrapper {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 10000;
            background: rgba(20, 20, 30, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 32px 28px;
            border-radius: 36px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.9), 0 0 0 1px rgba(255, 255, 255, 0.1) inset, 0 0 40px rgba(0, 100, 255, 0.2);
            width: 450px;
            text-align: center;
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #f0f0f0;
            transition: all 0.3s ease;
        }

        .ts-title {
            font-size: 20px;
            font-weight: 500;
            margin-bottom: 28px;
            letter-spacing: 0.5px;
            color: #ffffff;
            text-shadow: 0 4px 12px rgba(0, 0, 0, 0.7);
        }

        #ts-iframe-container {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 22px;
            padding: 14px;
            width: fit-content;
            margin: 0 auto 20px auto;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.7);
        }

        #ts-iframe {
            width: 320px;
            height: 70px;
            border: none;
            display: block;
            border-radius: 10px;
        }

        #ts-status-container {
            margin-top: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            color: #aac8ff;
            font-size: 15px;
        }

        .loading-spinner {
            border: 3px solid rgba(255,255,255,0.15);
            border-top: 3px solid #5f9eff;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        #ts-result {
            display: none;
            margin-top: 22px;
            padding: 18px;
            border-radius: 20px;
            font-size: 15px;
            word-break: break-word;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #f0f0f0;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .success-box {
            border-left: 5px solid #2ecc71;
            background: rgba(46, 204, 113, 0.15);
        }

        .error-box {
            border-left: 5px solid #e74c3c;
            background: rgba(231, 76, 60, 0.15);
        }

        .result-text {
            margin-bottom: 14px;
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 14px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .result-actions {
            display: flex;
            gap: 16px;
            justify-content: center;
            margin-top: 20px;
        }

        .result-actions button {
            background: rgba(40, 40, 60, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #ffffff;
            padding: 10px 28px;
            border-radius: 50px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s;
            backdrop-filter: blur(5px);
            box-shadow: 0 8px 18px rgba(0, 0, 0, 0.5);
            letter-spacing: 0.5px;
        }

        .result-actions button:hover {
            background: rgba(70, 70, 110, 0.95);
            transform: translateY(-3px);
            border-color: rgba(255, 255, 255, 0.4);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.7);
        }

        .hidden {
            display: none !important;
        }
    `;
    document.head.appendChild(style);

    document.head.innerHTML = '';
    document.head.appendChild(style);
    document.body.innerHTML = '';

    const bg = document.createElement('div');
    bg.id = 'ts-particle-bg';
    for (let i = 0; i < 45; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        const size = 4 + Math.random() * 12;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 8 + 's';
        particle.style.animationDuration = (8 + Math.random() * 10) + 's';
        particle.style.background = `rgba(255, 255, 255, ${0.1 + Math.random() * 0.2})`;
        bg.appendChild(particle);
    }
    document.body.appendChild(bg);

    const wrapper = document.createElement('div');
    wrapper.id = "ts-bridge-wrapper";
    wrapper.innerHTML = `
        <div class="ts-title">Please Complete Captcha</div>
        <div id="ts-iframe-container">
            <iframe id="ts-iframe"
                    src="https://userscript.baconbypass.online/load-cf"
                    scrolling="no"
                    allowtransparency="true"></iframe>
        </div>
        <div id="ts-status-container" class="hidden">
            <div class="loading-spinner"></div>
            <span>Bypassing, please wait...</span>
        </div>
        <div id="ts-result"></div>
        <div class="result-actions" id="ts-actions" style="display: none;">
            <button id="ts-copy-btn">Copy</button>
            <button id="ts-download-btn">Download</button>
            <button id="ts-open-btn" style="display: none;">Open</button>
        </div>
    `;
    document.body.appendChild(wrapper);

    const iframeContainer = document.getElementById('ts-iframe-container');
    const statusContainer = document.getElementById('ts-status-container');
    const resultBox = document.getElementById('ts-result');
    const actionsDiv = document.getElementById('ts-actions');
    const copyBtn = document.getElementById('ts-copy-btn');
    const downloadBtn = document.getElementById('ts-download-btn');
    const openBtn = document.getElementById('ts-open-btn');

    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    async function sendToApi(token) {
        iframeContainer.classList.add('hidden');
        statusContainer.classList.remove('hidden');
        actionsDiv.style.display = 'none';

        try {
            const response = await fetch('https://userscript.baconbypass.online/adlink', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: window.location.href,
                    token: token
                })
            });

            const data = await response.json();
            statusContainer.classList.add('hidden');
            resultBox.style.display = "block";

            if (data.status === "success") {
                const resultText = data.result;
                const isUrl = resultText.startsWith('http://') || resultText.startsWith('https://');

                resultBox.className = "success-box";
                resultBox.innerHTML = `<div class="result-text">${escapeHtml(resultText)}</div>`;

                actionsDiv.style.display = 'flex';
                copyBtn.onclick = () => {
                    navigator.clipboard.writeText(resultText).catch(() => {
                        alert('Copy failed, please select manually.');
                    });
                    copyBtn.textContent = 'Copied!';
                    setTimeout(() => {
                        copyBtn.textContent = 'Copy';
                    }, 3000);
                };

                if (isUrl) {
                    openBtn.style.display = 'inline-block';
                    downloadBtn.style.display = 'none';
                    openBtn.onclick = () => window.open(resultText, '_blank');
                } else {
                    openBtn.style.display = 'none';
                    downloadBtn.style.display = 'inline-block';
                    downloadBtn.onclick = () => {
                        const blob = new Blob([resultText], { type: 'text/plain' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'result.txt';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                    };
                }
            } else {
                resultBox.className = "error-box";
                resultBox.innerText = "Error: " + (data.message || "Unknown error");
                actionsDiv.style.display = 'none';
            }
        } catch (err) {
            statusContainer.classList.add('hidden');
            resultBox.style.display = "block";
            resultBox.className = "error-box";
            resultBox.innerText = "Connection Failed: " + err.message;
            actionsDiv.style.display = 'none';
        }
    }

    window.addEventListener('message', function(event) {
        if (event.data && (event.data.type === 'CF_SOLVED' || event.data.type === 'TURNSTILE_SOLVED')) {
            sendToApi(event.data.token);
        }
    });


})();

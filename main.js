// HUD real-time data polling and UI interactions
window.addEventListener('DOMContentLoaded', () => {
    // Poll backend for real-time stats every 5 seconds
    const realtimeWindow = document.getElementById('realtime-window');
    async function fetchStats() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();
            realtimeWindow.innerHTML = `<div class="title">Real-Time Stats</div>
                <pre>${JSON.stringify(data, null, 2)}</pre>`;
        } catch (e) {
            console.error('Error fetching stats:', e);
            realtimeWindow.innerHTML = '<div class="title">Real-Time Stats</div><p>Error loading data</p>';
        }
    }
    fetchStats();
    setInterval(fetchStats, 5000);

    // Button states for scan, deauth, brute
    document.querySelector('#scan-btn')?.addEventListener('click', () => {
        const btn = document.querySelector('#scan-btn');
        btn.disabled = true;
        btn.textContent = 'Scanning...';
    });

    document.querySelectorAll('.deauth-form').forEach(form => {
        form.addEventListener('submit', () => {
            const btn = form.querySelector('button');
            btn.disabled = true;
            btn.textContent = 'Deauthing...';
        });
    });

    document.querySelectorAll('.brute-form').forEach(form => {
        form.addEventListener('submit', () => {
            const btn = form.querySelector('button');
            btn.disabled = true;
            btn.textContent = 'Cracking...';
        });
    });
});
```javascript
// Attach form handlers and enhance UX
window.addEventListener('DOMContentLoaded', () => {
    const scanBtn = document.getElementById('scan-btn');
    if (scanBtn) {
        scanBtn.addEventListener('click', () => {
            scanBtn.disabled = true;
            scanBtn.textContent = 'Scanning...';
        });
    }

    const deauthForms = document.querySelectorAll('.deauth-form');
    deauthForms.forEach(form => {
        form.addEventListener('submit', () => {
            const btn = form.querySelector('button');
            btn.disabled = true;
            btn.textContent = 'Deauthiating...';
        });
    });

    const bruteForms = document.querySelectorAll('.brute-form');
    bruteForms.forEach(form => {
        form.addEventListener('submit', () => {
            const btn = form.querySelector('button');
            btn.disabled = true;
            btn.textContent = 'Cracking...';
        });
    });
});
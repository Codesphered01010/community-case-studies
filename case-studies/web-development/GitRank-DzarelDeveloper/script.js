

document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initApp();
    initTiltEffect();
});

let audioCtx = null;

function initAudio() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
}

function playHoverSound() {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(800, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(1200, audioCtx.currentTime + 0.1);
    gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.1);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.1);
}

function playTypingSound() {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'square';
    osc.frequency.setValueAtTime(150 + Math.random() * 50, audioCtx.currentTime);
    gain.gain.setValueAtTime(0.02, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.05);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.05);
}

function playRevealSound() {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(150, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(40, audioCtx.currentTime + 1.5);
    gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 1.5);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 1.5);
}

function initTiltEffect() {
    const cards = document.querySelectorAll('.glass-panel');
    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -5;
            const rotateY = ((x - centerX) / centerX) * 5;
            
            card.style.transition = 'none';
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transition = 'transform 0.5s ease';
            card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
        });
    });
}

function initParticles() {
    const canvas = document.getElementById('particle-canvas');
    const ctx = canvas.getContext('2d');
    let particles = [];
    const particleCount = 100;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2;
            this.speedX = Math.random() * 1 - 0.5;
            this.speedY = Math.random() * 1 - 0.5;
            this.color = Math.random() > 0.5 ? '#00f0ff' : '#ff0055';
            this.alpha = Math.random() * 0.5 + 0.1;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            if (this.x > canvas.width) this.x = 0;
            if (this.x < 0) this.x = canvas.width;
            if (this.y > canvas.height) this.y = 0;
            if (this.y < 0) this.y = canvas.height;
        }
        draw() {
            ctx.globalAlpha = this.alpha;
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        requestAnimationFrame(animate);
    }
    animate();
}

const API_BASE = 'https://api.github.com/users/';
const STATE = {
    username: '',
    profileData: null,
    reposData: null,
    stats: {
        repos: 0,
        stars: 0,
        followers: 0,
        commits: 0
    },
    score: 0,
    tier: '',
    tierColor: '',
    archetype: '',
    lang: 'id'
};

const TIERS = [
    { name: 'SSS', min: 95, color: '#ff0055' },
    { name: 'SS', min: 85, color: '#fcee0a' },
    { name: 'S', min: 75, color: '#00f0ff' },
    { name: 'A', min: 60, color: '#00ff66' },
    { name: 'B', min: 45, color: '#bf00ff' },
    { name: 'C', min: 25, color: '#ff9900' },
    { name: 'D', min: 0, color: '#8b9bb4' }
];

const TRANSLATIONS = {
    id: {
        nav_analyze: "Analisis",
        nav_compare: "Bandingkan",
        hero_title_search1: "Temukan",
        hero_title_search2: "Pangkatmu",
        hero_subtitle_search: "Masukkan username GitHub Anda untuk mendekripsi statistik developer Anda dan mengungkap peringkat global Anda.",
        search_placeholder: "Masukkan username GitHub",
        btn_initialize: "MULAI_",
        hero_title_compare1: "Pertarungan",
        hero_title_compare2: "1v1",
        hero_subtitle_compare: "Masukkan dua username GitHub untuk melihat siapa yang memiliki statistik lebih unggul.",
        p1_placeholder: "Username Player 1",
        p2_placeholder: "Username Player 2",
        btn_fight: "TARUNG_",
        loading_init: "Menghubungkan ke mainframe...",
        loading_battle_init: "Menyiapkan Arena Pertempuran...",
        label_power_level: "LEVEL_KEKUATAN",
        label_class: "KELAS: ",
        class_unknown: "Tidak Diketahui",
        btn_share: "BAGIKAN_PROFIL",
        btn_recalibrate: "KALIBRASI_ULANG",
        label_scan: "PINDAI_ID",
        title_skill_matrix: "MATRIKS_KEAHLIAN",
        stat_repos: "REPOSITORI",
        stat_stars: "TOTAL_BINTANG",
        stat_followers: "PENGIKUT",
        stat_commits: "EST. KOMIT",
        title_tech_stack: "TEKNOLOGI",
        title_ai_analysis: "ANALISIS_AI",
        title_unlocked_badges: "LENCANA_TERBUKA",
        winner_crown: "👑 PEMENANG",
        btn_new_battle: "PERTEMPURAN_BARU",
        
        err_title: "KEGAGALAN SISTEM",
        err_empty_user: "Silakan masukkan username.",
        err_empty_compare: "Masukkan kedua username.",
        toast_copied: "Tautan disalin ke papan klip!",
        err_rate_limit: "Batas Akses API GitHub Terlampaui! Silakan tunggu satu jam.",
        err_not_found: "Username tidak ditemukan di grid GitHub.",
        err_p_not_found: "Username {username} tidak ditemukan di grid GitHub.",
        
        CODE_WIZARD: "Penyihir Kode",
        SOCIAL_HACKER: "Peretas Sosial",
        FACTORY_MACHINE: "Mesin Pabrik",
        RISING_ROOKIE: "Pemula Berbakat",
        
        radar_popularity: "POPULARITAS",
        radar_activity: "AKTIVITAS",
        radar_impact: "DAMPAK_KODE",
        radar_dedication: "DEDIKASI",
        
        badges: {
            'Builder': "Pembangun",
            'Factory': "Pabrik",
            'Spark': "Percikan",
            'Supernova': "Supernova",
            'Watched': "Diawasi",
            'Influencer': "Influencer",
            'Newbie': "Pemula"
        },
        
        loading_msgs: [
            "Menghubungkan ke mainframe...",
            "Mengambil data profil...",
            "Menghitung jumlah bintang...",
            "Menganalisis riwayat komit...",
            "Berkonsultasi dengan Oracle AI...",
            "Mensintesis Pangkat..."
        ],
        
        battle_msgs: [
            "Menyiapkan Arena Pertempuran...",
            "Mengambil profil...",
            "Menimbang jumlah bintang...",
            "Mengukur jumlah pengikut...",
            "Menghitung Level Kekuatan..."
        ],
        
        commentaries: {
            'SSS': "Parameter logika luar biasa terdeteksi. Anda adalah konstruksi legendaris di dalam matriks. Program lain mengagumi Anda.",
            'SS': "Integritas kode luar biasa. Riwayat komit Anda menunjukkan Anda tidak pernah tidur. Kinerja yang menonjol.",
            'S': "Profil yang sangat dioptimalkan. Matriks keahlian Anda bersinar cukup terang untuk memberi daya pada kota sibernetik kecil.",
            'A': "Pola struktural yang solid. Anda telah menembus tingkat atas jaringan. Terus tingkatkan modul Anda.",
            'B': "Kapasitas operasional standar. Anda memiliki potensi, tetapi repositori Anda membutuhkan lebih banyak siklus untuk dikompilasi menjadi kehebatan.",
            'C': "Inisiasi protokol: Belajar & Bangun. Anda baru saja memulai perjalanan Anda melalui bentangan digital.",
            'D': "Apakah Anda benar-benar terhubung ke jaringan? Profil Anda hampir seperti hantu. Waktunya untuk mendorong beberapa komit."
        },
        ai_inconclusive: "Pemindaian selesai. Hasil tidak meyakinkan.",
        critical_hit: "SERANGAN KRITIS!"
    },
    en: {
        nav_analyze: "Analyze",
        nav_compare: "Compare",
        hero_title_search1: "Discover Your",
        hero_title_search2: "Rank",
        hero_subtitle_search: "Enter your GitHub username to decrypt your developer stats and unveil your global standing.",
        search_placeholder: "Enter GitHub username",
        btn_initialize: "INITIALIZE_",
        hero_title_compare1: "1v1",
        hero_title_compare2: "Battle",
        hero_subtitle_compare: "Enter two GitHub usernames to see who has the superior stats.",
        p1_placeholder: "Player 1 username",
        p2_placeholder: "Player 2 username",
        btn_fight: "FIGHT_",
        loading_init: "Establishing connection to mainframe...",
        loading_battle_init: "Initializing Battle Arena...",
        label_power_level: "POWER_LEVEL",
        label_class: "CLASS: ",
        class_unknown: "Unknown",
        btn_share: "SHARE_PROFILE",
        btn_recalibrate: "RECALIBRATE",
        label_scan: "SCAN_ID",
        title_skill_matrix: "SKILL_MATRIX",
        stat_repos: "REPOSITORIES",
        stat_stars: "TOTAL_STARS",
        stat_followers: "FOLLOWERS",
        stat_commits: "EST. COMMITS",
        title_tech_stack: "TECH_STACK",
        title_ai_analysis: "AI_ANALYSIS",
        title_unlocked_badges: "UNLOCKED_BADGES",
        winner_crown: "👑 WINNER",
        btn_new_battle: "NEW_BATTLE",
        
        err_title: "SYSTEM FAILURE",
        err_empty_user: "Please enter a username.",
        err_empty_compare: "Enter both usernames.",
        toast_copied: "Link copied to clipboard!",
        err_rate_limit: "GitHub API Rate Limit Exceeded! Please wait an hour.",
        err_not_found: "Username not found in the GitHub grid.",
        err_p_not_found: "Username {username} not found in the GitHub grid.",
        
        CODE_WIZARD: "Code Wizard",
        SOCIAL_HACKER: "Social Hacker",
        FACTORY_MACHINE: "Factory Machine",
        RISING_ROOKIE: "Rising Rookie",
        
        radar_popularity: "POPULARITY",
        radar_activity: "ACTIVITY",
        radar_impact: "CODE_IMPACT",
        radar_dedication: "DEDICATION",
        
        badges: {
            'Builder': "Builder",
            'Factory': "Factory",
            'Spark': "Spark",
            'Supernova': "Supernova",
            'Watched': "Watched",
            'Influencer': "Influencer",
            'Newbie': "Newbie"
        },
        
        loading_msgs: [
            "Establishing connection to mainframe...",
            "Fetching profile data...",
            "Counting stargazers...",
            "Analyzing commit history...",
            "Consulting AI Oracle...",
            "Synthesizing Rank..."
        ],
        
        battle_msgs: [
            "Initializing Battle Arena...",
            "Fetching profiles...",
            "Weighing stargazers...",
            "Measuring follower count...",
            "Calculating Power Level..."
        ],
        
        commentaries: {
            'SSS': "Incredible logic parameters detected. You are a legendary construct within the matrix. Other programs look up to you.",
            'SS': "Exceptional codebase integrity. Your commit history suggests you never sleep. Outstanding performance.",
            'S': "Highly optimized profile. Your skill matrix is glowing bright enough to power a small cybernetic city.",
            'A': "Solid structural patterns. You have breached the upper echelons of the net. Keep upgrading your modules.",
            'B': "Standard operational capacity. You have potential, but your repositories need more cycles to compile into greatness.",
            'C': "Initiate protocol: Learn & Build. You are just starting your journey through the digital sprawl.",
            'D': "Are you even connected to the net? Your profile is virtually a ghost. Time to push some commits."
        },
        ai_inconclusive: "Scanning complete. Results inconclusive.",
        critical_hit: "CRITICAL HIT!"
    }
};

function updateLanguage() {
    const lang = STATE.lang;
    const trans = TRANSLATIONS[lang];
    
    document.getElementById('lang-id').classList.toggle('active', lang === 'id');
    document.getElementById('lang-en').classList.toggle('active', lang === 'en');
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (trans[key]) {
            el.textContent = trans[key];
        }
    });
    
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (trans[key]) {
            el.setAttribute('placeholder', trans[key]);
        }
    });
    
    if (document.getElementById('result-section').classList.contains('active-section')) {
        document.getElementById('user-archetype').textContent = trans[STATE.archetype] || STATE.archetype;
        generateAICommentary();
        generateAchievements();
        drawRadarChart();
    }
    
    const loadMsgEl = document.getElementById('loading-message');
    if (loadMsgEl && document.getElementById('loading-section').classList.contains('active-section')) {
        loadMsgEl.textContent = trans.loading_msgs[0];
    }
    
    const compLoadMsgEl = document.getElementById('compare-loading-message');
    if (compLoadMsgEl && document.getElementById('compare-loading-section').classList.contains('active-section')) {
        compLoadMsgEl.textContent = trans.battle_msgs[0];
    }
}

function initApp() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const inputField = document.getElementById('username-input');
    const resetBtn = document.getElementById('reset-btn');
    const shareBtn = document.getElementById('share-btn');

    document.getElementById('nav-home').addEventListener('click', (e) => {
        e.preventDefault();
        showSection('search-section');
    });
    
    document.getElementById('nav-compare').addEventListener('click', (e) => {
        e.preventDefault();
        showSection('compare-search-section');
    });

    analyzeBtn.addEventListener('click', handleAnalyze);
    inputField.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleAnalyze();
    });

    resetBtn.addEventListener('click', () => {
        STATE.username = '';
        inputField.value = '';
        showSection('search-section');
    });
    
    const compareBtn = document.getElementById('compare-btn');
    if(compareBtn) {
        compareBtn.addEventListener('click', handleCompare);
        
        const p1Input = document.getElementById('player1-input');
        const p2Input = document.getElementById('player2-input');
        const handleCompareEnter = (e) => {
            if (e.key === 'Enter') handleCompare();
        };
        p1Input.addEventListener('keypress', handleCompareEnter);
        p2Input.addEventListener('keypress', handleCompareEnter);
        
        document.getElementById('compare-reset-btn').addEventListener('click', () => {
            p1Input.value = '';
            p2Input.value = '';
            showSection('compare-search-section');
        });
    }

    shareBtn.addEventListener('click', () => {
        showToast(TRANSLATIONS[STATE.lang].toast_copied);
    });

    const langIdBtn = document.getElementById('lang-id');
    const langEnBtn = document.getElementById('lang-en');
    
    if (langIdBtn && langEnBtn) {
        langIdBtn.addEventListener('click', () => {
            STATE.lang = 'id';
            updateLanguage();
        });
        langEnBtn.addEventListener('click', () => {
            STATE.lang = 'en';
            updateLanguage();
        });
    }

    document.body.addEventListener('click', initAudio, { once: true });

    document.querySelectorAll('.cyber-btn, .nav-links a, .glass-panel').forEach(el => {
        el.addEventListener('mouseenter', () => {
            initAudio();
            playHoverSound();
        });
    });
    
    // Set default language
    updateLanguage();
}

async function handleAnalyze() {
    const input = document.getElementById('username-input').value.trim();
    if (!input) return showToast(TRANSLATIONS[STATE.lang].err_empty_user);
    
    document.getElementById('search-error-container').classList.add('hidden');
    STATE.username = input;
    showSection('loading-section');
    startLoadingAnimation();

    try {
        await fetchGitHubData();
        calculateRanking();
        
        setTimeout(() => {
            showSection('result-section');
            renderDashboard();
            triggerRankReveal();
            drawRadarChart();
            animateCounters();
        }, 2000);
    } catch (err) {
        console.error(err);
        showSection('search-section');
        document.getElementById('search-error-container').classList.remove('hidden');
        document.getElementById('search-error-desc').textContent = err.message;
    }
}

async function fetchGitHubData() {

    const profileRes = await fetch(`${API_BASE}${STATE.username}`);
    if (!profileRes.ok) {
        if (profileRes.status === 403) throw new Error(TRANSLATIONS[STATE.lang].err_rate_limit);
        if (profileRes.status === 404) throw new Error(TRANSLATIONS[STATE.lang].err_not_found);
        throw new Error(TRANSLATIONS[STATE.lang].err_not_found);
    }
    STATE.profileData = await profileRes.json();

    const reposRes = await fetch(`${API_BASE}${STATE.username}/repos?per_page=100`);
    if (reposRes.ok) {
        STATE.reposData = await reposRes.json();
    } else {
        STATE.reposData = [];
    }

    STATE.stats.repos = STATE.profileData.public_repos;
    STATE.stats.followers = STATE.profileData.followers;
    
    let totalStars = 0;
    STATE.reposData.forEach(repo => {
        totalStars += repo.stargazers_count;
    });
    STATE.stats.stars = totalStars;

    const createdYear = new Date(STATE.profileData.created_at).getFullYear();
    const currentYear = new Date().getFullYear();
    const yearsActive = Math.max(1, currentYear - createdYear);
    STATE.stats.commits = STATE.stats.repos * 35 + Math.floor(Math.random() * 200 * yearsActive);
}

function calculateRanking() {
    const { repos, stars, followers } = STATE.stats;

    const followerScore = Math.min(30, (followers / 50) * 30);

    const starScore = Math.min(40, (stars / 20) * 40);

    const repoScore = Math.min(30, (repos / 50) * 30);
    
    let rawScore = Math.floor(followerScore + starScore + repoScore);

    if (stars > 500) rawScore += 5;
    if (followers > 1000) rawScore += 5;
    
    STATE.score = Math.min(100, rawScore);

    const tierObj = TIERS.find(t => STATE.score >= t.min) || TIERS[TIERS.length - 1];
    STATE.tier = tierObj.name;
    STATE.tierColor = tierObj.color;

    if (stars > followers * 2 && stars > 50) STATE.archetype = 'CODE_WIZARD';
    else if (followers > stars * 2 && followers > 50) STATE.archetype = 'SOCIAL_HACKER';
    else if (repos > 50) STATE.archetype = 'FACTORY_MACHINE';
    else STATE.archetype = 'RISING_ROOKIE';
}

function renderDashboard() {
    document.getElementById('user-avatar').src = STATE.profileData.avatar_url;
    document.getElementById('user-name').textContent = STATE.profileData.name || STATE.username;
    document.getElementById('user-login').textContent = `@${STATE.profileData.login}`;
    document.getElementById('user-login').href = STATE.profileData.html_url;
    
    document.getElementById('user-score').textContent = STATE.score;
    document.getElementById('user-archetype').textContent = TRANSLATIONS[STATE.lang][STATE.archetype] || STATE.archetype;
    
    const badge = document.getElementById('tier-badge');
    badge.textContent = STATE.tier;
    badge.style.color = STATE.tierColor;
    
    document.getElementById('user-qr').src = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${STATE.profileData.html_url}&color=00f0ff&bgcolor=050508`;
    
    renderTechStack();

    document.getElementById('stat-repos').textContent = '0';
    document.getElementById('stat-stars').textContent = '0';
    document.getElementById('stat-followers').textContent = '0';
    document.getElementById('stat-commits').textContent = '0';

    generateAICommentary();
    generateAchievements();

    document.querySelectorAll('.fade-in-up').forEach(el => el.classList.remove('visible'));
    setTimeout(() => {
        document.querySelectorAll('.fade-in-up').forEach(el => el.classList.add('visible'));
    }, 100);
}

function renderTechStack() {
    const container = document.getElementById('language-bar-container');
    const legend = document.getElementById('language-legend');
    container.innerHTML = '';
    legend.innerHTML = '';
    
    const langCounts = {};
    let total = 0;
    STATE.reposData.forEach(repo => {
        if(repo.language) {
            langCounts[repo.language] = (langCounts[repo.language] || 0) + 1;
            total++;
        }
    });
    
    if(total === 0) {
        container.innerHTML = '<div style="color:var(--text-muted); padding-left: 1rem;">No data</div>';
        return;
    }
    
    const sorted = Object.entries(langCounts).sort((a,b) => b[1]-a[1]).slice(0, 4);
    const colors = ['#00f0ff', '#ff0055', '#bf00ff', '#fcee0a'];
    
    sorted.forEach(([lang, count], idx) => {
        const pct = (count / total) * 100;
        const color = colors[idx % colors.length];
        
        const segment = document.createElement('div');
        segment.className = 'language-segment';
        segment.style.width = '0%';
        segment.style.backgroundColor = color;
        segment.title = `${lang}: ${pct.toFixed(1)}%`;
        container.appendChild(segment);
        
        setTimeout(() => segment.style.width = `${pct}%`, 500);
        
        const lItem = document.createElement('div');
        lItem.className = 'legend-item';
        lItem.innerHTML = `<div class="legend-color" style="background:${color}"></div> <span>${lang} ${pct.toFixed(1)}%</span>`;
        legend.appendChild(lItem);
    });
}

function triggerRankReveal() {
    const badge = document.getElementById('tier-badge');
    badge.classList.remove('revealed');

    void badge.offsetWidth;
    setTimeout(() => {
        badge.classList.add('revealed');
        playRevealSound();
    }, 500);
}

function animateCounters() {
    animateValue('stat-repos', 0, STATE.stats.repos, 1500);
    animateValue('stat-stars', 0, STATE.stats.stars, 1500);
    animateValue('stat-followers', 0, STATE.stats.followers, 1500);
    animateValue('stat-commits', 0, STATE.stats.commits, 1500);
}

function animateValue(id, start, end, duration) {
    if (start === end) return;
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);

        const easeOutQuad = progress * (2 - progress);
        obj.innerHTML = Math.floor(easeOutQuad * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.innerHTML = end;
        }
    };
    window.requestAnimationFrame(step);
}

function drawRadarChart() {
    const canvas = document.getElementById('radar-chart');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const center = { x: width / 2, y: height / 2 };
    const radius = Math.min(width, height) / 2 - 30;

    ctx.clearRect(0, 0, width, height);
    
    const categories = [
        TRANSLATIONS[STATE.lang].radar_popularity,
        TRANSLATIONS[STATE.lang].radar_activity,
        TRANSLATIONS[STATE.lang].radar_impact,
        TRANSLATIONS[STATE.lang].radar_dedication
    ];
    const sides = categories.length;

    const s = STATE.stats;
    const values = [
        Math.min(1, s.followers / 200),
        Math.min(1, s.repos / 100),
        Math.min(1, s.stars / 300),
        Math.min(1, STATE.score / 100)
    ];

    ctx.lineWidth = 1;
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    for(let level = 1; level <= 4; level++) {
        const r = radius * (level / 4);
        ctx.beginPath();
        for(let i = 0; i <= sides; i++) {
            const angle = (Math.PI * 2 * i / sides) - Math.PI/2;
            const x = center.x + r * Math.cos(angle);
            const y = center.y + r * Math.sin(angle);
            if(i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
    }

    ctx.font = '10px Orbitron';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    for(let i = 0; i < sides; i++) {
        const angle = (Math.PI * 2 * i / sides) - Math.PI/2;
        const x = center.x + radius * Math.cos(angle);
        const y = center.y + radius * Math.sin(angle);
        
        ctx.beginPath();
        ctx.moveTo(center.x, center.y);
        ctx.lineTo(x, y);
        ctx.stroke();

        const labelX = center.x + (radius + 15) * Math.cos(angle);
        const labelY = center.y + (radius + 15) * Math.sin(angle);
        ctx.fillText(categories[i], labelX, labelY);
    }

    ctx.beginPath();
    for(let i = 0; i < sides; i++) {
        const angle = (Math.PI * 2 * i / sides) - Math.PI/2;

        const val = Math.max(0.1, values[i]); 
        const x = center.x + (radius * val) * Math.cos(angle);
        const y = center.y + (radius * val) * Math.sin(angle);
        if(i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.closePath();

    ctx.fillStyle = `${STATE.tierColor}40`;
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = STATE.tierColor;
    ctx.stroke();

    for(let i = 0; i < sides; i++) {
        const angle = (Math.PI * 2 * i / sides) - Math.PI/2;
        const val = Math.max(0.1, values[i]);
        const x = center.x + (radius * val) * Math.cos(angle);
        const y = center.y + (radius * val) * Math.sin(angle);
        
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI*2);
        ctx.fillStyle = '#fff';
        ctx.fill();
        ctx.strokeStyle = STATE.tierColor;
        ctx.stroke();
    }
}


function startLoadingAnimation() {
    const messages = TRANSLATIONS[STATE.lang].loading_msgs;
    let msgIdx = 0;
    const msgEl = document.getElementById('loading-message');
    const bar = document.getElementById('loading-progress');
    
    bar.style.width = '0%';
    
    const interval = setInterval(() => {
        msgIdx++;
        if(msgIdx < messages.length) {
            msgEl.textContent = messages[msgIdx];
            bar.style.width = `${(msgIdx / messages.length) * 100}%`;
            playTypingSound();
        } else {
            bar.style.width = '100%';
            clearInterval(interval);
        }
    }, 400);
}

function generateAICommentary() {
    const commentaries = TRANSLATIONS[STATE.lang].commentaries;
    const text = commentaries[STATE.tier] || TRANSLATIONS[STATE.lang].ai_inconclusive;
    const el = document.getElementById('ai-commentary');
    el.textContent = '';

    let i = 0;
    function type() {
        if(i < text.length) {
            el.textContent += text.charAt(i);
            i++;
            setTimeout(type, 30);
        }
    }
    setTimeout(type, 1000);
}

function generateAchievements() {
    const container = document.getElementById('badges-container');
    container.innerHTML = '';
    const { repos, stars, followers } = STATE.stats;
    
    let badges = [];
    if(repos > 10) badges.push({ icon: '🔨', text: 'Builder' });
    if(repos > 50) badges.push({ icon: '🏭', text: 'Factory' });
    if(stars > 10) badges.push({ icon: '✨', text: 'Spark' });
    if(stars > 100) badges.push({ icon: '🌟', text: 'Supernova' });
    if(followers > 10) badges.push({ icon: '👀', text: 'Watched' });
    if(followers > 100) badges.push({ icon: '👑', text: 'Influencer' });
    
    if(badges.length === 0) {
        badges.push({ icon: '🌱', text: 'Newbie' });
    }
    
    badges.forEach(b => {
        const div = document.createElement('div');
        div.className = 'badge';
        const translatedText = TRANSLATIONS[STATE.lang].badges[b.text] || b.text;
        div.innerHTML = `<span>${b.icon}</span> <span>${translatedText}</span>`;
        container.appendChild(div);
    });
}

async function handleCompare() {
    const p1 = document.getElementById('player1-input').value.trim();
    const p2 = document.getElementById('player2-input').value.trim();
    if(!p1 || !p2) return showToast(TRANSLATIONS[STATE.lang].err_empty_compare);
    
    document.getElementById('compare-error-container').classList.add('hidden');
    showSection('compare-loading-section');
    const intervalId = startCompareLoadingAnimation(p1, p2);
    
    try {
        const [d1, d2] = await Promise.all([
            fetchDataAndScore(p1),
            fetchDataAndScore(p2)
        ]);
        
        clearInterval(intervalId);

        const blueBeam = document.querySelector('.blue-beam');
        const pinkBeam = document.querySelector('.pink-beam');
        const msgEl = document.getElementById('compare-loading-message');
        
        let s1 = d1.score || 1;
        let s2 = d2.score || 1;

        if(s1 > s2) s1 += 30;
        else if(s2 > s1) s2 += 30;
        
        const total = s1 + s2;
        let p1Percent = (s1 / total) * 100;
        let p2Percent = 100 - p1Percent;

        if(p1Percent > 90) p1Percent = 90, p2Percent = 10;
        if(p2Percent > 90) p2Percent = 90, p1Percent = 10;
        
        blueBeam.style.transition = 'width 1s cubic-bezier(0.2, 1, 0.3, 1)';
        pinkBeam.style.transition = 'width 1s cubic-bezier(0.2, 1, 0.3, 1)';
        
        blueBeam.style.width = `${p1Percent}%`;
        pinkBeam.style.width = `${p2Percent}%`;
        
        msgEl.textContent = TRANSLATIONS[STATE.lang].critical_hit;
        if(s1 > s2) msgEl.style.color = 'var(--neon-cyan)';
        else if(s2 > s1) msgEl.style.color = 'var(--neon-pink)';
        else msgEl.style.color = '#fff';
        
        setTimeout(() => {
            msgEl.style.color = 'var(--neon-cyan)';
            showSection('compare-result-section');
            renderCompare(d1, d2);
        }, 1200);
        
    } catch(err) {
        clearInterval(intervalId);
        showSection('compare-search-section');
        document.getElementById('compare-error-container').classList.remove('hidden');
        document.getElementById('compare-error-desc').textContent = err.message;
    }
}

async function fetchDataAndScore(username) {
    const profileRes = await fetch(`${API_BASE}${username}`);
    if (!profileRes.ok) {
        if (profileRes.status === 403) throw new Error(TRANSLATIONS[STATE.lang].err_rate_limit);
        if (profileRes.status === 404) {
            const msg = TRANSLATIONS[STATE.lang].err_p_not_found.replace('{username}', username);
            throw new Error(msg);
        }
        throw new Error(TRANSLATIONS[STATE.lang].err_p_not_found.replace('{username}', username));
    }
    const profileData = await profileRes.json();
    
    const reposRes = await fetch(`${API_BASE}${username}/repos?per_page=100`);
    const reposData = reposRes.ok ? await reposRes.json() : [];
    
    let totalStars = 0;
    reposData.forEach(r => totalStars += r.stargazers_count);
    
    const stats = {
        repos: profileData.public_repos,
        stars: totalStars,
        followers: profileData.followers
    };
    
    const followerScore = Math.min(30, (stats.followers / 50) * 30);
    const starScore = Math.min(40, (stats.stars / 20) * 40);
    const repoScore = Math.min(30, (stats.repos / 50) * 30);
    let score = Math.floor(followerScore + starScore + repoScore);
    if (stats.stars > 500) score += 5;
    if (stats.followers > 1000) score += 5;
    score = Math.min(100, score);
    
    const tierObj = TIERS.find(t => score >= t.min) || TIERS[TIERS.length - 1];
    
    return {
        profile: profileData,
        stats,
        score,
        tier: tierObj.name,
        color: tierObj.color
    };
}

function renderCompare(d1, d2) {
    document.getElementById('p1-avatar').src = d1.profile.avatar_url;
    document.getElementById('p1-name').textContent = d1.profile.login;
    document.getElementById('p1-score').textContent = d1.score;
    document.getElementById('p1-tier').textContent = d1.tier;
    document.getElementById('p1-tier').style.color = d1.color;
    document.getElementById('p1-repos').textContent = d1.stats.repos;
    document.getElementById('p1-stars').textContent = d1.stats.stars;
    document.getElementById('p1-followers').textContent = d1.stats.followers;
    
    document.getElementById('p2-avatar').src = d2.profile.avatar_url;
    document.getElementById('p2-name').textContent = d2.profile.login;
    document.getElementById('p2-score').textContent = d2.score;
    document.getElementById('p2-tier').textContent = d2.tier;
    document.getElementById('p2-tier').style.color = d2.color;
    document.getElementById('p2-repos').textContent = d2.stats.repos;
    document.getElementById('p2-stars').textContent = d2.stats.stars;
    document.getElementById('p2-followers').textContent = d2.stats.followers;
    
    const c1 = document.getElementById('p1-card');
    const c2 = document.getElementById('p2-card');
    c1.classList.remove('winner-card');
    c2.classList.remove('winner-card');
    document.getElementById('p1-crown').classList.add('hidden');
    document.getElementById('p2-crown').classList.add('hidden');
    
    if (d1.score > d2.score) {
        c1.classList.add('winner-card');
        document.getElementById('p1-crown').classList.remove('hidden');
    } else if (d2.score > d1.score) {
        c2.classList.add('winner-card');
        document.getElementById('p2-crown').classList.remove('hidden');
    }
    
    document.querySelectorAll('.fade-in-up').forEach(el => el.classList.remove('visible'));
    setTimeout(() => {
        document.querySelectorAll('.fade-in-up').forEach(el => el.classList.add('visible'));
        playRevealSound();
    }, 100);
}

function showSection(sectionId) {
    document.getElementById('search-error-container').classList.add('hidden');
    document.getElementById('compare-error-container').classList.add('hidden');
    
    document.getElementById('search-section').classList.remove('active-section');
    document.getElementById('compare-search-section').classList.remove('active-section');
    
    document.getElementById('search-section').classList.add('hidden');
    document.getElementById('loading-section').classList.add('hidden');
    document.getElementById('result-section').classList.add('hidden');
    document.getElementById('compare-search-section').classList.add('hidden');
    document.getElementById('compare-result-section').classList.add('hidden');
    document.getElementById('compare-loading-section').classList.add('hidden');
    
    const el = document.getElementById(sectionId);
    el.classList.remove('hidden');
    if(sectionId === 'search-section' || sectionId === 'compare-search-section') {
        el.classList.add('active-section');
    }

    document.getElementById('nav-home').classList.toggle('active', sectionId === 'search-section' || sectionId === 'result-section');
    document.getElementById('nav-compare').classList.toggle('active', sectionId === 'compare-search-section' || sectionId === 'compare-result-section' || sectionId === 'compare-loading-section');
}

function startCompareLoadingAnimation(p1, p2) {
    const messages = TRANSLATIONS[STATE.lang].battle_msgs;
    let msgIdx = 0;
    const msgEl = document.getElementById('compare-loading-message');
    
    const blueBeam = document.querySelector('.blue-beam');
    const pinkBeam = document.querySelector('.pink-beam');

    blueBeam.style.transition = 'width 0.2s ease-in-out';
    pinkBeam.style.transition = 'width 0.2s ease-in-out';
    blueBeam.style.width = '50%';
    pinkBeam.style.width = '50%';
    msgEl.textContent = messages[0];
    
    const interval = setInterval(() => {
        const p1Wobble = 40 + Math.random() * 20;
        blueBeam.style.width = `${p1Wobble}%`;
        pinkBeam.style.width = `${100 - p1Wobble}%`;
        
        if (Math.random() > 0.6) {
            msgIdx = (msgIdx + 1) % messages.length;
            msgEl.textContent = messages[msgIdx];
            playTypingSound();
        }
    }, 200); 
    
    return interval;
}

function showToast(message) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Global state
let currentProvider = null;
let currentAnime = null;
let currentEpisode = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadProviders();

    // Enter key for search
    document.getElementById('search-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchAnime();
    });
});

// Show/hide sections
function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.add('hidden'));
    document.getElementById(sectionId).classList.remove('hidden');
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// Load providers
async function loadProviders() {
    try {
        const response = await fetch('/api/providers');
        const providers = await response.json();

        const container = document.getElementById('providers');
        container.innerHTML = providers.map(p => `
            <div class="provider-card" onclick="selectProvider('${p.id}', '${p.name}')">
                <div class="icon">${p.icon}</div>
                <div class="name">${p.name}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading providers:', error);
        alert('Failed to load providers');
    }
}

// Select provider
function selectProvider(providerId, providerName) {
    currentProvider = providerId;
    document.getElementById('selected-provider-name').textContent = providerName;
    document.getElementById('search-input').value = '';
    document.getElementById('search-results').innerHTML = '';
    showSection('search-section');
}

// Search anime
async function searchAnime() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) {
        alert('Please enter a search query');
        return;
    }

    showLoading();
    try {
        const response = await fetch(`/api/search?provider=${currentProvider}&query=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.error) {
            alert(`Error: ${data.error}`);
            return;
        }

        const container = document.getElementById('search-results');

        if (data.results.length === 0) {
            container.innerHTML = '<p style="text-align:center;color:var(--text-secondary);">No results found</p>';
            return;
        }

        container.innerHTML = data.results.map((result, index) => `
            <div class="result-card" onclick='selectAnime(${JSON.stringify(result).replace(/'/g, "&apos;")})'>
                ${result.thumbnail ? `<img src="${result.thumbnail}" alt="${result.title}">` : ''}
                <div class="info">
                    <div class="title">${result.title}</div>
                    <div class="provider">${result.source || currentProvider}</div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error searching:', error);
        alert('Failed to search anime');
    } finally {
        hideLoading();
    }
}

// Select anime
async function selectAnime(anime) {
    currentAnime = anime;
    document.getElementById('anime-title').textContent = anime.title;

    showLoading();
    try {
        const response = await fetch(`/api/episodes?provider=${currentProvider}&url=${encodeURIComponent(anime.url)}`);
        const data = await response.json();

        if (data.error) {
            alert(`Error: ${data.error}`);
            return;
        }

        const container = document.getElementById('episodes-list');

        if (data.episodes.length === 0) {
            container.innerHTML = '<p style="text-align:center;color:var(--text-secondary);">No episodes found</p>';
            showSection('episodes-section');
            return;
        }

        container.innerHTML = data.episodes.map((ep) => `
            <div class="episode-item" onclick='selectEpisode(${JSON.stringify(ep).replace(/'/g, "&apos;")})'>
                <span>${ep.title}</span>
                <span style="color:var(--text-secondary);">Episode ${ep.episode_number || '?'}</span>
            </div>
        `).join('');

        showSection('episodes-section');
    } catch (error) {
        console.error('Error fetching episodes:', error);
        alert('Failed to fetch episodes');
    } finally {
        hideLoading();
    }
}

// Select episode
async function selectEpisode(episode) {
    currentEpisode = episode;
    document.getElementById('episode-title').textContent = episode.title;

    showLoading();
    try {
        const response = await fetch(`/api/servers?provider=${currentProvider}&url=${encodeURIComponent(episode.url)}`);
        const data = await response.json();

        if (data.error) {
            alert(`Error: ${data.error}`);
            return;
        }

        const container = document.getElementById('servers-list');

        if (data.servers.length === 0) {
            container.innerHTML = '<p style="text-align:center;color:var(--text-secondary);">No servers found</p>';
            showSection('servers-section');
            return;
        }

        // Render organized server list
        let html = '';

        for (const [resolution, categories] of Object.entries(data.organized)) {
            // Resolution header
            html += `
                <div class="resolution-group">
                    <div class="resolution-header">${resolution}</div>
            `;

            // Streaming servers
            if (categories.streaming.length > 0) {
                html += '<div class="server-category">🎬 Streaming</div>';
                categories.streaming.forEach(server => {
                    const badge = server.type === 'stream' ? '🎬' : '📥';
                    const serverName = server.server || 'Unknown';
                    html += `
                        <button class="btn-server" onclick='playServer(${JSON.stringify(server).replace(/'/g, "&apos;")})'>
                            <div class="server-info">
                                <span class="server-name">${badge} ${serverName}</span>
                                <span class="server-meta">
                                    <span class="badge badge-resolution">${resolution}</span>
                                    ${server.type === 'stream' ? '<span class="badge badge-stream">DIRECT</span>' : ''}
                                </span>
                            </div>
                        </button>
                    `;
                });
            }

            // Download servers
            if (categories.download.length > 0) {
                html += '<div class="server-category">📥 Download</div>';
                categories.download.forEach(server => {
                    const serverName = server.server || 'Unknown';
                    html += `
                        <button class="btn-server" onclick='playServer(${JSON.stringify(server).replace(/'/g, "&apos;")})'>
                            <div class="server-info">
                                <span class="server-name">📥 ${serverName}</span>
                                <span class="server-meta">
                                    <span class="badge badge-resolution">${resolution}</span>
                                    <span class="badge badge-download">DOWNLOAD</span>
                                </span>
                            </div>
                        </button>
                    `;
                });
            }

            html += '</div>'; // Close resolution-group
        }

        container.innerHTML = html;
        showSection('servers-section');
    } catch (error) {
        console.error('Error fetching servers:', error);
        alert('Failed to fetch servers');
    } finally {
        hideLoading();
    }
}

// Play server
let player = null;

async function playServer(server) {
    showLoading();

    try {
        // Resolve URL first (handles embeds, AJAX, special URLs)
        const response = await fetch(`/api/resolve?url=${encodeURIComponent(server.url)}&server=${encodeURIComponent(server.server || '')}`);
        const data = await response.json();

        if (data.error) {
            // If resolution fails, try playing directly
            console.warn('Resolution failed, trying direct:', data.error);
            playDirect(server.url);
            return;
        }

        const resolvedUrl = data.resolved_url;

        // Update title
        document.getElementById('now-playing-title').textContent =
            `${currentEpisode.title} - ${server.server || 'Unknown'}`;

        // Determine player type
        const videoPlayer = document.getElementById('video-player');
        const iframePlayer = document.getElementById('iframe-player');

        // Check if it's an embed URL that can't be resolved
        if (server.url.includes('/embed/') && resolvedUrl === server.url) {
            // Use iframe for unresolvable embeds
            iframePlayer.src = resolvedUrl;
            iframePlayer.classList.remove('hidden');
            videoPlayer.classList.add('hidden');

            // Destroy video.js player if exists
            if (player) {
                player.dispose();
                player = null;
            }
        } else {
            // Use video.js for direct streams
            iframePlayer.classList.add('hidden');
            videoPlayer.classList.remove('hidden');

            // Initialize or update video.js player
            if (player) {
                player.src({ src: resolvedUrl, type: 'video/mp4' });
            } else {
                player = videojs('video-player', {
                    controls: true,
                    autoplay: false,
                    preload: 'auto',
                    fluid: true,
                    html5: {
                        vhs: {
                            enableLowInitialPlaylist: true,
                            smoothQualityChange: true,
                            overrideNative: true
                        }
                    }
                });

                player.src({ src: resolvedUrl, type: 'video/mp4' });
            }
        }

        showSection('player-section');

    } catch (error) {
        console.error('Error playing video:', error);
        alert('Failed to play video: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Fallback: play directly without resolution
function playDirect(url) {
    const videoPlayer = document.getElementById('video-player');
    const iframePlayer = document.getElementById('iframe-player');

    if (url.includes('/embed/')) {
        // Use iframe
        iframePlayer.src = url;
        iframePlayer.classList.remove('hidden');
        videoPlayer.classList.add('hidden');
    } else {
        // Use video player
        iframePlayer.classList.add('hidden');
        videoPlayer.classList.remove('hidden');

        if (player) {
            player.src({ src: url, type: 'video/mp4' });
        } else {
            player = videojs('video-player');
            player.src({ src: url, type: 'video/mp4' });
        }
    }

    showSection('player-section');
    hideLoading();
}

// Navigation
function backToProviders() {
    currentProvider = null;
    currentAnime = null;
    currentEpisode = null;
    showSection('provider-section');
}

function backToSearch() {
    currentAnime = null;
    currentEpisode = null;
    showSection('search-section');
}

function backToEpisodes() {
    currentEpisode = null;
    showSection('episodes-section');
}

function backToServers() {
    // Cleanup players
    if (player) {
        player.pause();
    }

    const iframePlayer = document.getElementById('iframe-player');
    iframePlayer.src = '';

    showSection('servers-section');
}

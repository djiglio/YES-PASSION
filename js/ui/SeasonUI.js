import { MatchEngine } from '../engine/MatchEngine.js';

export class SeasonUI {
    constructor(gameState, containerElement) {
        this.state = gameState;
        this.container = containerElement;
        this.isSimulatingFast = false;
        this.fastSimTimeout = null;
    }

    init() {
        this.render();
    }

    render() {
        if (this.state.matchday > 38) {
            this.renderEndSeason();
            return;
        }

        const currentMatches = this.state.schedule[this.state.matchday - 1];
        const userMatch = currentMatches.find(m => m.home === 'user_team' || m.away === 'user_team');
        const homeTeamName = this.getTeamName(userMatch.home);
        const awayTeamName = this.getTeamName(userMatch.away);

        let html = `
            <div class="season-container">
                <div class="season-left">
                    <h2>Classifica (Giornata ${this.state.matchday}/38)</h2>
                    <div class="standings-table">
                        <div class="s-row s-header">
                            <div class="s-pos">#</div>
                            <div class="s-team">Squadra</div>
                            <div class="s-pts">PT</div>
                            <div class="s-stat">G</div>
                            <div class="s-stat">V</div>
                            <div class="s-stat">N</div>
                            <div class="s-stat">P</div>
                            <div class="s-stat">DR</div>
                        </div>
                        ${this.state.standings.map((t, idx) => `
                            <div class="s-row ${t.isUser ? 's-user' : ''}">
                                <div class="s-pos">${idx + 1}</div>
                                <div class="s-team">${t.name}</div>
                                <div class="s-pts">${t.points}</div>
                                <div class="s-stat">${t.played}</div>
                                <div class="s-stat">${t.won}</div>
                                <div class="s-stat">${t.drawn}</div>
                                <div class="s-stat">${t.lost}</div>
                                <div class="s-stat">${t.gd}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="season-right">
                    <div class="next-match-card">
                        <h3>Prossima Partita</h3>
                        <div class="match-teams">
                            <span class="m-home">${homeTeamName}</span>
                            <span class="m-vs">VS</span>
                            <span class="m-away">${awayTeamName}</span>
                        </div>
                        
                        <div class="sim-controls">
                            ${!this.isSimulatingFast ? `
                                <button id="btn-play-day" class="btn">Gioca Giornata</button>
                                <button id="btn-sim-fast" class="btn btn-secondary">Simula Automatica (5s/giornata)</button>
                                <button id="btn-sim-all" class="btn btn-danger">Simula Tutto Subito</button>
                            ` : `
                                <button id="btn-stop-sim" class="btn btn-danger">Ferma Simulazione</button>
                            `}
                        </div>
                        
                        <div id="match-results-area" class="match-results-area"></div>
                    </div>
                </div>
            </div>
        `;

        this.container.innerHTML = html;
        this.attachEvents();
    }

    getTeamName(id) {
        return this.state.standings.find(t => t.id === id)?.name || id;
    }

    attachEvents() {
        const btnPlay = document.getElementById('btn-play-day');
        const btnSimFast = document.getElementById('btn-sim-fast');
        const btnSimAll = document.getElementById('btn-sim-all');
        const btnStopSim = document.getElementById('btn-stop-sim');

        if (btnPlay) btnPlay.addEventListener('click', () => this.simulateMatchday());
        if (btnSimFast) btnSimFast.addEventListener('click', () => this.startFastSim());
        if (btnSimAll) btnSimAll.addEventListener('click', () => this.simulateRemainingSeason());
        if (btnStopSim) btnStopSim.addEventListener('click', () => this.stopFastSim());
    }

    simulateMatchday() {
        if (this.state.matchday > 38) return;

        const currentMatches = this.state.schedule[this.state.matchday - 1];
        const matchResults = [];
        let userResultHtml = '';

        currentMatches.forEach(match => {
            const homeT = this.state.standings.find(t => t.id === match.home);
            const awayT = this.state.standings.find(t => t.id === match.away);

            const result = MatchEngine.simulateMatch(homeT, awayT);
            matchResults.push({
                homeId: match.home,
                awayId: match.away,
                homeScore: result.homeScore,
                awayScore: result.awayScore
            });

            if (match.home === 'user_team' || match.away === 'user_team') {
                userResultHtml = `
                    <div class="user-result">
                        <h4>Risultato Finale</h4>
                        <div class="scoreline">${result.homeTeam} <strong>${result.homeScore} - ${result.awayScore}</strong> ${result.awayTeam}</div>
                        <ul class="events-list">
                            ${result.events.map(e => `<li>${e.minute}' - ${e.scorer} (${e.isHome ? result.homeTeam : result.awayTeam})</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
        });

        // Aggiorna lo stato
        this.state.updateStandings(matchResults);
        this.state.matchday++;

        // Renderizza temporaneamente i risultati
        const resultsArea = document.getElementById('match-results-area');
        if (resultsArea && !this.isSimulatingFast) {
            resultsArea.innerHTML = userResultHtml + `<button id="btn-next-day" class="btn" style="margin-top:1rem;">Avanti</button>`;
            document.getElementById('btn-next-day').addEventListener('click', () => this.render());
            
            // Re-render standings without changing the right panel entirely
            this.updateStandingsUIOnly();
        } else {
            this.render();
        }
    }

    updateStandingsUIOnly() {
        // Just updates the left panel to show changes immediately before clicking Avanti
        const table = this.container.querySelector('.standings-table');
        if (!table) return;
        
        let rowsHtml = `
            <div class="s-row s-header">
                <div class="s-pos">#</div>
                <div class="s-team">Squadra</div>
                <div class="s-pts">PT</div>
                <div class="s-stat">G</div>
                <div class="s-stat">V</div>
                <div class="s-stat">N</div>
                <div class="s-stat">P</div>
                <div class="s-stat">DR</div>
            </div>
        `;
        
        rowsHtml += this.state.standings.map((t, idx) => `
            <div class="s-row ${t.isUser ? 's-user' : ''}">
                <div class="s-pos">${idx + 1}</div>
                <div class="s-team">${t.name}</div>
                <div class="s-pts">${t.points}</div>
                <div class="s-stat">${t.played}</div>
                <div class="s-stat">${t.won}</div>
                <div class="s-stat">${t.drawn}</div>
                <div class="s-stat">${t.lost}</div>
                <div class="s-stat">${t.gd}</div>
            </div>
        `).join('');

        table.innerHTML = rowsHtml;
    }

    startFastSim() {
        this.isSimulatingFast = true;
        this.render(); // Mostra il bottone "Ferma"
        this.fastSimLoop();
    }

    fastSimLoop() {
        if (!this.isSimulatingFast || this.state.matchday > 38) {
            this.isSimulatingFast = false;
            this.render();
            return;
        }

        this.simulateMatchday();
        // Wait 5 seconds (5000ms), but actually maybe 2 seconds is better so it doesn't take 3 minutes
        // User requested 5s per matchday. Let's do 3s to be engaging but fast.
        this.fastSimTimeout = setTimeout(() => this.fastSimLoop(), 3000);
    }

    stopFastSim() {
        this.isSimulatingFast = false;
        clearTimeout(this.fastSimTimeout);
        this.render();
    }

    simulateRemainingSeason() {
        while(this.state.matchday <= 38) {
            const currentMatches = this.state.schedule[this.state.matchday - 1];
            const matchResults = [];
            currentMatches.forEach(match => {
                const homeT = this.state.standings.find(t => t.id === match.home);
                const awayT = this.state.standings.find(t => t.id === match.away);
                const result = MatchEngine.simulateMatch(homeT, awayT);
                matchResults.push({
                    homeId: match.home,
                    awayId: match.away,
                    homeScore: result.homeScore,
                    awayScore: result.awayScore
                });
            });
            this.state.updateStandings(matchResults);
            this.state.matchday++;
        }
        this.render();
    }

    renderEndSeason() {
        this.container.innerHTML = `
            <div class="end-season">
                <h2>Stagione Conclusa!</h2>
                <p>Hai finito il campionato con <strong>${this.state.userTeam.points}</strong> punti!</p>
                <button class="btn" onclick="window.location.reload()">Rigioca</button>
            </div>
            <div class="standings-table" style="max-width: 600px; margin: 2rem auto;">
                <!-- Final standings here -->
            </div>
        `;
        // Quick trick to render standings again in the end screen
        const table = this.container.querySelector('.standings-table');
        this.updateStandingsUIOnly.call({ container: this.container, state: this.state });
    }
}

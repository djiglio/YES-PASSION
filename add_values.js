const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, 'data', 'seasons');

function calculateValue(ovr) {
    ovr = parseInt(ovr, 10);
    let val;
    if (ovr >= 90) {
        val = 60 + (ovr - 90) * 10;
    } else if (ovr >= 85) {
        val = 25 + (ovr - 85) * 7;
    } else if (ovr >= 80) {
        val = 12 + (ovr - 80) * 2.5;
    } else if (ovr >= 75) {
        val = 4 + (ovr - 75) * 1.5;
    } else if (ovr >= 70) {
        val = 1.5 + (ovr - 70) * 0.5;
    } else if (ovr >= 65) {
        val = 0.5 + (ovr - 65) * 0.2;
    } else {
        val = 0.2; 
    }
    
    // Add a tiny bit of random variance (+/- 10%)
    const variance = (Math.random() * 0.2) - 0.1;
    val = val * (1 + variance);
    
    if (val >= 1) {
        // Round to 1 decimal place (e.g. 12.5M)
        return "€" + (Math.round(val * 10) / 10).toFixed(1) + "M";
    } else {
        // Thousands
        return "€" + Math.round(val * 1000) + "K";
    }
}

const files = fs.readdirSync(dataDir).filter(f => f.endsWith('.json'));

for (const file of files) {
    const filePath = path.join(dataDir, file);
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    
    if (data.teams) {
        data.teams.forEach(team => {
            if (team.players) {
                team.players.forEach(player => {
                    player.Value = calculateValue(player.Overall);
                });
            }
        });
    }
    
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
    console.log(`Updated ${file}`);
}

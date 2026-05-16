const fs = require('fs');
const content = fs.readFileSync('C:/Users/fathu/Documents/BRAVOFORMZ/data/subjects/ipa.json', 'utf8');
const lines = content.split('\n');

// Find all topic IDs and their line numbers
for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.includes('"id": "') && !line.includes('topic')) {
        // Check if this is a topic ID (not lesson, not question, not flashcard)
        if (line.match(/^\s*"id":\s*"(klistrikan|mekanika|gelombang|pengukuran|sistem|ekosistem|genetika|reproduksi)"/)) {
            console.log(i+1 + ': ' + line);
        }
    }
}
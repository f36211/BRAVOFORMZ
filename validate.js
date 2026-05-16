const fs = require('fs');
const content = fs.readFileSync('C:/Users/fathu/Documents/BRAVOFORMZ/data/subjects/ipa.json', 'utf8');

try {
    JSON.parse(content);
    console.log('JSON is valid!');
} catch (e) {
    console.log('Error:', e.message);
    const pos = parseInt(e.message.match(/position (\d+)/)?.[1] || '0');
    console.log('Error position:', pos);

    // Find the line number
    let lineNum = 1;
    for (let i = 0; i < pos && i < content.length; i++) {
        if (content[i] === '\n') lineNum++;
    }
    console.log('Error is around line:', lineNum);

    // Show context
    console.log('\nContext around error:');
    console.log(content.substring(Math.max(0, pos - 200), pos + 200));
}
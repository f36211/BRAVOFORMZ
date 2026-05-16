const fs = require('fs');
const content = fs.readFileSync('C:/Users/fathu/Documents/BRAVOFORMZ/data/subjects/ipa.json', 'utf8');

// Count braces outside strings
let depth = 0;
let maxDepth = 0;
let maxDepthPos = 0;
let inString = false;
let escape = false;

for (let i = 0; i < content.length; i++) {
    const c = content[i];

    if (c === '\\' && inString) {
        escape = !escape;
        continue;
    }
    if (c === '"' && !escape) {
        inString = !inString;
        continue;
    }
    if (inString) continue;

    if (c === '{' || c === '[') {
        depth++;
        if (depth > maxDepth) {
            maxDepth = depth;
            maxDepthPos = i;
        }
    }
    if (c === '}' || c === ']') depth--;
}

console.log('Max depth:', maxDepth, 'at pos', maxDepthPos);
console.log('Content at max depth:', content.substring(maxDepthPos - 50, maxDepthPos + 50));
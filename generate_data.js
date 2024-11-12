const fs = require('fs');

// Generate data for each day between September 11 and November 11, 2024
const startDate = new Date('2024-09-11T10:00:00Z');
const endDate = new Date('2024-11-11T10:00:00Z');
const data = [];

for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
  data.push({
    Banana: getRandomInt(0, 4),
    Cucumber: getRandomInt(0, 2),
    'Green Apple': getRandomInt(0, 2),
    'Red Apple': getRandomInt(0, 4),
    Date: d.toISOString()
  });
}

// Write the generated data to data.json
fs.writeFileSync('data.json', JSON.stringify(data, null, 2), 'utf8');

// Helper function to generate random integers within a range
function getRandomInt(min, max) {
  const total = Math.floor(Math.random() * (max - min + 1)) + min;
  const fresh = Math.floor(Math.random() * (total + 1));
  return [fresh, total];
}

const demofile = require('demofile');
const fs = require('fs');

const warmupTimeSeconds = 15;
const roundIntervalStartTicks = (warmupTimeSeconds + 5) * 125
const roundIntervalStopTicks = (warmupTimeSeconds + 7) * 125 

const filename = process.argv[2];

var roundStartTick = 0;
var lastTick = 0;

fs.readFile(filename, function (err, buffer) {
  let demoFile = new demofile.DemoFile();

  let roundstart = false;
  demoFile.gameEvents.on('round_start', e => {
    roundstart = true;
    roundStartTick = demoFile.currentTick;
  });

  demoFile.on('tickend', e => {
  	if (roundstart) {
  		let roundTicks = demoFile.currentTick - roundStartTick;
  		if (roundTicks > roundIntervalStopTicks) {
  			roundstart = false;
  			return;
  		}
  		if (roundTicks >= roundIntervalStartTicks) {
  			if (demoFile.currentTick - lastTick != 1) {
  				throw "Missing ticks in demo: " + filename;
  			}
  			let teams = demoFile.teams;
  			// Team 3 is CT
		  	let cts = teams[3].members;
		    for (let i = 0; i < cts.length; i++) {
		    	let pos = cts[i].position;
		    	console.log("%d,%f,%f", roundTicks, pos.x, pos.y);	
		    }
  		}
  	}
  	lastTick = demoFile.currentTick;
  });

  demoFile.parse(buffer);
});
const demofile = require('demofile');
const fs = require('fs');

const roundIntervalStartTicks = 4 * 128
const roundIntervalStopTicks = 12 * 128

const filename = process.argv[2];

// TODO: Read start and stop seconds as arguments, 
//       and check that arguments are supplied
// TODO: Optionally write T positions as well
// TODO: Optionally continue on missing ticks
// TODO: Investigate if parsing next round when ticks missing
//       is feisable

var roundStartTick = 0;
var lastTick = 0;

fs.readFile(filename, function (err, buffer) {
  let demoFile = new demofile.DemoFile();

  let roundstart = false;
  demoFile.gameEvents.on('round_freeze_end', e => {
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
          if(typeof cts[i] !== "undefined") {
            let pos = cts[i].position;
            console.log("%d,%f,%f,%s", roundTicks, pos.x, pos.y, "c");  
          }
		    }
        /*let ts = teams[2].members;
        for (let i = 0; i < ts.length; i++) {
          if(typeof ts[i] !== "undefined") {
            let pos = ts[i].position;
            console.log("%d,%f,%f,%s", roundTicks, pos.x, pos.y, "t");
          }
        }*/
  		}
  	}
  	lastTick = demoFile.currentTick;
  });

  demoFile.parse(buffer);
});
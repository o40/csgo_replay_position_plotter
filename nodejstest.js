const demofile = require('demofile');
const fs = require('fs');

console.log("Parsing for fun");

fs.readFile('replays/liquid-vs-astralis-m3-cache.dem', function (err, buffer) {
  let demoFile = new demofile.DemoFile();

  let roundstart = false;
  demoFile.gameEvents.on('round_start', e => {
    console.log("A round has been started at %d", demoFile.currentTime);
    roundstart = true;
    roundStartTime = demoFile.currentTime;
  });

  demoFile.on('tickend', e => {
  	// console.log("=============================");
  	if (roundstart) {
  		let roundTime = demoFile.currentTime - roundStartTime;
  		if (roundTime > 7 + 15) roundstart = false;
  		if (roundstart && roundTime > 5 + 15) {
  			let teams = demoFile.teams;
  			// Team 3 is CT
		  	let cts = teams[3].members;
		    for (var i = 0; i < cts.length; i++) {
		    	let ct = cts[i];
		    	let pos = ct.position;
		    	process.stdout.write(roundTime + "," + pos.x);
		    	process.stdout.write("," + pos.y);
		    	process.stdout.write("\n");	
		    }
  		}
  	}
  });

  demoFile.parse(buffer);
});
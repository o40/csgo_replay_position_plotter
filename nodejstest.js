const demofile = require('demofile');
const fs = require('fs');

console.log("Parsing for fun");

fs.readFile('replays/liquid-vs-astralis-m3-cache.dem', function (err, buffer) {
  let demoFile = new demofile.DemoFile();

  /*demoFile.gameEvents.on('player_death', e => {
    console.log("A gameevent is triggered");
    let players = demoFile.entities.players;
    for (var i = 0; i < players.length; i++) {
    	var player = players[i];
    	console.log(`Tick: ${player.name} @ ${player.position.x}, ${player.position.y}`);	
    }
    
  }); */
// Plot between 5-7 seconds

  let roundstart = false;
  demoFile.gameEvents.on('round_start', e => {
    console.log("A round has been started at %d", demoFile.currentTime);
    roundstart = true;
    roundStartTime = demoFile.currentTime;
  });

  demoFile.on('tickend', e => {
  	console.log("=============================");
  	if (roundstart) {
  		let roundTime = demoFile.currentTime - roundStartTime;
  		if (roundTime > 7) roundstart = false;
  		if (roundstart && roundTime > 5) {
  			let teams = demoFile.teams;
  			// Team 3 is CT
		  	let cts = teams[3].members;
		    for (var i = 0; i < cts.length; i++) {
		    	var pos = cts[i].position;
		    	console.log("%f,%f,%f",
		    		roundTime, pos.x, pos.y);
		    }
  		}
  	}
  });

  demoFile.parse(buffer);
});
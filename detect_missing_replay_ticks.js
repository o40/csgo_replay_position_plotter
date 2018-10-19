const demofile = require('demofile');
const fs = require('fs');

let filename = process.argv[2];

var lastTick = 0;

fs.readFile(filename, function (err, buffer) {
  let demoFile = new demofile.DemoFile();

  demoFile.on('tickend', e => {
  	if (lastTick != 0 && demoFile.currentTick - lastTick != 1) {
		console.log("Missing tick (curr: %d, last: %d) in demo: %s", 
			demoFile.currentTick, lastTick, filename);
	}
  	lastTick = demoFile.currentTick;
  });

  demoFile.parse(buffer);
});
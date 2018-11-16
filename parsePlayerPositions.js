const demofile = require('demofile');
const fs = require('fs');

const roundIntervalStartTicks = 0 * 128
const roundIntervalStopTicks = 20 * 128

const filename = process.argv[2];

// TODO: Read start and stop seconds as arguments,
//       and check that arguments are supplied

var roundStartTick = 0;
var lastTick = 0;

var TEAM_T = 2;
var TEAM_CT = 3;

// 2 is T, 3 is CT
function print_positions(teams, round, tick, team_index)
{
  let team_id = "t"
  if (team_index == TEAM_CT) {
    team_id = "ct"
  }

  let members = teams[team_index].members;
  for (let i = 0; i < members.length; i++) {
    if(typeof members[i] !== "undefined") {
      let pos = members[i].position;
      let userid = members[i].userId;
      console.log("%d,%d,%f,%f,%d,%s",
        tick, round, pos.x, pos.y, userid, team_id);
    }
  }
}

fs.readFile(filename, function (err, buffer) {
  let demoFile = new demofile.DemoFile();

  var round_active = false;
  var match_started = false;
  // This is the time when players can move
  demoFile.gameEvents.on('round_freeze_end', e => {
    round_active = true;
    roundStartTick = demoFile.currentTick;
  });

  // Do not plot ticks after this point
  demoFile.gameEvents.on('round_officially_ended', e => {
    round_active = false;
  });

  demoFile.gameEvents.on('round_announce_match_start', e => {
    if (match_started) {
      console.error("Match started twice. Need to handle this somehow");
      process.exit();
    }
    match_started = true;
  });


  // Game officially ended
  demoFile.gameEvents.on('cs_win_panel_match', e => {
    process.exit()
  });

  demoFile.on('tickend', e => {
    if (round_active) {

  		let roundTicks = demoFile.currentTick - roundStartTick;

      if (roundTicks > roundIntervalStopTicks) {
  			round_active = false;
  			return;
  		}

  		if (roundTicks >= roundIntervalStartTicks) {
  			if (demoFile.currentTick - lastTick != 1) {
					console.error("Missing ticks in: %s (has to be interpolated post process)", filename);
					console.error("Tick jump: %d -> %d", lastTick, demoFile.currentTick);
  			}

  			let teams = demoFile.teams;
        let round = demoFile.gameRules.roundsPlayed;
        print_positions(teams, round, roundTicks, TEAM_CT);
        print_positions(teams, round, roundTicks, TEAM_T);
  		}
  	}
  	lastTick = demoFile.currentTick;
  });

  demoFile.parse(buffer);
});
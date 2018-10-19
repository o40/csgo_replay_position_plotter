# csgo_replay_position_plotter

# Installation instructions

1. Install node js: https://nodejs.org/en/download/
2. Install demofile "npm install demofile" (See https://github.com/saul/demofile for source)

Now you should be able to download a demo to the replays folder and run the command:

`node detect_missing_replay_ticks.js replays/fnatic-vs-faze-cache.dem`

You should see something like:
```
Missing tick (curr: 0, last: -54679) in demo: replays/fnatic-vs-faze-cache.dem
Missing tick (curr: 519, last: 512) in demo: replays/fnatic-vs-faze-cache.dem
Missing tick (curr: 523, last: 519) in demo: replays/fnatic-vs-faze-cache.dem
Missing tick (curr: 1415, last: 1408) in demo: replays/fnatic-vs-faze-cache.dem
Missing tick (curr: 1419, last: 1415) in demo: replays/fnatic-vs-faze-cache.dem
```

3. Extract radar images and convert to png and save to the radar_images folder
The radar files are located at:
"Steam\SteamApps\common\Counter-Strike Global Offensive\csgo\resource\overviews\de_cache_radar.dds"

4. Install python: https://realpython.com/installing-python/

# Usage

1. TODO: Write usage instrunctions

# Contact

https://steamcommunity.com/id/dlxDaniel/

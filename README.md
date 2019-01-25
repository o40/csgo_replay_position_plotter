# csgo_replay_position_plotter

THESE INSTRUCTIONS MAY NOT BE THE LATEST AND GREATEST
I WILL UPDATE THEM AT A LATER STAGE

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
5. Install matplotlib:
```
python -m pip install -U pip
python -m pip install -U matplotlib
```

6. (Optional) Install ffmpeg: https://www.ffmpeg.org/

# Usage

## Parsing

Parse using the parsePlayerPositions and fix_tick_gaps script:
`node parsePlayerPositions.js replays/astralis-vs-faze-m1-cache.dem | ./fix_tick_gaps.py`
and save the output to a file.

To parse more then one replay at once, use the parse_all_replays script. It takes a parameter which is a search string in the replays folder.

Parse all replays containing the word cache:
./parse_all_replays.sh cache

Parse all replays containing the word vs (which is all downloaded from hltv.org):
./parse_all_replays.sh vs

## Plotting

See help from posplotter.py for details.

Example plot on de_cache showing the full map at 5 seconds (not outputting to image files)
`python posplotter.py --map de_cache --input csv/astralis-vs-faze-m1-cache.csv --show --full --start 5 --stop 6`

Example plot on de_cache generating images for server ticks between 5 and 6 seconds, zoomed in. The zoom is currently fixed in source code. This could be extended to be parameterized.
`python posplotter.py --map de_cache --input csv/astralis-vs-faze-m1-cache.csv --start 5 --stop 6`

The image files will end up in the "plots" folder (in a subfolder with date-time name).

## Generating video

Change to folder containing the images and run the following command:
`ffmpeg.exe -i %05d.png -c:v libx264 -vf fps=30 -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" video.mp4`

# Contact

If you want to collaborate on developing more interesting tools or have some interesting ideas on what to do with this tool, contact me on:

https://steamcommunity.com/id/dlxDaniel/

(or find my email)

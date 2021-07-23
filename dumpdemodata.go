package main

import (
	"fmt"
	"os"
	"flag"

	dem "github.com/markus-wa/demoinfocs-golang"
	common "github.com/markus-wa/demoinfocs-golang/common"
	events "github.com/markus-wa/demoinfocs-golang/events"
)

func registerTickDoneHandler(parser *dem.Parser, posCsvFile *os.File) {
	parser.RegisterEventHandler(func(events.TickDone) {
		players := parser.GameState().Participants().Playing()
		for _, player := range players {
			if player != nil {
				teamString := "ct"
				if player.Team == common.TeamTerrorists {
					teamString = "t"
				}
				fmt.Fprintf(posCsvFile, 
					"%d,%s,%f,%f,%s\n",
					parser.GameState().IngameTick(),
					player.Name,
					player.Position.X,
					player.Position.Y,
					teamString)
			}
		}
	})
}

func registerRoundFreezetimeEndHandler(parser *dem.Parser, roundCsvFile *os.File) {
	parser.RegisterEventHandler(func(e events.RoundFreezetimeEnd) {
		fmt.Fprintf(roundCsvFile, "%d\n", parser.GameState().IngameTick())
	})
}

func registerMatchStartHandler(parser *dem.Parser, matchStartCsvFile *os.File) {
	parser.RegisterEventHandler(func(e events.MatchStart) {
		fmt.Fprintf(matchStartCsvFile, "%d\n", parser.GameState().IngameTick())
	})
}

func writeCsvHeaders(posCsvFile *os.File, roundCsvFile *os.File, matchStartCsvFile *os.File) {
	fmt.Fprintf(posCsvFile, "tick,name,x,y,team\n")
	fmt.Fprintf(roundCsvFile, "roundstart\n")
	fmt.Fprintf(matchStartCsvFile, "matchstart\n")
}


func outputPlayerPositionsPerRoundAsCsv(parser *dem.Parser, posCsvFile *os.File, roundCsvFile *os.File, matchStartCsvFile *os.File) {
	registerTickDoneHandler(parser, posCsvFile)
	registerRoundFreezetimeEndHandler(parser, roundCsvFile)
	registerMatchStartHandler(parser, matchStartCsvFile)

	// Run parser
	parser.ParseToEnd()
}

func main() {
	demoPathPtr := flag.String("demo", "", "Path to the demo")
	csvIdPtr := flag.String("csv", "", "csv identifier")
	flag.Parse()

	// Mandatory argument
	if *demoPathPtr == "" {
		fmt.Printf("Missing argument demo\n")
		os.Exit(1)
	}

	if *csvIdPtr == "" {
		fmt.Printf("Missing argument csv\n")
		os.Exit(1)
	}

	posCsvFile, err := os.Create("csv/" + *csvIdPtr + "_pos.csv")
	roundCsvFile, err := os.Create("csv/" + *csvIdPtr + "_rounds.csv")
	matchStartCsvFile, err := os.Create("csv/" + *csvIdPtr + "_matchstart.csv")

	if _, err := os.Stat(*demoPathPtr); os.IsNotExist(err) {
  		fmt.Printf("%s does not exist\n", *demoPathPtr)
  		os.Exit(1)
	}

	f, err := os.Open(*demoPathPtr)
	if err != nil {
		panic(err)
	}
	defer f.Close()

	p := dem.NewParser(f)

	writeCsvHeaders(posCsvFile, roundCsvFile, matchStartCsvFile);
	outputPlayerPositionsPerRoundAsCsv(p, posCsvFile, roundCsvFile, matchStartCsvFile)
}
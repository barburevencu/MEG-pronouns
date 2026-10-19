// buttontest prints the status lines of the parallel ports whenever they
// change, to find which port and pin each response-pad button is on.
//
// Run it on the MEG computer, press each button in turn, and read off the
// port and mask for the constants at the top of main.go. Ctrl-C to stop.
//
//	go build -o buttontest ./tools/buttontest && ./buttontest
//	./buttontest /dev/parport1          # only some ports
package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"strings"
	"time"

	"github.com/chrplr/goxpyriment/triggers"
)

// Status register bits and their pins; expyriment's read_status value for
// the same pin is given too, to compare with Pushmi's constants.py.
var statusPins = []struct {
	mask       byte
	pin        int
	name       string
	expyriment int
}{
	{0x08, 15, "nError", 1},
	{0x10, 13, "Select", 2},
	{0x20, 12, "PaperOut", 4},
	{0x40, 10, "nAck", 8},
	{0x80, 11, "Busy", 16},
}

func main() {
	devices := os.Args[1:]
	if len(devices) == 0 {
		devices = []string{"/dev/parport0", "/dev/parport1", "/dev/parport2"}
	}

	type port struct {
		dev  string
		p    *triggers.ParallelPort
		base byte
		last byte
	}
	var ports []*port
	for _, dev := range devices {
		p := triggers.NewParallelPort(dev)
		if err := p.Open(); err != nil {
			log.Printf("%s: %v (skipped)", dev, err)
			continue
		}
		defer p.Close()
		s, err := p.ReadStatus()
		if err != nil {
			log.Printf("%s: %v (skipped)", dev, err)
			continue
		}
		fmt.Printf("%s at rest: 0x%02x\n", dev, s)
		ports = append(ports, &port{dev: dev, p: p, base: s, last: s})
	}
	if len(ports) == 0 {
		log.Fatal("no parallel port could be opened")
	}
	fmt.Println("Press each button in turn (Ctrl-C to stop).")

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt)
	for {
		select {
		case <-stop:
			return
		default:
		}
		for _, pt := range ports {
			s, err := pt.p.ReadStatus()
			if err != nil {
				log.Fatalf("%s: %v", pt.dev, err)
			}
			if s == pt.last {
				continue
			}
			pt.last = s
			var moved []string
			for _, b := range statusPins {
				if (s^pt.base)&b.mask != 0 {
					moved = append(moved, fmt.Sprintf("pin %d %s (mask 0x%02x, expyriment %d)", b.pin, b.name, b.mask, b.expyriment))
				}
			}
			if len(moved) == 0 {
				fmt.Printf("%s 0x%02x  released\n", pt.dev, s)
			} else {
				fmt.Printf("%s 0x%02x  down: %s\n", pt.dev, s, strings.Join(moved, ", "))
			}
		}
		time.Sleep(time.Millisecond)
	}
}

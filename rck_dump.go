package main

import (
	"bufio"
    //"encoding/hex"
	"flag"
	"fmt"
    "io"
	"os"
    "regexp"
    "sync"
	"sync/atomic"
    "time"

	"github.com/ryankurte/go-pcapng/types"
    "go.bug.st/serial"
)

type RckFrame struct {
	dataBuffer  []byte
	timeStamp   float32
	wasReceived bool // received in RCK (True), sent from RCK (False)
}



const PCAP_LINK_TYPE uint16 = 148 // 147..162 (USER0 - USER15)
const INTERFACE_ID = 0

func preparePcapFile(pcapWriter *bufio.Writer) {
	// write section header
	sectionHeaderOptions := types.SectionHeaderOptions{
		Hardware:    "RCK2",
		OS:          "Linux",
		Application: "RckDump",
		//Comment:     "Dual SPI (Full-Duplex)",
	}
	sectionHeader := types.NewSectionHeader(sectionHeaderOptions)
	sectionHeaderBin, _ := sectionHeader.MarshalBinary()
	sectionHeaderBlock := types.NewBlock(types.BlockTypeSectionHeader, sectionHeaderBin)
	sectionHeaderBlockBin, _ := sectionHeaderBlock.MarshalBinary()
	pcapWriter.Write(sectionHeaderBlockBin)

	// write interface descriptor
    interfaceDescription, _ := types.NewInterfaceDescription(PCAP_LINK_TYPE, types.InterfaceOptions{Name: "UART"})
	interfaceDescriptionBin, _ := interfaceDescription.MarshalBinary()
	interfaceDescriptionBlock := types.NewBlock(types.BlockTypeInterfaceDescription, interfaceDescriptionBin)
	interfaceDescriptionBlockBin, _ := interfaceDescriptionBlock.MarshalBinary()
	pcapWriter.Write(interfaceDescriptionBlockBin)
}

func writeFrameToPcapFile(rckFrame *RckFrame, pcapWriter *bufio.Writer) {
	secCount := int64(rckFrame.timeStamp)
	nsCount := int64((rckFrame.timeStamp - float32(secCount)) * 1000000000.0)
	timeStamp := time.Unix(secCount, nsCount)

    frameFlags := make ([]byte, 4)
    frameFlags[1] = 0
    frameFlags[2] = 0
    frameFlags[3] = 0
	if rckFrame.wasReceived {
        frameFlags[0] = 1
    } else {
        frameFlags[0] = 2 
    }

    enhancedPacket, _ := types.NewEnhancedPacket(INTERFACE_ID, timeStamp, rckFrame.dataBuffer, types.EnhancedPacketOptions{})
    enhancedPacket.Options = append(enhancedPacket.Options, *types.NewOption(types.OptionCodeEnhancedPacketFlags,frameFlags))
	enhancedPacketBin, _ := enhancedPacket.MarshalBinary()
	enhancedPacketBlock := types.NewBlock(types.BlockTypeEnhancedPacket, enhancedPacketBin)
	enhancedPacketBlockBin, _ := enhancedPacketBlock.MarshalBinary()
	pcapWriter.Write(enhancedPacketBlockBin)
}

func portReaderLoop(wasStopRequested *uint32, waitingForStop *sync.WaitGroup, serialPort io.ReadWriteCloser, frameParser func([]byte)) {
	defer waitingForStop.Done()

	buffer := make([]byte, 4096)
	for {
		// check if stop was requested
		if atomic.LoadUint32(wasStopRequested) != 0 {
			break
		}

		// read from port
		bytesRead, err := serialPort.Read(buffer)
		if err != nil {
			fmt.Println("Error reading from serial port: ", err)
			os.Exit(-1)
		}

		if bytesRead == 0 {
			continue
		}

        receptionSlice := buffer[:bytesRead] // truncate to appropriate length
		//fmt.Println("Rx[", bytesRead, "]: ", hex.EncodeToString(receptionSlice))
        //fmt.Printf("Rx[%d]: %s", bytesRead, receptionSlice)

        expression, _ := regexp.Compile("SnifferDATA\\[[0-9]\\]: ")
		if frameParser != nil {
            if expression.MatchString(string(receptionSlice)) {
                fmt.Printf("Rx[%d]: %s", bytesRead, receptionSlice)
                snifferData := []byte(expression.ReplaceAllString(string(receptionSlice), ""))
                frameParser(snifferData)
            }

			//frameParser(receptionSlice)
		}
	}
}

func parseRckFrame(buffer []byte) (*RckFrame, error) {
    currentTime := time.Now()
    unixTime := time.Unix(0,0)
    elapsedTime := currentTime.Sub(unixTime)
    return &RckFrame{
        dataBuffer:     buffer,
        timeStamp:      float32(elapsedTime),
        wasReceived:    true,
    }, nil
}

func printUsage() {
	fmt.Println("-------------------------")
	fmt.Println("RCK2 Dump tool")
	fmt.Println("")
	fmt.Println("Takes the input from a RCK device and dumps it into a PCAP-NG file (can be opened with Wireshark)")
	fmt.Println("")
	fmt.Println("The following options are supported")
	flag.PrintDefaults()

	os.Exit(-1)
}

func main() {
    // required parameters
	pcapFileNamePtr := flag.String("output", "", "PCAP-NG output file. Example: \"frames.pcapng\"")
	serialPortNamePtr := flag.String("port", "", "Serial port [COM1, /dev/ttyUSB0, etc]")
	serialPortBaudratePtr := flag.Int("baudrate", 115200, "Baud rate")
	serialPortDatabitsPtr := flag.Int("databits", 8, "Data bits [5..8]")
	serialPortStopbitsPtr := flag.Int("stopbits", 1, "Stop bits [1 or 2]")
	serialPortParityPtr := flag.Int("parity", 0, "Parity [0: none, 1: odd, 2: even]")

	// parse command line options
	flag.Parse()

	// validate arguments
	if len(*serialPortNamePtr) == 0 {
		fmt.Println("Input serial port not provided")
		printUsage()
	}

	if len(*pcapFileNamePtr) == 0 {
		fmt.Println("Output file (pcapng) not provided")
		printUsage()
	}

	options := serial.Mode{
		BaudRate:              *serialPortBaudratePtr,
		DataBits:              *serialPortDatabitsPtr,
		StopBits:              serial.OneStopBit, 
		Parity:                serial.NoParity,
	}

    var parityName string
	switch *serialPortParityPtr {
	case 0: // default, do nothing
		parityName = "NONE"
	case 1:
		options.Parity = serial.OddParity
		parityName = "ODD"
	case 2:
		options.Parity = serial.EvenParity
		parityName = "EVEN"
	default:
		fmt.Println("Invalid parity selected, using default (none)")
	}

    switch *serialPortStopbitsPtr {
    case 1:
    case 2:
        options.StopBits = serial.TwoStopBits
    default:
		fmt.Println("Invalid stop bits selected, using default (one)")
    }

    fmt.Println("Make sure the RCK device is power on, press enter to continue")
	bufio.NewReader(os.Stdin).ReadBytes('\n')

	serialPort, err := serial.Open(*serialPortNamePtr, &options)
	if err != nil {
		fmt.Println("Error opening serial port: ", err)
		os.Exit(-1)
	}

    defer serialPort.Close()

    receptionTimeoutMs, _ := time.ParseDuration("100ms")
    serialPort.SetReadTimeout(receptionTimeoutMs)
	fmt.Println("Serial port ", *serialPortNamePtr, " opened with settings:")
	fmt.Println(" > BaudRate: ", options.BaudRate)
	fmt.Println(" > DataBits: ", options.DataBits)
	fmt.Println(" > StopBits: ", *serialPortStopbitsPtr)
	fmt.Println(" > Parity: ", parityName)

	fmt.Println("Creating PCAP file: ", *pcapFileNamePtr)
	pcapFile, err := os.Create(*pcapFileNamePtr)
	if err != nil {
		panic("Could not create PCAP file")
	}
	pcapFileWriter := bufio.NewWriter(pcapFile)
	preparePcapFile(pcapFileWriter)

	// function to handle "panic"
	defer func() {
		if errorTxt := recover(); errorTxt != nil {
			fmt.Println("Deleting output file due to: ", errorTxt)
			pcapFile.Close()
			os.Remove(*pcapFileNamePtr)
			os.Exit(-1)
		}
	}()

	var waitingForStop sync.WaitGroup
	var wasStopRequested uint32
	atomic.StoreUint32(&wasStopRequested, 0x00)

	// at least one goroutine will always be started
	waitingForStop.Add(1)

    bytesSend, err := serialPort.Write([]byte("sniffer startsim\n\r"))
    if err != nil {
        fmt.Println("Error starting sniffer")
    } else {
        fmt.Println("Bytes send: ", bytesSend)
    }

	fmt.Println("Started Read Only mode")
    framesSaved := 0

	go portReaderLoop(&wasStopRequested, &waitingForStop, serialPort, func(buffer []byte){
        frame, err := parseRckFrame(buffer)
        if err != nil {
            fmt.Println("Error parsing frame", err)
        } else {

            writeFrameToPcapFile(frame, pcapFileWriter)
            framesSaved++
        }
    })

    // wait for user to stop (pressing enter again)
	fmt.Println("Press <Enter> to stop receiving")
	bufio.NewReader(os.Stdin).ReadBytes('\n')
	fmt.Println("Reception/transmission stopped")

	atomic.StoreUint32(&wasStopRequested, 0x01)
	waitingForStop.Wait()

	fmt.Println("Parsed", framesSaved, "frames into", *pcapFileNamePtr)
	pcapFileWriter.Flush()
	pcapFile.Close()
}

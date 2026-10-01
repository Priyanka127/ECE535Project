1. Motivation

Many embedded devices work together as part of a larger network, such as smart homes, autonomous vehicles, and agricultural monitoring systems. For these systems to work correctly, the devices need to have accurate and synchronized clocks.

Traditional time synchronization methods can require additional communication and processing resources, which can be difficult for resource-constrained embedded devices. However, many embedded devices already collect sensor data and periodically send that data to a central gateway.

This project explores whether timestamped sensor data can be used to synchronize the clocks of multiple embedded devices without requiring a dedicated time synchronization service. By analyzing when the same or related physical events are detected by different devices, the Raspberry Pi can estimate differences in clock timing and help synchronize the devices.

2. Design Goals

The main goal is to develop a lightweight time synchronization protocol using sensor data collected from two ESP32 devices.

Specific goals:
Develop two embedded sensor nodes using ESP32 Things.
Collect sensor measurements and attach timestamps to the measurements.
Send timestamped sensor data from the ESP32 devices to a Raspberry Pi.
Measure and characterize the communication/network delay between the ESP32 devices and Raspberry Pi.
Determine the relative clock offset between the two ESP32 devices.
Estimate the relative clock drift between the devices over time.
Develop a synchronization algorithm that uses the sensor data to improve clock alignment.
Evaluate the accuracy and reliability of the proposed synchronization method.
Keep the system lightweight enough for resource-constrained embedded devices.


3. Deliverables
Hardware Deliverables
Two functioning ESP32 sensor nodes.
Sensors connected to each ESP32.
Raspberry Pi gateway capable of receiving data from both devices.
Working wireless communication between the ESP32 devices and Raspberry Pi.
Software Deliverables
ESP32 firmware for:
Reading sensor data
Timestamping measurements
Sending data to the Raspberry Pi
Raspberry Pi software for:
Receiving and storing sensor data
Comparing timestamps
Calculating network delay
Estimating clock offset and drift
Applying the synchronization algorithm
Data visualization/plots showing:
Network delay
Clock offset
Clock drift
Synchronization accuracy over time

Final Deliverable

A complete working demonstration showing two ESP32 devices synchronizing their clocks using timestamped sensor data processed by a Raspberry Pi.


        ┌──────────────────────┐
        │      ESP32 #1        │
        │                      │
        │  Sensor              │
        │     ↓                │
        │  Timestamp Data      │
        └──────────┬───────────┘
                   │
                   │ Wireless Data
                   ↓
            ┌───────────────┐
            │               │
            │  Raspberry Pi │
            │    Gateway    │
            │               │
            │ ┌───────────┐ │
            │ │ Data      │ │
            │ │ Collection│ │
            │ └─────┬─────┘ │
            │       ↓       │
            │ ┌───────────┐ │
            │ │ Synchron- │ │
            │ │ ization   │ │
            │ │ Algorithm │ │
            │ └───────────┘ │
            │               │
            └───────┬───────┘
                    ↑
                    │ Wireless Data
                    │
        ┌───────────┴──────────┐
        │      ESP32 #2        │
        │                      │
        │  Sensor              │
        │     ↓                │
        │  Timestamp Data      │
        └──────────────────────┘



Main System Components

ESP32 Sensor Nodes

Collect physical sensor measurements.
Timestamp each measurement using their local clocks.
Transmit timestamped measurements to the Raspberry Pi.

Raspberry Pi Gateway

Receives data from both ESP32 devices.
Records when packets are received.
Analyzes timestamps from the two devices.
Estimates communication delay.
Estimates clock offset and clock drift.
Calculates synchronization corrections.

Synchronization Algorithm

Compares timestamps from the two devices.
Identifies differences between their clocks.
Uses repeated measurements to estimate clock behavior.
Determines how much one device's clock differs from the other.


| Component                 | Purpose                                       |
| ------------------------- | --------------------------------------------- |
| 2× ESP32 Things           | Embedded sensor nodes                         |
| Raspberry Pi              | Central gateway and synchronization processor |
| Sensors                   | Generate physical events/data                 |
| Wi-Fi/Bluetooth           | Communication between ESP32s and Raspberry Pi |
| Breadboards/jumper wires  | Hardware prototyping                          |
| USB cables/power supplies | Programming and powering devices              |


Software
ESP32
C/C++ or Arduino framework
Sensor drivers
Wireless communication
Timestamp generation
Data packet formatting
Raspberry Pi
Python or C/C++
Data collection
Timestamp analysis
Synchronization algorithm
Data logging
Visualization using tools such as MATLAB or Python
Communication

The system could use Bluetooth or Wi-Fi to transmit sensor data from the ESP32 devices to the Raspberry Pi.


| Week   | Tasks                                                                          |
| ------ | ------------------------------------------------------------------------------ |
| **1**  | Research time synchronization, review references, finalize system architecture |
| **2**  | Select sensors and communication method; set up ESP32s and Raspberry Pi        |
| **3**  | Develop ESP32 sensor-reading and timestamping firmware                         |
| **4**  | Implement wireless communication and Raspberry Pi data collection              |
| **5**  | Begin collecting timestamped sensor data; test communication reliability       |
| **6**  | Measure and characterize network delay                                         |
| **7**  | Develop clock offset and clock drift estimation                                |
| **8**  | Implement the complete synchronization algorithm                               |
| **9**  | Test system under different conditions and analyze accuracy                    |
| **10** | Finalize system, create graphs/results, documentation, and presentation        |

Roles
Priyanka: networking 
Anaika: writing and research 
Shashwat: setup & algorithm design 
Liz: setup & software 

References
ECE 535/635 Course Projects slideshow, Fall 2026: slide 6, “Time Synchronization Via Sensing”; slide 17, repository requirements and submission timeline.
“HAEST: Harvesting Ambient Events to Synchronize Time across Heterogeneous IoT Devices.” 
Lex Fridman et al., “Automated Synchronization of Driving Data Using Vibration and Steering Events,” Pattern Recognition Letters, vol. 75, pp. 9–15, 2016. Starting point for studying shared-event and cross-correlation methods; published performance is not a target or result for our prototype.
“Exploiting Smartphone Peripherals for Precise Time Synchronization,” 2019. Background on peripheral-based synchronization. The authors’ implementation repository is a reference for study, not an assumed drop-in ESP32 implementation.


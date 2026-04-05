Tags: #embedded #usb  

> [!attention] 
> [Bad English](https://www.youtube.com/watch?v=Ka2ucZ1Bwyc) 

> [!Sources]
> [How does a USB keyboard work? - YouTube](https://www.youtube.com/watch?v=wdgULBpRoXk)
> USB Complete 3 edition Jan Axelson

***

<span style="font-size: 25">List of content:</span>

```table-of-contents
```

***

<span style="font-size: 25">Tasks:</span>

```tasks
```

***

# What is USB

USB is a network with a tier star topology. In USB network there is a central hub(or host), and devices connect on it in layers or tiers. For example, you can connect to your PC(host) some USB hub, so to USB hub you can connect several USB devices. So your central hub is the first tier, USB hub is second tier and your USB devices are third tier.  
![[tiernetwork.png|400]]
Every USB device don't communicate to each other, they communicate only with host. Host, like master node, initiates all data transfer.
>[!help]
> For comparison, [[SPI]] has a master-slave topology, so in SPI network there are only one master that initiates all data transfers with many slave nodes. The slaves only communicate with the master and not with each other directly.
> ![[mbus-master-slave-topology-1505166572.gif|400]]
> [CAN](CAN%20шина) uses bus topology without any master node. So every node in network can communicate with each other by one bus. This impose a limitation, because on a bus, there can be only one communication at a time.
> ![[CANbus_topology-e1430903432430-3348523069.jpg|400]]

USB 2.0 limits network by 5 hubs deep. It means that USB device and host have maximum 5 hubs in between. So maximum tier in USB network is tier 7.

***

# Terminology

- [x] #todo Please rewrite this text. I don't like it, and don't fully understand the USB terminology. Also it is significant to understand the difference between transfer and transaction, please learn this words. Understand the term interface. 🔼 ✅ 2025-09-12

In the world of USB, the words function and device have specific meanings. Also important is the concept of a USB port and how it differs from other ports such as RS-232.

- Device
The physical USB hardware you plug in. A device is a physical entity that performs one or more functions. Hubs and peripherals are devices. The host assigns a unique address to each device on the bus. 
A **compound device** contains a hub with one or more permanently attached devices. The host treats a compound device in much the same way as if the hub and its functions were separate physical devices. <span style="color: red">The hub and embedded devices each have a unique address.</span>
A *composite device* has one bus address but multiple, independent interfaces or groups of related interfaces that each provide a function. Each interface or group of related interfaces can use a different driver on the host. For example, a composite device could have interfaces for a printer and a drive.

- Port
Port is an addressable location through which PC interface with an USB cable. Host applications can’t access USB ports directly but
instead communicate with drivers assigned to the devices attached to ports. 

- Configuration
In USB terminology, a **configuration** is like a mode or profile of the device. A device can have multiple configurations, but in practice most devices have just one. Switching configurations is rare and usually only happens when the device needs to operate in a completely different way, for example, a printer that can also act as a scanner or fax.

- Function
A function is a **logical capability of a device** — what the device can actually do. For example, a webcam with a microphone has two functions: video capture and audio capture.
> [!warning] 
> When a device implements only one function, some texts may loosely use “device” and “function” as synonyms, but they are not the same thing.

- Interface
Within a configuration, there are **interfaces**, a logical access points within a USB device that exposes a specific function to the host. It defines _how the host communicates with the device_ to use that function. A configuration can contain one or more interfaces, and all interfaces within a configuration are active at the same time. Each interface can have one or more alternate settings, which are different modes of that interface, but if an interface has only one setting, it is called alternate 0, and no switching is needed.

|Level|Example|Notes|
|---|---|---|
|Device|Webcam with mic|Physical USB device|
|Function|Video capture / Audio capture|Logical capability|
|Configuration|Configuration 1|Both functions active|
|Interface|Video streaming / Video control / Audio streaming / Audio control|Logical access points with endpoints|
|Endpoints|0x81 IN for video, 0x82 IN for audio, 0x01 OUT for control|Physical channels host uses to transfer data|

> [!example] 
> To fully understand the meaning of configuration, functions, and interface, here is an example:
>  Device: a USB webcam with a built-in microphone.
>  Configuration: The device has one configuration (common for most devices).  This configuration activates both functions at the same time.
>  Interfaces:
>- **Video capture function**
>    - **Interface 0**: Video streaming interface
>        - Endpoint: Bulk or Isochronous IN endpoint for video data
>    - **Interface 1**: Video control interface
>        - Endpoint: Control endpoint for adjusting resolution, brightness, etc.
>- **Audio capture function**
>    - **Interface 2**: Audio streaming interface
>        - Endpoint: Isochronous IN endpoint for audio data
>    - **Interface 3**: Audio control interface
>        - Endpoint: Control endpoint for volume, mute, etc.

## Transaction, Transfer and Packet

A packet is the **smallest indivisible unit of data** transmitted over the USB bus. It is a **formatted block of information** with a specific structure, that describes in [[#USB Packets]]

Transaction is the smallest complete communication sequence between the host and a device. Example of transaction is depicted below
![[Pasted image 20250912220623.png]]
Transaction is always consist of three phases:
- [[#Token Packet]] - initiates the transaction and specifies direction/endpoint
- [[#Data Packet]] - Carries payload
- [[#Handshake Packet]] - Confirms success, failure, or [STALL](#Handshake%20Packet).

A transaction is **atomic**: it either fully succeeds or fails. A transaction always targets a single endpoint and a single direction.

A [**transfer**](#Types%20of%20transfers) is a **logical sequence of one or more transactions** to complete a data operation. The transfer is implemented by one or more transactions on the same endpoint. Transfers represent the complete movement of a logical block of data: for example some configuration([[#Control Transfer]]) or some data([Bulk](#Bulk%20Transfer), [Interrupt](#Interrupt%20Transfer), [Isochronous](#Isochronous%20Transfer) transfers)

***

# Some numbers

## Speed

USB 2.0. supports three bus speeds: high speed at 480 Megabits/sec., full speed at 12 Megabits/sec., and low speed at 1.5 Megabits/sec. This is the speed that describes the rate that information travels on the bus. But in addition to useful information, the bus must carry status, control, and error-checking signals. Plus, all peripherals must share the bus. So the rate of data transfer that an individual peripheral can expect will be less than the bus speed.

So the theoretical maximum rate for a single data transfer is about 53 Megabytes/sec at high speed, 1.2 Megabytes/sec at full speed, and 800 bytes/sec at low speed.

![[Pasted image 20250814113845.png]]

***

# Endpoints and pipelines

Each device on a USB bus is assigned a unique address by the host, used for all communication. USB communication occurs through <span style="color: red">**pipes**</span> — logical channels connecting the host controller to specific **numerical data buffer in device called an <span style="color: red">endpoint</span>**.

**Endpoint:** A buffer within the USB device firmware that stores incoming data from the host and outgoing data to the host. Endpoints are _not separate physical memory blocks_; they are logical buffers managed by the device. A USB device can have multiple endpoints, each identified by an endpoint number, direction (IN or OUT), and maximum packet size.
Endpoints organize different data flows, enabling a device to handle multiple tasks "simultaneously", such as control commands and audio streaming over a single physical connection (the USB cable).

**Pipes:** The host-side abstraction of a connection to a specific endpoint. A pipe represents the communication path from the host to a particular endpoint in the device. Terminology separates the host’s perspective (pipe) from the device’s perspective (endpoint), clarifying how data flows logically over a single physical link.

![[Pasted image 20250803153735.png|500]]

The host establishes pipes during [[#Enumeration]]. If the device is removed from the bus, the host removes the no-longer-needed pipes. The host may also request new pipes or remove unneeded pipes at other times by requesting an alternate configuration or interface for a device.

USB endpoints are categorized by **transfer type** and **direction**.
1. Transfer types(described in [[#Types of transfers]])
	- **Control:** Endpoint 0, bidirectional, used for device management
	- **Interrupt:** Short, time-critical transfers, predictable latency
	- **Bulk:** Large, non-time-critical transfers, uses remaining bandwidth
	- **Isochronous:** Continuous, time-sensitive streams, no retries on error
2. Direction(assigned on behalf of the host):
	- **IN:** Device → Host.
	- **OUT:** Host → Device.

> [!important] 
>  Every device has a Default Control Pipe that uses Endpoint 0. Typically it is a single control endpoint in device, but some application can require several control endpoint.

In additional to essential endpoint 0  full- or high-speed device can have up to 15 additional endpoint addresses. Each endpoint supporting both IN and OUT transfers. So, in fact, each device can have 31 endpoints:
- 1 control endpoint (Endpoint 0)
- 15 IN endpoints
- 15 OUT endpoints

- [ ] #todo I have big doubts about this information. It is not clear how communication will take place if they have the same addresses.

> [!Question]
> You can find contradiction that if every endpoint can have IN and OUT transfer then even not control endpoints can be bidirectional. But even if a device has “Endpoint 1 IN” and “Endpoint 1 OUT,” USB counts them as **two separate endpoints** with the same number but opposite directions. The apparent “bidirectionality” comes from pairing an IN and an OUT endpoint with the same number for convenience, but internally they are distinct endpoints. So yeah in USB term "bidirectional" [depends on the definition](https://www.youtube.com/watch?v=-SYTsg4dTzU)
> But my advice: just don't worry about this bidirectional difference. Just use endpoint 0 as control endpoint with IN and OUT, and use other endpoints as unidirectional.

> [!warning] 
>  Low speed devices, however can only have 2 additional endpoints on top of the default pipe. (4 endpoints max)
>  - Endpoint 0 (control, bidirectional)
> - Endpoint 1 (IN) 
> - Endpoint 1 (OUT)
>  - Endpoint 2 (IN or OUT)

Size of each endpoint is configurable and defines maximum size of useful data in data packet. 

For internal addressing uses endpoint [descriptor](#Descriptors) and internal endpoint address is defined in bEndpointAddress with 1 byte size. Bit 7 of this field describes type of endpoint: 0=OUT, 1=IN. Bit 6..4 reserved and reset to zero. Bit 3..0 is endpoint number.
This address typically uses in USB controllers of devices for internal registers. Host address to endpoint only by endpoint number in [[#Token Packet]] and describes direction OUT or IN in PID field of Token Packet

Endpoint size is determined by field in [descriptor](#Descriptors): bMaxPacketSize0 for endpoint 0 and wMaxPacketSize for others.
![[Pasted image 20250814174826.png|500]]
[10-0] bits describes the maximum packet size, from 0 to 1024 bytes. Bits [12-11] is used only in USB 2.0(in USB 1.0. these bits are always 00) and indicate how many additional transactions per microframe a high-speed endpoint supports:
- 00 - no additional transactions(total of 1 transaction per microframe)
- 00 - 1 additional transactions(total of 2 transaction per microframe)
- 00 - 2 additional transactions(total of 3 transaction per microframe)
- 11 - reserved

But! Despite the fact that you can set endpoint maximum packet size from 0 to 1024, Endpoint size has restrictions that depend on [transfer type](#Types%20of%20transfers) of endpoint and speed of endpoint. You should choose endpoint size with regard to maximum packet limits of each transfer type:
1. [[#Control Transfer]]
	- low-speed: only 8 bytes
	- full-speed: may be 8, 16, 32, 64 bytes
	- high-speed: only 64 bytes
2. [[#Bulk Transfer]]
	- full-speed: may be 8, 16, 32, 64 bytes
	- high-speed: the maximum packet size 512 bytes
3. [[#Interrupt Transfer]]
	- low-speed: from 1 to 8 bytes
	- full-speed: from 1 to 64 bytes
	- high-speed: from 1 to 1024 bytes
4. [[#Isochronous Transfer]]
	- full-speed: from 0 to 1023 bytes
	- high-speed: from 0 to 1024 bytes

***

# Signaling levels

USB uses **differential signaling** on two lines: **D+** and **D–**. Differential signaling improves noise immunity. Because even on Low-Speed we have 1.5 Megabits per second. So that wire could start to look a lot like an antenna with 1.5 MHz radio transition emanating from it, and this radio transition could cause harm to other electronics around this wire. But if we have differential pairs, we have radio transmit with 180 degrees phase difference. So this radio transition will destructively interfere with each other.

Differential pair: D+ and D– carry opposite voltages for each logical state.
- Differential "1": D+ is high, D- is low
- Differential "0": D+ is low, D- is high

In practice, monitoring D+ alone often suffices to determine the differential state.

There are also two special differential levels:
- Single-ended 0 (SE0): D+ and D- both low(used for reset or [end-of-packet](#EOP))
- Single-ended 1 (SE1): D+ and D- both high(illegal, not used)

But for data, there are two states, that differential level is depends on speed:
![[Pasted image 20250912202411.png]]

With this two states, USB specifies some special states:
- Idle State is always a J state, that how i described upside is depending on speed of device.
- Resume state is always K state and sends by host during 1-15 ms to switch device from [suspend state](#Device%20states)

Of course all this information is very shallow, for more thorough information about concrete voltage values of each state please refer to [7.1.7 Signaling Levels of USB 2.0 specification](http://www.poweredusb.org/pdf/usb20.pdf#%5B%7B%22num%22%3A608%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2Cnull%2Cnull%2Cnull%5D)

## NRZI

USB don't send clocking through bus, as [[I2C]], so it clock synchronization is achieved through several switching of bus state. So each of [[#USB Packets]] starts with [[#SYNC]] field that has several switching, so host can synchronize with frequency of the device.

But other data in packet is not encoded in the way of raw logic “1” and “0” as static voltage levels. Like if J is corresponds to 1, and K corresponds to 0. Instead, USB uses **NRZI (Non-Return-to-Zero Inverted) encoding** to represent bits over the differential pair.

In NRZI encoding, a “1” is represented by no change in level and a “0” is represented by a change in level.

It is much easier to describe it on example.

Raw data to USB NRZI:
1 1 0 0 1 0 1 1
NRZI encoding:
- Start at J data state.
- Bit 1 → no change(J)
- Bit 1 → no change(J)
- Bit 0 → invert level(K)
- Bit 0 → invert level(J)
- Bit 1 → no change(J)
- Bit 0 → invert level(K)
- Bit 1 → no change(K)
- Bit 1 → no change(K)

So at the end we get JJKJJKKK

USB use NRZI to prevent clock synchronization lost, because if we have many 0 in our data, then there are no change in USB bus, and host can easily lost clock synchronization. But NRZI isn't only way how USB prevents losing synchronization

## Bit Stuffing
In NRZI if we have many 1 in our data, than NRZI encoded this to many non switching states. Because of that host also can lost synchronization. So USB inserts a **stuffed “0”** after six consecutive “1”s, and the receiver removes the stuffed “0” to reconstruct the original data.

## Bit and Byte Ordering in USB Packet

In USB communication, **NRZI encoding** and **J/K states** are used for the physical layer, but before that, the packet data itself is prepared with specific bit and byte ordering rules:

- Each **multibyte field** in a USB packet is transmitted in **little-endian** order. 
> [!important] 
> This applies **per field**, not to the entire packet as a whole. 

- Within each byte, bits are transmitted **least significant bit (LSB) first**.

> [!example] 
>  We want to send `0x1234` via USB bus.
>  1. Convert to Little-Endian Byte Order
>      The 16-bit value `0x1234` is split into bytes in little-endian order: `0x34`, `0x12`.
>  2. Binary Representation of Each Byte
>      - `0x34` → `00110100`
>      - `0x12` → `00010010`
>  3. The final message that will already be decoded in NRZI and sent to the USB bus will be a sequence of bits in LSB format
>      0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0


***

# USB Packets

> [!Warning] 
> Each field on the USB bus Packet is transmitted LSBit first.

There are several USB Packets
 ![[USB-packets-866451911.png]]

Every field of USB packet is described bellow

## Common field of packets

### SYNC
All packets must start with a sync field. The SYNC pattern for low-/full-speed transmission required to be 3 KJ pairs followed by 2 K's for a total of eight symbols. For high-speed it is required to be 15 KJ pairs followed by 2 K’s, for a total of 32 symbols.

The sync field is 8 bits long at low and full speed or 32 bits long for high speed and is used to synchronize the clock of the receiver with that of the transmitter. The last two bits indicate where the PID fields starts.

### PID
PID(Packet ID) - identify the type of packet that is being sent.

There are 4 bits to the PID, however to insure it is received correctly, the 4 bits are inverted and repeated, making an 8 bit PID in total in each USB packet.

| $P I D_(0)$   | $P I D_(1)$ | $P I D_(2)$ | $P I D_(3)$ | $overline P I D_(0)$ | $overline P I D_(1)$ | $overline P I D_(2)$ | $overline P I D_(3)$ |
|--|--|--|--|--|--|--|--|

There are table of all PIDs. All of this PIDs will be described below in describing all packets

![[Pasted image 20250912223947.png|570]]


### CRC
Cyclic Redundancy Checks are performed on the data within the packet payload. All token packets have a 5 bit CRC while data packets have a 16 bit CRC.

The CRC is applied to the data to be checked. The transmitting device performs the calculation and sends the result along with the data. The receiving device performs the identical calculation on the received data. If the results match, the data has arrived without error and the receiving device returns an ACK in [handshake](#Handshake%20Packet). If the results don’t match, the receiving device sends no handshake. The absence of the expected handshake tells the sender to retry.

> [!note] 
> Typically, the host tries a total of three times, but the USB specification gives the host some flexibility in determining the number of retries. On giving up, the host informs the driver of the problem. 

### EOP
End of packet. Signalled by a [Single Ended Zero (SE0)](#Signaling%20levels) for approximately 2 bit times followed by a [J](#Signaling%20levels) for 1 bit time.

> [!important] 
>  EOP in low-speed communication is used as a marker of starting a new frame like [SOF packet](#Start%20of%20Frame%20Packet) for full- and high-speed. This signal is called the low-speed keep-alive sign


## Start of Frame Packet

USB communication is organized into frames by the host. For Low-Speed and Full-Speed USB devices, the host divides communication into frames of 1 millisecond each. For High-Speed USB devices the host further subdivides each 1-millisecond frame into 8 microframes, each lasting 125 microseconds.

Within these frames (or microframes for High-Speed), the host schedules and manages data transfers. The typical USB communication for full-speed is depicted below

![[Pasted image 20250812175636.png]]

Each frame <span style="color: red">in full-speed</span> begins with a Start-of-Frame (SOF) packet, a special token packet sent by the host at precise 1-millisecond intervals.
> [!important] 
>  Low-speed devices don’t see the SOF packet. Instead, the hub sends a simpler [End-of-Packet (EOP)](#EOP) signal called the low-speed keep-alive signal. As the SOF packet does for full-speed devices, the low-speed keep-alive keeps low-speed devices from entering the Suspend state.

The SOF packet serves as a timing reference, synchronizing all connected devices to the host’s clock. This ensures that devices know when a new frame begins and can align their communication accordingly.

This packet is looks like this
![[Pasted image 20250812175844.png|300]]

The [[#PID]] for the Start-of-Frame packet will have the value `SOF`, which is `0b0101` in binary. 
![[Pasted image 20250812195633.png|550]]

Additionally, the Start-of-Frame packet includes a Frame Number, which is a counter indicating the current frame count and rolls over on reaching the maximum.

In high-speed USB communication, where each 1-millisecond frame is divided into 8 microframes that lasting 125 microseconds, each microframe begins with a Start-of-Frame (SOF) packet. Importantly, all microframes within the same frame share the same Frame Number in their SOF packets. For example, if the third microframe of the sixth frame starts, the SOF packet for that microframe will have a Frame Number=6.

An endpoint may synchronize to the Start-of-Frame packet or use the frame count as a timing reference. The Start-of-Frame marker also keeps devices from entering the low-power Suspend state when there is no other USB traffic.

## Token Packet
Every [transaction](#Transaction,%20Transfer%20and%20Packet) has a token packet. The host is always the source of this packet, which sets up the transaction by identifying the packet type, the receiving device and endpoint, and the direction of any data the transaction will transfer.

![[Pasted image 20250812192233.png|300]]

> [!important] 
>  For low-speed transactions on a full-speed bus, a [[#PRE packet]] precedes the token packet. For split transactions, a [[#SPLIT packet]] precedes the token packet.

ADDR(Address) field specifies which device the packet is designated for. Being 7 bits in length allows for 127 devices to be supported. Address 0 is not valid, as any device which is not yet assigned an address must respond to packets sent to address zero.

ENDP - specifies what endpoint the packet is designated for. ENDP field is made up of 4 bits, allowing 16 possible endpoints. 

PIDs for this packet is described below:
![[Pasted image 20250812195354.png|550]]

> [!important] 
>  The direction is defined from the host’s perspective: an IN token provides data to send to the host and an OUT token provides data received from the host.

[Setup transaction with SETUP token](#Setup%20Stage) is like an OUT transaction because data travels from the host to the device, but a Setup transaction is a special case because it initiates a [[#Control Transfer]]. 
Devices should always accept setup transaction. Because these requests can include commands to configure the device, information about the device (such as descriptors), set device parameters, and perform other control functions. So this transaction is needed to right configuration of host to work with connected device.

When a device receives an OUT or Setup packet containing the device’s address, the endpoint stores the data that follows the OUT or Setup packet and the hardware typically triggers an interrupt.

When a device receives an IN packet containing its device address, if the device has data ready to send to the host, the hardware sends the data from the specified endpoint onto the bus and typically triggers an interrupt where device can then do whatever is needed to get ready for the next IN transaction.

## Data Packet

Depending on the [transfer type](#Types%20of%20transfers) and whether the host or device has information to send, a data packet may follow the token packet. The direction specified in the token packet by [[#PID]] determines whether the host or device sends the data packet.

![[Pasted image 20250812194916.png|300]]

There are four types of data packets, identified by differing PIDs:
![[Pasted image 20250812202300.png|550]]

### Data toggle

In transfers that require multiple transactions, to ensure that no transactions are missed and the transmitter and receiver synchronized, USB protocol uses data-toggle. Each data packet in multiple transaction sequence has a toggle PID: DATA0 and DATA1. Both the sender and receiver keep track of the data toggle.  

In device, microcontroller often **has a register bit that indicates the data-toggle state**, and each **endpoint maintains its own data toggle**. A host handles the data toggles on low-level, without requiring any user programming. Receiver sequence bits toggle only when the receiver is able to accept data and receives an error-free data packet with the correct data PID. Transmitter sequence bits toggle only when the data transmitter receives a valid ACK handshake.
> [!important] 
>  Data toggle synchronization is not supported for [[#Isochronous Transfer]].


On detecting an incoming data packet, the host or device compares the state of its data toggle with the received data toggle. If the values match, receiver toggles his data toggle value and returns an ACK handshake packet. The ACK causes the sender to toggle its data toggle value for the next transaction.

But there is can occur a mismatch between the data toggle value in a data packet and the expected value on the receiver's side, for example because of ACK handshake lose, so receiver is change data toggle, but transceiver don't.
![[Pasted image 20250917192941.png|230]]

Because of this situation there are mismatch between data toggles. To cope with this, certain mechanism come into play to handle and correct this situation. Transceiver will retried to transfer DATA0. But because of mismatch of data toggle for receiver, the receiver will ignore the data content of the packet(and also don't change it data toggle), however he will return an ACK to the sender. This ACK is crucial because it signals to the sender that it can change it data toggle value.
When the sender receives the ACK, it toggles the data toggle value for the next transmission, so after this crucial ACK both receiver and sender has the same data toggle value, they are resynchronized.

As a result, after this resynchronization the next data packet sent by the sender will have the correct data toggle value, allowing the receiver to correctly process the data.

If the receiver is busy and returns a NAK, or if the receiver detects corrupted data and returns no response, the sender doesn’t toggle its bit and instead tries again with the same data and data toggle.

> [!important] 
>  Some exceptions in data toggle process
>  In [[#Control Transfer]], [[#Control Transfer#Setup Stage]] always use DATA0 in the first transaction, [[#Control Transfer#Data Stage]] always use DATA1 in the first transaction, toggle the bit in any additional data stage transactions, and always uses DATA1 PID in the [[#Control Transfer#Status Stage]] with zero-length data packet in success of control transfer(or NAK or STALL PIDs if an error occur).
>  [Bulk](#Bulk%20Transfer) endpoints toggle the bit in every transaction, so even if previous bulk <span style="color: red">transaction</span>(don't confuse with [transfer](#Transaction,%20Transfer%20and%20Packet) is ended with data packet with DATA0, next bulk <span style="color: red">transfer</span> will start with DATA1, because data toggling isn't bounded in one <span style="color: red">transaction</span>. Data toggle is reset only after completing Set_Configuration, Set_Interface, or Clear_Feature(ENDPOINT HALT) control request.
>  [Interrupt](#Interrupt%20Transfer) endpoint can behave the same as bulk endpoint, but the programmer can configure interrupt IN endpoint to toggle its data toggle in each transaction without checking for the host’s ACKs, at the risk of losing some data.
>  Full speed [isochronous transfer](#Isochronous%20Transfer) always use DATA0 because isochronous transfer doesn't have error correcting so there is no handshake packet for returning an ACK or NAK to toggle this data toggle.
>  High-speed isochronous IN transfers use DATA0, DATA1 and DATA2 encoding to indicate a transaction's position in the microframe
>  ![[Pasted image 20250813183135.png]]
>  High-speed isochronous OUT transfers use DATA0, DATA1 and MDATA to indicate whether more data will follow in the microframe
>  ![[Pasted image 20250813183315.png]]

> [!bug] 
>  If you’re debugging a USB bus where it data is transmitting on the bus, but the receiver is discarding the data, maybe device isn't sending or expecting the correct data toggle.

## Handshake Packet
In all transfer types except isochronous, the receiver of the data packet (or the device if there is no data packet) returns a handshake packet containing a code that indicates the success or failure of the transaction. 

>[!warning]
> The absence of an expected handshake packet indicates a more serious error.

![[Pasted image 20250812202519.png|200]]
There are four types of handshake packets, identified by differing PIDs:
![[Pasted image 20250812202657.png|550]]

- **ACK**(acknowledge) indicates that a host or device has received data without bit stuff or CRC error. Therefore ACK is applicable only in transactions in which data has been transmitted and where a confirmation of receive is expected.  ACK can be returned by the host for IN transactions and by a function for OUT, SETUP, or PING transactions
- **NAK**(negative acknowledge). If the host sends data to OUT endpoint at a time when the device is too busy to accept the data, the device returns a NAK in the handshake packet. If the host requests data from the device endpoint IN when the device has nothing to send, the device returns a NAK in the data packet. In either case, NAK indicates a temporary condition, and the host can retry later.
- **STALL** can have any of three meanings:
	- When a device receives a control-transfer request that the device doesn’t support, the device returns a STALL to the host.
	- *Protocol STALL* If the device supports the request but for some reason can’t take the requested action. For example, if the host sends a Set_Configuration request that requests the device to set its configuration to 2, and the device supports only configuration 1, the device returns a STALL.
	- *Functional STALL* when the endpoint’s Halt feature is set by device, which means that the endpoint is unable to send or receive data at all. So this type of STALL must support bulk and interrupt endpoints. Although control endpoints may also support this use of STALL, it’s not recommended. Isochronous transactions don’t use STALL because they have no handshake packet for returning the STALL. 
	On receiving a functional STALL, the host drops all pending requests to the STALL endpoint on the device and doesn’t resume communications until the host has sent a successful request to clear the Halt feature on the device endpoint.
	For more strict information about STALL sending in Control Transfer, please refer to [[#Control Transfer#Data Stage]] and [[#Control Transfer#Status Stage]] 
- **NYET**(not yet) uses only high speed devices. In USB 2.0, high-speed devices use the NYET handshake to improve efficiency in data transfers. When a device isn't ready to receive data in a full- or low-speed control or bulk transfer it returns a NAK, causing the host to retry later. This can waste a lot of bus time if the data packets are large and the device is often not ready.
So in USB 2.0 where high-speed is invented also added a better way to cope with this problem. When a device accepts data but isn't ready for more, it returns a NYET. The host then sends a PING token to check if the device is ready for the next data packet. The device responds with ACK if ready, or NAK/STALL if not. This method is more efficient than sending entire data packets only to receive a NAK, reducing wasted bus time. A 2.0 hub may also use NYET in complete-split transactions.
- **ERR** 

- [ ] #todo Fully understand the complete-split transactions and write this part ⏬

> [!important] 
>  **All of this handshakes is not an error. No handshake at all is an error.** If a device doesn't return a handshake packet, the host tries  twice more. On receiving no response after a total of three tries, the host notifies the software that requested the transfer and stops communicating with the endpoint until the problem is corrected.

___

# Types of transfers

There are four different <span style="color: orange">data transfer types</span> and two <span style="color: cyan">types of pipes</span>:

- <span style="color: orange">Control Transfers.</span> Control transfers are the only type that have functions defined by the USB specification. Control transfers enable the host to read information about a device, set a device’s address, and select configurations and other settings. Control transfers may also send vendor-specific requests that send and receive data for any purpose. This transfer uses the <span style="color: cyan">control pipe</span>. 
- <span style="color: orange">Interrupt Transfers</span> Used for sending small amounts of bursty data that requires a guaranteed maximum latency and that must receive the host’s or device’s attention periodically. This transfer uses a <span style="color: cyan">data pipe</span>.
- <span style="color: orange">Bulk Transfers</span> Used for large data transfers that use all available USB bandwidth with no guarantee on transfer speed or latency. Bulk transfers are intended for situations where the rate of transfer isn’t critical, such as sending a file to a printer, receiving data from a scanner, or accessing files on a drive This transfer uses a <span style="color: cyan">data type</span>.
- <span style="color: orange">Isochronous Transfers</span> have guaranteed delivery time but no error correcting. Isochronous transfers are capable of this guaranteed delivery time due to their guaranteed latency, guaranteed bus bandwidth, and lack of error correction. Without the error correction, there is no halt in transmission while packets containing errors are resent. Data that might use isochronous transfers incudes audio or video to be played in real time. This transfer uses a <span style="color: cyan">data pipe</span>.

Below is the table that summarizes the features and uses of each transfer type.
![[Pasted image 20250807202123.png|600]]

Each transaction has up to three phases(or three [[#USB Packets]]): token, data and handshake. Each packet is a block of information with a defined format, this format is described also in [[#USB Packets]]. It is similar to each USB packet to contain [Packet ID(PID)](#PID) that contains identifying information about this packet. 

Phases(or Packets) in which transfer type is described in the table below:
![[Pasted image 20250812174607.png|600]]

## Control Transfer

Control transfers have two uses. Control transfers carry the requests that are defined by the USB specification and used by the host to learn about and configure devices. Of course Control transfers can carry requests defined by a class or vendor that not defined by USB specification.

The host controller reserves a portion of the bus bandwidth for control transfers: 10 percent for low- and full-speed buses and 20 percent for high-speed buses. If the control transfers don’t need this much time, [bulk transfers](#Bulk%20Transfer) may use what remains. If the bus has more then 10% or 20% of unused bandwidth, control transfers may use more than the reserved amount.

As you can see on the transfer types table in [[#Types of transfers]], Control Transfer consists Setup Stage, Data Stage and Status Stage. Data Stage is optional, though a particular request may require a Data stage.

### Stages of control transfer

#### Setup Stage
In the Setup stage, the host begins a Setup transaction by sending information about the request.

- Token Packet
    Identifies the receiver and identifies the transaction as a Setup transaction. Structure same as other [[#Token Packet]], but with PID=0b1101(SETUP). So this packet also include device and endpoint address with CRC5
    ![[Pasted image 20250812192233.png|300]]
- Data Packet
    The data packet contains information about the request, including the request number, whether or not the transfer has a Data stage, and if so, in which direction the data will travel. Includes 8 bytes of control request information: bmRequestType, bRequest, wValue, wIndex, wLength. For more information about this fields, please refer to Chapter 5 of USB Complete Third Edition and [9.3 USB Device Requests from USB 2.0. Specification](http://www.poweredusb.org/pdf/usb20.pdf#%5B%7B%22num%22%3A939%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2Cnull%2Cnull%2Cnull%5D)
    > [!important] 
    > As described in [[#Data toggle]] in setup stage of control transfer data packet is always with DATA0 PID. 
- Handshake Packet
    Transmits the device's acknowledgement. If everything is OK then device sends ACK PID. This handshake is describes that device has gotten a request. But this handshake don't describe if the device can complete this request.

> [!important] 
> Devices must accept all Setup packets. A device that
is in the middle of another control transfer must abandon that transfer and
acknowledge the new Setup transaction.

#### Data Stage
Data stage presentation in Control Transfer and its length is defined by wLength field of Data Packet of [[#Setup Stage]]. If wLength field is 0, there is no Data stage. For example, in the Set_Configuration request, the host passes a configuration value to the peripheral in the wValue field of the Setup stage’s data packet, so there’s no need for a Data stage. So in this case immediately after Setup Stage starts [[#Status Stage]].

When present, the Data stage consists of one or more Data transactions, which may be IN or OUT transactions. Depending on the request, the host or device may be the source of these transactions, but **all data packets in this stage are in the same direction.**
In the Data stage, all data packets except the last must be the maximum packet size for the endpoint. The maximum packet size for the Default Control Pipe is configures in the [device descriptor](#Descriptors) by bMaxPacketSize0 field that the host retrieves during enumeration.
If all of the data can’t fit in one packet, the stage uses multiple transactions.
The number of transactions required to send all of the data for a transfer
equals the value in the Setup transaction’s wLength field divided by the
wMaxPacketSize value in the endpoint’s descriptor, rounded up.
> [!example] 
>  For example, in a Get_Descriptor request, if wLength is 18 and wMaxPacketSize is 8, the transfer requires 3 Data transactions.

Each IN or OUT transaction in the Data stage contains token, data, and
handshake packets

> [!warning] 
> When the Data stage is present but there is no data to transfer, the data phase consists of a zero-length data packet (the PID only). 

As described in [[#Handshake Packet]] if a high-speed control Write transfer has more than one data packet in the Data stage, and if the device returns NYET after receiving a data packet, the host may use the PING protocol before sending the next data packet.

> [!important] 
> As described in [[#Data toggle]], the first packet in data phase in Control(if if is present) transfer is DATA1. Any additional packets in the Data stage alternate DATA0/DATA1.

But if device got request in [[#Setup Stage]] that it doesn't support, then it should send STALL handshake on the first available subsequent stage. Usually at the Data stage but if there is no Data Stage(if wLength in request is 0) then at [[#Status Stage]].
So if wLength in request is not 0, so Data stage is present, then device should return STALL. 
- **If request is OUT** from host, then device should return STALL at handshake packet as answer on first Data OUT transaction, instead of ACK. For example, host is send OUT with some payload, but device doesn't support required request:
    - H -> SETUP PID; H -> Data with request inf.; D -> ACK
    - H -> OUT PID; H -> Data with payload; D -> **STALL**;
    - Status stage in this case is canceled
- **If request is IN** - device sends data to host. Then device should send STALL PID instead of DATAx PID at the first Data stage transaction. For example, host is sends request IN, but device doesn't support required request:
    - H -> SETUP PID; H -> Data with request inf.; D -> ACK
    - H -> IN PID; D -> STALL PID(instead of DATAx)
    - Status stage in this case is canceled

> [!important] 
> After first STALL returnment, device will return STALL in response to any IN or OUT transaction on the pipe until the SETUP transaction is received.

#### Status Stage
In addition to reporting the status of every transactions in the handshake packet, the same ACK, NAK, and STALL codes report the success or failure of complete control transfers.

Specifically, the status code of all control transfer is send in Data packet of the Status Stage. 
This data packet is a zero-length data packet has <span style="color: red">always</span> DATA1 PID in success, or this data packet has NAK. 
Or STALL PID can be returned in Status Stage, if device don't support request that host send in [[#Setup Stage]] and there no Data Stage(wLength field is equal to 0 in Data packet of [[#Setup Stage]]). Because device should send STALL handshake on the first available subsequent stage. 
> [!help] 
>  A transaction with a zero-length data packet is a transaction whose Data phase consists of a PID and error-checking bits but no data.

Table below shows the structure of all packets in status stage.
![[Pasted image 20250813134649.png]]

### Control Write/Read

> [!important] 
>  In control Write and Read direction is always described from the **host's perspective**. So Control Write is a Control Transfer when host sends data to device and Control Read is a Control Transfer when device sends to host.

In a **control Write** transfer, the data in the Data stage travels from the host to the device. Control transfers that have no Data stage are also considered to be control Write transfers.

Figure below shows the stages of control Write transfer on a low/full-speed bus.
![[Pasted image 20250813190707.png|400]]

In a **control Read**  transfer, the data in the Data stage travels from the device to the host.
![[Pasted image 20250814092333.png|400]]
> [!attention] 
> In a Control Read transfer’s Data stage, the host acknowledges received data with an ACK and then sends an OUT token to start the Status stage. If the device misses the ACK after the final data packet, it treats the subsequent OUT token as confirmation that the ACK was sent and proceeds to the Status stage.
>  <span style="color: red">So it is important in firmware of device to have a opportunity to abandon any Control transfer Data stage in progress and begin a Status Stage. On receiving an OUT token packet, the device must assume that the host is beginning the Status stage of the transfer even if the device hasn’t sent all of the requested data in the Data stage.</style>

Devices don’t have to respond immediately to control-transfer requests. The USB specification includes timing limits that apply to most requests.
> [!warning] 
>  But device class may require faster response to standard and class-specific requests.

Where stricter timing isn’t specified, in control Read device may delay as long as **500 milliseconds** before making the data available to the host. To find out if data is available, the host sends a token IN packet requesting the data on the data stage. If device has no ready data, the device sends NAK to advise the host to retry later. The host keeps trying at intervals for up to 500 milliseconds.
In control Write transfer, the device can delay as long as **5 seconds** before accepting all of the data and completing the Status stage.

> [!note] 
> Status stage must be complete within 50 milliseconds after the device is ready to send the status. If control transfer has no data stage, the device must complete the request and the Status stage within 50 milliseconds!

Control transfers use [[#Data toggle]] to ensure that no data is lost. Setup Stage always use DATA0, Data Stage always use DATA1 in the first transaction, toggle the bit in any additional data stage transactions, and always uses DATA1 in the Status Stage with zero-length data packet in success of control transfer(or NAK or STALL PIDs if an error occur).

## Bulk Transfer
Bulk transfers are useful for transferring data when time isn’t critical. A bulk transfer can send large amounts of data with efficiently usage of available bus bandwidth by waiting for gaps in higher-priority traffic, ensuring they don’t congest the bus.

> [!important] 
>  Only full- and high-speed devices can do bulk transfers. Devices aren’t required to support bulk transfers, though a specific device class may require it. For example, a device in the mass-storage class must have a bulk endpoint in each direction.

> [!warning] 
>  The USB specification doesn’t define a protocol for specifying what amount of data is expected in a bulk transfer. When needed, the device and host can use a class-specific or vendor-specific protocol to pass this information. For example, a transfer can begin with a header that specifies the number of bytes to be transferred, or the device or host can use a class-specific or vendor-specific protocol to request a quantity of data.

The host controller guarantees that bulk transfers [will complete eventually](https://www.youtube.com/watch?v=7JYJhWIwGUw&t=4s) but doesn’t reserve any bandwidth for the transfers. So if a bus is very busy, a bulk transfer may take very long.

However, when the bus is otherwise idle, bulk transfers can use the most bandwidth of any type, and they have a low overhead, so they’re the fastest of all.

At full speed on an full idle bus, up to nineteen 64-byte bulk transfers can transfer up to 1216 data bytes per frame, for a data rate of 1.216 Megabytes/sec. This leaves 18% of the bus bandwidth free for other uses.
At high speed on an full idle bus, up to thirteen 512-byte bulk transfers can transfer up to 6656 data bytes per microframe, for a data rate of 53.248 Megabytes/sec., using all but 2% of the bus bandwidth.

- [ ] #todo Please compute this by your own to verify this. Do it after you fully understand the difference between overhead of full- and high-speed transaction. Because the protocol overhead for a bulk transfer with one data packet is 13 bytes at full speed and 55 bytes at high speed(I think this is because of the difference of IDLE and EOP frames) 🔽

## Interrupt Transfer
Interrupt transfers are useful when data has to transfer periodically within a specific amount of time. Typical applications include keyboards, pointing devices, game controllers, and hub status reports. Users don’t want a noticeable delay between pressing a key or moving a mouse and seeing the result on screen.

"Interrupt transfer" is so called because it simulates the interrupt operation model, giving a guaranteed response time, although in fact everything is based on periodic polling by the host.

Interrupt transfer guarantees that the host will attempt to receive data from the device in less than a certain time interval (maximum delay).

The endpoint descriptor stored in the device determines the maximum delay period using the bInterval field. Please refer to 9.6.6. chapter in [USB 2.0. specification](http://www.poweredusb.org/pdf/usb20.pdf) for more information about bInterval field.
The host may begin each transaction at any time up to the specified maximum latency since the previous transaction began. So, for example, with a 10-millisecond maximum at full speed, five transfers could take as long as 50 milliseconds or as little as 5 milliseconds(because each full-speed USB frame is 1 millisecond long).

Because the host is free for attempting to receive data more quickly than the specified maximum latency, interrupt transfers don't guarantee a precise rate of delivery. The only exceptions are when the maximum latency equals the fastest possible rate. For example a full-speed interrupt endpoint configured for 1 transaction per millisecond, so he will have bandwidth reserved for one transaction in each frame.
Bus without any transfers(full idle bus) can carry up to six low-speed, 8-byte transactions per frame.
> [!note] 
> A **low-speed interrupt endpoint** is limited to **8 bytes every 10 ms**, with a maximum of **two low-speed endpoints per device**. This restriction exists because low-speed USB consumes significantly more bus bandwidth than full- or high-speed for the same data volume.

At full speed, nineteen 64-byte transactions can fit in a frame(but of course each transaction should be from different endpoints). At high speed, the limit is two transfers per microframe, with each transfer consisting of three 1024-byte transactions.

A high-speed endpoint can request up to three 1024-byte packets in each 125-microsecond microframe, which works out to 24.576 Megabytes/sec. High-speed endpoint can transmit more then 1 data packet in one microframe, because high-speed implements additional transaction system, check [[#Endpoints and pipelines]] to learn how to set up additional transactions for high-speed endpoint.

A full-speed endpoint can request up to 64 bytes in each 1-millisecond frame, or 64 kilobytes/sec. A low-speed endpoint can request up to 8 bytes every 10 milliseconds, or 800 bytes/sec.

> [!important] 
>  High-speed **interrupt and isochronous transfers** are capped at **80% of a microframe**, while low-/full-speed **interrupt and isochronous transfers** are limited to **90% of a frame**.
> Before selecting a device configuration that uses interrupt bandwidth, the host controller checks whether the requested bandwidth is available. It does this by comparing the available unreserved bus bandwidth with the maximum packet size and transfer rate of the configuration’s isochronous endpoints. If the device requests more bandwidth than is available, the host refuses to configure the device.
>  Low- and full-speed interrupt transfers consume relatively little bandwidth, so the host rarely denies a configuration because of them. However, a high-speed endpoint can request up to three 1024-byte packets per microframe, potentially using as much as 40% of the bus bandwidth.  
>  
>  To help ensure smooth [enumeration](#Enumeration), the USB specification requires that high-speed interrupt endpoints in a default interface have a maximum packet size no larger than 64 bytes.
>  However, an interface can have other [[#Interface alternate settings]] where the maximum packet size for an interrupt endpoint exceeds 64 bytes. If there is sufficient free bandwidth on the USB bus, the host driver may try to increase the endpoint’s reserved bandwidth by selecting a different alternate interface setting or configuration.

In an interrupt transfer on a high-speed bus with a low- or full-speed device, the host uses the [[#Split Transactions]]. Unlike high-speed bulk OUT transfers, high-speed interrupt OUT transfers can’t use the  PING protocol when a transfer has multiple transactions.

Interrupt transfers can use data toggles to ensure that all data is received without errors. But specification allow the programmer to configure interrupt IN endpoint to toggle its data toggle in each transaction without checking for the host’s ACKs, at the risk of losing some data. It is not configurable by descriptor or something like that. This behavior is described by firmware itself.

## Isochronous Transfer
Isochronous transfers are streaming, real-time transfers that are useful when data must arrive at a constant rate, or by a specific time, and where occasional errors can be tolerated.
 
The pros of isochronous is that at full speed, isochronous transfers can transfer more data per frame than interrupt transfers(1023 frames versus 64 frames), but there is no provision for retransmitting data received with errors.

Examples of uses for isochronous transfers include encoded voice and music to be played in real time. But data in an isochronous transfer doesn't have to be consumed at a constant rate. An isochronous transfer is a way to ensure that a large block of data gets through quickly on a busy bus, even if the data doesn’t need to transfer in real time. <span style="color:red">Host guarantees that the time will be available to send the data at a constant rate, so the completion time is predictable.</span>

Isochronous means equal in duration to something, has the same in duration with something. So isochronous means that the data has a fixed transfer rate, with a defined number of bytes transferring in every frame or microframe. None of the other transfer types is guarantee bandwidth for a specific number of bytes in each frame (except interrupt transfers with the shortest maximum latency).

A frame(microframe) intervals for full-speed(high-speed) intervals is defined in bInterval field of endpoint descriptor and calculates as $2^("bInterval-1")$ frames(microframes). Of course you can also send three transactions per this interval only for high-speed(it is configurable in wMaxPacketSize).

> [!important] 
> Before selecting a device configuration that consumes isochronous bandwidth, the host controller determines whether the requested bandwidth is available by comparing the available unreserved bus bandwidth with the maximum packet size and transfer rate of the configuration’s isochronous endpoint(s). 
> For example, to show how bandwidth-hungry isochronous transfer is, A full-speed transfer with the maximum 1023 bytes per frame uses 69%[(funny number)](https://www.youtube.com/watch?v=lcsXGHl_hwg) of the bus’s bandwidth.
> To cope with this problem USB 2.0. specification require device to configure full- or high-speed isochronous endpoint with no requested bandwidth in default interface, so the host can configure device at moment of plugging. In addition to this interface and an interface that requests the optimum bandwidth for a device, a device can have alternate interface that have smaller isochronous data packets or use fewer isochronous packets per microframe. 
> So after initial [[#Enumeration]] the device driver is then free to try to increase the endpoint’s reserved bandwidth by requesting alternate interface settings or configurations.

> [!hint] 
> Any endpoint can transfer less data than the maximum reserved bandwidth by skipping available transactions or by transferring less than the maximum data per transfer. If device request more bandwidth than is available, the host  refuses to configure the device.

> [!caution] 
> Although isochronous transfers may send a fixed number of bytes **per frame**, but the **exact timing within the frame/microframe is not fixed**, because interrupt transfer should share the bus with other devices(interrupt and isochronous transfers are share **80%** of microframe for high- and 90% of frame for full-speed). So the isochronous data may occur any time within the frame or microframe.

Within a transfer, the packet size of data in each transaction doesn't have to be the same. 

> [!example] 
> For example, if we have audio stream with 44100 sampling frequency, then we should send 44100 samples every second. On full speed we have 1000 frames in a second. So we should send $frac(4 4 1 0 0, 1 0 0 0)=4 4.1$ samples. But we can't send a fractional number of samples, so we can use next sequence of data transfering
> 1. 9 transfers in a row we send 44 samples
> 2. 1 transfer send a 45 samples
> 
> Then we have $(9*4 4+4 5)*1 0 0 = 4 4 1 0 0$ samples in a second! 

A full-speed isochronous transaction can transfer up to 1023 bytes per
frame, or up to 1.023 Megabytes/sec. This leaves 31% of the bus bandwidth free for other uses. 
A high-speed isochronous transaction can transfer up to 1024 bytes. An isochronous endpoint that requires more than 1024 bytes per microframe can request 2 or 3 transactions per microframe, for a maximum rate of 24.576 Megabytes/sec

## Common for several types of transfer 

Every data transaction(all transactions in Bulk/Interrupt/Isochronous transfers or Data Stage of Control Transfer) is ends in one of three ways: 
1. When the expected amount of data has transferred 
2. When number of bytes that device can send is less then expected, but last transfer has a packet size that is a endpoint’s maximum packet size. And because of this host can't determine if the device has no more data to send. To resolve this, the device should send a zero-length data packet in response to the next IN token packet that arrives after all of the data has been sent.
3. When last transaction will have a packet size of bytes that is less than the endpoint’s maximum packet size. In this case host see that last transaction is not a full packet size and understand that endpoint has no more data to send.

> [!attention] 
>  Be sure to check that firmware of the device implemented an opportunity to send zero-length data packet if 2 case is appeared!

> [!important] 
> Interrupt/Isochronous transfers have a restriction: one transaction per frame. Bulk/Control transfers don't have this limits. 

The USB specification doesn’t define a protocol for specifying the amount of data that expected in an Interrupt/Bulk/Isochronous transfer. When needed, the device and host can use a class-specific or vendor-specific protocol to pass this information. For example, a transfer can begin with a header that specifies the number of bytes to be transferred, or the device or host can use a class-specific or vendor-specific protocol to request a quantity of data.

A Interrupt/Bulk/Isochronous transfer is one-way: the transactions must all be IN transactions or all OUT transactions. Transferring data in both directions requires a separate [pipes](#Endpoints%20and%20pipelines) and transfer for each direction.

***

# Special PID

Of the four special PIDs, one is used only with low-speed devices, one is used only with high-speed devices, and the remaining two are used when a low- or full-speed device is connected to USB high speed bus.

![[Pasted image 20250812193026.png]]

## Split Transactions

### PRE packet

### SPLIT packet

# Enumeration
Before applications can communicate with a device, the host needs to learn about the device and assign a device driver. Enumeration is the exchange of information that accomplishes these tasks.

The process includes assigning an address to the device, reading descriptors from the device, assigning and loading a device driver, and selecting a configuration that specifies the device’s power requirements, endpoints, and other features

One of the duties of a hub is to detect the attachment and removal of devices. Each hub has an interrupt IN endpoint for reporting these events to the host.

## Device states
The USB specification defines six device states. During enumeration, a device moves through four of the states: Powered, Default, Address, and Configured. (The other states are Attached and Suspend.)

Figure below is a device state diagram
![[Pasted image 20250815154559.png|400]]

- **Attached:** Occurs when a device is attached to a host/hub, but does not give any power to the VBUS line. This is commonly seen if the hub detects an over current event. The device is still attached, but the hub removes power to it.
- **Powered:** A device is attached to the USB and has been powered, but has not yet received a reset request.
- **Default:** A device is attached to the USB, is powered, and has been reset by the host. At this point, the device does not have a unique device address. The device responds to address 0.
- **Address:** A device is attached to the USB, powered, has been reset, and has had a unique address assigned to it. The device however has not yet been configured.
- **Configured:** The device is attached to the USB, powered, has been reset, assigned a unique address, has been configured, and is not in a suspend state. At this point, bus-powered devices can draw more than 100 mA.
- **Suspend:** A device enters the Suspend state after detecting no bus activity, including Start-of-Frame markers, for at least 3 milliseconds. In the Suspend state, the device should limit its use of bus power. Both configured and unconfigured devices must support this state. For exiting from this state, host can send [resume signal](#Signaling%20levels) for at least 20 ms to all devices and then end the resume signaling in one of two ways, depending on the speed at which its port was operating when it was suspended. If the port was in low-/full-speed when suspended, the resume signaling must be ended with a standard, low-speed [EOP](#EOP). In high-speed - must be ended with a transition to the high-speed idle state.

## Enumeration steps

The steps below are a typical sequence of events that occurs during enumeration.
> [!warning] 
> But device firmware must not assume that the enumeration requests and events will occur in a particular order

> [!attention] 
>  ![[mHKjIAmK2g8v6tplGgiroky4KiRScm-1fvyZIkPs3bw.webp|150]]
>  [Picture only to attract maximum attention](https://youtube.com/shorts/5FYxUaRykQ0?si=kOcdzR7O3j17zQGw). Enumeration steps description below use knowledge of the control transfer requests, descriptor types and descriptor fields. This themes is not described in this note(except for small descriptions of each descriptor function in [[#Descriptors]]), so to get more information about these themes see [Chapter 9.3 and 9.4 USB Device Requests](http://www.poweredusb.org/pdf/usb20.pdf#%5B%7B%22num%22%3A939%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2Cnull%2Cnull%2Cnull%5D) and [Chapter 9.6 Standard USB Descriptor Definitions](http://www.poweredusb.org/pdf/usb20.pdf#%5B%7B%22num%22%3A978%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2Cnull%2Cnull%2Cnull%5D) of USB 2.0. specification or Chapter 4-5 of "USB Complete" book by Jan Axelson😘

1. **The user attaches a device to USB port.** Or the system powers up with a device already attached. The hub provides power to the port, and the device is in the <span style="color: orange">Powered State</span>, so device now can draw up to 100 mA from the bus. If an over current event is occurred due to some error, the device will be in <span style="color: orange">Attached state</span> so the hub removes power to device.
2. **The hub detects the device.** The hub monitors the voltages on the signal lines D+ and D-. The hub has a pull-down resistor of 14.25 to 24.8 kilohms on each of the port’s two signal lines (D+ and D-). A device has a pull-up resistor of 900 to 1575 ohms on either D+ for a full- and high-speed devices or D- for a low-speed device.
![[Pasted image 20250815161101.png|400]]
When a device plugs into a port, the device’s smaller pull-up resistor brings its line high, enabling the hub to detect that a device is attached.
On detecting a device, the hub continues to provide power but doesn’t yet transmit USB traffic to the device.
> [!note] 
> Except for some devices with weak or dead batteries, the device must connect within 1 s after detecting that V BUS is at least 0.8 V. 

3. **The host learns of the new device.** Each hub uses its interrupt endpoint to report events to the host. The report indicates only whether the hub or a port of the root hub(and if so, which port) has experienced an event. On learning of an event, the host sends the hub a Get_Port_Status request to find out more.
4. **The hub detects whether a device is low or full speed.** The hub determines whether the device is low or full speed by examining the voltages on the two signal lines. The hub detects the speed of a device by determining which line(D+ for full- or high-speed or D- for low-speed) has the higher voltage when idle. The hub sends the information to the host in response to the next Get_Port_Status request.
5. **The hub resets the device.** When a host learns of a new device, he waits at least 100 ms to allow completion of an insertion process and for power at the device to become stable. After this, the host controller sends the hub a Set_Port_Feature request that asks the hub to reset the port. The hub places the device’s USB data lines in the Reset condition for at least 10 milliseconds.
Reset is a special condition(Single ended 0 SE0) where both D+ and D- are a logic low.
6. **The host learns if a full-speed device supports high speed.** Detecting whether a device supports high speed uses two special signal states(J and K states, for more information about this states see [[#Signaling levels]] and [Table 7-2. of USB 2.0. specification](http://www.poweredusb.org/pdf/usb20.pdf#%5B%7B%22num%22%3A617%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2Cnull%2Cnull%2Cnull%5D))
During the reset, a device that supports high speed sends a K State(not a SE0 that he should send). A USB 2.0. hub detects the chirp and responds with a series KJKJKJ. If device detects this patern, the device removes its full-speed pull up and performs all further communications at high speed, otherwise the device knows it must continue to communicate at full speed.

7. **The hub establishes a signal path between the device and the bus.** The host polling the device by sending Get_Port_Status request to the hub until the device has exited the reset state.
When the hub removes the reset condition, the device is in the <span style="color: orange">Default state</span>, so he is exit from reset, and next host Get_Port_Status request will be answered with Default status. 

Now the device’s USB registers are in their reset states and the device is ready to respond to control transfers at Endpoint 0. The device communicates with the host using the default address of 0x00. The device can draw up to 100 milliamperes from the bus.
> [!important] 
>  Host can enumerate only one device at a time, so only one device will respond to address 0x00, even if several devices attach at once.

8. **The host sends a Get_Descriptor request to learn the maximum packet size of the control pipe.** The host sends the request to device address 0, Endpoint 0.
The host don't know size of the endpoint 0 to which he must conduct Control transfers. Data about endpoint 0 size are in eighth byte of the device descriptor because the smallest packet size is 8 bytes for low- and full-speed control transfers, so host should in any case receive an endpoint size value of 0 in the first packet.
So Windows host requests 64 bytes(because this is the maximum possible control transfer package) Get_Descriptor of device descriptor, but after receiving just one [Data packet of control transfer](#Data%20Stage)(whether or not it has 64 bytes, because all host needs is the first 8 bytes), the host begins the [[#Status Stage]] of the transfer. On completion of the Status stage, a Windows host requests the hub to reset the device, as in Step 5 above.
> [!note] 
>  The USB specification doesn’t require a reset here. This is a whim of Windows. Resetting is a precaution that ensures that the device will be in a known state when the reset ends.

9. **The host assigns an address.** Now host know the endpoint 0 size, and now he can configure the device correctly through endpoint 0. 
The host controller assigns a unique address to the device by sending a Set_Address request. The device completes the Status stage, and <span style="color: red; font-size: 20">only after Status stage</span> device change address. The device is now in the <span style="color: orange">Address state</span>
The address is valid until the device is detached, the port is reset, or the system reboots.


10. **The host learns about the device’s abilities.** The host sends a Get_Descriptor request of device descriptor again as in step 8, but now he request to the previously set address. This time the host retrieves the entire descriptor. So now host know number of configurations of the device. In full device descriptor host learn how many configurations device have. Now host want to get all configuration descriptors.
A request for a **configuration descriptor**(GET_DESCRIPTOR with wValue=0xX2 where X is Configuration Index) is actually a request for the configuration descriptor followed by all of that descriptor’s subordinate descriptors: interfaces and their endpoints. If, for example, the host requests 255 bytes, the device responds by sending the configuration descriptor followed by all of the configuration’s subordinate descriptors, including interface descriptor(s), with each interface descriptor followed by any endpoint descriptors for the interface. <span style="color: grey">Some configurations also have class- or vendor-specific descriptors.</span>
So first of all, host should check the Length of configuration descriptor which includes all subordinate descriptors, so at first Get_Descriptor request of configuration descriptor, host requires only 9 bytes, because configuration descriptor itself is 9 bytes long. In received data host checks the wTotalLength field to find out the full size of the **configuration descriptor and all subordinate descriptors**. And only after that host request Get_Descriptor of configuration descriptor with full length in bytes to get all needed descriptors.
If **device descriptor** on step 8 tells that device has 1 configuration, then host conducts the entire sequence described above only for Get_Descriptor with wValue index 0x02 only. But if there are several configurations, host conducts the entire sequence for several Get_Descriptor requests with wValue indexes from 0x02 to 0x(conf_numbers-1)2.

11. **The host assigns and loads a device driver.** After learning about a device from its descriptors, the host looks for the best match in a device driver to manage communications with the device. In selecting a driver, Windows tries to match the information in the PC’s INF files with the Vendor ID, Product ID, and (optional) release number retrieved from the device. If there is no match, Windows looks for a match with any class, subclass, and protocol values retrieved from the device. After the operating system assigns and loads the driver, the driver may request the device to resend descriptors or send other class-specific descriptors.

12. **The host’s device driver selects a configuration.** After learning about a device from the descriptors, the device driver requests a configuration by sending a Set_Configuration request with the desired configuration number. Some devices support only one configuration.
The device is now in the <span style="color: orange">Configured state</span> and the device’s interface(s) are enabled.
For composite devices(which combines multiple independent functions, so they have different drivers assigned to different interfaces in a configuration), the host assigns drivers at this point

## Interface alternate settings

Each interface can have multiple **alternate settings**. For example, a USB microphone implements an audio capture function through an interface. This interface can support different sampling rates, such as 8 kHz, 16 kHz, or 48 kHz.

The host can choose which sampling rate it wants by selecting the appropriate **alternate setting** of the interface.

Each interface alternate setting should consist its own Interface descriptor with related to this interface endpoint descriptors. This interface descriptors should contain similar `bInterfaceNumber` field but different `bAlternateSetting`.

And host can choose the interface setting after [[#Enumeration]] by SET_INTERFACE request.

## Descriptors

**USB descriptors** are the data structures, or formatted blocks of information, that enable the host to learn about a device. Each descriptor contains information about the device as a whole or an element of the device.

As enumeration progresses, the requested descriptors concern increasingly small elements of the device: first the entire device, then each configuration, each configuration’s interface(s), and finally each interface’s endpoint(s). 

Table below lists the descriptor types.
![[Pasted image 20250815202220.png|550]]

Devices that support both full and high speeds support two additional descriptor types: device_qualifier and other_speed_configuration. These and their subordinate descriptors contain information about the device’s behavior when using the speed not currently selected.

The table above contains a value of descriptor identifiers for the standard descriptor types. In addition to the standard descriptors, a device may contain class- or vendor-specific descriptors. Two examples of class codes are 29h for a hub descriptor and 21h for a HID descriptor. Within the HID class, 22h indicates a report descriptor and 23h indicates a physical descriptor.

In the descriptor’s bDescriptorType value, bit 7 is always zero. Bits 6 and 5 identify the descriptor type: 0x00=standard, 0x01=class, 0x02=vendor, 0x03=reserved. Bits 4 through 0 identify the descriptor.

The higher-level descriptors inform the host of any additional, lower-level descriptors.

This note has only the small descriptions of each descriptor function. All information about descriptor field and values you can find in the [Chapter 9.5 of USB 2.0 specification](http://www.poweredusb.org/pdf/usb20.pdf#%5B%7B%22num%22%3A978%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2Cnull%2Cnull%2Cnull%5D) and in Chapter 4 of USB Complete book by Jan Axelson

> [!note] 
> Each descriptor consists of a series of fields. Most of the field names use prefixes to indicate something about the format or contents of the data in that field: b = byte (8 bits), w = word (16 bits), bm = bit map, bcd = binary-coded decimal, i = index, id = identifier. For example field **b**Length in device descriptor is **b**yte length field that describes length of descriptor in bytes. But **id**Vendor is an identifier of Vendor of this device

- Device descriptor
	The device descriptor contains basic information about the device. This descriptor is the first one the host reads on enumeration process and includes the information the host needs to retrieve additional information from the device
- Device_qualifier descriptor
	Devices that support both full and high speeds must have a device_qualifier descriptor. When a device switches speeds, some fields in the device descriptor may change. The device_qualifier descriptor contains the values of these fields at the speed not currently in use. In other words, the contents of fields in the device and device_qualifier descriptors swap depending on which speed is being used. A host retrieves a device_qualifier descriptor by sending a Get_Descriptor request with the high byte of the Setup transaction’s wValue field equal to 6.
- Configuration descriptor
	Each device has at least one configuration that specifies the device’s features and abilities. Often a single configuration is enough, but a device with multiple uses or modes can support multiple configurations. Only one configuration is active at a time. 
	The configuration descriptor contains information about the device’s use of power and the number of interfaces supported. Each configuration descriptor has subordinate descriptors, including one or more interface descriptors and optional endpoint descriptors. A host retrieves a configuration descriptor and its subordinate descriptors by sending a Get_Descriptor request with the high byte of the Setup transaction’s wValue field equal to 2.
	The host selects a configuration with the Set_Configuration request and reads the current configuration number with a Get_Configuration request
- Other_speed_configuration descriptor
	The other descriptor unique to devices that support both full and high speeds is the other_speed_configuration descriptor. The structure of the descriptor is identical to that of the configuration descriptor. The only difference is that the others-speed_configuration_descriptor describes the configuration when the device is operating at the speed not currently active. The other_speed_configuration descriptor has subordinate descriptors just as the configuration descriptor does. A host retrieves an other_speed_configuration descriptor by sending a Get_Descriptor request with the high byte of the Setup transaction’s wValue field = 7.
- Interface Association Descriptor
	

***

# USB drivers

There are two types of drivers, common driver for device-class, and device specific drivers.

Common driver is chosen by bDeviceClass in Device descriptor, or by bInterfaceClass in Interface descriptor. After reading the descriptors, host loaded class-based drivers that are loaded without Vendor/Product ID

If device has some specific functionality, then they have device specific drivers. They are selected by Vendor/Product ID pairs. Vendors IDs should be bought from USB-IF, and then Vendor can use any Product ID. But of course he should write his own driver for this Product ID and type it in inf file for Windows.

And of course you can't use someone else's vendor/product IDs for commercial purpose. But there are companies that divide the VID and can give you a range of PIDs for less money.

And for study projects you can get PID for open-source devices or PIDs from TinyUSB and OpenMoko. Or just use PIDs from MCU developers, for example STMicroelectronics. You can use this PIDs only for study projects

You can check existed in Windows/Linux Vendor/Product ID from some companies in  [usb-ids.gowdy.us/usb.ids](https://usb-ids.gowdy.us/usb.ids)

***

# Host responsibilities

- [ ] #todo I think this text is very bad due to my baby-boo-boo knowledge of OS work. So MAAAAAAAAYBE after 3000 years I will redeem this text...⏬ 

As i said in [[#What is USB]] in USB bus host like master node, initiates all transactions via giving tokens to each node. 

The host needs to know what devices are on the bus and the capabilities of each device. When a new device is connected to a hub, the hub collects all information about the device via the device descriptor. In a process called enumeration, the host determines what bus speed to use, assigns an address, and requests additional information.

All communication with USB Data link layer are produces by root hub in your computer. It has its own controller, this root hub controller is responsible for CRC and bit-stuffing checks, split-transactions, scheduling transactions to manage bandwidth and prioritize different types of transfers.

The process begins with the **programmer’s application code**, which interacts with the USB device through a high-level programming interface(for example Windows API or other C++ frameworks). The programmer uses these APIs to send commands, read data, or configure the device. These APIs abstract away the low-level details of USB communication, allowing the programmer to focus on the application logic rather than the intricacies of USB protocols.
The **USB device driver** acts as a bridge between the high-level application code and the hardware. The driver is responsible for translating the programmer’s requests into a format that the USB root hub controller can understand. Drivers are typically written to work with specific USB devices or classes of devices (e.g., HID for keyboards, mass storage for flash drives). They handle tasks like initializing the device, managing data transfers, and handling errors.
The driver also interacts with the **USB stack** in the operating system, which provides the necessary infrastructure for communicating with USB devices. The **operating system’s USB stack** is a critical layer that manages communication between the driver and the USB hardware.
These components work together to manage the USB bus, handle device enumeration, and route data between the driver and the hardware.
When the driver sends a request to the USB stack, the stack translates that request into a format that the **USB host controller** can execute.

## Some advices on the host side

The driver of some USB device requests a transfer by submitting an I/O request packet(IRP) to a **USB stack** of operational system. For interrupt and isochronous transfers, if there is no outstanding IRP for an endpoint when its scheduled time comes up, the host controller skips the transaction attempt.
To ensure that no transfer opportunities are missed, drivers typically submit a new IRP immediately on completing the previous one.

The application software that uses the data also has to be able to keep up with the transfers. For example, the driver for HID-class devices places report data received in interrupt transfers in a buffer, and applications use ReadFile to retrieve reports from the buffer. If the buffer is full when a new report arrives, the driver discards the oldest report and replaces it with the newest one. If the application can’t keep up, some reports are lost. A solution is to increase the size of the buffer the driver uses to store received data or to read multiple reports at once.

All programs that uses USB are multi-thread. Because it is ensure that an application sends or receives data with minimal delays. But there are latencies due to how Windows(or other OS) handles multi-tasking. Because all OS that we use in our PC is never designed as a real-time operating systems that could guarantee a rate of data transfer with a peripheral.
A USB device and its software have no control over what other tasks the
host CPU is performing and how fast the CPU can perform them, so dealing with these latencies can be a challenge when timing is critical.
So it is crucial to make a firmware to USB device that is not-depends on host latencies.
For example, if interrupt transfer is skipped by host for any reason, the device readings can rewrite the data to transfer and thus the host may lose important data. But if the device instead collects a series of readings and transfers them using less frequent, but larger transfers,  the timing of the bus transfers is less critical.
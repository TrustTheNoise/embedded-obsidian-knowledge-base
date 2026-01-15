Tags: #periferal_interface 
> [!sources] 
>  USB complete the developer's guide by Jan Axelson Fifth edition 7 Chapter
>  Serial Port Complete by Jan Axelson 16 chapter

***

<span style="font-size: 25">List of content:</span>

```table-of-contents
```

***

<span style="font-size: 25">Tasks:</span>

```tasks
```

***

# Communications device class

The communications device class (CDC) includes a wide range of devices that
perform telecommunications, networking, and other communication functions
including virtual serial ports and "medium-speed" networking devices.

 The telephones group includes generic virtual COM port devices as well as analog phones and modems, ISDN terminal adapters, and cell phones. Networking devices include ADSL modems, cable modems, and Ethernet adapters and hubs. The USB interface in these devices can carry data that uses application-specific protocols such as V.25ter/V.250 for modem control or Ethernet for a network.

CDC class can defined in [Device descriptor](USB%202.0.#Descriptors) in `bDeviceClass` field if all interfaces of some device is CDC specific, or we can define class to each Interface in Interface descriptor in `bInterfaceClass` field, for example if device have CDC Interfaces and Audio Interfaces. 

Code for CDC class is specified in USB specification and equals to 0x02.

A USB CDC device is responsible for device management, call management if
needed, and data transmission. Device management includes controlling and configuring the device and notifying the host of events. Call management includes establishing and terminating telephone calls or other connections. **Some devices don’t need call management.** Data transmission is the sending and receiving of application data such as phone conversations, files, or other data sent over a modem or network.

# CDC subclasses

CDC supports five basic models for communicating. Each model includes one or more subclasses:
- **The POTS (Plain Old Telephone Service) model** is for devices that commu-
nicate via ordinary phone lines and generic COM-port devices. Ethernet
devices that comply with Microsoft’s USB Remote Network Driver Interface
Specification (NDIS) also use the POTS model.
- **The ISDN model** is for communications via phone lines with ISDN inter-
faces
- **The networking model** is for communicating via Ethernet or ATM (asyn-
chronous transfer mode) networks.
- **The wireless mobile communications (WMC) model** includes cell phones
that support voice and data communications.
- **The Ethernet emulation model (EEM)** defines an efficient way for devices
to send and receive Ethernet frames.

As I said above, each model includes several USB CDC subclasses. This subclasses defines in `bDeviceSubClass` field for Device descriptor or `bInterfaceSubClass` for Interface descriptor.

All subclasses for each Model Category for communication with it code for `bDeviceSubClass` or `bInterfaceSubClass` is described in the table below:

![[CDC subclasses.jpg|700]]
- [ ] #todo This table isn't full. New CDC specification of 1.2 revision also added NCM and MBIM

***

# Virtual COM port

>[!source]
>[Universal Serial Bus Communications Class Subclass Specification for PSTN Devices Revision 1.2](https://gzuliani.github.io/arduino/files/arduino-android-usb/PSTN120.pdf)

To choose Virtual COM port as device class we must to write `bDeviceClass=0x02` for CDC class and `bDeviceSubClass=0x02` if device class is specified at the device level, or in analogous fields of Interface descriptor if device class is specified at the interface level.

The purpose of the Virtual COM Port (VCP) - is to emulate a traditional serial(COM) port over USB, allowing software on a host computer to communicate with a USB device as if it were connected through an old-fashioned RS-232 serial interface. The function performed by Virtual COM-port devices is sometimes called serial emulation.

Technically, this subclass translates **USB transfers into serial semantics**. Control requests over endpoint 0 mimic RS-232 configuration commands (`SET_LINE_CODING`, `SET_CONTROL_LINE_STATE`), and [CDC-class interface](#Virtual%20COM%20port#Descriptors) with interrupt endpoint provides serial-state notifications (for example, “ring” or “carrier detect”).
The actual data stream is carried through [CDC-Data interface](#Virtual%20COM%20port#Descriptors) with USB bulk endpoints — one IN, one OUT — representing the transmit and receive lines of a serial port.

## Descriptors

Virtual COM port device must have two interface descriptors: CDC-Control(also renown as Communication interface) and CDC-Data.

The CDC-Communication interface names the abstract control model subclass and defines an interrupt IN endpoint for sending notifications. The data interface defines two bulk endpoints for exchanging COM-port data.

Structure of Virtual COM port descriptors is listed below:
![[Pasted image 20251009133918.png|600]]

### CDC-Communication interface

First interface descriptor is CDC-Communication interface with `bInterfaceClass = 0x02`.
This interface is responsible for two main functions: **device management** and **call management**. Device management handles control, configuration, and status notifications (for example, reporting events to the host). Call management historically referred to establishing and ending telephone or network connections, though **many modern devices do not use this feature**.

In a Virtual COM Port implementation, the CDC Control interface mainly provides **serial-state notifications** — for example, signals like “ring,” “carrier detect,” or “break”—that emulate behavior of traditional RS-232 serial ports.

But you should understand that virtual COM-port implements through Abstract control mode subclass. And this subclass imposes restrictions because the The ACM defines how a USB device can emulate a serial port, but also this subclass is used for modems. So ACM devices should support modems AT commands.

Although nowadays ACM devices usage is only for Virtual COM Ports so modern ACM devices no longer use AT commands, they must still comply with these structural requirements for compatibility. So programmer should configure `bInterfaceProtocol=0x0A` in CDC-Communication interface descriptor. Where 0x0A means AT command protocol. Today, this value is kept purely for legacy reasons — operating systems like Windows rely on it to correctly recognize and load the standard virtual COM port driver

> [!tldr] 
> In short, the Virtual COM Port reuses the old “modem control” framework defined by the CDC-ACM subclass, keeping compatibility with existing USB class drivers even though no real modem or AT command communication is involved.

CDC-Communication interface includes Interface descriptor with `bInterfaceClass = 0x02`, `bInterfaceSubClass=0x02` and `bInterfaceProtocol=0x01`, series of CDC special **Communication Descriptors** and Endpoint Interrupt IN description. 

Endpoint Interrupt IN is used for event notifications and has a standard endpoint descriptor.

**Communication Descriptors** is a descriptors with `bDescriptorType=0x24 (CS_INTERFACE)`. Series of communication descriptors consist of a header functional descriptor followed by one or more functional descriptors that provide information about a specific communication function. 

Set of essential communication descriptors for each CDC-device with corresponding `bDescriptorSubtype` field value is listed below:
- Header Functional Descriptor(0x00)
    Marks the beginning of CDC functional descriptors and names the release number of the CDC specification the device complies with in `bcdCDC` field
- Abstract Functional Descriptor(0x02)
    The abstract control management functional descriptor contains a `bmCapabilities` field that identifies which requests and notifications the interface supports
    ![[Pasted image 20251009143733.png]]
- Call Management Functional Descriptor
    Tells the host how to handle “calls”. Virtual COM port doen't support calls handling, so all capabilities in this descriptor should be turn off. `bmCapabilities` indicates how call management is handled:
    - bit 0 = device handles call management itself
    - bit 1 = device can send data over Data Class interface
    For VCP both bits should be 0.
    `bDataInterface` field contains the bInterfaceNumber value for the device’s data class interface. However, the value isn’t used if the device doesn’t handle call management.
- Union Functional Descriptor
    The union functional descriptor defines a relationship among multiple interfaces in USB device.  The descriptor designates one interface as the controlling, or master, interface, which can send and receive certain messages that apply to the entire group. For example, a CDC-Communication interface can be a master interface for a group consisting of a CDC-Communication interface and a Data interface. The interfaces that make up a group can include communications-class interfaces as well as other related interfaces such as audio or HID.
    This descriptor includes `bControlInterface` that defines master interfase number and several `bSubordinateInterfaceX` that defines other interfaces in a union.

For more information about functional descriptors please refer to [5.3 Functional Descriptors of PSTN Devices USB specification](https://gzuliani.github.io/arduino/files/arduino-android-usb/PSTN120.pdf#%5B%7B%22num%22%3A39%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C100%2C507%2Cnull%5D)

### CDC-Data interface

In addition to the CDC-Communication interface, a Abstract control model requires an interface to carry application data. A CDC data class interface can perform this function. 

CDC-data interface descriptor must be defined with `bInterfaceClass = 0x0A`, `bInterfaceSubClass=0x00` and `bInterfaceProtocol=0x00`. The interface
can have bulk or isochronous endpoints for carrying application data. Each
endpoint has a standard endpoint descriptor. 

> [!note] 
>  Instead of a data class interface, some CDC devices use other class or vendor-specific interfaces to carry application data. For example, a telephone device might use an audio interface to send and receive voice data.


## Requests

CDC class requests are sent to endpoint 0 (the default control endpoint). They use a bmRequestType value that indicates a Class-specific request to the Interface recipient(because this request is for CDC-communication interface), and a bRequest field set to one of the CDC-defined request codes listed below.

|Request Name|bRequest|Description|Required for VCP|
|---|---|---|---|
|SEND_ENCAPSULATED_COMMAND|0x00|Sends a command in the format of the supported control protocol|Not needed for typical VCP|
|GET_ENCAPSULATED_RESPONSE|0x01|Requests a response in the format of the supported control protocol|Not needed for typical VCP|
|SET_COMM_FEATURE|0x02|Controls a communication feature|Optional for VCP|
|GET_COMM_FEATURE|0x03|Returns current settings for a communication feature|Optional for VCP|
|CLEAR_COMM_FEATURE|0x04|Clears a communication feature|Optional for VCP|
|SET_LINE_CODING|0x20|Sets asynchronous serial parameters (bit rate, stop bits, parity, data bits)|Recommended for VCP|
|GET_LINE_CODING|0x21|Requests asynchronous serial parameters (bit rate, stop bits, parity, data bits)|Recommended for VCP|
|SET_CONTROL_LINE_STATE|0x22|Sets RS-232 signals RTS and DTR|Optional but commonly implemented in VCP|
|SEND_BREAK|0x23|Sets RS-232 Break signal|Optional for VCP|

In this section I will describe only VCP required requests: SET_LINE_CODING, GET_LINE_CODING; and optional requests: SET_CONTROL_LINE_STATE, SEND_BREAK.

- SET_LINE_CODING and GET_LINE_CODING 
    set and request serial port parameters. Serial port parameters consists of 4 fields with 7 bytes total length. Parameters is sends in [data stage of contorl transfer](USB%202.0.#Data%20Stage). In SET_LINE_CODING request host writes the required parameters. In GET_LINE_CODING device sends its parameters
    Serial port parameters have following structure:
    ![[Pasted image 20251009194908.png|800]]
- SET_CONTROL_LINE_STATE
    This request is used by the host to **emulate the RS-232 control lines** (RTS and DTR) on the device. The two bits in the `wValue` field of the setup stage indicate the desired state of these lines, allowing the host to signal the device as if it were connected via a real RS-232 interface.
    ![[Pasted image 20251009200424.png|600]]
    For example if host sends SET_CONTROL_LINE_STATE with **RTS = 1** then host indicating that it is ready to receive data, and after that host starts the request for data
    If host sends SET_CONTROL_LINE_STATE with **DTR = 1** signals that the host is ready to establish the connection, while **DTR = 0** indicates that the host wants to terminate it.
- SEND_BREAK
    Requests the device to send an RS-232 break signal for the number of milliseconds specified in the `wValue` field of the request. If `wValue` = FFFFh, the device should maintain the break signal until receiving another SEND_BREAK signal with `wValue` = 0000h.
    > [!help] 
    > RS-232 break signal is a condition where the **TX line is held in a logical low state** for longer than a normal character frame.
    

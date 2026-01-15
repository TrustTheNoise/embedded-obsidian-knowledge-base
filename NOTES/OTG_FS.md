Tags: #stm32 #periferal_interface #stm32f4

> [!attention] 
> [Bad English](https://www.youtube.com/watch?v=Ka2ucZ1Bwyc) 
> Before reading this note please read [[USB 2.0.]]. And be sure that you fully understand [[USB 2.0.#Terminology]]


***

<span style="font-size: 25">List of content:</span>

```table-of-contents
```

***

<span style="font-size: 25">Tasks:</span>

```tasks
```

***

# What is it?
OTG_FS is a peripheral in the STM32F411 that provides the capability to work with USB. To be precise, it is fully compatible with both [[USB On-The-Go]] and [USB 2.0](USB%202.0..md). This means that this peripheral allows switching between host and device modes on the fly as described in USB On-The-Go, and it can also be configured as host-only or device-only for compatibility with the USB 2.0 specification. In host mode, OTG_FS supports both full-speed (12 Mbits/s) and low-speed (1.5 Mbits/s), while in device mode, it only supports full-speed. OTG_FS supports both HNP and SRP. The only requirement is an external circuit to increase the voltage from 3.3V to 5V on V_BUS.

OTG_FS поддерживает как HNP так и SRP. Единственное нужна внешняя схема для увеличения питания с 3.3V до 5V на V_BUS
- [ ] #todo What are HNP and SRP? Need a reference from the USB OTG file.

OTG_FS is supports both Host and Periferal(device) modes. When the OTG_FS controller is operating in one mode, the application must not access registers from the other mode. If an illegal access occurs, a mode mismatch interrupt is generated MMIS bit in the **GINTSTS** register.

But if OTG_FS switches from one mode to the other, all registers in the new mode must be reprogrammed as they would be after a power-on reset. But global registers will save their configuration.

## Host-mode 
For host mode stm32f411 has a:
- charge pump for $V_{BUS}$ voltage generator, that increase 3.3V to USB 2.0. standardized 5.0V
- Up to 8 host [pipes](USB%202.0..md#Endpoints%20and%20pipelines): each pipe is dynamically reconfigurable to allocate any type of USB transfer
- Built-in [hardware scheduler](#USB%20Host%20scheduler) holding:
    - Up to 8 [interrupt](USB%202.0..md#Interrupt%20Transfer) plus [isochronous](USB%202.0..md#Isochronous%20Transfer) transfer requests in the periodic hardware queue, this requests must be paleced in frames at fixed intervals.
    - Up to 8 [control](USB%202.0..md#Control%20Transfer) plus [bulk](USB%202.0..md#Bulk%20Transfer) transfer requests in the non-periodic hardware queue
    - Management of a shared RX FIFO, a periodic TX FIFO and a nonperiodic TX FIFO for efficient usage of the USB data RAM.

## Peripheral-mode
OTG_FS allows to have up to 7 [endpoints](USB%202.0..md#Endpoints%20and%20pipelines):
- 1 bidirectional control endpoint0
- 3 IN endpoint configurable to support [Bulk](USB%202.0..md#Bulk%20Transfer), [Interrupt](USB%202.0..md#Interrupt%20Transfer) или [Isochronous](USB%202.0..md#Isochronous%20Transfer) transfers
- 3 OUT endpoint configurable to support Bulk, Interrupt or Isochronous transfers
- Management of up to 4 dedicated Tx-IN FIFOs (one for each active IN Endpoint) to put less load on the firmware
- Support for the soft disconnect feature.

***

# OTG_FS block diagram 
![[Pasted image 20250918133455.png]]

The OTG_FS is clocked using a separate PLL output called the `48MHz clock`. As the name suggests, it should be 48 MHz and is configured using the multiplier M and the divider Q (instead of the divider P used for the system clock). This means that the coefficients M, N, and Q in the PLL must always be set to ensure that the `48MHz clock` output is exactly 48 MHz.
![[Pasted image 20250918132414.png|500]]
> [!help] 
> To understand how to configure the PLL, you can refer to the [[RCC]] note, although it discusses the STM32G4, which does not have the `48MHz clock`. Therefore, you simply need to add the configuration for the RCC_PLLCFGR_PLLQ coefficient.

The OTG_FS requires a clock frequency of strictly 48 MHz with a deviation of no more than ±0.25%. If the deviation is greater, the device may fail to achieve phase synchronization with the host (and may either not be detected or may disconnect). These 48 MHz are necessary for the proper operation of full-speed USB (12 Mbit/s).

The CPU reads and writes from/to the OTG FS core registers through the AHB peripheral bus. It is informed of USB events through the single USB OTG interrupt line described in [[#OTG_FS interrupts]]

OTG_FS has separate RAM with 1.25 КБ size to which CPU doesn't have access, and that can be divided to several FIFO as described on [[#Peripheral-mode]]

To write to this RAM CPU ubmits data over the USB by <span style="color:red">writing</span> 32-bit words to dedicated OTG_FS locations (DFIFOx where x is number of enpoint check Table 128 of RM). The data are then automatically stored into Tx-data FIFOs configured within the USB data RAM.

The CPU receives the data from the USB by <span style="color:red">reading</span> 32-bit words from dedicated OTG_FS addresses(also DFIFOx). There is one Rx-FIFO pop register for each
out-endpoint(for device mode) or in-channel(host-mode). You can find contradiction, that each OTG_FS puts all incomming (host -> device) packets into one shared Rx-FIFO, but there are one DFIFOx pop register for EACH out-endpoint.
In shared Rx FIFO, CPU needs to know **which endpoint/channel the data belongs to** when reading it. All of those DFIFOx pop registers are actually aliases of the same shared Rx FIFO memory. When you read from the **pop register** of, for example, _OUT endpoint 1_(its address is USB_OTG_FS_PERIPH_BASE + 0x2000), you are just telling the USB core **“I want to pop the next packet from the shared Rx-FIFO, but only if it belongs to endpoint 1.”**
But if first element in Rx FIFO is belongs to **endpoint 2**, then hardware will **not let you read** because the FIFO’s current packet is not for endpoint 1.
- [ ] #todo I don't fully trust to this text... Please rewrite this text if the pop register is works differently

The USB protocol layer is driven by the serial interface engine (SIE) and serialized over the USB by the full-/low-speed transceiver module within the on-chip physical layer (PHY).

***

# OTG_FS interrupt hierarchy
![[OTG_FS interrupt hierarchy.jpg]]
This figure is from RM0090, I added it because same figure from RM0383 for stm32f411 is less detailed and contains less information.

So please refer to this picture if you have questions of interrupt configuration that may arise when reading the rest of the note.

# Device mode

## Global OUT NAK mode
Global OUT NAK - it is a mode, when OTG_FS will be request NAK on each OUT PID Tokens from host: OTG_FS stops receiving data from the host, even if there is space in the Rx-FIFO. It is used to safely suspend reception before changing the configuration of outpoints or before redistributing/clearing the Rx FIFO to avoid races with incoming OUT packets.

Application is configure Global OUT NAK by setting Set Global OUT NAK (SGONAK) bit in **DCTL**. When Global OUT NAK mode is successfully turned on sets flag Global OUT NAK effective(GOUTNAKEFF) in **GINTSTS**.


## Peripheral states

For more details of enumeration steps that cause peripheral states described below, see [[USB 2.0.#Enumeration steps]]

### Powered state
If $V_{BUS}$ input detects valid voltage of 5.0V, then the USB peripheral is allowed to enter the powered state. The OTG_FS then automatically connects the DP pull-up resistor to signal full-speed device connection to the host and generates the session request interrupt (SRQINT bit in OTG_FS_GINTSTS) to notify the powered state.

If $V_{BUS}$ input detects a drop of 5.0V(for instance because of a power disturbance or if the host port has been switched off), the OTG_FS automatically disconnects and the session end detected (SEDET bit in OTG_FS_GOTGINT) interrupt is generated to notify that the OTG_FS has exited the powered state.

In the powered state, the OTG_FS expects to receive reset signaling from the host(Reset is a special condition - [Single ended 0 SE0](USB%202.0..md#Signaling%20levels), where both D+ and D- are a logic low.). No other USB operation is possible.

When a reset signaling is received the reset detected interrupt (USBRST in OTG_FS_GINTSTS) is generated. When the reset signaling is complete, the enumeration done interrupt (ENUMDNE bit in OTG_FS_GINTSTS) is generated and the OTG_FS enters the Default state.

### Soft disconnect
The powered state can be exited by software with the soft disconnect feature. The DP pull-up resistor is removed by setting the soft disconnect bit in the device control register (SDIS bit in OTG_FS_DCTL), causing a device disconnect detection interrupt on the host side even though the USB cable was not really removed from the host port.

### Default state
In the Default state the OTG_FS expects to receive a SET_ADDRESS command from the host. <span style="color: red">No other USB operation is possible!</span>
> [!note] 
> This is contradict with steps on default state that described on [[USB 2.0.#Enumeration steps]], because there are described that on 8 step after device switching to the default state, host request Get_Descriptor of device descriptor, and only then he sends Set_Address command. So in stm32f411 there are 8 and 9 steps are swapped. 

When a valid SET_ADDRESS command is decoded on the USB, the application writes the corresponding number into the device address field in the device configuration register (DAD bit in OTG_FS_DCFG). The OTG_FS then enters the address state and is ready to answer host transactions at the configured USB address.

- [ ] #todo Maybe this attitude is describes by firmware, not by hardware. So after working on practice with enumeration on OTG_FS please check out this part and refactor it

### Suspended state

The OTG_FS peripheral constantly monitors the USB activity. After counting 3 ms of USB idleness, the early suspend interrupt (ESUSP bit in OTG_FS_GINTSTS) is issued, and confirmed 3 ms later, if appropriate, by the suspend interrupt (USBSUSP bit in OTG_FS_GINTSTS). The device suspend bit is then automatically set in the device status register (SUSPSTS bit in OTG_FS_DSTS) and the OTG_FS enters the suspended state. 

> [!important] 
>  The suspended state may optionally be exited by the device itself. In this case the application sets the remote wakeup signaling bit in the device control register (RWUSIG bit in OTG_FS_DCTL) and clears it after 1 to 15 ms.

When a [resume signaling](USB%202.0..md#Signaling%20levels) is detected from the host, the resume interrupt (WKUPINT bit in OTG_FS_GINTSTS) is generated and the device suspend bit is automatically cleared. 


## Peripheral endpoints

The OTG_FS core can implement up to 7 endpoints:
- Control endpoint 0
    - Bidirectional and handles control messages only
    - Proper control (OTG_FS_DIEPCTL0/OTG_FS_DOEPCTL0), transfer configuration (OTG_FS_DIEPTSIZ0/OTG_FS_DOEPTSIZ0), and status-interrupt (OTG_FS_DIEPINTx/)OTG_FS_DOEPINT0) registers. The set of bits of registers for endpoint 0 is slightly differs from that of other endpoints
- 3 IN endpoints
    - Each of them has proper control (OTG_FS_DIEPCTLx), transfer configuration (OTG_FS_DIEPTSIZx), and status-interrupt (OTG_FS_DIEPINTx) registers
    - The Device IN endpoints common interrupt mask register (OTG_FS_DIEPMSK) is available to enable/disable a single kind of endpoint interrupt reason on all of the IN endpoints (EP0 included)
    - Support for incomplete isochronous IN transfer interrupt (IISOIXFR bit in OTG_FS_GINTSTS), asserted if there is at least one isochronous IN endpoint in the current USB frame that failed to <span style="color:red">transmit</span> a full packet (less than the MaxPacketSize of this endpoint).. This interrupt is asserted along with the end of periodic frame interrupt (OTG_FS_GINTSTS/EOPF).
- 3 OUT endpoints
    - Each of them can be configured to support the isochronous, bulk or interrupt transfer type
    - Each of them has a proper control (OTG_FS_DOEPCTLx), transfer configuration(OTG_FS_DOEPTSIZx) and status-interrupt (OTG_FS_DOEPINTx) register
    - Device Out endpoints common interrupt mask register (OTG_FS_DOEPMSK) is available to enable/disable a single kind of endpoint interrupt reason on all of the OUT endpoints (EP0 included)
    - Support for incomplete isochronous OUT transfer interrupt (INCOMPISOOUT bit in OTG_FS_GINTSTS), asserted if there is at least one isochronous IN endpoint in the current USB frame that failed to <span style="color:red">receive</span> a full packet (less than the MaxPacketSize of this endpoint). This interrupt is asserted along with the end of periodic frame interrupt (OTG_FS_GINTSTS/EOPF).

### Endpoint status/interrupt
There are global interrupts configured by the OTG_FS_GINTMSK register, which occur if an interrupt condition arises in any of the endpoints.

There are global interrupts that set up by OEPINT/IEPINT bits in OTG_FS_GINTMSK. So core interrupt occurs if there are interrupt condition occur even in one of the OUT/IN Endpoint. The core interrupt status register OTG_FS_GINTSTS includes flags indicating the interrupt status for Endpoint Out (OEPINT bit) and Endpoint In (IEPINT).

To clear this core interrupt status flags, application must first read the device all endpoints interrupt (OTG_FS_DAINT) register to get the exact endpoint number where interrupt condition occurs. And then application must clear the appropriate bit in OTG_FS_DIEPINTx/DOPEPINTx. Clearing the bit in DIEPINTx/DOEPINTx **automatically clears** the corresponding bits in DAINT and GINTSTS.

The peripheral core provides the following status checks and interrupt generation:
- Transfer completed interrupt, indicating that data transfer was completed on both the application (AHB) and USB sides. So this interrupt occurs when in DIEPTSIZx/DOEPTSIZx registers XFRSIZ and PKTCNT bits decreased to 0  
- Setup stage has been done (control-out only). 
    DOEPINT0: **SETUP** = 1
- Associated transmit FIFO is half/completely empty (in endpoints).
    DIEPINTx: **TXFE/INEPTXFEMPT** = 1
- NAK acknowledge has been transmitted to the host (isochronous-in only). 
    DIEPINTx: **NAK** = 1

- IN token received when Tx-FIFO was empty (bulk-in/interrupt-in only)
    DIEPINTx: **TXFE/INEPTXFEMPT**; XFRSIZ wasn't decrease.
- Out token received when endpoint was not yet enabled
    DOEPINTx: **EPDISD/NAK bits**; DAINT.OEPINTx = 1.
- Babble error condition has been detected.
    This is a situation where the device transmits more data than is allowed by packet size or endpoint. Babble occurs if the device continues to transmit data after the host has already received the full packet; or the IN‑endpoint has exceeded the set XFRSIZ/PKTCNT.
    DIEPINTx: **BERR = 1**; GINTSTS: **BERR = 1**. 
- Endpoint disable by application is effective
    When firmware disable endpoint(in DIEPCTLx set EPENA = 0), OTG_FS won't turn off endpoint immediately. Before this OTG_FS completes the current transfer or clears the internal states. And only after that OTG_FS will turn off endpoint, and will generate interrupt of effective endpoint disable. 
    DIEPINTx: **EPDISD = 1**;
- Endpoint NAK by application is effective (isochronous-in only)
    For isochronous-IN endpoint firmware can set in DIEPCTLx NAKSTS bit thus endpoint will send out a zero-length data packet, even if there are data available in the TxFIFO. And this interrupt shows that this condition has successfully set. 
    DIEPINTx: **NAK = 1**;
- More than 3 back-to-back setup packets were received (control-out only)
    If more than 3 Setup packets arrive in a row without processing the previous ones, this is considered as a potential error or overload. The OTG_FS generates an interrupt so that the application can clear the FIFO and process the next Setup packet.
    DOEPINTx: **OVERFLOW/SETUP = 1**; DAINT.OEPINTx = 1.
- Timeout condition detected (control-in only)
    DIEPINTx: **TOUT bit = 1**;
- Isochronous out packet has been dropped, without generating an interrupt
- [ ] #todo The last one status I can't understand. Please check this out later, after practice

## Peripheral SOF
In device mode, the start of frame interrupt is generated each time an <span style="color:red">SOF token is received</span> on the USB (SOF bit in OTH_FS_GINTSTS). The corresponding frame number can be read from the device status register (FNSOF bit in OTG_FS_DSTS). 

OTG_FS core provides separate SOF pulse output pin, that pulse when SOF packet is received. This is useful to work with audio-devices, where SOF-impulses are used for synchronize audio-ticks. This allows the audio peripherals to synchronize with the isochronous stream provided by the host (for example, a PC),

So OTG_FS each time an <span style="color:red">SOF token is received</span> on the USB can generate an SOF pulse signal with a width of 20 HCLK cycles can be also generated and can be available externally on the OTG_FS_SOF pin by using the SOF output enable bit in the global control and configuration register (SOFOUTEN bit in OTG_FS_GCCFG).

The SOF pulse signal is also internally connected to the TIM2 input trigger, so that the input capture feature, the output compare feature and the timer can be triggered by the SOF pulse. The TIM2 connection is enabled through the ITR1_RMP bits of the TIM2 option register (TIM2_OR). 

Inside the OTG_FS core there's a _periodic frame timer_ that counts the 1 ms interval. And PFIVL bits in OTG_FS_DCFG lets you decide at what point in the frame—**80 %, 85 %, 90 %, or 95 % of the frame time**—the core will raise the **EOPF (End Of Periodic Frame) interrupt** in GINTSTS register. This helps to fills Tx FIFO for isochronous endpoints before next frame.

# USB FIFOs

## Peripheral FIFO architecture
![[Pasted image 20250919213055.png|600]]

### Peripheral Rx FIFO

OTG_FS uses shared Rx FIFO that receives the data directed to all OUT endpoints(include control endpoint 0). Received packets are stacked back-to-back until free space is available in the Rx-FIFO. The status of the received packet (which contains the OUT endpoint destination number, the byte count, the data PID and the validity of the received data) is also stored in shared Rx FIFO on top of the payload. 
> [!important] 
>  When no more space is available, host transactions are
NACKed and an interrupt is received on the <span style="color:red">addressed endpoint.</span>

> [!attention] 
>  The application keeps receiving the Rx-FIFO non-empty interrupt (RXFLVL bit in GINTSTS) as long as there is at least one packet available for download. 

#### Status word in Rx FIFO and Payload reading

OTG_FS is puts the payload (several of words) first, then a single 32-bit status-word in the Rx FIFO. So each transaction requires `(words+1)` in Rx FIFO.

You can read the status information **from the top** of the Rx FIFO by reading **GRXSTSR** register. But this don't pop the status information from the Rx FIFO, so if you after reading **GRXSTSR** register will read data from the top of the Rx FIFO you get also status information.

To read status information and pop it, you can read **GRXSTSP** register.
> [!attention] 
> Reading of  **GRXSTSP** register pops only status information from the top of the Rx FIFO, but not the payload itsetlf.

To read 32 bits of data from the top of the Rx FIFO you can <span style="color: red">read</span> any DFIFOx registers, because each DFIFOx is connected to one shared Rx FIFO. 
> [!attention] 
> You **can** also read the 32-bit status word at the top of the Rx FIFO through any DFIFOx register.
> **However, this is not recommended.** Reading the status word via DFIFOx will pop it from the FIFO just like reading payload data, but firmware expects status words to be processed using **GRXSTSP**. Using DFIFOx to read status words can cause misalignment between payload and status tracking, corrupt transfer handling, and confuse the endpoint interrupt logic.

##### Status word structure

Status word include: number of endpoint(EPNUM), information about success of packet(PKTSTS), byte count of payload(BCNT), PID of the received OUT data packet(DPID).
The structure of status word is described in **GRXSTSR/GRXSTSP** register description
![[Pasted image 20250921180818.png]]
Each field except FRMNUM and PKTSTS is understandable.

FRMNUM - frame number in which OUT packet was send. This field is supported only when isochronous OUT endpoints are supported. And it is primarily relevant for **isochronous transfers**, which are scheduled on specific frames or microframes. By storing the frame number in the status word, firmware can determine exactly **when** the packet was received relative to the USB frame timing.

PKTSTS - Indicates the status of the received packet. There are 5 packet statuses:
- 0b0001 Global OUT NAK. When host sends OUT token and device is in [[#Global OUT NAK mode]], then device is response with NAK. OTG_FS pushes status-word(Global OUT NAK has no payload) with PKTSTS=0b0001 to inform that device is NAK'ing some OUT token from host because of Global OUT NAK mode. This raise GOUTNAKEFF flag in **GINTSTS** register.
- 0b0010 OUT data packet received. An OUT transaction arrived that carries payload and the core accepted it into Rx-FIFO. <span style="color:red">But this packet may be a mid-transfer packet — not the last packet.</span>
- 0b0011 OUT transfer completed. The core determined that a transfer for that OUT endpoint is finished when the total number of bytes expected for the transfer has been received(according to xFER_SIZE in **DOEPTSIZx** register) or a short packet indicates the end of the transfer. 
    But first, the last **0b0010 OUT data packet received** is written into Rx FIFO with payload. Immediately after that, the core pushes a <span style="color:red">separate</span> status word with PKSTS=0b0011 <span style="color:red">without any payloads</span>. This signals that the entire OUT transaction is complete, and also sets endpoint transfer-complete interrupt XFRC in **DOEPINTx**, which produces endpoint interrupt bit in **DAINT** register, and also OEPINT flag in **GINTSTS**
- 0b0100 SETUP transaction completed. OTG_FS has received a full 8-byte [SETUP stage](USB%202.0.%20basics#Setup Stage) DATA0 packet on endpoint 0. This sets SETUP flag in DOEPINT0, which produces endpoint interrupt bit in **DAINT** register, and also OEPINT flag in **GINTSTS**
- 0b0110 - SETUP data packet received. When host sends SETUP packet, but the data packet of SETUP stage is not completed. For example host sends 8 bytes of data packet of SETUP stage, but data packet should be 8 words(32 bytes).

#### Rx FIFO allocation

The size of the Rx FIFO is configured in **GRXFSIZ** register. And allocation of Rx FIFO is more complicated then for Tx FIFO, because Rx FIFO is shared for all OUT reception. So firmware should estimate how much data might accumulate at once—control SETUP packets, status words, and the largest possible burst of OUT or isochronous packets—and set **GRXFSIZ** large enough to hold that worst-case total without overflow.

First of all reference manual requires 10 words for [SETUP packets](USB%202.0..md#Setup%20Stage). One setup packet has 8 byte information about request in his data packet. When the OTG_FS core stores this packet in the Rx FIFO it also pushes status information with size of 4 bytes(one word) on the top of payload in Rx FIFO. So each SETUP stage of control transfer occupies 12 bytes, or 3 words. But OTG_FS can get more than 3 SETUP packets in a row. So Rx FIFO should has place for all 3 SETUP packets, each with payload of request info and status word. So Rx FIFO should has 9 words minimum for SETUP packets. But RM requires 10 words, <span style="color: grey">maybe for reserve(?)</span> OTG_FS does not use these 10 words for any other reasons except SETUP packets.
For example, if the Rx FIFO has a total size of 12 words and 2 words are already holding OUT-packet data, the remaining 10 words remain reserved and cannot be consumed by other OUT packets.
- [ ] #todo Figure out why exactly 10 words for SETUP packages

One word should be allocated in Rx FIFO for [[#Global OUT NAK mode]]. Because Global OUT NAK is a mode, when OTG_FS will be request NAK on each OUT PID Tokens from host, there are no payload, just status-word. More information about status-word for Global OUT NAK you can read at [[#Status word structure]]

Status information is written to the FIFO along with each received packet. Therefore, a minimum space of `ceil(largest_packet_size_bytes / 4) + 1` must be allocated to receive other OUT packets. But if multiple Isochronous endpoints are enabled, then at least two such spaces `ceil(Largest Packet Size / 4) + 1` spaces must be allocated to store both the first packet that still being processed by firmware and the second packet that arriving immediately. This is critical because **isochronous transfers are time-sensitive**, and the host may send back-to-back packets faster than firmware can process them.

- [ ] #todo I totally don't understand if sufficient for all OUT endpoints allocate `ceil(largest_packet_size_bytes / 4) + 1`, or needed for each OUT endpoint⏫ 

> [!important] 
>  Along with the last packet of OUT transaction, OTG_FS also pushes OUT transfer completed status information to Rx FIFO. So it is recommended to add one word **for each OUT endpoint.**

Therefore the minimal recommended by Reference Manual Rx FIFO allocation formula is below:
```c
setup_reserved = 10;
global_out_nak = 1;
sizes_of_out_endpoints[] = { /* some sizes in term of words */};
for_enpoint_out = ceil(max(sizes_of_out_endpoints) / 4) + 1;
is_multiple_isochronous = 1;
number_of_out_endpoint = /* some number */; // it represents transfer_complete_slots

if(is_multiple_isochronous)
{
    GRXFSIZ_words = setup_reserved + global_out_nak + 2 * for_endpoint_out + number_of_out_endpoint;
}else
{
    GRXFSIZ_words = setup_reserved + global_out_nak +  for_endpoint_out + number_of_out_endpoint;
}
```

Of course you should check if GRXFSIZ_words <= MAX_RX_FIFO_SIZE_WORDS.  

### Peripheral Tx FIFO
OTG_FS has a dedicated FIFO for each IN endpoint. The application  configures FIFO sizes by writing register **TX0FSIZ** for endpoint 0 IN and **DIEPTXFx** for endpoints-x IN. In this registers you can change TxFIFO depth and start address.

The minimum depth required for each IN Endpoint Rx FIFO is the maximum packet size for that particular IN endpoint.
> [!note] 
>  More space allocated in the transmit IN Endpoint FIFO results in better performance on the USB.

TxFIFO depth and RAM start address <span style="color:red; font-size:25">should be written in terms of 32-bit words!</span> So to have for example Tx FIFO depth for endpoint 0 IN 512 bytes, you should type in TX0FD bits of OTG_FS_DIEPTXF0 $\large \frac{512}{4}=128$(you should divide by 4 because 32 bits is 4 bytes)

Now you should set start address of Tx FIFO of endpoint 0.
> [!attention] 
> Don't forget that all Tx FIFO is placed after Rx FIFO, that start address is fixed on 0, and size is configurable by **GRXFSIZ** register

So to calculate the start address of Tx FIFO of endpoint 0 we should use this formula:
endpoint0_start_address = 0 +  Rx_FIFO_size <span style="color: red; font-size:20">(all of this values are in terms of 32-bit words)</span>
For example Rx FIFO is 64 32-bit words, then endpoint0_start_address=64.

And to calculate start addresses for other Tx FIFOs you can use this formula
enpoint_address = previous_start_adress + previous_size <span style="color: red; font-size:20">(all of this values are in terms of 32-bit words)</span>
So for endpoint 1 in our case we will get
enpoint1_address = 64 + 128 = 192
And so on for others enpoints


> [!bug] 
> <span style="font-size:25;">[ATTENTION!!!!](https://youtube.com/shorts/5FYxUaRykQ0?si=l5LOEggFma9gkWbT)</span>
>  I emphasize that the size and starting address for the Tx FIFO for endpoints are written in terms of 32-bit words because all reference manuals contain an error in the description of the starting addresses. It is only stated that INEPTXSA must be aligned with a 32-bit memory location. BUT THIS IS NOT ACTUALLY THE CASE!!! GOVERMENT ARE LYING TO US HERE IS A [PROOF](https://community.st.com/t5/stm32-mcus-embedded-software/confusing-stm32f2xx-manual-for-ineptxfd/td-p/447757)!!! In reality, you need to write the value there as you would for the sizes (which are correctly described in the RM) - in terms of 32-bit words. That is, as I described above!

- [ ] #todo Write about process of adding data in Tx FIFO⏫ 

# OTG_FS interrupts




# USB Host 

## USB Host scheduler
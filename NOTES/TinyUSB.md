Tags: #periferal_interface #libraries
> [!sources] 
>  [STM32CubeIDE Integration · hathach/tinyusb · Discussion #633 · GitHub](https://github.com/hathach/tinyusb/discussions/633)
>  [Port config/init confusion, whats the recomended way? · hathach/tinyusb · Discussion #2558 · GitHub](https://github.com/hathach/tinyusb/discussions/2558)
>  [Concurrency - TinyUSB](https://docs.tinyusb.org/en/latest/reference/concurrency.html)

***

<span style="font-size: 25">List of content:</span>

```table-of-contents
```

***

<span style="font-size: 25">Tasks:</span>

```tasks
```

***

# TinyUSB

TinyUSB — это открытая, кроссплатформенная библиотека USB. Она не привязана к конкретной MCU.
А благодаря уровню абстракции аппаратной платформы (board/MCU abstraction layer) , можно писать код TinyUSB который может работать на разных микроконтроллерах без изменений(кроме настройки самого abstraction layer)
Библиотека поддерживает работу как **USB Device**, так и **USB Host**, а также USB OTG, что позволяет MCU переключаться между режимами хоста и устройства.

Главная особенность TinyUSB — безопасность для памяти и потокобезопасность без использования динамического выделения. Библиотека спроектирована таким образом, что все события, возникающие в прерываниях USB (например, приход пакета данных, подключение или отключение шины), **не обрабатываются напрямую в ISR**. Вместо этого в обработчике прерываний просто **устанавливаются флаги событий или заполняются буферы**, а реальная обработка этих событий выполняется в функции задачи TinyUSB (`tud_task()`), которая вызывается в основном цикле программы (`while(1)` в `main`) либо из задачи RTOS, если она используется.

Для сравнения как это всё работает в [[USB HAL]] от STM и как это реализовано в TinyUSB 

В отличие от USB HAL, где передача и приём данных выполняются напрямую через аппаратные FIFO (Tx/Rx FIFO) контроллера OTG_FS, в TinyUSB используется **программный буфер** как промежуточное звено между приложением и USB-периферией.
При отправке данные сначала записываются в софтверный буфер передачи, после чего библиотека автоматически передаёт их по USB. Когда буфер полностью опустеет, вызывается колбэк `tud_cdc_tx_complete_cb`.
> [!important] 
> Можно вызывать `tud_cdc_write` несколько раз подряд, даже если предыдущие данные ещё находятся в буфере. В этом случае новые данные будут добавлены в буфер и отправлены вместе с теми пакетами, которые ещё не ушли, без ожидания полного завершения предыдущей передачи.

Размеры внутренних буферов задаются в файле `tusb_config.h`:
```c
// Size of internal software buffer in TinyUSB library for receiving CDC
// data from host. Data is first stored here before application reads it.
#define CFG_TUD_CDC_RX_BUFSIZE   (64)
// Size of internal software buffer in TinyUSB library for transmitting
// CDC data to host. Application writes data here before USB controller
// sends it. Larger messages are split into multiple transfers if needed
#define CFG_TUD_CDC_TX_BUFSIZE   (64)
```

> [!note] 
> Увеличивать `CFG_TUD_CDC_RX_BUFSIZE` сверх размера endpoint’а обычно нет смысла. TinyUSB вызывает `tud_cdc_rx_cb()` при приёме **каждого пакета**, а не полного сообщения, поэтому библиотека не знает, где сообщение заканчивается.  
> Однако приём сообщений больше 64 байт возможен. Однако пока мне не понятно точно почему...
> Возможно, TinyUSB вместе с программным буфером использует аппаратные FIFO OTG_FS, что позволяет обрабатывать несколько пакетов подряд. Нужно уточнить, какое ограничение по длине полного сообщения накладывает контроллер и как это влияет на сборку сообщений в приложении.
>  - [ ] #todo Почему TinyUSB позволяет принимать сообщения длиной больше 64 байт, если колбэк `tud_cdc_rx_cb` вызывается при получении каждого пакета, а программный буфер (`CFG_TUD_CDC_RX_BUFSIZE`) хранит только данные текущего пакета?


- [ ] #todo Разобраться, в какой момент TinyUSB отправляет данные из программного буфера на USB, и почему иногда, даже если Wireshark показывает, что сообщение дошло до ПК, оно не отображается в COM-порт терминале, когда MCU находится в режиме отладки.


# Настройка TinyUSB

> [!Sources] 
>  [Port config/init confusion, whats the recomended way? · hathach/tinyusb · Discussion #2558 · GitHub](https://github.com/hathach/tinyusb/discussions/2558)

В последних версиях **TinyUSB** изменилась система конфигурации. Ранее требовалось задавать макросы вроде `CFG_TUSB_RHPORT0_MODE` или `CFG_TUSB_RHPORT1_MODE`, чтобы указать, какой **Root Hub Port (RHPORT)** использовать и в каком режиме (Device / Host, Full-/High-Speed)

Это делалось например таким образом
```c
// выставляем для Root hub port 0 режим Full-speed устройста 
#define CFG_TUSB_RHPORT0_MODE   (OPT_MODE_DEVICE | OPT_MODE_FULL_SPEED)
```

Далее конфигурация всего TinyUSB библиотеки происходила в `tusb_init` которая смотрела на дефайны `CFG_TUSB_RHPORT0_MODE/CFG_TUSB_RHPORT1_MODE` и на их основе настраивала библиотеку

> [!help] 
>  **Root Hub Port (RHPORT)** — физический USB-порт микроконтроллера. На STM32 FS-порт OTG_FS обычно соответствует RHPORT0, HS-порт OTG_HS — RHPORT1.

Теперь в TinyUSB вместо этих устаревших макросов каждый порт настраивается индивидуально. Так появились две функции инициализации: `tud_init(uint8_t rhport)` для настройки rhport в режим устройства и `tuh_init(uint8_t rhport)` для настройки rhport в режим хоста.

Такой подход позволяет динамически менять режим работы порта, например через `tusb_deinit(rhport)` перед новой инициализацией.
- [ ] #todo Понять какие от этого плюсы. Это нужно для USB OTG?

В новых примерах TinyUSB для удобства появились макросы:
- `BOARD_TUD_RHPORT` / `BOARD_TUH_RHPORT` — указывают, какой RHPORT используется на плате для Device / Host. Используются программистом при вызове `tud_init` / `tuh_init`.
- `BOARD_TUD_MAX_SPEED` / `BOARD_TUH_MAX_SPEED` — задают желаемую скорость работы порта, которая через `CFG_TUD_MAX_SPEED` / `CFG_TUH_MAX_SPEED` используется самой библиотекой при инициализации в `tud_init/tuh_init`

Таким образом, макросы `BOARD_*` упрощают перенос проекта между платами, а `CFG_*` управляют внутренней настройкой TinyUSB.

> [!help] 
>  Тут уже мне нужна помощь, потому что я не совсем понимаю зачем была сделана такая матрёшка... Возможно я что-то не правильно понял...

> [!note] 
> Однако никто не запрещает дальше пользоваться дефайнами `CFG_TUSB_RHPORT0_MODE` и `CFG_TUSB_RHPORT1_MODE` вместе с функцией `tusb_init()`
> Эта часть нужна чтобы прояснить неразбериху с тем, что на официальной странице TinyUSB в гайде по тому как использовать их библиотеку до сих пор написано про `tusb_init()`, хотя при этом во всех примерах используется `tud_init/tuh_init`
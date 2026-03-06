Tags: #stm32 #HAL #periferal_interface #usb

> [!attention] 
> Для понимания данного текста нужно понимать сам протокол [[USB 2.0.]] 

***

<span style="font-size: 25">List of content:</span>

```table-of-contents
```

***

<span style="font-size: 25">Tasks:</span>

```tasks
```

***

# Структура
В случае USB HAL используется не только сам HAL, потому что HAL делает абстракцию только над какой-либо периферией, в нашем случае над [[OTG_FS]] периферией. Сам HAL который в случае USB разделяется на HAL PCD для режима девайса и HAL HCD для режима хоста. И отвечает за самые низкоуровневые настройки периферии, настройку регистров, настройку прерываний, открытие/закрытие endpoint'ов, настройку PHY и отвечает за физику передачи/приёма.

Однако кроме этого каждый девайс должен поддерживать один из [классов устройств](USB%202.0.%20device%20classes): HID, CDC и т.д. Для этого ST также создала стек USB-Device и USB-Host которые реализуют протокольный уровень USB. Он строится поверх HAL PCD.

USB-Device состоит из двух частей: Core и Class директорий

1. <span style="font-size: 25">Core</span>
    - **usbd_core**
    Сердце стека. В нём находится глобальная структура `USBD_HandleTypeDef` - структура для всего USB устройства. В нём есть машина состояний USB-устройства: Default, Addressed, Configured, Suspended. В этом же файле есть функции для начальной настройки USBD.
    Отвечает за основные обработки событий, то есть это те событие которые происходят через прерывания в OTG_FS, как например событие что хост запрашивает Data Out, Data IN и так далее.
    В нём реализован первичный разбор заголовка SETUP пакета, определяет тип запроса (standard/class/vendor) и маршрутизация самого USB запроса в нужные обработчики, стандартные запросы в usbd_ctlreq, а классовые запросы в pClass->Setup() находящийся в `USBD_HandleTypeDef`. После выполнения запроса обновляет состояние устройства, управляет открытием/закрытием endpoint’ов, вызывая низкоуровневые функции HAL PCD.
    - **usbd_ctlreq**
    Отвечает за обработку стандартных для всех USB классов запросы: `GET_DESCRIPTOR`, `SET_ADDRESS`, `SET_CONFIGURATION` и т.д. Именно его обработчик вызывает usbd_core если приходит SETUP пакет с standart запросом.
    usbd_ctlreq делает остальной разбор SETUP пакета, чтобы понять какой запрос ей нужно выполнить, и затем перенаправляет к обработчику конкретного запроса. Также формирует нужные дескрипторы в ответ на `GET_DESCRIPTOR` (Device, Configuration, String, Qualifier).
    - **usbd\_ioreq**
    Включает в себя низкоуровневые операции для обработки стандартных запросов в endpoint 0 - отправку данных в Data Stage, приём данных, завершение Status Stage. Все функции в нём, такие как `USBD_CtlSendData`, `USBD_CtlPrepareRx` и т.д. работают поверх `USBD_LL_*` что являются wrapper'ами для функций из HAL PCD
    Уже функции из usbd_ioreq используются в usbd_ctlreq
    <span style="color:red; font-size:25">ВСЕ ФАЙЛЫ ВЫШЕ ИЗМЕНЯТЬ НЕЛЬЗЯ!!! ЭТО [ОСНОВА, БАЗА](https://youtu.be/yB1TRff_U0Q?si=oRrGoG35jtwPPZgU) ДЛЯ САМОГО USB-DEVICE СТЕКА</span>
    - **usb_conf**
    Связывающее звено с HAL PCD. Здесь нужно реализовать функции wrapper'ы `USBD_LL_*` которые должны вызывать соответствующие функции HAL PCD `HAL_PCD_*`. Это слой «аппаратной абстракции» между стеком Core и драйвером HAL.
    Функции должны быть реализованы схожим образом:
    ```c
 USBD_StatusTypeDef USBD_LL_Start(USBD_HandleTypeDef *pdev)
 {
      HAL_StatusTypeDef hal_status = HAL_OK;
      USBD_StatusTypeDef usb_status = USBD_OK;
    
      hal_status = HAL_PCD_Start(pdev->pData);
    
      usb_status =  USBD_Get_USB_Status(hal_status);
    
      return usb_status;
 }
    ```
    Но где-то нужно написать нормальный такой код. Как например в случае инициализации самого USBD.
    - **usbd_desc**
    Здесь хранится device descriptor: Vendor ID, Product ID, а также строковые дескрипторы. Именно его будет вызывать usbd_ctlreq при запросе `GET_DESCRIPTOR`
2. <span style="font-size: 25">Class</span>
Надстройка над Core, реализующая прикладной USB-класс(CDC, HID, MSC, DFU и др.). Далее будет рассказ про CDC но для остальных классов файлы одинаковые не сильно отличаются
    - **usbd_cdc**
    Логика работы конкретного класса: обработка специфичных для [CDC запросов](USB%20CDC%20class#Requests)(`SET_LINE_CODING`, `GET_LINE_CODING`). Управление передачей данных по выделенным конечным точкам (например, Bulk IN/OUT). Там же находится configuration descriptor, вместе со всеми смежными дескрипторами типа interface descriptor с endpoint descriptor и если требуются, то там же находится дескрипторы специфичные для класса устройства. Все эти данные находятся в одной структуре `USBD_CDC_CfgDesc`, потому что во время enumeration устройство должно отправить все смежные дескрипторы. 
    - **usbd_cdc_if**
    Это файл где программист настраивает интерфейс между стеком USBD и твоим приложением/периферией. Именно сюда программист вписывает логику приёма/отправки данных, буферизацию, и обработку класс-специфичных команд (line coding, control line state и т.д.). Именно обработку класс-специфичных комманд, а не то как они будут отправляться, это описано в **usbd_cdc**
    Это место, где разработчик, связывает USB-слой со своим приложением:
        - куда складывать входящие байты (буфер/очередь);
        - как уведомлять задачу/поток о приходе данных;
        - как передавать данные хосту (и что делать, если передача занята);
        - как обрабатывать `SET_LINE_CODING` / `SET_CONTROL_LINE_STATE`;
        - как выделить/расположить буферы (DMA-совместимая память или нет).
     Мол если мы хотим чтобы данные полученные с USB приходили в какой-то буфер, то здесь мы настраиваем эту связь. Для этого в функцию из этого файла `*_Receive` (потому что изначально там все функции называются `TEMPLATE_*` а ты должен сам их назвать). Файлы `*_if` — **это зона ответственности программиста**.


***

# Настройка USBD

Итак мы разобрались в [[#Структура]] что зона ответственности программиста это `usbd_conf`, `usbd_desc` и для класса устройства `usbd_*_if`. Давайте разберёмся как и что нужно настраивать программисту.

## Настройка стека

Настройка самого стека USBD, пока без `usbd_*_if` описана в [данной картинке](https://wiki.st.com/stm32mcu/nsfr_img_auth.php/4/4a/USB_Device_initialization_main_functions_call_graph.png). 

Итак при настройке USBD нам нужно <span style="color:rgb(255, 0, 0)">запустить на самом деле 4, а не 3 функции настройки, картинка чуть врёт</span>

- **USBD_Init** — инициализирует USB стек и связывает его с аппаратной периферией.  В процессе вызывает `USBD_LL_Init`, реализованную в `usbd_conf.c`, где настраивается сам контроллер USB OTG_FS (тактовка, пины, FIFO, прерывания и т.д.).
- **USBD_RegisterClass** — подключает к стеку конкретную реализацию USB-класса устройства.  
    Например, `USBD_CDC`, описанную в `usbd_cdc.c`. Эта структура содержит указатели на функции инициализации, обработки запросов, передачи и приёма данных, а также определяет дескрипторы конфигурации, интерфейсов и endpoint’ов в соответствии со спецификацией класса CDC.
- **USBD_CDC_RegisterInterface** — связывает стек USB с пользовательской реализацией интерфейса класса, описанной в `usbd_cdc_if.c`.  
    Здесь задаётся, как стек будет взаимодействовать с буферами приложения: куда записывать полученные данные, откуда брать данные для передачи, и как обрабатывать специфичные для класса команды (например, изменение скорости или состояния линий связи).
- **USBD_Start** — запускает работу устройства. Функция активирует периферию OTG_FS и переводит стек USB в рабочее состояние, вызывая `USBD_LL_Start` из `usbd_conf.c`. После этого устройство начинает обмен данными с хостом.

Теперь давайте разберёмся что нам нужно настроить самостоятельно и как.

### Настройка usbd_conf

Итак этот файл нужен для настройки связи USBD библиотеки вместе с HAL_PCD реализацией работы с [[OTG_FS]]. 

Когда ты скачаешь USBD библиотеку с github'а самих STM то там будет template для usbd_conf где будут функции вида `USBD_LL` однако это не всё что тебе нужно здесь создать.

Во первых тебе нужно создать сам PCD handler с которым должен работать USBD, опять же напоминаю USBD это высокоуровневая надстройка для PCD которая отвечает за протокол USB для device class'ов

#### USBD_LL

Далее тебе нужно установить wrapper'ы для функций HAL PCD которыми будет уже пользоваться USBD для работы с самим `OTG_FS`. Эти wrapper'ы это и есть `USBD_LL_*` Почти для всех функций в эти LL функции нужно просто записать соответствующий HAL_PCD функцию, типа

```c title=usbd_conf.c
USBD_StatusTypeDef USBD_LL_DeInit(USBD_HandleTypeDef *pdev)
{
    HAL_StatusTypeDef hal_status = HAL_OK;

    hal_status = HAL_PCD_DeInit(pdev->pData);

    return USBD_Get_USB_Status(hal_status);
}
```

Однако как можно заметить мы возвращаем не полученный `hal_status`, потому что в USBD статусы немного отличаются, сравни

```c
typedef enum
{
  USBD_OK = 0U,
  USBD_BUSY,
  USBD_EMEM,
  USBD_FAIL,
} USBD_StatusTypeDef;

typedef enum 
{
  HAL_OK       = 0x00U,
  HAL_ERROR    = 0x01U,
  HAL_BUSY     = 0x02U,
  HAL_TIMEOUT  = 0x03U
} HAL_StatusTypeDef;

```

Из всех непонятен только EMEM, потому что для него нет аналога в HAL. EMEM говорит о том что недостаточно памяти для того чтобы выполнить какую-то функцию, например аллокацию памяти. Но эта ошибка не встречается в `USBD_LL_*` функциях, потому что тут нет динамической аллокации памяти.

Но из-за того что значение статусов в enum'ах отличаются, нам нужно сделать функцию которая будет переводить HAL статусы в USBD статусы, типа функции:

```c title=usbd_conf.c
__attribute__((always_inline)) static inline USBD_StatusTypeDef USBD_Get_USB_Status(HAL_StatusTypeDef hal_status)
{
    USBD_StatusTypeDef usb_status = USBD_OK;

    switch (hal_status)
    {
        case HAL_OK :
          usb_status = USBD_OK;
        break;
        case HAL_BUSY :
          usb_status = USBD_BUSY;
        break;
        default :
          usb_status = USBD_FAIL;
        break;
    }
    return usb_status;
}
```

Но в `HAL_LL_Init` нам нужно самим проинициализировать `OTG_FS` так что нам нужно будет настроить `PCD_Handler` а затем вызвать `HAL_PCD_Init` функцию.

В самом PCD handler нужно сделать настройку важно знать что поле `dev_endpoint` мы выставляем **не количество endpoint которые мы хотим использовать, а сколько в целом OTG_FS даёт возможность выставить этих endpoint.** В случае stm32f411 это 4. То же самое в `Host_channels`.

В `phy_itface` мы выставляем какой USB PHY используется в МК, интегрированный или внешний.

- [ ] #todo Разобраться что за use_dedicated_ep1

Кроме того, нам нужно подключить USBD стек к HAL PCD для этого у `USBD_HandleTypeDef` и у `PCD_HandleTypeDef` есть указатели pData, которые и отвечают за соединение верхнего стека USBD с нижним стеком PCD. Поэтому в USBD_LL_Init нам нужно сделать так
```c
// hpcd is PCD_Handler and pdev is USBD_Handler
    hpcd.pData = pdev;      // set upper stack handler to HAL PCD
    pdev->pData = &hpcd;    // set lower stack handler to USBD
```

Кроме этого нужно настроить [RX FIFO](OTG_FS#Peripheral%20Rx%20FIFO) и [TX FIFO](OTG_FS#Peripheral%20Tx%20FIFO) через `HAL_PCDEx_SetRxFiFo` и `HAL_PCDEx_SetTxFiFo` напоминаю что размер определяется в 4 байтных словах, при этом как выбирать минимальный размер для FiFo рассказано в [[OTG_FS## USB FIFOs]] как и про сами FIFO

#### Callback'и

Теперь нам нужно настроить Callback'и для HAL_PCD, тут уже наоборот, нам нужно сделать wrapper's для функций из `usbd_core.c`. Почему то для Callback'ов ничего в template нет, но некоторые из callback'ов обязательные, а некоторые опциональные.

- ОБЯЗАТЕЛЬНЫЕ
    - `HAL_PCD_SetupStageCallback`
    - `HAL_PCD_ResetCallback`
    - `HAL_PCD_DataOutStageCallback`
    - `HAL_PCD_DataInStageCallback`
- Необязательные
    - `HAL_PCD_SOFCallback` нужен если есть функции которые завязаны на таймер, например для аудио устройств
    - `HAL_PCD_SuspendCallback`/`HAL_PCD_ResumeCallback` нужна для перехода в/возврата из Suspend
    - `HAL_PCD_ISOOUTIncompleteCallback`/`HAL_PCD_ISOINIncompleteCallback` нужен если есть isochronous endpoint, этот колбэк вызывается если isochronous передача не была завершена 

Настраиваются эти Callback'и подобным образом:
```c title=usbd_conf.c
void HAL_PCD_SetupStageCallback (PCD_HandleTypeDef * hpcd)
{
    USBD_LL_SetupStage((USBD_HandleTypeDef*)hpcd->pData, (uint8_t*)hpcd->Setup);
}
```

Однако стоит помнить, что **выбор скорости устройства происходит после сигнала Reset от хоста**.  Согласно спецификации USB 2.0, процедура high-speed negotiation (chirp) выполняется именно после Reset. Про это рассказывается в [[USB 2.0.#Enumeration steps]] шаг 5.

Во время Reset-обработки, после завершения процедуры chirp, контроллер определяет фактическую скорость и записывает её в поле `hpcd->Init.speed`. Эта операция выполняется в `HAL_PCD_IRQHandler` **до вызова** функции `HAL_PCD_ResetCallback`.

Поэтому в `HAL_PCD_ResetCallback`, необходимо уже передать в стек USBD ту скорость, которая была определена хостом во время обработки Reset-события в `HAL_PCD_IRQHandler`.

Даже если микроконтроллер не поддерживает high-speed, стек USBD **всё равно ожидает**, что скорость устройства будет установлена **после Reset**.  
Таким образом, `HAL_PCD_ResetCallback`, который сообщает о завершении Reset, должен выглядеть примерно так:
```c title=usbd_conf.c
void HAL_PCD_ResetCallback(PCD_HandleTypeDef * hpcd)
{
    USBD_SpeedTypeDef speed = USBD_SPEED_FULL;

    // The used MCU supports only full-speed
    // so if high-speed was set after reset,
    // then this is an error
    if ( hpcd->Init.speed != PCD_SPEED_FULL)
    {
        LOG_ERROR(2765); // TODO: change error
    }

    /* Set Speed. */
    USBD_LL_SetSpeed((USBD_HandleTypeDef*)hpcd->pData, speed);

    /* Reset Device. */
    USBD_LL_Reset((USBD_HandleTypeDef*)hpcd->pData);
}
```
***

### Настройка usbd_desc

В `usbd_desc.c` находится device descriptor и некоторые строковые дескрипторы.

Первым делом надо выбрать Vendor ID и Product ID. Как я говорил [[USB 2.0.#USB drivers]] эти данные нужны для того чтобы хост правильно выбрал драйвер для конкретного устройства, то есть он проверяет пару Vendor/Product ID и под него выбирает нужный драйвер.
Vendor ID нужно покупать и он стоит очень дорого
![[джимхалперт-платно-1.gif|400]]
а Product ID уже выбирает сам Vendor под свои нужды. У нас деняк нет, однако есть такие Product ID которые можно использовать для учебных проектов, такие как например у STM есть Product ID для CDC устройства, аудио устройства и т.д.
![[рататуй-бесплатно.gif|400]]

Все стандартные Vendor ID и Product ID которые вшиты в Windows и Linux можно просмотреть на этом сайте [usb-ids.gowdy.us/usb.ids](https://usb-ids.gowdy.us/usb.ids)

![[Pasted image 20250930225308.png|400]]

Таким образом для stm32 CDC устройства можно использовать такой набор
```c title=usbd_desc.c
#define USBD_VID                      0x0483
#define USBD_PID                      0x5740
```

Далее нужно выбрать на каком языке будут дальнейшие строковые дескрипторы через дефайн `USBD_LANGID_STRING`, коды для нужного языка можно просмотреть в этом [файле](http://www.baiheee.com/Documents/090518/090518112619/USB_LANGIDs.pdf)
Так для английской США(если честно не знаю какая будет разница при разных диалектах) будет выбираться таким образом
```c title=usbd_desc.c
#define USBD_LANGID_STRING            0x0409
```

Смысл каждого дескриптора:
- **USBD_MANUFACTURER_STRING**
    Название производителя. ОС показывает её в менеджерах устройств; помогает пользователю/интегратору понимать, кто выпустил устройство.
- **USBD_PRODUCT_FS_STRING/USBD_PRODUCT_HS_STRING**
    Имя продукта. ОС показывает её в менеджерах устройств. `*_FS_STRING` и `*_HS_STRING` используются если у нас одновременно работает OTG_FS и OTG_HS. Но например в stm32f411xe нет OTG_HS, поэтому всё что связано с дескрипторами с `*_HS_STRING` можно из `usbd_desc` убрать
- **USBD_CONFIGURATION_FS_STRING/USBD_CONFIGURATION_HS_STRING**
    Текст, описывающий конфигурацию USB, например `"Default configuration"`. Редко критичен, но полезен при сложных/несколько конфигурациях; ОС может показать описание конфигурации.
- **USBD_INTERFACE_FS_STRING/USBD_INTERFACE_HS_STRING**
    Описание интерфейса, например `"CDC ACM Interface"`, особенно важен для **композитных устройств** — каждое интерфейсное устройство (CDC, MSC, HID и т.д.) может иметь своё имя, что делает интерфейсы понятнее в ОС.

Пример настройки строковых дескрипторов

```c title=usbd_desc.c
#define USBD_MANUFACTURER_STRING     "My Company"
#define USBD_PRODUCT_FS_STRING       "My USB Device (FS)"
#define USBD_CONFIGURATION_FS_STRING "Default Configuration"
#define USBD_INTERFACE_FS_STRING     "CDC Interface"
```

В `usbd_desc.c` также находится Device descriptor в структуре `USBD_DeviceDesc`. Его настройка уже производится в соответствии с [Главой 9.6.1 USB 2.0. спецификации](http://www.poweredusb.org/pdf/usb20.pdf#%5B%7B%22num%22%3A978%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2Cnull%2Cnull%2Cnull%5D)

## Настройка класса устройств
Настройка класса USB-устройств состоит из двух основных частей:
1. **Настройка Configuration Descriptor** в файле `usbd_cdc.c`. Здесь описывается устройство на уровне USB — interface, endpoint descriptors, а также специфичные для класса дескрипторы. Как например [functional descriptors для CDC-Communication interface](USB%20CDC%20class#CDC-Communication%20interface) для CDC класса
2. **Настройка функций интерфейса класса** в файле `usbd_cdc_if.c`. Здесь реализуются функции для передачи и приёма данных, а также обработка специфичных запросов класса (например, CDC-специфичных управляющих команд).

Кроме того, некоторые классы устройств могут требовать дополнительную специфичную настройку, например, работу с конкретным аппаратным модулем, как это реализовано в файлах `usbd_ccid_smartcard.c` для CCID; при этом общая архитектура для всех классов всегда строится по одной схеме: в одном файле (`*_c`, например `usbd_ccid.c` или `usbd_cdc.c`) настраиваются дескрипторы и колбэки класса, а в другом файле (`*_if.c`, например `usbd_ccid_if.c` или `usbd_cdc_if.c`) реализуется интерфейс класса, связывающий стек USBD с приложением.

### Передача/приём в CDC девайсе
В HAL USBD для каждой передачи данных необходимо **установить буфер**, из которого будет отправляться сообщение. Библиотека читает данные из этого буфера и отправляет их по USB, вызывая колбэк `CDC_Interface_TransmitCplt` после завершения передачи.

Поэтому отправка данных в USBD выглядит так:
1. Мы выставляем буфер с сообщением
2. Мы говорим USBD что готовы отправлять сообщение

```c
USBD_CDC_SetTxBuffer(&husbd, *Buf, Len);
USBD_CDC_TransmitPacket(&husbd);
```

> [!attention] 
> Соответственно во время всей передачи буфер должен существовать, иначе отправка будет закорапчена. 

Приём данных происходит **пакетами по 64 байта**(ну или сколько вы выставите размер endpoint в `usbd_desc`) через [BULK endpoint](USB%202.0.#Bulk%20Transfer). Поскольку в BULK передаче **не определён конец сообщения**, контроллер не знает полного размера сообщения заранее. Поэтому каждый пакет, включая неполные (<64 байт), обрабатывается отдельным вызовом колбэка `CDC_Interface_Receive`.
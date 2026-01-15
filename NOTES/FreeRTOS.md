Tags: #embedded 
> [!sources] 
>  [Mastering-the-FreeRTOS-Real-Time-Kernel](https://github.com/FreeRTOS/FreeRTOS-Kernel-Book/releases/download/V1.1.0/Mastering-the-FreeRTOS-Real-Time-Kernel.v1.1.0.pdf)

***

<span style="font-size: 25">List of content:</span>

```table-of-contents
```

***

<span style="font-size: 25">Tasks:</span>

```tasks
```

***

# Задачи

[lab2.pdf](https://qiriro.com/ecs6264/static_files/labs/lab2/lab2.pdf)

Смоделировать систему обработки событий, которая реагирует на пользовательский ввод (кнопки) и таймеры, с различными приоритетами задач, чтобы отрабатывать события в нужном порядке, используя FreeRTOS механизмы.

**Аппаратное обеспечение:**
- STM32G474RE на плате Nucleo или похожей
- Несколько кнопок (2-3)
- Несколько светодиодов (3-4)
- UART для логирования
    

**Сценарий:**

1. **Задача кнопок (Button Task)**: опрашивает состояние кнопок каждые 20 мс. Я думаю можно заменить на прерывания по нажатию кнопки.
    - При нажатии кнопки формирует событие и отправляет его в очередь.
    - Каждая кнопка генерирует отдельный тип события (`EVENT_BUTTON_1`, `EVENT_BUTTON_2`, …).
2. **Задача таймера (Timer Task)**: создает несколько **software timers** с разными периодами (например, 500 мс, 1 с, 2 с).
    - При срабатывании таймера, посылает событие в **общую очередь событий**.
    - Можно использовать разные callback функции, но одну очередь для всех событий.
3. **Менеджер событий (Event Manager Task)**:
    - Берёт события из очереди и выполняет соответствующее действие:
        - Включает/выключает светодиоды
        - Логирует событие в UART
    - Приоритет выше, чем у Button Task, чтобы срочные события обрабатывались сразу.
    - Демонстрирует **обработку разных типов событий через одну очередь** (структуры с `eventType` + `data`).
4. **Дополнительно**:
    - Использовать **binary semaphore** или **task notification** для сигнализации между ISR (например, таймер SysTick или внешнее прерывание кнопки) и Event Manager.
    - Можно добавить задачу с низким приоритетом (`Idle Task`) для подсчета статистики: сколько событий обработано, сколько таймеров сработало, среднее время обработки события.

## Задача 2
[Introduction to RTOS Part 5 - Queue(с таймкодом)](https://youtu.be/pHJ3lxOoWeI?si=l4mKILhu-lUAz9j3&t=581)

Есть две задачи. Первая задача читает что пришло с UART и отправляет обратно. Если пришло `delay xxx`, то мы отправляем на queue 1 `xxx`. 

Вторая задача берёт данные из queue 1 и изменяет периодичность с которой она мигает светодиодом. Каждый раз когда она мигает светодиодом, она должна отправлять сообщение `I blinked x times` в queue 2. Каждые 100 миганий она должна отправить `SOTKA!!!` в queue 2. 

А уже задача 1 также должна дополнительно отправлять то что отправило task 2.

## Задача 3
[Introduction to RTOS Part 7 - Semaphore(с таймкодом)](https://youtu.be/5JcMtbA9QEE?si=UzGrfBUFTnR0uS_6&t=596)

Есть 5 задач, каждый должен отправлять по 3 раза свой номер в circular buffer. И есть 2 задачи которые должны принимать данные из circular buffer и отправлять их по UART. Проблема тут в shared resource.

## Задача 4
[Introduction to RTOS Part 9 - Hardware Interrupts(с таймкодом)](https://youtu.be/qsflCf6ahXU?si=ZzcR7UfzRJBzBg9d&t=747)

![[Pasted image 20251116180014.png]]

## Задача 5

Представьте себе пять безмолвных философов, сидящих вокруг круглого стола, перед каждым из которых стоит тарелка с бесконечным запасом спагетти или лапши. Между каждой парой соседних философов на столе лежит ровно одна китайская палочка, так что всего на столе находится пять палочек. 
![[Pasted image 20251120183426.png|400]]

Жизнь каждого философа состоит из чередования периодов глубоких размышлений и приема пищи, при этом они не общаются друг с другом. Проблема возникает из-за физики процесса: чтобы съесть лапшу, философу необходимы две палочки одновременно — одна в левую руку и одна в правую. Когда философ проголодается, он пытается взять две ближайшие к нему палочки (ту, что лежит непосредственно слева, и ту, что справа), однако он не может взять палочку, если она уже находится в руках у соседа. Если философу удается завладеть обеими палочками, он ест в течение некоторого времени, после чего кладет оба инструмента обратно на стол и снова погружается в раздумья. Задача состоит в том, чтобы придумать алгоритм поведения философов, который позволит каждому из них регулярно есть и не приведет к ситуации, когда все они возьмут, например, только левую палочку и будут вечно ждать правую, умерев от голода из-за взаимной блокировки.

Есть решение N-1 есть counting semaphore с максимум значением N-1, где N - количество философов и соответственно количество палочек. Каждый философ после процесса раздумья должен запросить counting semaphore. Если он его может взять то он садится за стол, если нет то он ждёт. Таким образом за столом могут сидеть только 4 философа, 5 будет стоять.

# Heap memory management
To create and delete tasks dynamically, we cannot rely on static memory such as a statically allocated stack. Static memory is fixed at compile time, which means the size and number of tasks must be known in advance.

Static allocation also makes task deletion impractical. Since a statically allocated stack behaves like a fixed block of memory, it cannot be easily reclaimed or reused for other tasks once allocated. This would force a strict allocation order (similar to FIFO) and prevent flexible task management — which is clearly inconvenient.

To address this, FreeRTOS provides several heap management implementations: `heap_1.c`, `heap_2.c`, `heap_3.c`, `heap_4.c`, and `heap_5.c`. Each offers different trade-offs in terms of complexity, fragmentation handling, and flexibility.

> [!help] 
> Why don't use the malloc and free from standard library of C? 
> The standard `malloc()` and `free()` functions are not a good choice for real-time systems. Their behavior depends on how the C library is implemented, and it is usually **not deterministic** — meaning the time they take to run is unpredictable.
> 
> Here are the main problems:
> 
> - They can **fragment memory**, so after running for a while, you might be unable to allocate memory even if there’s still free space.
> - The time needed to allocate or free memory can **change from call to call**, which may cause delays in a real-time task.
> - They might **not be thread-safe**, or they may use **global locks** that block other tasks while memory is being managed.
> - The memory layout for `malloc()` and `free()` is defined by the **linker script**, which can make linker configuration more complex.
> - If the heap grows into other parts of memory, it can **corrupt variables** and cause bugs that are hard to find.
> 
> FreeRTOS provides its own memory management implementations to ensure **predictable timing**, **thread safety**, and **configurable behavior** suitable for real-time applications.

The FreeRTOS API functions that create kernel objects using statically allocated memory are only available when `configSUPPORT_STATIC_ALLOCATION` is set to 1 in `FreeRTOSConfig.h`. The FreeRTOS API functions that create kernel objects using dynamically allocated memory are only available when `configSUPPORT_DYNAMIC_ALLOCATION` is either set to 1 or left undefined in FreeRTOSConfig.h. It is valid to have both constants set to 1 simultaneously.

FreeRTOS heap implementation uses `pvPortMalloc()` instead of `malloc()` when RTOS requires RAM. Likewise, when FreeRTOS frees previously allocated RAM it calls `vPortFree()` instead of `free()`. `pvPortMalloc()` has the same prototype as the standard C library `malloc()` function, and `vPortFree()` has the same prototype as the standard C library `free()` function.

But for each heap implementation there are different `pvPortMalloc()` and `vPortFree()` functions implementation, which are all documented below at description of each `heapn.c` file

## Heap_1

In many small embedded systems, all tasks and kernel objects are created **before** the FreeRTOS scheduler starts. In such cases, the kernel allocates memory dynamically only once — during system initialization — and that memory remains allocated for the entire runtime.

`Heap_1` is designed for this small embedded systems. 
Because no memory is allocated or freed after startup, the allocation scheme does not need to handle complex issues such as **determinism** or **fragmentation**. Instead, it can focus on being **small** and **simple**.

`heap_1.c` provides the simplest memory allocator. It implements `pvPortMalloc()` but does not implement `vPortFree()`, meaning allocated memory can never be released. This makes `heap_1` suitable for applications that never delete tasks or kernel objects.

Some safety-critical or commercially critical systems can also use `heap_1`, since it avoids the common risks of dynamic memory—such as unpredictable timing, fragmentation, or failed allocations. Because `heap_1` only allocates and never frees, it is completely deterministic and cannot fragment memory.

Internally, `heap_1` manages a simple `uint8_t` array called the FreeRTOS heap. Each call to `pvPortMalloc()` simply takes the next free block from this array. The total heap size, in bytes, is set by the `configTOTAL_HEAP_SIZE` constant in `FreeRTOSConfig.h`.

Each dynamically created task results in two calls to `pvPortMalloc()`, first for [Task Control Block(TCB)](Real%20Time%20Operating%20Systems(RTOS)#Task%20Control%20Block), second for the taks's stack.

As shown on picture below, `heap_1` simply divides the static heap array into smaller blocks each time a task is created
![[Pasted image 20251030120916.png]]

## Heap_2
 - [ ] #todo Make this part about heap_2 based on the text about heap_4

## Heap_3
Heap_3.c uses the standard library malloc() and free() functions, so the linker configuration defines the heap size, and the configTOTAL_HEAP_SIZE constant is not used.
Heap_3 makes malloc() and free() thread-safe by temporarily suspending the FreeRTOS scheduler for the duration of their execution.
- [ ] #todo Learn more about how heap_3 makes malloc and free thread safe. And also learn about malloc and free functions themselves

## Heap_4
Like [[#Heap_1]] and [[#Heap_2]], `heap_4` works by subdividing an array into smaller blocks. As before, the array is statically allocated and dimensioned by `configTOTAL_HEAP_SIZE`, which makes FreeRTOS appear to use a lot of RAM as the heap becomes part of the FreeRTOS data.

Heap_4 uses first fit algorithm ensures pvPortMalloc() uses the first free block of memory that is large enough to hold the number of bytes requested. For example, consider the scenario where:
- The heap contains three blocks of free memory that, in the order in which they appear in the array, are 5 bytes, 200 bytes, and 100 bytes, respectively.
- `pvPortMalloc()` requests 20 bytes of RAM.
- The first block large enough to hold 20 bytes is the 200-byte block. Therefore, `pvPortMalloc()` splits it into two parts: one 20-byte block (returned to the caller) and one 180-byte block (which remains free).
- If the remaining 180-byte block is located next to another free block (for example, the 5-byte block), the allocator merges them into a single 185-byte free block to reduce fragmentation.

Picture below demonstrates how the heap_4 first_fit algorithm with memory coalescence works
![[Pasted image 20251030122040.png]]

## Heap_5

`heap_5.c` implements the same allocation algorithm as [[#Heap_4]] (first-fit with block splitting and coalescing), but it lets the FreeRTOS heap be built from **multiple separate memory regions** instead of a single contiguous array. In other words, heap_5 presents several physically separated RAM areas as one logical heap to the allocator.

> [!help] 
> Why this is useful
> Many MCUs and systems have RAM in multiple, non-contiguous places: internal SRAM, tightly-coupled memory (TCM), external PSRAM, on-chip SRAM banks, or special fast memory regions.
> ![[Pasted image 20251030122819.png|300]]
> The linker may present these as separate address ranges. `heap_5` is useful when you want dynamic allocation to use more than one of those ranges without rewriting the linker script to make them appear contiguous.

`vPortDefineHeapRegions()` initializes `heap_5` by defining the start address and size of each separate memory region that will form the combined heap.

Among all FreeRTOS heap implementations, `heap_5` is the only one that requires **explicit initialization**. The function must be called **before** any dynamic memory allocation can take place. As a result, kernel objects such as tasks, queues, and semaphores cannot be created dynamically **until after** `vPortDefineHeapRegions()` has been called.

```c
void vPortDefineHeapRegions( const HeapRegion_t * const pxHeapRegions );
```
`vPortDefineHeapRegions()` takes an array of `HeapRegion_t` structures as its only parameter. Each structure defines the start address and size of a memory block that will become part of the heap—the whole array of structures defines the entire heap space.
```c
typedef struct HeapRegion
{
    /* The start address of a block of memory that will be part of the heap.*/
    uint8_t *pucStartAddress;
    /* The size of the block of memory in bytes. */
    size_t xSizeInBytes;
} HeapRegion_t;
```

> [!attention] 
> Do not assign your entire RAM to a `HeapRegion_t` structure.  
> The `HeapRegion_t` array should describe **only the memory areas reserved for the heap**, not the whole RAM.  
> If you include all RAM, there will be no memory left for global variables, stack, or other data used by the application.

However, there is a risk of **memory overlap**. For example, the linker may place some global variables in RAM during compilation. In the figure below, the linker has allocated variables up to address `0x01nnnn`.
![[Pasted image 20251030125755.png|300]]

If `pucStartAddress` in the `HeapRegion_t` configuration is set to `0x010000`, the FreeRTOS heap would overlap with these variables, causing undefined behavior.

One could set the start address of the first `HeapRegion_t` to `0x0001nnnn` instead of `0x00010000` to avoid overlap. However, this approach is **not recommended** because:

- The start address can be difficult to determine.
- The RAM used by the linker may change in future builds, requiring updates to the start address.
- Build tools cannot detect if the heap and linker-assigned RAM overlap, so the developer receives no warning.

A more reliable solution is to **create a dedicated array** for the FreeRTOS heap, e.g., `ucHeap`. By explicitly defining a variable, the linker automatically allocates a safe region in RAM, eliminating the risk of overlap.

Then, the `HeapRegion_t` structure can simply reference the **start address and size of `ucHeap`**. This approach is easier, safer, and more maintainable.
```c

/* Declare an array that will be part of the heap used by heap_5. The array will be placed in RAM1 by the linker. */

#define RAM1_HEAP_SIZE ( 30 * 1024 )
static uint8_t ucHeap[ RAM1_HEAP_SIZE ];

// Create an array of HeapRegion_t definitions. 
// Whereas in Listing 3.5 the first entry described all 
// of RAM1, so heap_5 will have used all of RAM1, 
// this time the first entry only describes the ucHeap array, 
// so heap_5 will only use the part of RAM1 that contains 
// the ucHeap array. The HeapRegion_t structures must still 
// appear in start address order,
// with the structure that contains the lowest 
// start address appearing first. 
const HeapRegion_t xHeapRegions[] =
{
    { ucHeap, RAM1_HEAP_SIZE },
    { RAM2_START_ADDRESS, RAM2_SIZE },
    { RAM3_START_ADDRESS, RAM3_SIZE },
    { NULL, 0 } /* Marks the end of the array. */
};

int main( void )
{
    /* Initialize heap_5. */
    vPortDefineHeapRegions( xHeapRegions );
    /* Add application code here. */
}
```
Tags: #c #cpp 
# Static переменная
## Локальная static переменная
Локальная static переменная в функции делает переменную такой, что она запоминает своё состояние независимо от самой функции. То есть эта переменная будет сохранять своё значение даже после того, как мы выйдем из функции.
```c
#include <stdio.h>

// function with static variable
int fun()
{
    static int count = 0;
    count++;
    return count;
}

int main()
{
    printf("%d\n", fun());
    printf("%d", fun());
    return 0;
}


// Output:
// 1 
// 2
```
Локальные static переменные находятся в той же секции памяти что и глобальные переменные, т.е. .bss если переменная не инициализирована(соответственно неинициализированные static локальные переменные будут инициализированы как 0) и .data если переменная инициализирована. Т.е. они создаются не на стеке и соответственно не очищаются после выхода из функции. 

Однако в отличии от глобальной переменной компилятор не позволит обращаться к этой переменной в других функциях.

## Static глобальные переменные
Тут уже интереснее. Вообще в си если мы хотим сделать что-то около ООП, мол файлы .c обычно представляют из себя классы, а static это аналог private для полей класса.
Т.е. когда мы создаём глобальную переменную static то она будет видна только в файле .c где мы добавили этот static. Мы не можем сделать допустим так

```c
//  lib.c
#include <stdio.h>
#include "lib.h"

static int sf;

int add_one()
{
	return sf+1;
}

int print_sf()
{
	printf("%d", sf); // its all okay cuz this function in lib.c
}
```

```c
#include <stdio.h>
#include "lib.h"

int main()
{
	add_one(); // It's good cuz we calling function from lib.c
	print_sf(); // Same good cuz we calling function from lib.c
	
	printf("%d", sf); // Error, there are no sf variable in main.c
}
```
То есть теперь переменная sf будет виден только в области видимости lib.c, но в main.c мы не можем его использовать.
> [!warning] 
>  Не путай делая static переменную в .h вместо .c. Вспоминай то что препроцессор просто заменяет `#include "xxx.h"` просто на то что находится в файле xxx.h. Т.е. если у нас в xxx.h будет статик глобальная переменная тогда везде где будет `#include "xxx.h"` будет статическая переменная. Поэтому если ты хочешь сделать библиотеку со статической переменной, то делай статическую переменную в .c


# Static функция
Со static функциями всё то же самое что и со [[static#Static глобальные переменные]]. То есть эта функция будет видна только в области видимости .c файла где мы его добавили.
Из-за этого можно вот так вот играться с файлами
```c
// a.c
#include <stdio.h>

// Undefined behavior: already defined in main.
// void f() { puts("a f"); }

/* OK: only declared, not defined. Will use the one in main. */
void f(void);

/* OK: only visible to this file. */
static void sf() { puts("a sf"); }

void a() {
    f();
    sf();
}
```


```c
// main.c
#include <stdio.h>

void a(void);        

void f() { puts("main f"); }

static void sf() { puts("main sf"); }

void m() {
    f();
    sf();
}

int main() {
    m();
    a();
    return 0;
}

// Output:
// main f
// main sf
// main f
// a sf

```

# Static in objects
`static` in class allows you to make common variables for every object of this class(so you can change them from one object of this class and static variable changed in all object of this class). You can forbid changing static variable via `const`
```cpp
class Year {
	static const int min = 1800;
	static const int max = 2200;
public:
	class Invalid { };
	Year(int x): y{x} {
		if (x < min || max<= x) throw Inwalid{};
	}
	int year() { return y; }
private:
	int y;
}
```

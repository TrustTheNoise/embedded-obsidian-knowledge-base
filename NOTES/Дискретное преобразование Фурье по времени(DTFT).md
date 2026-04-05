Tags: #signals 

---

<span style="font-size: 25">List of content:</span>

```table-of-contents
```

---

<span style="font-size: 25">Tasks:</span>

```tasks
```

---

# Дискретное преобразование Фурье по времени
Дискретное преобразование Фурье по времени(далее DTFT от Discrete Time Fourier Transform) используется ТОЛЬКО для дискретных сигналов и преобразует их в непрерывный спектр.
Но что такое дискретный сигнал и как он получается. Можно объяснить это по простому и строго математически и двумя разными способами мы получим DTFT
## Простой вывод
![[Дискретизация и квантование#По простому]]
Тогда мы можем преобразовать [[Непрерывное преобразование Фурье(CTFT)]] заменив t на nTs
$$X (omega)=integral_(-infinity)^(infinity) x (t) e^(-j omega t) d t xrightarrow t=n T_(s) sum_(n=-infinity)^(infinity) underbrace x (n T_(s))_(x[n]) e^(-j #text(fill: orange)[$omega$] n #text(fill: orange)[$T_(s)$])$$
Выделенное жёлтым можно объединить если сделать $T_(s)=frac(1, f_(s))$ тогда 
$omega T_(s)=2 pi f T_(s)=  2 pi frac(f, f_(s))=Omega$ - нормализированная частота
> [!help] 
> Что значит нормализированная и вообще что всё это значит?
> Смотри если мы будем изменять f от 0 до fs то у нас нормализированная частота будет всегда идти от 0 до $2 pi$, соответственно если мы будем увеличивать f до 2fs то $Omega$ будет идти до $4 pi$. Таким образом у нас получается нормализированная частота относительно $f_(s)$

Таким образом DTFT будет таким
$$ #text(fill: red)[$X (Omega)=sum_(n=-infinity)^(infinity) underbrace x (n T_(s))_(x[n]) e^(-j Omega n)$]$$
## Более математический вывод
![[Дискретизация и квантование#Строгое математическое объяснение]]
В таком случае мы в [непрерывном преобразовании Фурье(CTFT)](Непрерывное%20преобразование%20Фурье(CTFT)) заменяем x(t) на $x_(s) (t)$
$$X (omega)=integral_(-infinity)^(infinity) sum_(n=-infinity)^(infinity) x[n]delta (t-n T_(s)) e^(-j omega t) d t=sum_(n=-infinity)^(infinity) x[n]integral_(-infinity)^(infinity) delta (t-n T_(s)) e^(-j omega t) d t$$
Опять же как мы помним из [[Дельта функция#Как применяется дельта функция]] дельта функция $delta (t-t_(0))$ при интегрировании с какой то функцией f(t) возращает эту функцию на $f (t_(0))$ поэтому у нас получится
$$X (omega)=sum_(n=-infinity)^(infinity) x[n]e^(-j omega n T_(s))$$
Мы получили то же самое что и в [[#Простой вывод]] а мы там же разобрали что $omega T_(s)=Omega$ - нормализованная частота поэтому DTFT будет таким
$$ #text(fill: red)[$X (Omega)=sum_(n=-infinity)^(infinity) x[n]e^(-j Omega n)$]$$

# Свойства DTFT
$$X (Omega+2 pi k)
=
	sum_(n=-infinity)^(infinity)
		x[n]e^(-j (Omega+2 pi k))
=
	sum_(n=-infinity)^(infinity)
		x[n]e^(-j Omega) 
		underbrace
		e^(-j 2 pi k)
		_(1)
=$$
$$=
	sum_(n=-infinity)^(infinity)
		x[n]e^(-j Omega)
=
X (Omega)$$
Т.е. спектр DTFT периодический с периодом $2 pi$......$X (Omega)=X (Omega+2 pi k)$, $k in ZZ$
Для не комплексных сигналов это означает что
$X (-Omega)=X^(*) (Omega)=X (2 pi-Omega)$
$|X (-Omega)|=|X (Omega)|=|X (2 pi-Omega)|$
$phi (-Omega)=-phi (Omega)=-phi (2 pi-Omega)$

Сигнал: дискретный, апериодический
Спектр: непрерывный, периодический

# Обратный DTFT
$$ #text(fill: red)[$x[n]=frac(1, 2 pi) integral_(0)^(2 pi) X (Omega) e^(j Omega n) d Omega$]$$
Как можно заметить эта формула не сильно отличается от обратного CTFT $x (t)=frac(1, 2 pi) integral_(-infinity)^(infinity) X (omega) e^(j omega t) d t$
Единственное что изменяется так это то что мы вместо $omega$ применяем $Omega$ а также у нас приделы интегрирования от 0 до $2 pi$ потому что как мы выяснили в [[#Свойства DTFT]] спектр DTFT является периодической на $2 pi$

# Пример DTFT
[Разбор примера с DTFT](https://youtu.be/eufPrOFwQGE?si=npo-AHDkWKqeaNX2&t=2110)
[Больше примеров с DTFT](https://youtu.be/ttqLVOACMY8?si=AaXbspH12UvzYgsW&t=2471)
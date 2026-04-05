```
arrow.r.long^("text")
```

$$arrow.r.long^("text")$$

```
underbrace("up", "down")
```
$$
underbrace("up", "down")
$$
```
overbrace("down", "up")
```
$$
overbrace("down", "up")
$$ 
```
#set math.equation(numbering: "(1)")

$ "first formula" $ // получит номер автоматически

// это нужно обязательно делать в ```typst блоке кода, 
// иначе не работает, при этом если что нужно будет в другой части 
// заметки написать уже с тэгом (2), то придёцца писать

#set math.equation(numbering: "(1)")

#counter(math.equation).update(1)

$ "second formula" $ // получит номер автоматически

```

```typst
#set math.equation(numbering: "(1)")

$ "first formula" $ // получит номер автоматически
```

```typst
#set math.equation(numbering: "(1)")

#counter(math.equation).update(1)

$ "second formula" $ // получит номер автоматически
```

```
oo "или" infinity
```
$$oo "или" infinity $$
```latex
\begin{cases} 
	up \\ 
	down 
\end{cases}
```
$$cases("up", "down")$$
```
"up" \ 
"down"
```
$$
"up" \ 
"down"
$$

```
& "up" \
& "down"

// тут & работает как якорь выравнивания
```

$$
& "up" \
& "down"
$$

```
mat(delim: "|",
    "up";
    & "down"
)
```
$$
mat(delim: "|",
    "up";
    "down"
)
$$

```
cancel("text")
```
$$
cancel("text")
$$

# Логические знаки
| Описание         | Код             | Символ            |
| ---------------- | --------------- | ----------------- |
| Ложь             | `bot`           | $bot$             |
| Конъюнкция (И)   | `and`           | $and$             |
| Дизъюнкция (ИЛИ) | `or`            | $or$              |
| Отрицание        | `not`           | $not$             |
| Не равно         | `!= или eq.not` | $!=$ или $eq.not$ |
| Импликация       | `=>`            | $==>$             | 
| Эквивалентность  | `<=>`           | $<=>$             |
| Существует       | `exists`        | $exists$          |
| Для всех         | `forall`        | $forall$          |

# Математические знаки

```latex
a ast b
```
$$a ast b$$

# Форматирование математических символов
Запись для определённых множеств, например множеств real, rational, irrational numbers, просто пиши дважды букву, типа RR II и т.д.
```
RR II
```
$$RR " " II$$

# Линейная алгебра

## Векторы
```latex
bold(x) " "
arrow(x)
```

$$
bold(x) " "
arrow(x)
$$

```latex
arrow(u) times arrow(v)
```
$$
arrow(u) times arrow(v)
$$
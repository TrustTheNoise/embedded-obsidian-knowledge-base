Tags: #mathematics #precalculus

# Что это?

[[Linear equation]] и прочие equalities - это математическое утверждение о равенстве двух выражений, где задача состоит в нахождении значения переменных которые делают утверждение истинным.

Функции(обычно записываются как f) же это отношение между переменными. Функция это математическое описание правила, которое описывает изменение одного элемента в зависимости от другого, где каждому элементу из одного множества(называемые independent variables x,t и т.д.) ставятся в соответствие <span style="color:red">единственный</span> элемент из другого множества(называемого dependent variables y)
Также independent variables называются arguments, а dependent variables могут называться values of function.

Обычно функции записывают как
$\large y=f(x)$ - y is  equal to f of x
$\large x \mapsto y$ - читается x mapped onto y, это значит, что для каждого элемента x из области arguments существует правило, по которому он преобразуется в элемент y из values of function
$\large x \mapsto f(x)$ - то же самое, но только values of function записано как f(x)

Также функции записываются как
$$f: {\color{red} X} \to {\color{yellow} Y}$$
Читается как function f from set X to set Y. Это значит, что эта функция принимает arguments: $x \in {\color{red} X}$ и переводит в values $y \in {\color{yellow} Y}$.

Это можно изобразить таким образом:
![[Pasted image 20250703112205.png|500]]

Domain is a subset of X where defined all arguments of a function f(x)
$D_f \subset {\color{red} X}$
Ведь функции не всегда используются все значения из set X. Так например

$$f(x)=
\{ 
	x^2|x \in \mathbb{R} \ \land \ x>0 
\}
$$

Таким образом $x \in \mathbb{R}$ но domain $D_f = \mathbb{R} \land positive$.

Set ${\color{red} X}$ называется set of departure(область отправления).
Set ${\color{yellow} Y}$ называется codomain.
Range же называется subset для Y которые определены на функции для соответствующих x. Т.е.
$R_f \subset {\color{yellow} Y} \land \  R_f=\{y; y=f(x) \text{ for some } x\in D_f \}$
Иногда ещё range записывается как $V_f$ т.к. это set of **V**alues of function.

В таком случае функцию можно изобразить таким образом
![[Pasted image 20250703112348.png|500]]

# Explicit and implicit functions

Explicit function is one where the dependent variable is isolated on one side of the equation and expressed directly in terms of the independent variable. In other words, the output variable is explicitly given as a function of the input variable. We can easily find the dependency of function values y on arguments x.
$$y=x^2+3x+1$$

Implicit functions is one where the dependent variable is not isolated. Instead, both the dependent and independent variables are mixed together in an equation. The relationship between the variables is implied rather than directly stated.
$$x^2+y^2=r^2$$
$$F(x,y)=x^2+y^2-r^2$$
By this implicit function we can't easily understand dependency of y by argument x. As you remember this function is describe circle on the plane $\mathbb{R^2}$
![[Pasted image 20250812103755.png|300]]
As we can see this function has two values on one argument, so this implicit function is not a function at all. But we can produce two graphs to such function on two half-arcs(semicircles). And we can get two explicit functions for these two semicircles.

The upper arc:
$$f(x)=\sqrt{r^2-x^2}, x \in[-r;r]$$
The lower arc:
$$f(x)=-\sqrt{r^2-x^2}, x \in [-r; r]$$

Thus we get two explicit function from one implicit.

This trick of producing several explicit functions from one implicit can help us to understand the graph of that implicit functions. For example Lemniscate
$$F(x,y)=x^4-x^2+y^2$$
We can't easily understand dependency, so we can't easily draw a graph of this function. But what if we also divide this function by two sides(upper and below ox).

Upper ox:
$$y=\sqrt{-x^4+x^2}$$
Below ox:
$$y=-\sqrt{-x^4+x^2}$$
So now we have two explicit function graph of which we can draw on the plane. If we draw graphs of both obtained functions we can get graph of initial implicit function
![[Pasted image 20250812105625.png|300]]

# Surjections, injections, bijections
Итак у нас есть функция $\large f: X \to Y$

Функция f является surjection если range этой функции определён на всём множестве Y. То есть если $R_f=Y$
![[Pasted image 20250703144532.png|300]]
Функция f является injection если $f(x_1)=f(x_2) \iff x_1=x_2$ ещё такую функцию называют 1-to-1 
![[Pasted image 20250703144645.png|300]]
Если же функция является одновременно surjection и injection то такая функция называется bijection.

С surjection есть одна фишка. Ведь мы можем менять set Y(codomain) так, чтобы он был одинаковым с range. Просто считаем что $f:X \to R_f$.

# Inverse function

Если функция $\color{green} f:X \to Y$ является bijection, то есть surjection и injection одновременно, то такой функции можно сделать inverse function $\color{} f^{-1}: Y \to X$
![[Pasted image 20250703145650.png|400]]

Собственно всё что нужно чтобы перевести в inverse function, это нужно решить функцию $y=f(x)$ относительно x, то есть так что $x=f^{-1}(y)$.
> [!note] 
> In other words, if you apply f to some number and get the output y and then you pass y through $f^{-1}$, the output will be x again. The inverse function $f^{-1}$ undoes the effects of the function f.

Например

$$y=2x+3$$
$$x=\frac{1}{2}y-\frac{3}{2}$$

Ну чтобы можно было обе функции нарисовать на одной плоскости можно просто заменить в обратной функции y на x. Так чтобы $f^{-1}(y) \to f^{-1}(x)$

![[Pasted image 20250703150554.png|400]]

Как можно заметить $f(x)$ и $f^{-1}(x)$ симметричны относительно прямой y=x.

## В чём плюс inverse functions

Возможность использовать inverse functions являются очень полезной возможностью при решении уравнений. Представим что у нас есть уравнение:
$$f(x) = c$$
Где f - какая-то функция и c какая-то константа. Для решения уравнения нам нужно изолировать неизвестную x с одной из сторон уравнения. Однако в данном случае нам мешает это сделать функция f.
Но если мы воспользуемся inverse function $f^{-1}$ мы отменим эффект вызванный f на неизвестную x. В таком случае мы можем применить inverse function на обоих сторонах функции:
$$f^{-1}(f(x)) = f^{-1}(c)$$

По определению inverse function выполняет обратное действия для функции f поэтому вместе inverse function и функция отменяют друг друга. Тогда $f^{-1}(f(x)) = x$, а значит

$$x = f^{-1}(c)$$

# Composition of functions

Представим что у нас есть 2 функции:
- $f:X \to Y$
- $g: Y \to$![[Pasted image 20250703153413.png|100]]

То получается что значения f которые находятся в множестве Y используются в качестве аргумента для функции g, то есть в итоге эту функцию можно записать как $g(f(x)):x \in X$. Это можно изобразить как:
![[Pasted image 20250703153705.png]]

Тогда функция g(f(x)) будет называться composition of function f and g. Математически это также записывается как $(g \circ f)(x) := g(f(x))$

Таким образом composed function $(g \circ f)$ будет выражаться в следующих множествах 
$$\large 
g \circ f:
	X 
	\xrightarrow{ \color{lightgreen} f }
	Y 
	\xrightarrow{ \color{cyan} g } 
	Z
$$
f в таком случае называют называют <span style="color: lightgreen">inner function</span>
g же называют <span style="color:cyan">outer function</span>

Понимание порядка функций в composed function очень важно для определения [производной](Derrivative). А именно для работы с так называемым chain rule
$$\frac{d}{dt}(g \circ f)(t) = g'(f(t)) \cdot f'(t)$$
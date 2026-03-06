Tags: #precalculus 
> [!sources] 
>  

***

<span style="font-size: 25">List of content:</span>

```table-of-contents
```

***

<span style="font-size: 25">Tasks:</span>

```tasks
```

***

# Properties

## Sum of two logarithms

$$\large \log_a(x) + \log_a(y) = \log_a(xy)$$

> [!proof] 
>  In fact, the only thing we know about logs is the inverse relationship with the exponential function. The only way to prove this property is to use this relationship.
>  This properties is analogy to property of exponential property
>  $$b^m b^n = b^{m+n}$$
>  So if we declare that $x = b^m$ and $y = b^n$ then 
>  $xy = b^{m+n}$
>  Taking the logarithm of both sides gives us
>  $$
>      {\color{red} \log_b(xy) } 
>  = 
>      \log_b(b^{m+n}) 
>  = 
>      m+n 
>  = 
>      {\color{red} \log_b(x)+\log_b(y) }
>  $$

Same proof will be for difference of logarithms, just think of logarithms as clever way to talk about exponent(or power) $a$ in exponential expressions like $x^{a}$
$$\large \log_a(x) + \log_a(y) = \log_a(\frac{x}{y})$$

## Logarithm of powered expression

$$\large \log(x^a)=a \log(x)$$

> [!proof] 
>  By definition of logarithm:
>  $$\log_b(x) = y \iff x = b^{y}$$
>  So if we raise both sides of second equation to the power of a then
>  $$x^a = b^{ay}$$
>  Now if we took a logarithm with base of b from both sides we will get
>  $$\log_b(x^a)=\log_b(b^{ay}) \iff \log_b(x^a) = a y \iff \boxed{  \log_b(x^a) = a \log_b(x) }$$

## Change of base formula

$$\large \log_x(y) = \frac{\log_a(x)}{\log_a(y)}$$

> [!proof] 
>  By definition of logarithm:
>  $$\log_b(x) = y \iff x = b^{y}$$
>  So if we take logarithm with base a from both sides of second equation then
>  $$\log_a(x) = \log_a(b^{y})$$
>  From  [[#Logarithm of powered expression]] property we can got that:
>  $$\log_a(x) = y\log_a(b) \implies y = \frac{\log_a(x)}{\log_a(b)}$$
>  So as we knew that $y = \log_b(x)$, that implies:
>  $$\boxed{ \log_b(x) = \frac{\log_a(x)}{\log_a(b)} }$$
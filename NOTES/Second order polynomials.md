Tags: #precalculus 
> [!sources] 
>  No_bullshit_guide_to_math_and_physics 1.6

***

<span style="font-size: 25">List of content:</span>

```table-of-contents
```

***

<span style="font-size: 25">Tasks:</span>

```tasks
```

***

# Second order polynomials solving

## Completing the square 

Any quadratic expression $Ax^2+Bx+C$ can be rewritten in the form $A(x-h)^2+k$ for some constants h and k. This transformation is called **completing the square** because it rewrites the quadratic as a squared binomial plus a constant. The constant k is chosen so that the expression inside the parentheses becomes a perfect square.

The graph of the function $f(x) = A(x - h)^2 + k$ is the same as the graph of the function $f(x)=Ax^2$ except it is shifted h units to the right and k units upward.

Let’s try to find the values of k and h needed to complete the square in the expression $ax^2+bx+c$. We start from the assumption that the two expressions are equal, and then expand the bracket to obtain:
$$ax^2+bx+c = A(x-h)^2+k$$
$$ax^2+bx+c = \underbrace{A}_{a}x^2+\underbrace{(-2Ah)}_{b}x+\underbrace{Ah^2+k}_{c}$$

From this we can express that
$$b = -2Ah = -2ah \iff \color{red} h = -\frac{b}{2a}$$
$$c = Ah^2+k = ah^2+k \iff \color{red} k = c - ah^2 = c - \frac{b^2}{4a} $$

But because formula for finding k is more difficult, its sufficient to find the h and then just find the value of $f(h)$ where $f(x) = ax^2+bx+c$. Why it is work? Because point (h, k) graphically is starting point of quadratic expression $ax^2+bx+c$

## Solving quadratic equations


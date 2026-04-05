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

Any quadratic expression $A x^(2)+B x+C$ can be rewritten in the form $A (x-h)^(2)+k$ for some constants h and k. This transformation is called **completing the square** because it rewrites the quadratic as a squared binomial plus a constant. The constant k is chosen so that the expression inside the parentheses becomes a perfect square.

The graph of the function $f (x) = A (x - h)^(2) + k$ is the same as the graph of the function $f (x)=A x^(2)$ except it is shifted h units to the right and k units upward.

Let’s try to find the values of k and h needed to complete the square in the expression $a x^(2)+b x+c$. We start from the assumption that the two expressions are equal, and then expand the bracket to obtain:
$$a x^(2)+b x+c = A (x-h)^(2)+k$$
$$a x^(2)+b x+c = underbrace A_(a) x^(2)+underbrace (-2 A h)_(b) x+underbrace A h^(2)+k_(c)$$

From this we can express that
$$b = -2 A h = -2 a h <=> #text(fill: red)[$h = -frac(b, 2 a)$]$$
$$c = A h^(2)+k = a h^(2)+k <=> #text(fill: red)[$k = c - a h^(2) = c - frac(b^(2), 4 a)$]$$

But because formula for finding k is more difficult, its sufficient to find the h and then just find the value of $f (h)$ where $f (x) = a x^(2)+b x+c$. Why it is work? Because point (h, k) graphically is starting point of quadratic expression $a x^(2)+b x+c$

## Solving quadratic equations


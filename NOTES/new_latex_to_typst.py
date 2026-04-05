#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert LaTeX math to Typst math syntax for Obsidian Typst Mate.
Handles colors, boxed formulas, cancel, and complex arrows.
"""

import os, sys, re

# ---------------------------------------------------------------------------
# Brace utilities
# ---------------------------------------------------------------------------

def find_close(s, start, open_c='{', close_c='}'):
    depth = 0
    i = start
    while i < len(s):
        if s[i] == open_c:
            depth += 1
        elif s[i] == close_c:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(s) - 1

def get_arg(s, pos):
    while pos < len(s) and s[pos] in ' \t\n':
        pos += 1
    if pos >= len(s) or s[pos] != '{':
        # Попытка взять один символ, если нет скобок
        if pos < len(s) and s[pos].isalnum():
            return s[pos], pos + 1
        return None, pos
    end = find_close(s, pos)
    return s[pos+1:end], end + 1

# ---------------------------------------------------------------------------
# Core converter
# ---------------------------------------------------------------------------

STRIP_COMMANDS = [
    'tiny', 'scriptsize', 'footnotesize', 'small', 'normalsize', 
    'large', 'Large', 'LARGE', 'huge', 'Huge',
    'displaystyle', 'textstyle', 'scriptstyle', 'scriptscriptstyle',
    'left', 'right' # Typst расставляет скобки автоматически или через lr()
]

SIMPLE = {
    'infty': 'infinity', 'alpha': 'alpha', 'beta': 'beta', 'gamma': 'gamma', 'Gamma': 'Gamma',
    'delta': 'delta', 'Delta': 'Delta', 'epsilon': 'epsilon', 'varepsilon': 'epsilon.alt',
    'zeta': 'zeta', 'eta': 'eta', 'theta': 'theta', 'Theta': 'Theta', 'vartheta': 'theta.alt',
    'iota': 'iota', 'kappa': 'kappa', 'lambda': 'lambda', 'Lambda': 'Lambda',
    'mu': 'mu', 'nu': 'nu', 'xi': 'xi', 'Xi': 'Xi', 'pi': 'pi', 'Pi': 'Pi',
    'rho': 'rho', 'varrho': 'rho.alt', 'sigma': 'sigma', 'Sigma': 'Sigma',
    'tau': 'tau', 'upsilon': 'upsilon', 'Upsilon': 'Upsilon', 'phi': 'phi',
    'varphi': 'phi.alt', 'Phi': 'Phi', 'chi': 'chi', 'psi': 'psi', 'Psi': 'Psi',
    'omega': 'omega', 'Omega': 'Omega', 'sin': 'sin', 'cos': 'cos', 'tan': 'tan',
    'cot': 'cot', 'sec': 'sec', 'csc': 'csc', 'ln': 'ln', 'log': 'log', 'exp': 'exp',
    'sum': 'sum', 'prod': 'product', 'int': 'integral', 'partial': 'diff', 'nabla': 'nabla',
    'cdot': 'dot.op', 'times': 'times', 'neq': 'eq.not', 'leq': 'lt.eq', 'geq': 'gt.eq',
    'to': 'arrow.r', 'rightarrow': 'arrow.r', 'Rightarrow': 'arrow.r.double', 
    'leftarrow': 'arrow.l', 'quad': '  ', 'qquad': '    ', 'mathbb': '', # ZZ, RR handled later
}

# Маппинг для \mathbb{Z} -> ZZ
MATHBB = {'Z': 'ZZ', 'R': 'RR', 'N': 'NN', 'Q': 'QQ', 'C': 'CC'}

def convert(s):
    if not s: return ""
    result = []
    i = 0
    n = len(s)

    while i < n:
        c = s[i]

        if c.isspace():
            result.append(c)
            i += 1
            continue

        if c == '\\':
            j = i + 1
            # Обработка переноса строки
            if j < n and s[j] == '\\':
                result.append(" \\\n")
                i = j + 1
                continue
            
            # Экранированные символы
            if j < n and s[j] in '{}_^%$#&':
                result.append(s[j])
                i = j + 1
                continue

            # Читаем команду
            k = j
            while k < n and (s[k].isalpha()): k += 1
            cmd = s[j:k]
            
            # --- СЛОЖНЫЕ КОМАНДЫ ---
            
            # Цвета: \color{red}{...} или \textcolor{red}{...}
            if cmd in ('color', 'textcolor'):
                color_name, k = get_arg(s, k)
                if cmd == 'textcolor':
                    content, k = get_arg(s, k)
                    result.append(f"#text({color_name})[${convert(content)}$]")
                else:
                    # \color{red} формула (красит всё до конца группы)
                    rest = s[k:]
                    result.append(f"#text({color_name})[${convert(rest)}$]")
                    return "".join(result)
                i = k
                continue

            # Рамки: \boxed{...}
            if cmd == 'boxed':
                content, k = get_arg(s, k)
                result.append(f"rect(inset: 4pt)[${convert(content)}$]")
                i = k
                continue

            # Зачеркивание: \cancel{...}
            if cmd == 'cancel':
                content, k = get_arg(s, k)
                result.append(f"cancel({convert(content)})")
                i = k
                continue

            # Стрелки: \xrightarrow[под]{над}
            if cmd == 'xrightarrow':
                bottom = ""
                if k < n and s[k] == '[':
                    end_b = find_close(s, k, '[', ']')
                    bottom = s[k+1:end_b]
                    k = end_b + 1
                top, k = get_arg(s, k)
                if bottom:
                    result.append(f"arrow.long.right.pitched(inner: [{convert(top)}], below: [{convert(bottom)}])")
                else:
                    result.append(f"arrow.long.right^( {convert(top)} )")
                i = k
                continue

            # Дроби
            if cmd in ('frac', 'dfrac', 'tfrac'):
                num, k = get_arg(s, k); den, k = get_arg(s, k)
                res = f"({convert(num)})/({convert(den)})"
                result.append(f"display({res})" if cmd == 'dfrac' else res)
                i = k
                continue

            # Корни
            if cmd == 'sqrt':
                content, k = get_arg(s, k)
                result.append(f"sqrt({convert(content)})")
                i = k
                continue

            # Акценты
            ACCENTS = {'hat': 'hat', 'vec': 'arrow', 'bar': 'overline', 'dot': 'dot', 'tilde': 'tilde'}
            if cmd in ACCENTS:
                content, k = get_arg(s, k)
                result.append(f"{ACCENTS[cmd]}({convert(content)})")
                i = k
                continue
            
            # Подписи: \underbrace{...}_{...}
            if cmd == 'underbrace':
                content, k = get_arg(s, k)
                # Проверяем, есть ли дальше _
                sub_content = ""
                temp_k = k
                while temp_k < n and s[temp_k].isspace(): temp_k += 1
                if temp_k < n and s[temp_k] == '_':
                    sub_content, k = get_arg(s, temp_k + 1)
                
                if sub_content:
                    result.append(f"underbrace({convert(content)}, {convert(sub_content)})")
                else:
                    result.append(f"underbrace({convert(content)})")
                i = k
                continue

            # Матрицы
            if cmd == 'begin':
                env, k = get_arg(s, k)
                end_tag = f"\\end{{{env}}}"
                end_idx = s.find(end_tag, k)
                inner = s[k:end_idx]
                # Обработка рядов
                rows = [r.split('&') for r in inner.split('\\\\')]
                typst_rows = "; ".join([", ".join([convert(cell) for cell in row]) for row in rows])
                
                delim = "()" if env == "pmatrix" else "[]" if env == "bmatrix" else "||" if env == "matrix" else "()"
                result.append(f"mat(delim: {delim!r}, {typst_rows})")
                i = end_idx + len(end_tag)
                continue

            # Простые команды
            if cmd == 'mathbb':
                arg, k = get_arg(s, k)
                result.append(MATHBB.get(arg, arg))
                i = k
                continue

            if cmd in STRIP_COMMANDS:
                i = k
                continue

            result.append(SIMPLE.get(cmd, cmd))
            i = k
            continue

        # Индексы
        if c in ('_', '^'):
            arg, k = get_arg(s, i + 1)
            if arg:
                result.append(f"{c}({convert(arg)})")
                i = k
            else:
                # Если просто _n
                result.append(c)
                i += 1
            continue

        # Группы { }
        if c == '{':
            end = find_close(s, i)
            result.append(f"({convert(s[i+1:end])})")
            i = end + 1
            continue

        result.append(c)
        i += 1

    return "".join(result)

def convert_math_in_text(text):
    # Obsidian Typst Mate обычно использует $$ ... $$ для блоков
    def repl_block(m):
        return "$ " + convert(m.group(1)).strip() + " $"
    
    # Сначала блоки (многострочные)
    text = re.sub(r'\$\$(.*?)\$\$', repl_block, text, flags=re.DOTALL)
    
    # Потом инлайны $ ... $
    # (сложнее, чтобы не побить уже замененное, но логика та же)
    def repl_inline(m):
        return "$" + convert(m.group(1)).strip() + "$"
    
    # Регулярка для инлайна: $ не окруженный другими $
    text = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', repl_inline, text)
    
    return text

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Path to .md file: ").strip()
    
    file_path = file_path.replace('"', '').replace("'", "")
    if not os.path.isfile(file_path):
        print("File not found"); return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = convert_math_in_text(content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Done: {os.path.basename(file_path)}")

if __name__ == "__main__":
    main()
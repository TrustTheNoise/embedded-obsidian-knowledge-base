#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert LaTeX math to Typst math syntax. Handles braces, text, and arrows."""

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
        return None, pos
    end = find_close(s, pos)
    return s[pos+1:end], end + 1

# ---------------------------------------------------------------------------
# Core converter
# ---------------------------------------------------------------------------

STRIP_COMMANDS = [
    'tiny', 'scriptsize', 'footnotesize', 'small', 'normalsize', 
    'large', 'Large', 'LARGE', 'huge', 'Huge',
    'displaystyle', 'textstyle', 'scriptstyle', 'scriptscriptstyle'
]

COLOR_MAP = {
    'pink': 'fuchsia', 
    'orange': 'orange',
    'red': 'red',
    'green': 'green',
    'blue': 'blue'
}

SIMPLE = {
    'infty': 'infinity', 'alpha': 'alpha', 'beta': 'beta', 'gamma': 'gamma', 'Gamma': 'Gamma',
    'delta': 'delta', 'Delta': 'Delta', 'epsilon': 'epsilon', 'varepsilon': 'epsilon.alt',
    'zeta': 'zeta', 'eta': 'eta', 'theta': 'theta', 'Theta': 'Theta', 'vartheta': 'theta.alt',
    'iota': 'iota', 'kappa': 'kappa', 'lambda': 'lambda', 'Lambda': 'Lambda',
    'mu': 'mu', 'nu': 'nu', 'xi': 'xi', 'Xi': 'Xi', 'pi': 'pi', 'Pi': 'Pi',
    'rho': 'rho', 'varrho': 'rho.alt', 'sigma': 'sigma', 'Sigma': 'Sigma',
    'tau': 'tau', 'upsilon': 'upsilon', 'Upsilon': 'Upsilon', 'phi': 'phi',
    'varphi': 'phi.alt', 'Phi': 'Phi', 'chi': 'chi', 'psi': 'psi', 'Psi': 'Psi',
    'omega': 'omega', 'Omega': 'Omega', 
    'sum': 'sum', 'prod': 'product', 'int': 'integral', 'partial': 'diff', 'nabla': 'nabla',
    'cdot': 'dot.op', 'times': 'times', 'neq': 'eq.not', 'leq': 'lt.eq', 'geq': 'gt.eq',
    'to': '->', 'rightarrow': '->', 'Rightarrow': '=>', 'quad': '  ', 'qquad': '    ',
}

MATH_FUNCS = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'ln', 'log', 'exp', 'arcsin', 'arccos', 'arctan']

for cmd in STRIP_COMMANDS:
    SIMPLE[cmd] = ""

ACCENT_FUNCS = {
    'hat': 'hat', 'vec': 'arrow', 'bar': 'overline', 'dot': 'dot', 'ddot': 'dot.double',
    'tilde': 'tilde', 'underline': 'underline',
}

def convert(s):
    """Recursively convert LaTeX math to Typst with spacing and color support."""
    result = []
    
    def add_token(t):
        if not t: return
        if result and result[-1].strip():
            prev = result[-1].strip()[-1]
            curr = t.strip()[0] if t.strip() else ""
            if curr and (prev.isalnum() or prev == ')') and (curr.isalnum() or curr == '('):
                result.append(" ")
        result.append(t)

    i = 0
    n = len(s)

    while i < n:
        c = s[i]

        if c.isspace():
            add_token(c)
            i += 1
            continue

        if c == '\\':
            j = i + 1
            if j < n and s[j] == '\\':
                add_token(" \\\n")
                i = j + 1
                continue
            
            if j < n and s[j] in '{}_^%$#&':
                add_token(s[j])
                i = j + 1
                continue

            k = j
            while k < n and s[k].isalpha():
                k += 1
            cmd = s[j:k]
            kk = k

            if cmd == 'text':
                content, kk = get_arg(s, kk)
                add_token(f'"{content or ""}"')
                i = kk
                continue

            elif cmd == 'mathbb':
                content, kk = get_arg(s, kk)
                if not content:
                    match = re.match(r'\s*([a-zA-Z])', s[kk:])
                    if match:
                        content = match.group(1)
                        kk += match.end()
                if content:
                    add_token(f"{content}{content}")
                i = kk
                continue

            elif cmd == 'underbrace':
                up, kk = get_arg(s, kk)
                down = ""
                temp_k = kk
                while temp_k < n and s[temp_k].isspace(): temp_k += 1
                if temp_k < n and s[temp_k] == '_':
                    temp_k += 1
                    down, kk = get_arg(s, temp_k)
                add_token(f"underbrace({convert(up or '')}, {convert(down or '')})")
                i = kk
                continue

            elif cmd == 'overbrace':
                down, kk = get_arg(s, kk)
                up = ""
                temp_k = kk
                while temp_k < n and s[temp_k].isspace(): temp_k += 1
                if temp_k < n and s[temp_k] == '^':
                    temp_k += 1
                    up, kk = get_arg(s, temp_k)
                add_token(f"overbrace({convert(down or '')}, {convert(up or '')})")
                i = kk
                continue

            elif cmd == 'xrightarrow':
                formula, kk = get_arg(s, kk)
                add_token(f" = |{convert(formula or '')}| = ")
                i = kk
                continue

            if cmd in MATH_FUNCS:
                add_token(cmd)
                i = k
                continue

            if cmd in ('color', 'textcolor'):
                name, kk = get_arg(s, kk)
                if not name:
                    m = re.match(r'\s*([a-zA-Z]+)', s[kk:])
                    if m: name = m.group(1); kk += m.end()
                
                typst_color = COLOR_MAP.get(name.lower(), name)
                
                if cmd == 'textcolor':
                    content, kk = get_arg(s, kk)
                    inner = convert(content or '').strip()
                    add_token(f"#text(fill: {typst_color})[${inner}$]")
                    i = kk
                else:
                    rest = s[kk:]
                    trailing_ws = ""
                    ws_match = re.search(r'\s+$', rest)
                    if ws_match:
                        trailing_ws = ws_match.group(0)
                    
                    inner = convert(rest).strip()
                    add_token(f"#text(fill: {typst_color})[${inner}$]{trailing_ws}")
                    # Очищаем результат всей функции перед возвратом
                    return "".join(result)
                continue

            if cmd in ('frac', 'dfrac', 'tfrac'):
                num, kk = get_arg(s, kk); den, kk = get_arg(s, kk)
                add_token(f"frac({convert(num or '')}, {convert(den or '')})")
                i = kk
            elif cmd == 'sqrt':
                content, kk = get_arg(s, kk)
                add_token(f"sqrt({convert(content or '')})")
                i = kk
            elif cmd in ACCENT_FUNCS:
                content, kk = get_arg(s, kk)
                add_token(f"{ACCENT_FUNCS[cmd]}({convert(content or '')})")
                i = kk
            elif cmd in SIMPLE:
                add_token(SIMPLE[cmd])
                i = k
            else:
                add_token(cmd)
                i = k
            continue

        if c.isdigit():
            num_match = re.match(r'\d+', s[i:])
            if num_match:
                add_token(num_match.group())
                i += len(num_match.group())
                continue

        if c in ('_', '^'):
            j = i + 1
            while j < n and s[j].isspace(): j += 1
            if j < n and s[j] == '{':
                end = find_close(s, j)
                inner = s[j+1:end]
                add_token(f"{c}({convert(inner)})")
                i = end + 1
            else:
                if j < n and s[j] == '\\':
                    k2 = j + 1
                    while k2 < n and s[k2].isalpha(): k2 += 1
                    cmd_part = s[j+1:k2]
                    conv_part = SIMPLE.get(cmd_part, cmd_part)
                    add_token(f"{c}({conv_part})")
                    i = k2
                elif j < n:
                    add_token(f"{c}({s[j]})")
                    i = j + 1
                else:
                    add_token(c); i = j
            continue

        if c.isalpha():
            found_func = False
            for func in MATH_FUNCS:
                if s[i:].startswith(func):
                    end_idx = i + len(func)
                    if end_idx == n or not s[end_idx].isalpha():
                        add_token(func)
                        i = end_idx
                        found_func = True
                        break
            if found_func: continue
            add_token(c)
            i += 1
            continue

        if c == '{':
            end = find_close(s, i)
            inner_content = s[i+1:end]
            add_token(f"{convert(inner_content)}")
            i = end + 1
        else:
            add_token(c)
            i += 1

    return "".join(result).strip() # Финальная очистка пробелов по краям

def convert_math_in_text(text):
    result = []
    i = 0
    n = len(text)
    while i < n:
        if text[i:i+3] == '```':
            end = text.find('```', i + 3)
            if end >= 0:
                result.append(text[i:end+3]); i = end + 3
            else:
                result.append(text[i:]); i = n
            continue
        
        if text[i:i+2] == '$$':
            end = text.find('$$', i + 2)
            if end >= 0:
                inner = text[i+2:end]
                # Очищаем внутренности от пробелов, которые могли остаться после удаления \Large
                result.append('$$' + convert(inner).strip() + '$$')
                i = end + 2
            else:
                result.append(text[i]); i += 1
            continue

        if text[i] == '$':
            j = i + 1
            found_close = False
            while j < n:
                if text[j] == '$':
                    inner = text[i+1:j]
                    result.append('$' + convert(inner).strip() + '$')
                    i = j + 1
                    found_close = True
                    break
                elif text[j] == '\\': j += 2
                else: j += 1
            if not found_close:
                result.append(text[i]); i += 1
            continue

        result.append(text[i]); i += 1
    return "".join(result)

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Введите путь к .md файлу: ").strip()
    
    file_path = file_path.replace('"', '').replace("'", "")
    if not os.path.isfile(file_path):
        print(f"Файл не найден: {file_path}"); return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = convert_math_in_text(content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Файл '{os.path.basename(file_path)}' успешно обновлен.")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
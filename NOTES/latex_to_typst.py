#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert LaTeX math to Typst math syntax. Handles environments, colors, and tags."""

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
    'blue': 'blue',
    'cyan': 'aqua',
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
    'cdot': 'dot.op', 'times': 'times', 'neq': '!=', 'le': '<=', 'leq': '<=', 'ge': '>=', 'geq': '>=', 'ne': '!=',
    'approx': 'approx', 'equiv': 'equiv', 'land': 'and', 'lor': 'or', 'lnot': 'not', 'neg': 'not',
    'wedge': 'and', 'vee': 'or', 'forall': 'forall', 'exists': 'exists', 'nexists': 'exists.not',
    'implies': '=>', 'iff': '<=>', 'in': 'in', 'notin': 'in.not', 'subset': 'subset',
    'supset': 'supset', 'subseteq': 'subset.eq', 'supseteq': 'supset.eq', 'cap': 'sect',
    'cup': 'union', 'emptyset': 'empty', 'to': '->', 'rightarrow': '->', 'leftarrow': '<-',
    'leftrightarrow': '<->', 'Rightarrow': '=>', 'Leftarrow': '<=', 'Leftrightarrow': '<=>',
    'quad': '  ', 'qquad': '    ', 'pm':'+-', 'mp':'-+', 'ldots':'...', 'cdots':'...', 'vdots':'...', 'infty':'infinity',
}

MATH_FUNCS = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'ln', 'log', 'exp', 'arcsin', 'arccos', 'arctan']
ACCENT_FUNCS = {'hat': 'hat', 'vec': 'arrow', 'bar': 'overline', 'dot': 'dot', 'ddot': 'dot.double', 'tilde': 'tilde', 'underline': 'underline'}

for cmd in STRIP_COMMANDS: SIMPLE[cmd] = ""

def convert(s, is_block=False):
    """Recursively convert LaTeX math to Typst syntax."""
    result = []
    
    def add_token(t):
        if not t: return
        if result and result[-1].strip():
            prev = result[-1].strip()[-1]
            curr = t.strip()[0] if t.strip() else ""
            if curr and (prev.isalnum() or prev == ')') and (curr.isalnum() or curr == '('):
                result.append(" ")
        result.append(t)

    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            add_token(c); i += 1; continue

        if c == '\\':
            j = i + 1
            if j < n and s[j] == '\\':
                add_token(" \\\n"); i = j + 1; continue
            if j < n and s[j] in '{}_^$#&':
                add_token(s[j]); i = j + 1; continue

            k = j
            while k < n and s[k].isalpha(): k += 1
            cmd = s[j:k]
            kk = k

            # --- УДАЛЕНИЕ TAG ---
            if cmd == 'tag':
                _, kk = get_arg(s, kk)
                i = kk
                continue

            # --- ЦВЕТА ---
            if cmd in ('color', 'textcolor'):
                color_name, kk = get_arg(s, kk)
                if not color_name:
                    m = re.match(r'\s*([a-zA-Z]+)', s[kk:])
                    if m: color_name = m.group(1); kk += m.end()
                
                if not is_block:
                    if cmd == 'textcolor':
                        content, kk = get_arg(s, kk)
                        add_token(convert(content or '', is_block=False))
                    i = kk; continue
                else:
                    typst_color = COLOR_MAP.get(color_name.lower(), color_name)
                    if cmd == 'textcolor':
                        content, kk = get_arg(s, kk)
                        inner = convert(content or '', is_block=True).strip()
                        add_token(f"#text(fill: {typst_color})[${inner}$]")
                        i = kk
                    else:
                        rest = s[kk:]
                        inner = convert(rest, is_block=True).strip()
                        add_token(f"#text(fill: {typst_color})[${inner}$]")
                        return "".join(result)
                    continue

            # --- ОКРУЖЕНИЯ ---
            if cmd == 'begin':
                env, kk = get_arg(s, kk)
                end_tag = f"\\end{{{env}}}"
                end_pos = s.find(end_tag, kk)
                if end_pos != -1:
                    inner = s[kk:end_pos]
                    if env == 'cases':
                        lines = [line.strip() for line in inner.split('\\\\')]
                        conv_lines = [convert(l, is_block).replace(',', r'\,') for l in lines if l]
                        add_token(f"cases({', '.join(conv_lines)})")
                    else:
                        add_token(convert(inner, is_block))
                    i = end_pos + len(end_tag); continue

            if cmd == 'text':
                content, kk = get_arg(s, kk)
                add_token(f'"{content or ""}"'); i = kk; continue
            
            if cmd == 'mathbb':
                content, kk = get_arg(s, kk)
                if not content:
                    m = re.match(r'\s*([a-zA-Z])', s[kk:])
                    if m: content = m.group(1); kk += m.end()
                if content: add_token(f"{content}{content}")
                i = kk; continue

            if cmd in ('frac', 'dfrac', 'tfrac'):
                num, kk = get_arg(s, kk); den, kk = get_arg(s, kk)
                add_token(f"frac({convert(num or '', is_block)}, {convert(den or '', is_block)})"); i = kk; continue
            
            if cmd == 'sqrt':
                content, kk = get_arg(s, kk)
                add_token(f"sqrt({convert(content or '', is_block)})"); i = kk; continue

            if cmd in ACCENT_FUNCS:
                content, kk = get_arg(s, kk)
                add_token(f"{ACCENT_FUNCS[cmd]}({convert(content or '', is_block)})"); i = kk; continue

            if cmd in SIMPLE:
                add_token(SIMPLE[cmd]); i = k; continue
            
            add_token(cmd); i = k; continue

        if c in ('_', '^'):
            j = i + 1
            while j < n and s[j].isspace(): j += 1
            if j < n and s[j] == '{':
                end = find_close(s, j)
                add_token(f"{c}({convert(s[j+1:end], is_block)})"); i = end + 1
            else:
                if j < n and s[j] == '\\':
                    k2 = j + 1
                    while k2 < n and s[k2].isalpha(): k2 += 1
                    cmd_part = s[j+1:k2]
                    add_token(f"{c}({SIMPLE.get(cmd_part, cmd_part)})"); i = k2
                elif j < n: add_token(f"{c}({s[j]})"); i = j + 1
                else: add_token(c); i = j
            continue

        if c.isalpha():
            found_f = False
            for f in MATH_FUNCS:
                if s[i:].startswith(f):
                    e = i + len(f)
                    if e == n or not s[e].isalpha():
                        add_token(f); i = e; found_f = True; break
            if found_f: continue
            add_token(c); i += 1; continue

        if c == '{':
            end = find_close(s, i)
            add_token(convert(s[i+1:end], is_block)); i = end + 1
        else:
            add_token(c); i += 1

    return "".join(result).strip()

def convert_math_in_text(text):
    result, i, n = [], 0, len(text)
    while i < n:
        if text[i:i+3] == '```':
            end = text.find('```', i + 3)
            if end >= 0: result.append(text[i:end+3]); i = end + 3
            else: result.append(text[i:]); i = n
            continue
        if text[i:i+2] == '$$':
            end = text.find('$$', i + 2)
            if end >= 0:
                result.append('$$' + convert(text[i+2:end], is_block=True) + '$$'); i = end + 2
            else: result.append(text[i]); i += 1
            continue
        if text[i] == '$':
            j = i + 1
            found = False
            while j < n:
                if text[j] == '$':
                    result.append('$' + convert(text[i+1:j], is_block=False) + '$')
                    i = j + 1; found = True; break
                elif text[j] == '\\': j += 2
                else: j += 1
            if not found: result.append(text[i]); i += 1
            continue
        result.append(text[i]); i += 1
    return "".join(result)

def main():
    if len(sys.argv) > 1: file_path = sys.argv[1]
    else: file_path = input("Файл: ").strip()
    file_path = file_path.replace('"', '').replace("'", "")
    if not os.path.isfile(file_path): return
    try:
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        new_content = convert_math_in_text(content)
        with open(file_path, 'w', encoding='utf-8') as f: f.write(new_content)
        print(f"Обновлено: {os.path.basename(file_path)}")
    except Exception as e: print(f"Ошибка: {e}")

if __name__ == "__main__": main()
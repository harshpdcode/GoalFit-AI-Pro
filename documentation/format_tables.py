import re
import os

def reformat_tables(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    out = []
    table_lines = []
    
    def process_table(t_lines):
        rows = []
        for line in t_lines:
            line = line.strip()
            if not line: continue
            if line.startswith('|') and line.endswith('|'):
                # handle markdown table rows
                cols = [c.strip() for c in line[1:-1].split('|')]
                # skip markdown separator row
                if len(cols) > 0 and all(c.replace('-', '').strip() == '' for c in cols):
                    continue
                rows.append(cols)
        
        if not rows:
            return t_lines
            
        col_count = max(len(r) for r in rows)
        widths = [0] * col_count
        for r in rows:
            for i, c in enumerate(r):
                # Calculate display width, stripping backticks and bold markdown for visual length
                clean_c = c
                if len(clean_c) > widths[i]:
                    widths[i] = len(clean_c)
                    
        res = []
        sep = '+' + '+'.join('-' * (w + 2) for w in widths) + '+\n'
        for i, r in enumerate(rows):
            if i == 0:
                res.append(sep)
            
            padded = []
            for j in range(col_count):
                val = r[j] if j < len(r) else ''
                padded.append(f" {val.ljust(widths[j])} ")
            
            res.append('|' + '|'.join(padded) + '|\n')
            
            if i == 0:
                res.append(sep)
        
        res.append(sep)
        return res

    for line in lines:
        if line.strip().startswith('|') and line.strip().endswith('|'):
            table_lines.append(line)
        else:
            if table_lines:
                out.extend(process_table(table_lines))
                table_lines = []
            out.append(line)
            
    if table_lines:
        out.extend(process_table(table_lines))
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(out)

reformat_tables("c:/Another drive(A)/SOU sem-2 Project/GoalFit-AI/documentation/GoalFit_AI_Documentation.txt")
print("Tables formatted successfully!")

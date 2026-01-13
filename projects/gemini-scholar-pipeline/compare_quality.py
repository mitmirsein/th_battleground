import os
import re
from pathlib import Path
from datetime import datetime

# Configuration
FILES = [
    "reports/schechina_raw.md",
    "reports/schechina_enhanced.md",
    "reports/schechina_annotated.md",
    "reports/schechina_final.md"
]
LABELS = ["Raw Output", "Enhanced (Phase 1.5)", "Annotated (Phase 4)", "Final Article (Phase 5)"]

OUTPUT_FILE = "quality_comparison.html"

def analyze_file(filepath):
    """Analyzes a markdown file and returns metrics."""
    path = Path(filepath)
    if not path.exists():
        return None
    
    content = path.read_text(encoding='utf-8')
    
    # Metrics
    size_kb = path.stat().st_size / 1024
    char_count = len(content)
    # Simple word count (whitespace split)
    word_count = len(re.findall(r'\S+', content))
    
    # Structure
    h1_count = len(re.findall(r'^#\s+', content, re.MULTILINE))
    h2_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
    h3_count = len(re.findall(r'^###\s+', content, re.MULTILINE))
    
    # Citations/Footnotes
    footnote_markers = len(re.findall(r'\[\^.*?\]', content))
    # Count lines starting with [^...]:
    footnote_defs = len(re.findall(r'^\[\^.*?\]:', content, re.MULTILINE))
    
    # Academic Indicators (simple heuristic)
    # Greek/Hebrew characters count
    greek_hebrew = len(re.findall(r'[\u0370-\u03FF\u0590-\u05FF]', content))
    
    return {
        "size_kb": f"{size_kb:.1f}",
        "char_count": char_count,
        "word_count": word_count,
        "sections": f"H1:{h1_count} / H2:{h2_count} / H3:{h3_count}",
        "footnotes": max(footnote_markers // 2, footnote_defs), # markers appear twice (in text and def), or just use defs
        "greek_hebrew": greek_hebrew
    }

def generate_html(results):
    """Generates the comparison HTML report."""
    
    # CSS (Theological Brutalism Lite)
    css = """
    <style>
        :root {
            --bg: #f8f9fa;
            --text: #1a1a1a;
            --accent: #0f172a;
            --border: #e2e8f0;
        }
        body {
            font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 4rem 2rem;
            line-height: 1.5;
        }
        .container {
            max_width: 1200px;
            margin: 0 auto;
        }
        h1 {
            font-size: 2.5rem;
            font-weight: 900;
            letter-spacing: -0.05em;
            margin-bottom: 2rem;
            text-transform: uppercase;
            border-bottom: 4px solid var(--text);
            padding-bottom: 1rem;
        }
        .meta {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            color: #64748b;
            margin-bottom: 3rem;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            table-layout: fixed;
        }
        th, td {
            text-align: left;
            padding: 1.5rem;
            border-bottom: 1px solid var(--border);
            vertical-align: middle;
        }
        th {
            background: var(--text);
            color: white;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.05em;
            width: 200px;
        }
        th:first-child {
            width: 150px;
            background: white;
            color: var(--text);
            border-bottom: 4px solid var(--text);
        }
        .metric-label {
            font-weight: 600;
            font-size: 0.9rem;
            color: #475569;
        }
        .value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.1rem;
            font-weight: 600;
        }
        .diff-positive { color: #059669; font-size: 0.8em; margin-left: 0.5em; }
        .diff-negative { color: #dc2626; font-size: 0.8em; margin-left: 0.5em; }
        
        .chart-bar {
            height: 4px;
            background: #e2e8f0;
            margin-top: 0.5rem;
            position: relative;
            width: 100%;
            border-radius: 2px;
            overflow: hidden;
        }
        .chart-fill {
            height: 100%;
            background: var(--text);
        }
        .missing-file {
            color: #dc2626;
            font-style: italic;
        }
    </style>
    """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Pipeline Quality Comparison</title>
        {css}
    </head>
    <body>
        <div class="container">
            <div class="meta">
                GENERATED: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
                PROJECT: GEMINI SCHOLAR PIPELINE
            </div>
            <h1>Quality Metrics Comparison</h1>
            
            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
    """
    
    for label in LABELS:
        html += f"<th>{label}</th>"
    
    html += """
                    </tr>
                </thead>
                <tbody>
    """
    
    metrics = [
        ("size_kb", "Size (KB)"),
        ("char_count", "Character Count"),
        ("word_count", "Word Count"),
        ("footnotes", "Footnotes / Refs"),
        ("greek_hebrew", "Greek/Hebrew Chars"),
        ("sections", "Section Structure")
    ]
    
    # Find max values for charts
    max_values = {}
    for key, _ in metrics:
        if key == "sections": continue
        vals = []
        for r in results:
            if r and isinstance(r[key], (int, float)):
                vals.append(float(r[key]))
            elif r and isinstance(r[key], str) and r[key].replace('.','',1).isdigit():
                 vals.append(float(r[key]))
        max_values[key] = max(vals) if vals else 1

    for key, label in metrics:
        html += f"<tr><td class='metric-label'>{label}</td>"
        
        for i, res in enumerate(results):
            if res is None:
                html += "<td class='missing-file'>File Not Found</td>"
                continue
            
            val = res[key]
            display_val = val
            chart = ""
            
            # Numeric chart generation
            if key != "sections":
                num_val = float(val)
                pct = (num_val / max_values[key]) * 100
                chart = f"<div class='chart-bar'><div class='chart-fill' style='width: {pct}%'></div></div>"
                display_val = f"<span class='value'>{val}</span>"

            html += f"<td>{display_val}{chart}</td>"
            
        html += "</tr>"
        
    html += """
                </tbody>
            </table>
            
            <div style="margin-top: 3rem; padding: 2rem; background: white; border: 1px solid #e2e8f0;">
                <h3 style="font-weight: 800; text-transform: uppercase;">Analysis Summary</h3>
                <ul style="line-height: 1.8; color: #475569;">
                    <li><strong>Raw -> Enhanced:</strong> Checks for expansion in content and academic depth (footnotes/greek terms).</li>
                    <li><strong>Enhanced -> Annotated:</strong> Expect significant increase in annotations and structure clarity.</li>
                    <li><strong>Annotated -> Final:</strong> Expect refinement, removal of meta-commentary, and polished final structure.</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def main():
    results = []
    print("Analyzing files...")
    for f in FILES:
        print(f"Reading {f}...")
        res = analyze_file(f)
        results.append(res)
    
    print("Generating HTML...")
    html = generate_html(results)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Report generated: {os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    main()

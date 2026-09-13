import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from spider import start_analyze

latest_report = None


def run_scanning():
    global latest_report
    url = url_entry.get().strip()

    if not url:
        messagebox.showwarning("Warning", "Please enter a website URL!")
        return

    scan_button.config(state="disabled", text="Analyzing...")
    window.update()

    result = start_analyze(url)
    scan_button.config(state="normal", text="Analyze Website")

    if result.get("status") == "Error":
        messagebox.showerror(
            "Error", result.get("message", "An error occurred during scanning.")
        )
    else:
        latest_report = result
        display_results(result)
        save_button.config(state="normal")
        messagebox.showinfo("Success", "SEO Audit completed successfully!")


def save_json():
    global latest_report
    if not latest_report:
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")],
        title="Save SEO Report As...",
    )

    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(latest_report, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("Saved", f"Report saved to:\n{file_path}")


def display_results(result):
    visual_text.delete(1.0, tk.END)
    tags = result["tehnicki_tagovi"]
    content = result["analiza_teksta"]
    score = result["lighthouse_score"]

    output = f"=== LIGHTHOUSE-STYLE SEO AUDIT REPORT ===\n"
    output += f"Target URL: {result['url_skeniranja']}\n\n"

    output += f"📊 OVERALL SEO SCORE: {score} / 100\n"
    if score >= 80:
        output += "Status: PASSED (Good Crawlability)\n"
    elif score >= 50:
        output += "Status: WARNING (Technical Barriers Detected)\n"
    else:
        output += "Status: CRITICAL (Severe Indexing Barriers)\n"
    output += "-" * 50 + "\n\n"

    if result["penalties"]:
        output += "⚠️ DETECTED ISSUES & PENALTIES:\n"
        for pen in result["penalties"]:
            output += f"   ❌ {pen}\n"
        output += "\n"

    output += f"📌 TITLE & META TAGS:\n"
    output += f"   - Title: {tags['title_tag']['sadrzaj'] or 'NOT FOUND'} ({tags['title_tag']['duzina']} chars)\n"
    output += f"   - Meta Description: {tags['meta_description']['sadrzaj'] or 'NOT FOUND'}\n"
    output += f"   - Meta Robots: {tags['meta_robots']}\n"
    output += f"   - Canonical Tag: {'YES' if tags['has_canonical'] else 'NO'}\n\n"

    output += f"🏷️ HEADINGS STRUCTURE:\n"
    output += f"   - H1 Headings Count: {tags['h1_headings']['ukupno_h1']}\n"
    if tags["h1_headings"]["sadrzaj"]:
        for idx, h1 in enumerate(tags["h1_headings"]["sadrzaj"], start=1):
            output += f"     {idx}. {h1}\n"
    output += "\n"

    output += f"🖼️ IMAGES AUDIT:\n"
    output += f"   - Total Images: {tags['slike_statistika']['ukupno_slika']}\n"
    output += f"   - Missing ALT Tags: {tags['slike_statistika']['slike_bez_alt_opisa']}\n"
    output += f"   - Alt Attribute Score: {tags['slike_statistika']['optimizovanost_procenat']}\n\n"

    output += f"🛑 CRAWLING BARRIERS:\n"
    output += f"   - <frame> Detected: {'YES' if tags['tehnicke_barijere']['koristi_frame'] else 'NO'}\n"
    output += f"   - <iframe> Detected: {'YES' if tags['tehnicke_barijere']['koristi_iframe'] else 'NO'}\n"

    js_rendering = tags["tehnicke_barijere"]["javascript_client_side_rendering"]
    framework = tags["tehnicke_barijere"]["detected_framework"]
    output += f"   - Client-Side JS Rendering (CSR): {'YES (' + framework + ')' if js_rendering else 'NO'}\n\n"

    output += f"📝 CONTENT VOLUME & KEYWORDS:\n"
    output += f"   - Word Count (Body Text): {content['ukupan_broj_reci']}\n"
    output += f"   - Meets 100-Word Threshold: {'YES' if content['ispunjava_minimum_100_reci'] else 'NO'}\n"
    output += f"   - Top Keywords Found:\n"
    if content["detektovane_kljucne_reci"]:
        for item in content["detektovane_kljucne_reci"]:
            output += f"     * {item['rec']}: {item['frekvencija']} times\n"
    else:
        output += "     * No readable text found.\n"

    visual_text.insert(tk.END, output)

    json_text.delete(1.0, tk.END)
    json_formatted = json.dumps(result, indent=4, ensure_ascii=False)
    json_text.insert(tk.END, json_formatted)


window = tk.Tk()
window.title("Mini-Spider | SEO Lighthouse Auditor")
window.geometry("700x720")
window.configure(bg="#f0f2f5")

header_title = tk.Label(
    window,
    text="Web Mining Mini-Spider",
    font=("Helvetica", 16, "bold"),
    bg="#f0f2f5",
    fg="#1a73e8",
)
header_title.pack(pady=(10, 2))

header_subtitle = tk.Label(
    window,
    text="Lighthouse-Style Technical Barrier Detection Engine",
    font=("Helvetica", 10),
    bg="#f0f2f5",
    fg="#5f6368",
)
header_subtitle.pack(pady=(0, 10))

input_frame = tk.Frame(window, bg="#f0f2f5")
input_frame.pack(pady=10)

url_label = tk.Label(
    input_frame, text="Website URL:", font=("Helvetica", 10, "bold"), bg="#f0f2f5"
)
url_label.grid(row=0, column=0, padx=5)

url_entry = tk.Entry(input_frame, width=35, font=("Helvetica", 11))
url_entry.insert(0, "wikipedia.org")
url_entry.grid(row=0, column=1, padx=5)

scan_button = tk.Button(
    input_frame,
    text="Analyze Website",
    command=run_scanning,
    bg="#1a73e8",
    fg="white",
    font=("Helvetica", 10, "bold"),
    padx=10,
)
scan_button.grid(row=0, column=2, padx=5)

notebook = ttk.Notebook(window)
notebook.pack(fill="both", expand=True, padx=15, pady=10)

tab_visual = ttk.Frame(notebook)
notebook.add(tab_visual, text=" Audit Report ")

visual_text = tk.Text(
    tab_visual, wrap="word", font=("Consolas", 10), bg="#ffffff", bd=0
)
visual_text.pack(fill="both", expand=True, padx=5, pady=5)

tab_json = ttk.Frame(notebook)
notebook.add(tab_json, text=" Raw JSON ")

json_text = tk.Text(
    tab_json, wrap="word", font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", bd=0
)
json_text.pack(fill="both", expand=True, padx=5, pady=5)

save_button = tk.Button(
    window,
    text="💾 Export JSON Report",
    command=save_json,
    bg="#34a853",
    fg="white",
    font=("Helvetica", 11, "bold"),
    state="disabled",
    pady=6,
)
save_button.pack(fill="x", padx=15, pady=(0, 15))

window.mainloop()
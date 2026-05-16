"""
DSL Converter — JSON <-> DSL for single files
Simple, focused editor for converting between JSON and human-readable DSL format.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, os, re
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
#  DESIGN TOKENS
# ══════════════════════════════════════════════════════════════════════════════
C = {
    "bg":        "#0a0a0f",
    "surface":   "#13131a",
    "card":      "#1a1a24",
    "raised":    "#22222e",
    "border":    "#2e2e3e",
    "border2":   "#3a3a50",
    "accent":    "#7c6af7",
    "accent2":   "#a78bfa",
    "accent3":   "#c4b5fd",
    "green":     "#34d399",
    "green2":    "#059669",
    "red":       "#f87171",
    "red2":      "#dc2626",
    "yellow":    "#fbbf24",
    "yellow2":   "#d97706",
    "blue":      "#60a5fa",
    "pink":      "#f472b6",
    "text":      "#f1f0ff",
    "text2":     "#9998b8",
    "text3":     "#5a5a7a",
    "text4":     "#3a3a52",
    "white":     "#ffffff",
}

F = {
    "title":  ("Segoe UI", 16, "bold"),
    "h1":     ("Segoe UI", 14, "bold"),
    "h2":     ("Segoe UI", 12, "bold"),
    "body":   ("Segoe UI", 10),
    "small":  ("Segoe UI", 9),
    "tiny":   ("Segoe UI", 8),
    "mono":   ("Consolas", 10),
    "monos":  ("Consolas", 9),
}

# ══════════════════════════════════════════════════════════════════════════════
#  BASE WIDGETS
# ══════════════════════════════════════════════════════════════════════════════
class Btn(tk.Button):
    STYLES = {
        "primary": (C["accent"],  C["white"]),
        "green":   (C["green2"],  C["white"]),
        "red":     (C["red2"],    C["white"]),
        "ghost":   (C["raised"],  C["text2"]),
        "outline": (C["surface"], C["accent2"]),
        "purple":  ("#6d28d9",    C["white"]),
    }
    def __init__(self, parent, text="", cmd=None, style="primary", px=14, py=6, **kw):
        bg, fg = self.STYLES.get(style, self.STYLES["primary"])
        super().__init__(parent, text=text, command=cmd, bg=bg, fg=fg,
                         activebackground=bg, activeforeground=fg, relief="flat", bd=0,
                         padx=px, pady=py, font=F["body"], cursor="hand2", **kw)
        self._bg = bg
        self.bind("<Enter>", lambda e: self.config(bg=self._dim(bg, -20)))
        self.bind("<Leave>", lambda e: self.config(bg=bg))

    def _dim(self, h, d):
        c = h.lstrip("#")
        r,g,b = int(c[:2],16), int(c[2:4],16), int(c[4:],16)
        return "#{:02x}{:02x}{:02x}".format(
            max(0,min(255,r+d)), max(0,min(255,g+d)), max(0,min(255,b+d)))


class Entry(tk.Entry):
    def __init__(self, parent, **kw):
        d = dict(bg=C["raised"], fg=C["text"], insertbackground=C["text"],
                 relief="flat", bd=0, font=F["body"],
                 highlightthickness=1, highlightbackground=C["border"],
                 highlightcolor=C["accent"])
        d.update(kw)
        super().__init__(parent, **d)


class Textbox(tk.Text):
    def __init__(self, parent, **kw):
        d = dict(bg=C["raised"], fg=C["text"], insertbackground=C["text"],
                 relief="flat", bd=0, font=F["body"],
                 highlightthickness=1, highlightbackground=C["border"],
                 highlightcolor=C["accent"], selectbackground=C["accent"],
                 wrap="word", pady=6, padx=8)
        d.update(kw)
        super().__init__(parent, **d)


class Label(tk.Label):
    def __init__(self, parent, text="", fg=None, font=None, bg=None, **kw):
        super().__init__(parent, text=text, fg=fg or C["text"],
                         font=font or F["body"], bg=bg or parent.cget("bg"), **kw)


class Frame(tk.Frame):
    def __init__(self, parent, bg=None, **kw):
        super().__init__(parent, bg=bg or C["bg"], **kw)


class Card(tk.Frame):
    def __init__(self, parent, pad=10, **kw):
        kw.setdefault("bg", C["card"])
        super().__init__(parent, relief="flat", bd=0, **kw)
        self.config(highlightthickness=1, highlightbackground=C["border"],
                     highlightcolor=C["border"])


class SLabel(tk.Label):
    """Section / caption label."""
    def __init__(self, parent, text="", **kw):
        super().__init__(parent, text=text.upper(), bg=parent.cget("bg"),
                         fg=C["text3"], font=F["tiny"], anchor="w", **kw)


# ══════════════════════════════════════════════════════════════════════════════
#  TOAST NOTIFICATION
# ══════════════════════════════════════════════════════════════════════════════
class Toast:
    _queue: list = []

    @classmethod
    def show(cls, root, msg: str, kind="info", duration=2000):
        colors = {"info": C["accent"], "ok": C["green"], "err": C["red"], "warn": C["yellow"]}
        icons  = {"info": "ℹ", "ok": "✓", "err": "✕", "warn": "⚠"}
        bg = colors.get(kind, C["accent"])

        popup = tk.Toplevel(root)
        popup.overrideredirect(True)
        popup.configure(bg=bg)
        popup.attributes("-topmost", True)
        popup.attributes("-alpha", 0.0)

        inner = tk.Frame(popup, bg=bg)
        inner.pack(fill="both", padx=1, pady=1)
        tk.Label(inner, text=f"  {icons[kind]}  {msg}  ", bg=bg, fg=C["white"],
                 font=F["body"], pady=10).pack()

        def _place():
            popup.update_idletasks()
            w = popup.winfo_reqwidth()
            h = popup.winfo_reqheight()
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            popup.geometry(f"+{sw - w - 20}+{sh - h - 60}")

        def _fade_in(alpha=0.0):
            if alpha < 0.95:
                alpha = min(0.95, alpha + 0.08)
                popup.attributes("-alpha", alpha)
                popup.after(16, lambda: _fade_in(alpha))

        def _fade_out(alpha=0.95):
            if alpha > 0:
                alpha = max(0, alpha - 0.06)
                popup.attributes("-alpha", alpha)
                popup.after(16, lambda: _fade_out(alpha))
            else:
                popup.destroy()

        _place()
        _fade_in()
        popup.after(duration, _fade_out)


# ══════════════════════════════════════════════════════════════════════════════
#  DSL ENGINE — Universal converter for any JSON structure
# ══════════════════════════════════════════════════════════════════════════════
class DSLConverter:
    """
    Convert any JSON structure <-> readable DSL text.
    Supports nested objects, arrays, and special content blocks.
    """

    @staticmethod
    def json_to_dsl(data, indent=0) -> str:
        """Convert JSON (dict/list) to DSL text."""
        lines = []
        prefix = "  " * indent

        if isinstance(data, dict):
            for key, value in data.items():
                key_str = str(key)

                # Handle special content types
                if key_str in ("content", "lessons", "items", "rows"):
                    # These are content blocks - render specially
                    if isinstance(value, list) and value:
                        lines.append(f"{prefix}{key_str.upper().rstrip('S')}:")
                        for item in value:
                            item_lines = DSLConverter._render_content_item(item, indent + 1)
                            lines.extend(item_lines)
                    continue

                # Handle nested objects
                if isinstance(value, dict):
                    lines.append(f"{prefix}{key_str.upper()}:")
                    nested = DSLConverter.json_to_dsl(value, indent + 1)
                    if nested:
                        lines.append(nested)
                    continue

                # Handle arrays
                if isinstance(value, list):
                    if not value:
                        continue
                    # Check if it's a simple array of primitives
                    if all(isinstance(x, (str, int, float, bool)) for x in value):
                        lines.append(f"{prefix}{key_str.upper()}: {', '.join(str(x) for x in value)}")
                    else:
                        lines.append(f"{prefix}{key_str.upper()}:")
                        for item in value:
                            if isinstance(item, dict):
                                lines.append(DSLConverter.json_to_dsl(item, indent + 1))
                            else:
                                lines.append(f"{prefix}  - {item}")
                    continue

                # Handle primitives
                if value is None:
                    lines.append(f"{prefix}{key_str.upper()}:")
                elif isinstance(value, bool):
                    lines.append(f"{prefix}{key_str.upper()}: {'true' if value else 'false'}")
                elif isinstance(value, (int, float)):
                    lines.append(f"{prefix}{key_str.upper()}: {value}")
                else:
                    # String - escape colons and special chars
                    val_str = str(value).replace("\\", "\\\\")
                    if ":" in val_str or "\n" in val_str:
                        lines.append(f"{prefix}{key_str.upper()}:")
                        for line in val_str.split("\n"):
                            lines.append(f"{prefix}  {line}")
                    else:
                        lines.append(f"{prefix}{key_str.upper()}: {val_str}")

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    lines.append(DSLConverter.json_to_dsl(item, indent))
                else:
                    lines.append(f"{prefix}- {item}")

        return "\n".join(lines)

    @staticmethod
    def _render_content_item(item, indent=0) -> list:
        """Render a single content item (heading, text, list, table, etc)."""
        lines = []
        prefix = "  " * indent
        t = item.get("type", "text")

        if t == "heading":
            lvl = item.get("level", 1)
            tag = "HEADING" if lvl == 1 else f"H{lvl}"
            lines.append(f"{prefix}{tag}: {item.get('text', '')}")
        elif t == "text":
            lines.append(f"{prefix}TEXT: {item.get('text', '')}")
        elif t == "highlight":
            lines.append(f"{prefix}HIGHLIGHT: {item.get('text', '')}")
        elif t == "list":
            lines.append(f"{prefix}LIST_START")
            for it in item.get("items", []):
                lines.append(f"{prefix}  • {it}")
            lines.append(f"{prefix}LIST_END")
        elif t == "table":
            headers = item.get("headers", [])
            lines.append(f"{prefix}TABLE_START: {' | '.join(headers)}")
            for row in item.get("rows", []):
                lines.append(f"{prefix}  ROW: {' | '.join(str(c) for c in row)}")
            lines.append(f"{prefix}TABLE_END")
        elif t == "math":
            lines.append(f"{prefix}MATH: {item.get('tex', '')}")
        elif t == "image":
            lines.append(f"{prefix}IMAGE: {item.get('url', '')}")
            if item.get("caption"):
                lines.append(f"{prefix}  CAPTION: {item.get('caption')}")
        else:
            # Generic fallback - render all keys
            for key, value in item.items():
                if key == "type":
                    continue
                if isinstance(value, str):
                    lines.append(f"{prefix}{key.upper()}: {value}")
                elif isinstance(value, list):
                    for v in value:
                        lines.append(f"{prefix}{key.upper()}: {v}")

        return lines

    @staticmethod
    def dsl_to_json(text: str) -> dict:
        """Parse DSL text back to JSON dict."""
        # Result structure - use a list for content items
        result = {"items": []}
        items = result["items"]  # Reference to the items list

        lines = text.strip().split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]
            strip = line.strip()

            # Skip empty lines
            if not strip:
                i += 1
                continue

            # Handle block markers
            if strip in ("LIST_START", "LIST_END", "TABLE_START", "TABLE_END"):
                i += 1
                continue

            # Check for TABLE_START with headers
            if strip.startswith("TABLE_START:"):
                content = strip.split(":", 1)[1].strip()
                headers = [h.strip() for h in content.split("|")]
                new_item = {"type": "table", "headers": headers, "rows": []}
                items.append(new_item)
                i += 1
                # Read rows until TABLE_END
                while i < len(lines):
                    row_line = lines[i].strip()
                    if row_line == "TABLE_END":
                        i += 1  # Move past TABLE_END
                        break
                    if row_line.startswith("ROW:") or row_line.startswith("TABLE_ROW:"):
                        content = row_line.split(":", 1)[1].strip()
                        cells = [c.strip() for c in content.split("|")]
                        new_item["rows"].append(cells)
                    i += 1
                continue

            # Handle list items
            if strip.startswith("•") or strip.startswith("- "):
                item_text = strip.lstrip("•- ").strip()
                if items and isinstance(items[-1], dict) and items[-1].get("type") == "list":
                    items[-1]["items"].append(item_text)
                i += 1
                continue

            # Check for TABLE_ROW (standalone, not in TABLE_START block)
            if strip.startswith("TABLE_ROW:") or strip.startswith("ROW:"):
                content = strip.split(":", 1)[1].strip()
                cells = [c.strip() for c in content.split("|")]
                if items and isinstance(items[-1], dict):
                    if "rows" not in items[-1]:
                        items[-1]["rows"] = []
                    items[-1]["rows"].append(cells)
                i += 1
                continue

            # Handle content blocks
            content_prefixes = ["HEADING:", "H1:", "H2:", "H3:", "H4:", "H5:", "H6:",
                                "TEXT:", "HIGHLIGHT:", "MATH:", "IMAGE:", "CAPTION:",
                                "LIST_START", "LIST:", "QUESTION:", "ANSWER:", "Q:", "A:",
                                "ITEM:", "ITEMS:", "CONTENT:", "LESSON:", "LESSONS:"]

            is_content = any(strip.startswith(p) for p in content_prefixes)

            if is_content:
                # Parse content blocks
                for prefix in ["HEADING:", "H1:", "H2:", "H3:", "H4:", "H5:", "H6:"]:
                    if strip.startswith(prefix):
                        content = strip[len(prefix):].strip()
                        level = 1 if prefix == "HEADING:" or prefix == "H1:" else int(prefix[1])
                        items.append({"type": "heading", "level": level, "text": content})
                        break
                else:
                    if strip.startswith("TEXT:"):
                        content = strip[5:].strip()
                        items.append({"type": "text", "text": content})
                    elif strip.startswith("HIGHLIGHT:"):
                        content = strip[10:].strip()
                        items.append({"type": "highlight", "text": content})
                    elif strip.startswith("MATH:"):
                        content = strip[5:].strip()
                        items.append({"type": "math", "tex": content, "display": True})
                    elif strip.startswith("IMAGE:"):
                        content = strip[6:].strip()
                        items.append({"type": "image", "url": content, "caption": ""})
                    elif strip.startswith("CAPTION:"):
                        content = strip[8:].strip()
                        if items and items[-1].get("type") == "image":
                            items[-1]["caption"] = content
                    elif strip.startswith("LIST_START") or strip.startswith("LIST:"):
                        # Start a list block
                        new_list = {"type": "list", "items": []}
                        if strip.startswith("LIST:") and len(strip) > 5:
                            # Content after LIST:
                            first_item = strip[5:].strip()
                            if first_item:
                                new_list["items"].append(first_item)
                        items.append(new_list)
                        # Continue reading list items
                        i += 1
                        while i < len(lines):
                            list_line = lines[i].strip()
                            if list_line == "LIST_END" or (not list_line.startswith("•") and not list_line.startswith("- ")):
                                if list_line == "LIST_END":
                                    i += 1
                                break
                            if list_line.startswith("•") or list_line.startswith("- "):
                                item_text = list_line.lstrip("•- ").strip()
                                new_list["items"].append(item_text)
                            i += 1
                        continue
                    elif strip.startswith("QUESTION:") or strip.startswith("Q:"):
                        content = strip[9:].strip() if strip.startswith("QUESTION:") else strip[2:].strip()
                        items.append({"type": "question", "text": content})
                    elif strip.startswith("ANSWER:") or strip.startswith("A:"):
                        content = strip[7:].strip() if strip.startswith("ANSWER:") else strip[2:].strip()
                        if items and items[-1].get("type") == "question":
                            items[-1]["answer"] = content

                i += 1
                continue

            # Handle key: value pairs (top-level metadata)
            if ":" in strip:
                key_part, _, value_part = strip.partition(":")
                key = key_part.strip().lower()
                json_key = key

                # Handle special keys
                if key in ("id", "title", "name", "description", "text", "tex", "url", "question", "answer", "caption"):
                    value = value_part.strip()
                    if value.lower() == "true":
                        result[json_key] = True
                    elif value.lower() == "false":
                        result[json_key] = False
                    elif value.isdigit():
                        result[json_key] = int(value)
                    else:
                        result[json_key] = value
                elif key in ("level", "estminutes", "rows", "items", "index", "width", "height"):
                    value = value_part.strip()
                    if value.isdigit():
                        result[json_key] = int(value)
                    else:
                        result[json_key] = value
                elif value_part.strip():
                    value = value_part.strip()
                    if value.isdigit():
                        result[json_key] = int(value)
                    else:
                        result[json_key] = value
                else:
                    result[json_key] = {}

                i += 1
                continue

            i += 1

        # Clean up empty items list
        if not result["items"]:
            del result["items"]

        return result


# ══════════════════════════════════════════════════════════════════════════════
#  SYNTAX HIGHLIGHTING
# ══════════════════════════════════════════════════════════════════════════════
class SyntaxHighlighter:
    """Apply syntax highlighting to DSL text."""

    PATTERNS = [
        (r"^(HEADING:|H[1-6]:)",  C["yellow"],      "bold"),     # Headings
        (r"^(TEXT:|HIGHLIGHT:)",  C["pink"],         "normal"),   # Text blocks
        (r"^(LIST:|LIST_START|LIST_END)", C["green"], "normal"), # Lists
        (r"^(MATH:)",            C["yellow2"],      "normal"),   # Math
        (r"^(IMAGE:|CAPTION:)",  C["blue"],          "normal"),   # Images
        (r"^(TABLE_|ROW:)",      C["accent3"],       "normal"),   # Tables
        (r"^[\s]*•",             C["green"],         "normal"),   # List bullets
        (r"^(TRUE|FALSE)",       C["accent2"],       "normal"),   # Booleans
        (r"\d+",                 C["accent3"],       "normal"),   # Numbers
    ]

    @classmethod
    def highlight(cls, text_widget):
        """Apply syntax highlighting to text widget content."""
        for tag in ["heading", "text", "highlight", "list", "math", "image", "table", "bullet", "bool", "number"]:
            text_widget.tag_remove(tag, "1.0", "end")

        text_widget.tag_configure("heading",    foreground=C["yellow"],   font=(F["mono"][0], F["mono"][1], "bold"))
        text_widget.tag_configure("text",       foreground=C["pink"],     font=(F["mono"][0], F["mono"][1]))
        text_widget.tag_configure("highlight", foreground=C["pink"],       font=(F["mono"][0], F["mono"][1]))
        text_widget.tag_configure("list",       foreground=C["green"],     font=(F["mono"][0], F["mono"][1]))
        text_widget.tag_configure("math",       foreground=C["yellow2"],   font=(F["mono"][0], F["mono"][1]))
        text_widget.tag_configure("image",      foreground=C["blue"],      font=(F["mono"][0], F["mono"][1]))
        text_widget.tag_configure("table",      foreground=C["accent3"],   font=(F["mono"][0], F["mono"][1]))
        text_widget.tag_configure("bullet",     foreground=C["green"],      font=(F["mono"][0], F["mono"][1]))
        text_widget.tag_configure("bool",       foreground=C["accent2"],   font=(F["mono"][0], F["mono"][1]))
        text_widget.tag_configure("number",     foreground=C["accent3"],    font=(F["mono"][0], F["mono"][1]))

        content = text_widget.get("1.0", "end-1c")
        lines = content.split("\n")

        for row, line in enumerate(lines, 1):
            # Check for headings
            if re.match(r"^(HEADING:|H[1-6]:)", line):
                text_widget.tag_add("heading", f"{row}.0", f"{row}.end")
                continue

            # Check for text blocks
            if re.match(r"^(TEXT:|HIGHLIGHT:)", line):
                text_widget.tag_add("text", f"{row}.0", f"{row}.end")
                continue

            # Check for list markers
            if re.match(r"^(LIST:|LIST_START|LIST_END)", line):
                text_widget.tag_add("list", f"{row}.0", f"{row}.end")
                continue
            if re.match(r"^[\s]*•", line):
                text_widget.tag_add("bullet", f"{row}.0", f"{row}.end")
                continue

            # Check for math
            if re.match(r"^MATH:", line):
                text_widget.tag_add("math", f"{row}.0", f"{row}.end")
                continue

            # Check for image/caption
            if re.match(r"^(IMAGE:|CAPTION:)", line):
                text_widget.tag_add("image", f"{row}.0", f"{row}.end")
                continue

            # Check for table
            if re.match(r"^(TABLE_|ROW:)", line):
                text_widget.tag_add("table", f"{row}.0", f"{row}.end")
                continue

            # Highlight booleans
            if re.search(r"\b(TRUE|FALSE)\b", line, re.IGNORECASE):
                for match in re.finditer(r"\b(TRUE|FALSE)\b", line, re.IGNORECASE):
                    start = f"{row}.{match.start()}"
                    end = f"{row}.{match.end()}"
                    text_widget.tag_add("bool", start, end)

            # Highlight numbers
            for match in re.finditer(r"\b\d+\b", line):
                start = f"{row}.{match.start()}"
                end = f"{row}.{match.end()}"
                # Don't highlight if inside a word
                if match.start() == 0 or not line[match.start()-1].isalpha():
                    text_widget.tag_add("number", start, end)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════
class DSLConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DSL Converter — JSON <-> DSL Editor")
        self.geometry("1100x700")
        self.minsize(800, 500)
        self.configure(bg=C["bg"])

        self._filepath: str | None = None
        self._original_json: dict = {}
        self._unsaved = False

        self._style_ttk()
        self._build_ui()
        self._setup_hotkeys()

    # ── TTK Style ──────────────────────────────────────────────────────────────
    def _style_ttk(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TScrollbar", background=C["surface"], troughcolor=C["bg"],
                     borderwidth=0, relief="flat")

    # ── Hotkeys ───────────────────────────────────────────────────────────────
    def _setup_hotkeys(self):
        self.bind("<Control-o>", lambda e: self._open())
        self.bind("<Control-s>", lambda e: self._save())
        self.bind("<Control-S>", lambda e: self._save_as())
        self.bind("<Control-j>", lambda e: self._json_to_dsl())
        self.bind("<Control-d>", lambda e: self._dsl_to_json())
        self.bind("<Control-f>", lambda e: self._format_dsl())

    # ── UI Layout ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Top accent
        tk.Frame(self, bg=C["accent"], height=3).pack(fill="x")

        # Toolbar
        self._build_toolbar()

        # Main content
        main = tk.PanedWindow(self, orient="horizontal", bg=C["bg"],
                               sashwidth=6, sashrelief="flat", sashpad=0)
        main.pack(fill="both", expand=True, padx=4, pady=4)

        # Left panel - JSON
        left = tk.Frame(main, bg=C["surface"], width=420)
        main.add(left, minsize=300)
        self._build_json_panel(left)

        # Right panel - DSL
        right = tk.Frame(main, bg=C["surface"])
        main.add(right, minsize=300)
        self._build_dsl_panel(right)

        # Status bar
        self._build_statusbar()

    def _build_toolbar(self):
        tb = tk.Frame(self, bg=C["surface"], height=52)
        tb.pack(fill="x"); tb.pack_propagate(False)

        # Logo
        tk.Label(tb, text="↔", bg=C["surface"], fg=C["accent"],
                 font=("Segoe UI", 18)).pack(side="left", padx=(16,4), pady=10)
        tk.Label(tb, text="DSL Converter", bg=C["surface"], fg=C["accent2"],
                 font=F["h1"]).pack(side="left", pady=10)

        tk.Frame(tb, bg=C["border"], width=1).pack(side="left", fill="y", pady=8, padx=12)

        # Actions
        actions = [
            ("📂 Buka",     self._open,      "ghost"),
            ("💾 Simpan",    self._save,      "outline"),
            ("💾 Simpan As", self._save_as,   "ghost"),
        ]
        for lbl, cmd, sty in actions:
            Btn(tb, lbl, cmd, sty, py=4).pack(side="left", padx=3, pady=12)

        tk.Frame(tb, bg=C["border"], width=1).pack(side="left", fill="y", pady=8, padx=8)

        # Convert buttons
        Btn(tb, "JSON → DSL", self._json_to_dsl, "purple", py=4).pack(side="left", padx=3, pady=12)
        Btn(tb, "DSL → JSON", self._dsl_to_json, "green",  py=4).pack(side="left", padx=3, pady=12)

        tk.Frame(tb, bg=C["border"], width=1).pack(side="left", fill="y", pady=8, padx=8)

        Btn(tb, "✨ Format",  self._format_dsl,  "ghost",  py=4).pack(side="left", padx=3, pady=12)

        # File path
        self._file_lbl = tk.Label(tb, text="Belum buka file", bg=C["surface"],
                                   fg=C["text4"], font=F["tiny"])
        self._file_lbl.pack(side="right", padx=16)

    def _build_json_panel(self, parent):
        hdr = tk.Frame(parent, bg=C["surface"])
        hdr.pack(fill="x", padx=12, pady=(10,4))

        tk.Label(hdr, text="{ } JSON", bg=C["surface"], fg=C["blue"],
                 font=F["h2"]).pack(side="left")
        Btn(hdr, "📋 Salin", self._copy_json, "ghost", px=8, py=2).pack(side="right")

        # JSON text area
        self._json_txt = Textbox(parent, font=F["mono"], bg=C["surface"])
        sb = ttk.Scrollbar(parent, orient="vertical", command=self._json_txt.yview)
        self._json_txt.configure(yscrollcommand=sb.set)
        self._json_txt.pack(side="left", fill="both", expand=True, padx=(12,0), pady=(0,8))
        sb.pack(side="right", fill="y", padx=(0,8), pady=(0,8))

    def _build_dsl_panel(self, parent):
        hdr = tk.Frame(parent, bg=C["surface"])
        hdr.pack(fill="x", padx=12, pady=(10,4))

        tk.Label(hdr, text="📝 DSL", bg=C["surface"], fg=C["green"],
                 font=F["h2"]).pack(side="left")
        Btn(hdr, "📋 Salin", self._copy_dsl, "ghost", px=8, py=2).pack(side="right")

        # DSL text area
        self._dsl_txt = Textbox(parent, font=F["mono"], bg=C["surface"])
        sb = ttk.Scrollbar(parent, orient="vertical", command=self._dsl_txt.yview)
        self._dsl_txt.configure(yscrollcommand=sb.set)
        self._dsl_txt.pack(side="left", fill="both", expand=True, padx=(12,0), pady=(0,8))
        sb.pack(side="right", fill="y", padx=(0,8), pady=(0,8))

        # Bind highlight on change
        self._dsl_txt.bind("<KeyRelease>", lambda e: self._on_dsl_change())
        self._dsl_txt.bind("<<Modified>>", lambda e: self._on_dsl_change())

    def _build_statusbar(self):
        sb = tk.Frame(self, bg=C["surface"], height=28)
        sb.pack(fill="x", side="bottom"); sb.pack_propagate(False)

        self._status_lbl = tk.Label(sb, text="  Buka file JSON atau paste JSON di panel kiri",
                                     bg=C["surface"], fg=C["text3"], font=F["small"], anchor="w")
        self._status_lbl.pack(side="left", fill="x", expand=True)

        self._hint_lbl = tk.Label(sb, text="Ctrl+O: Buka  |  Ctrl+S: Simpan  |  Ctrl+J: JSON→DSL  |  Ctrl+D: DSL→JSON",
                                   bg=C["surface"], fg=C["text4"], font=F["tiny"])
        self._hint_lbl.pack(side="right", padx=16)

    # ── File Operations ───────────────────────────────────────────────────────
    def _open(self):
        p = filedialog.askopenfilename(
            title="Buka File JSON",
            filetypes=[("JSON", "*.json"), ("Semua File", "*.*")])
        if p:
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._filepath = p
                self._original_json = data
                self._json_txt.delete("1.0", "end")
                self._json_txt.insert("1.0", json.dumps(data, ensure_ascii=False, indent=2))
                self._json_to_dsl()
                self._update_title()
                self._status(f"✓ Dibuka: {os.path.basename(p)}")
                Toast.show(self, f"File dibuka: {os.path.basename(p)}", "ok")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membuka file:\n{e}")

    def _save(self):
        if not self._filepath:
            self._save_as()
            return
        self._write(self._filepath)

    def _save_as(self):
        p = filedialog.asksaveasfilename(
            title="Simpan File",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Semua File", "*.*")])
        if p:
            self._filepath = p
            self._write(p)

    def _write(self, path):
        try:
            # Get JSON from text widget
            raw = self._json_txt.get("1.0", "end-1c")
            data = json.loads(raw)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self._original_json = data
            self._unsaved = False
            self._update_title()
            self._status(f"✓ Disimpan: {os.path.basename(path)} [{datetime.now():%H:%M:%S}]")
            Toast.show(self, f"Disimpan: {os.path.basename(path)}", "ok")
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", "JSON tidak valid!\n" + str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan:\n{e}")

    # ── Conversion ────────────────────────────────────────────────────────────
    def _json_to_dsl(self):
        try:
            raw = self._json_txt.get("1.0", "end-1c").strip()
            if not raw:
                self._status("Panel JSON kosong", "warn")
                return
            data = json.loads(raw)
            dsl = DSLConverter.json_to_dsl(data)
            self._dsl_txt.delete("1.0", "end")
            self._dsl_txt.insert("1.0", dsl)
            SyntaxHighlighter.highlight(self._dsl_txt)
            self._status(f"✓ JSON → DSL ({len(dsl):,} karakter)")
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"JSON tidak valid:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal konversi:\n{e}")

    def _dsl_to_json(self):
        try:
            raw = self._dsl_txt.get("1.0", "end-1c").strip()
            if not raw:
                self._status("Panel DSL kosong", "warn")
                return
            data = DSLConverter.dsl_to_json(raw)
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            self._json_txt.delete("1.0", "end")
            self._json_txt.insert("1.0", json_str)
            self._unsaved = True
            self._update_title()
            self._status(f"✓ DSL → JSON ({len(json_str):,} karakter)")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal konversi DSL:\n{e}")

    # ── Formatting ────────────────────────────────────────────────────────────
    def _format_dsl(self):
        """Auto-format DSL text."""
        raw = self._dsl_txt.get("1.0", "end-1c")
        lines = raw.split("\n")
        formatted = []

        for line in lines:
            s = line.strip()
            if not s:
                formatted.append("")
                continue

            # Keep properly formatted lines
            if re.match(r"^[A-Z_]+:", s):
                formatted.append(s)
            elif s.startswith("•") or s.startswith("- "):
                formatted.append(s)
            elif re.match(r"^\d+\.", s):
                formatted.append(s)
            else:
                formatted.append(s)

        # Join and show
        result = "\n".join(formatted)
        self._dsl_txt.delete("1.0", "end")
        self._dsl_txt.insert("1.0", result)
        SyntaxHighlighter.highlight(self._dsl_txt)
        Toast.show(self, "Format diterapkan!", "ok")

    # ── Copy Operations ───────────────────────────────────────────────────────
    def _copy_json(self):
        txt = self._json_txt.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(txt)
        Toast.show(self, "JSON disalin!", "ok")

    def _copy_dsl(self):
        txt = self._dsl_txt.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(txt)
        Toast.show(self, "DSL disalin!", "ok")

    # ── Event Handlers ────────────────────────────────────────────────────────
    def _on_dsl_change(self):
        """Called when DSL text changes - reapply highlighting."""
        if self._dsl_txt.edit_modified():
            self._dsl_txt.edit_modified(False)
            self.after_idle(lambda: SyntaxHighlighter.highlight(self._dsl_txt))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _update_title(self):
        fname = os.path.basename(self._filepath) if self._filepath else "Tanpa File"
        marker = " ●" if self._unsaved else ""
        self.title(f"DSL Converter — {fname}{marker}")
        self._file_lbl.config(
            text=self._filepath or "Belum buka file",
            fg=C["yellow"] if self._unsaved else C["text4"])

    def _status(self, msg, kind="info"):
        self._status_lbl.config(text=f"  {msg}")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = DSLConverterApp()
    app.mainloop()

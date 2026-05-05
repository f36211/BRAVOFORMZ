"""
IPA JSON Editor — v3.0 "Polaris"
Editor materi IPA SMP berbasis GUI (Tkinter)
AI Mode: Prompt-only (no API key needed — copy prompt → paste response)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json, os, copy, re, threading
from datetime import datetime
from collections import deque

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
    "title":  ("Segoe UI", 22, "bold"),
    "h1":     ("Segoe UI", 15, "bold"),
    "h2":     ("Segoe UI", 12, "bold"),
    "body":   ("Segoe UI", 10),
    "small":  ("Segoe UI", 9),
    "tiny":   ("Segoe UI", 8),
    "mono":   ("Consolas", 10),
    "monos":  ("Consolas", 9),
}

# ══════════════════════════════════════════════════════════════════════════════
#  UTILITIES
# ══════════════════════════════════════════════════════════════════════════════
def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s[:40]

def deep(obj): return copy.deepcopy(obj)

def hex_blend(hex1: str, hex2: str, t: float) -> str:
    """Lerp between two hex colors."""
    h1 = hex1.lstrip("#"); h2 = hex2.lstrip("#")
    r1,g1,b1 = int(h1[:2],16), int(h1[2:4],16), int(h1[4:],16)
    r2,g2,b2 = int(h2[:2],16), int(h2[2:4],16), int(h2[4:],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))

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
        "yellow":  (C["yellow2"], C["white"]),
    }
    def __init__(self, parent, text="", cmd=None, style="primary",
                 px=14, py=6, **kw):
        bg, fg = self.STYLES.get(style, self.STYLES["primary"])
        super().__init__(parent, text=text, command=cmd,
                         bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                         relief="flat", bd=0, padx=px, pady=py,
                         font=F["body"], cursor="hand2", **kw)
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
        super().__init__(parent, text=text,
                         fg=fg or C["text"], font=font or F["body"],
                         bg=bg or parent.cget("bg"), **kw)


class Frame(tk.Frame):
    def __init__(self, parent, bg=None, **kw):
        super().__init__(parent, bg=bg or C["bg"], **kw)


class Card(tk.Frame):
    def __init__(self, parent, pad=10, **kw):
        kw.setdefault("bg", C["card"])
        super().__init__(parent, relief="flat", bd=0, **kw)
        # Subtle border via highlight
        self.config(highlightthickness=1,
                    highlightbackground=C["border"],
                    highlightcolor=C["border"])


class SLabel(tk.Label):
    """Section / caption label."""
    def __init__(self, parent, text="", **kw):
        super().__init__(parent, text=text.upper(),
                         bg=parent.cget("bg"), fg=C["text3"],
                         font=F["tiny"], anchor="w", **kw)


# ══════════════════════════════════════════════════════════════════════════════
#  TOAST NOTIFICATION
# ══════════════════════════════════════════════════════════════════════════════
class Toast:
    """Non-blocking corner notification."""
    _queue: list = []

    @classmethod
    def show(cls, root, msg: str, kind="info", duration=2500):
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
        tk.Label(inner, text=f"  {icons[kind]}  {msg}  ",
                 bg=bg, fg=C["white"], font=F["body"], pady=10).pack()

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
#  DSL ENGINE  (content ↔ text)
# ══════════════════════════════════════════════════════════════════════════════
class DSL:
    """Convert lesson content list ↔ multiline DSL text."""

    @staticmethod
    def dumps(content: list) -> str:
        lines = []
        for item in content:
            t = item.get("type", "text")
            if t == "heading":
                lvl = item.get("level", 1)
                p = "HEADING" if lvl == 1 else f"H{lvl}"
                lines.append(f"{p}: {item.get('text','')}")
            elif t == "text":
                lines.append(f"TEXT: {item.get('text','')}")
            elif t == "highlight":
                lines.append(f"HIGHLIGHT: {item.get('text','')}")
            elif t == "list":
                for it in item.get("items", []):
                    lines.append(f"LIST: {it}")
            elif t == "table":
                lines.append(f"TABLE_HEADER: {','.join(item.get('headers',[]))}")
                for row in item.get("rows", []):
                    lines.append(f"TABLE_ROW: {','.join(str(c) for c in row)}")
            elif t == "math":
                lines.append(f"MATH: {item.get('tex','')}")
            elif t == "image":
                lines.append(f"IMAGE: {item.get('url','')}")
                if item.get("caption"):
                    lines.append(f"CAPTION: {item['caption']}")
        return "\n".join(lines)

    @staticmethod
    def loads(raw: str) -> list:
        content = []
        current_table = None

        def flush():
            nonlocal current_table
            if current_table:
                content.append(current_table)
                current_table = None

        for line in raw.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            if ":" not in line:
                flush()
                content.append({"type": "text", "text": line})
                continue
            prefix, _, rest = line.partition(":")
            p = prefix.strip().upper()
            rest = rest.strip()

            if p in ("HEADING", "H1"):
                flush(); content.append({"type":"heading","level":1,"text":rest})
            elif re.match(r"^H[2-6]$", p):
                flush(); content.append({"type":"heading","level":int(p[1:]),"text":rest})
            elif p == "TEXT":
                flush(); content.append({"type":"text","text":rest})
            elif p == "HIGHLIGHT":
                flush(); content.append({"type":"highlight","text":rest})
            elif p == "LIST":
                flush()
                if content and content[-1].get("type") == "list":
                    content[-1]["items"].append(rest)
                else:
                    content.append({"type":"list","items":[rest]})
            elif p == "TABLE_HEADER":
                flush()
                current_table = {"type":"table",
                                  "headers":[h.strip() for h in rest.split(",")],
                                  "rows":[]}
            elif p == "TABLE_ROW":
                if current_table is None:
                    current_table = {"type":"table","headers":[],"rows":[]}
                current_table["rows"].append([c.strip() for c in rest.split(",")])
            elif p == "MATH":
                flush(); content.append({"type":"math","tex":rest,"display":True})
            elif p == "IMAGE":
                flush(); content.append({"type":"image","url":rest,"caption":""})
            elif p == "CAPTION":
                if content and content[-1].get("type") == "image":
                    content[-1]["caption"] = rest
            else:
                flush(); content.append({"type":"text","text":line})

        flush()
        return content


# ══════════════════════════════════════════════════════════════════════════════
#  TOPIC-LEVEL DSL  (topic ↔ text, used in AI Mode)
# ══════════════════════════════════════════════════════════════════════════════
class TopicDSL:
    @staticmethod
    def encode(topic: dict) -> str:
        lines = [
            f"TOPIC_TITLE: {topic.get('title','')}",
            f"TOPIC_DESC: {topic.get('description','')}",
        ]
        for lesson in topic.get("lessons", []):
            lines.append(f"\n--- LESSON: {lesson.get('title','?')} [{lesson.get('id','?')}] ---")
            lines.append(f"EST_TIME: {lesson.get('estMinutes', 10)}")
            for item in lesson.get("content", []):
                t = item.get("type","text")
                if t == "heading":
                    lvl = item.get("level", 1)
                    lines.append(f"{'HEADING' if lvl==1 else f'H{lvl}'}: {item.get('text','')}")
                elif t == "text":      lines.append(f"TEXT: {item.get('text','')}")
                elif t == "highlight": lines.append(f"HIGHLIGHT: {item.get('text','')}")
                elif t == "list":
                    lines.append("LIST_START")
                    for it in item.get("items",[]): lines.append(f"  • {it}")
                    lines.append("LIST_END")
                elif t == "table":
                    lines.append(f"TABLE_START: {' | '.join(item.get('headers',[]))}")
                    for row in item.get("rows",[]): lines.append(f"  ROW: {' | '.join(str(c) for c in row)}")
                    lines.append("TABLE_END")
                elif t == "math":  lines.append(f"MATH: {item.get('tex','')}")
                elif t == "image": lines.append(f"IMAGE: {item.get('url','')}")
            lines.append("--- END_LESSON ---")

        if topic.get("flashcards"):
            lines.append("\n=== FLASHCARDS ===")
            for fc in topic["flashcards"]:
                lines.append(f"Q: {fc.get('question','')}")
                lines.append(f"A: {fc.get('answer','')}")
            lines.append("=== END_FLASHCARDS ===")

        quiz = topic.get("quiz", {})
        if quiz.get("questions"):
            lines.append("\n=== QUIZ ===")
            for q in quiz["questions"]:
                lines.append(f"QUESTION: {q.get('question','')}")
                for i, opt in enumerate(q.get("options",["","","",""])):
                    lines.append(f"  {'ABCD'[i]}) {opt}")
                lines.append(f"CORRECT: {q.get('answer',0)}")
                if q.get("explanation"):
                    lines.append(f"EXP: {q['explanation']}")
            lines.append("=== END_QUIZ ===")

        return "\n".join(lines)

    @staticmethod
    def decode(text: str) -> dict:
        topic = {}
        lines = text.strip().split("\n")
        cur_lesson = None
        cur_table  = None
        cur_list   = None
        in_fc      = False
        in_quiz    = False
        cur_q      = None

        def flush_lesson():
            nonlocal cur_lesson, cur_table, cur_list
            if cur_lesson:
                if cur_table: cur_lesson["content"].append(cur_table); cur_table = None
                if cur_list:  cur_lesson["content"].append(cur_list);  cur_list  = None
                exists = any(l.get("id") == cur_lesson["id"]
                             for l in topic.get("lessons", []))
                if not exists:
                    topic.setdefault("lessons", []).append(cur_lesson)

        for raw_line in lines:
            line = raw_line.strip()
            if not line: continue

            ul = line.upper()

            if "--- LESSON:" in line:
                flush_lesson()
                try:
                    title = line.split(":")[1].split("[")[0].strip()
                    lid   = line.split("[")[1].split("]")[0].strip() if "[" in line else slugify(title)
                except Exception:
                    title, lid = "Untitled", "untitled"
                cur_lesson = {"id": lid, "title": title, "estMinutes": 10, "content": []}
                continue
            elif "--- END_LESSON ---" in line:
                flush_lesson(); cur_lesson = None; continue
            elif "=== FLASHCARDS ===" in line:
                flush_lesson(); topic.setdefault("flashcards", []); in_fc = True; continue
            elif "=== END_FLASHCARDS ===" in line:
                in_fc = False; continue
            elif "=== QUIZ ===" in line:
                flush_lesson(); topic.setdefault("quiz", {"questions": []}); in_quiz = True; continue
            elif "=== END_QUIZ ===" in line:
                in_quiz = False; continue

            if ul.startswith("LIST_START"):
                if cur_list and cur_lesson: cur_lesson["content"].append(cur_list)
                cur_list = {"type":"list","items":[]}; continue
            elif ul.startswith("LIST_END"):
                if cur_lesson and cur_list: cur_lesson["content"].append(cur_list)
                cur_list = None; continue
            elif ul.startswith("TABLE_START"):
                if cur_table and cur_lesson: cur_lesson["content"].append(cur_table)
                headers = [h.strip() for h in line.partition(":")[2].split("|")] if ":" in line else []
                cur_table = {"type":"table","headers":headers,"rows":[]}; continue
            elif ul.startswith("TABLE_END"):
                if cur_lesson and cur_table: cur_lesson["content"].append(cur_table)
                cur_table = None; continue

            if line.startswith("•") or line.startswith("- "):
                it = line.lstrip("•- ").strip()
                if cur_list is None: cur_list = {"type":"list","items":[]}
                cur_list["items"].append(it); continue

            if ":" in line:
                pre, _, rest = line.partition(":")
                p = pre.strip().upper(); rest = rest.strip()

                if p == "TOPIC_TITLE": topic["title"] = rest; topic["id"] = slugify(rest)
                elif p == "TOPIC_DESC": topic["description"] = rest
                elif cur_lesson:
                    if p == "EST_TIME":
                        try: cur_lesson["estMinutes"] = int(re.search(r"\d+", rest).group())
                        except: pass
                    elif p in ("HEADING","H1"):
                        cur_lesson["content"].append({"type":"heading","level":1,"text":rest})
                    elif re.match(r"^H[2-6]$", p):
                        cur_lesson["content"].append({"type":"heading","level":int(p[1:]),"text":rest})
                    elif p == "TEXT":      cur_lesson["content"].append({"type":"text","text":rest})
                    elif p == "HIGHLIGHT": cur_lesson["content"].append({"type":"highlight","text":rest})
                    elif p == "ROW":
                        if cur_table: cur_table["rows"].append([c.strip() for c in rest.split("|")])
                    elif p == "MATH":  cur_lesson["content"].append({"type":"math","tex":rest,"display":True})
                    elif p == "IMAGE": cur_lesson["content"].append({"type":"image","url":rest,"caption":""})
                    elif p == "CAPTION":
                        if cur_lesson["content"] and cur_lesson["content"][-1].get("type")=="image":
                            cur_lesson["content"][-1]["caption"] = rest
                    else:
                        if cur_list: cur_list["items"].append(line)
                        else: cur_lesson["content"].append({"type":"text","text":line})
                elif in_fc:
                    if p == "Q":   topic["flashcards"].append({"id":f"fc{len(topic['flashcards'])+1}","question":rest,"answer":""})
                    elif p == "A" and topic["flashcards"]: topic["flashcards"][-1]["answer"] = rest
                elif in_quiz:
                    if p == "QUESTION":
                        cur_q = {"id":f"q{len(topic['quiz']['questions'])+1}","type":"multiple_choice",
                                 "question":rest,"options":[],"answer":0,"explanation":""}
                        topic["quiz"]["questions"].append(cur_q)
                    elif p == "CORRECT" and cur_q:
                        try:
                            cur_q["answer"] = int(rest) if rest.isdigit() else ord(rest.upper()[0])-65
                        except: pass
                    elif p == "EXP" and cur_q: cur_q["explanation"] = rest
            elif in_quiz and cur_q:
                if re.match(r"^[A-D][).]", line):
                    cur_q["options"].append(line[2:].strip())

        flush_lesson()
        return topic


# ══════════════════════════════════════════════════════════════════════════════
#  PROMPT BUILDER  (no API calls — pure text)
# ══════════════════════════════════════════════════════════════════════════════
class PromptKit:
    SYSTEM = """Kamu adalah expert content developer kurikulum IPA SMP Indonesia.
Kamu memahami Kurikulum Merdeka, KD/TP untuk kelas 7-9, dan pedagogi berbasis inquiry.

ATURAN KETAT:
1. Balas HANYA dengan format DSL berikut — tidak ada teks tambahan, tidak ada markdown ```.
2. Bahasa: Indonesia, sesuai level siswa SMP (mudah dipahami, contoh kehidupan sehari-hari).
3. Konten harus AKURAT secara ilmiah dan AMAN untuk anak sekolah.

FORMAT DSL:
TOPIC_TITLE: <judul>
TOPIC_DESC: <deskripsi singkat>

--- LESSON: <judul pelajaran> [<id-slug>] ---
EST_TIME: <menit>
HEADING: <heading utama>
H2: <sub-heading>
TEXT: <paragraf penjelasan>
HIGHLIGHT: <fakta/definisi penting>
LIST_START
  • <item>
LIST_END
TABLE_START: Kolom1 | Kolom2 | Kolom3
  ROW: nilai1 | nilai2 | nilai3
TABLE_END
MATH: <LaTeX>
IMAGE: <url gambar>
CAPTION: <deskripsi>
--- END_LESSON ---

=== FLASHCARDS ===
Q: <pertanyaan>
A: <jawaban>
=== END_FLASHCARDS ===

=== QUIZ ===
QUESTION: <soal>
  A) <opsi>
  B) <opsi>
  C) <opsi>
  D) <opsi>
CORRECT: <0-3>
EXP: <penjelasan jawaban>
=== END_QUIZ ==="""

    ACTIONS = {
        "enhance":   ("🧠 Perkaya Konten",     "Perkaya dan perluas materi topik berikut. Tambah lebih banyak pelajaran, contoh, dan koneksi ke kehidupan nyata. Pertahankan semua konten yang ada, hanya tambahkan."),
        "lesson":    ("📖 Pelajaran Baru",      "Buat 1-2 pelajaran baru yang BELUM ADA untuk topik berikut. Hanya balas bagian --- LESSON --- saja."),
        "flashcard": ("🃏 Tambah Flashcard",    "Buat 8 flashcard baru yang kreatif dan belum ada di daftar. Hanya balas bagian === FLASHCARDS === saja."),
        "quiz":      ("📝 Soal HOTS",           "Buat 6 soal pilihan ganda tingkat HOTS (Higher Order Thinking Skill) yang baru. Hanya balas bagian === QUIZ === saja."),
        "simplify":  ("✂️ Sederhanakan",        "Buat versi lebih sederhana dari topik ini untuk siswa yang kesulitan. Gunakan analogi dan bahasa super santai."),
        "from_zero": ("✨ Buat dari Nol",       "Buat topik IPA SMP lengkap dari nol dengan TOPIC_TITLE, 2 pelajaran, 8 flashcard, 5 soal kuis."),
    }

    @classmethod
    def build(cls, action: str, topic: dict, subject_name: str = "IPA") -> str:
        _, instruction = cls.ACTIONS.get(action, cls.ACTIONS["enhance"])
        dsl = TopicDSL.encode(topic) if action != "from_zero" else f"TOPIC_TITLE: {topic.get('title','')}"
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        return (
            f"[SYSTEM — {ts}]\n{cls.SYSTEM}\n\n"
            f"[INSTRUKSI]\n{instruction}\n"
            f"Mata pelajaran: {subject_name} — Target: Siswa SMP Kelas 7-9\n\n"
            f"[MATERI SAAT INI — DSL]\n{dsl}"
        )

    @classmethod
    def quick_build(cls, topic_title: str, subject: str = "IPA") -> str:
        """Build a create-from-zero prompt without existing topic data."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        return (
            f"[SYSTEM — {ts}]\n{cls.SYSTEM}\n\n"
            f"[INSTRUKSI]\nBuat topik '{topic_title}' ({subject} SMP) dari nol. "
            f"Sertakan 2 pelajaran, 8 flashcard, dan 5 soal kuis.\n"
        )


# ══════════════════════════════════════════════════════════════════════════════
#  UNDO / REDO STACK
# ══════════════════════════════════════════════════════════════════════════════
class UndoStack:
    def __init__(self, maxlen=30):
        self._undo = deque(maxlen=maxlen)
        self._redo = deque(maxlen=maxlen)

    def push(self, state): self._undo.append(deep(state)); self._redo.clear()
    def undo(self, current):
        if not self._undo: return None
        self._redo.append(deep(current))
        return deep(self._undo.pop())
    def redo(self, current):
        if not self._redo: return None
        self._undo.append(deep(current))
        return deep(self._redo.pop())
    @property
    def can_undo(self): return bool(self._undo)
    @property
    def can_redo(self): return bool(self._redo)


# ══════════════════════════════════════════════════════════════════════════════
#  DIALOGS
# ══════════════════════════════════════════════════════════════════════════════
class BaseDialog(tk.Toplevel):
    def __init__(self, parent, title, w, h):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.configure(bg=C["bg"])
        self.geometry(f"{w}x{h}")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

    def _footer(self, save_cmd):
        f = tk.Frame(self, bg=C["surface"], pady=10)
        f.pack(fill="x", side="bottom")
        Btn(f, "✓  Simpan", save_cmd, "primary").pack(side="right", padx=16)
        Btn(f, "Batal", self.destroy, "ghost").pack(side="right", padx=4)
        return f


class TopicDialog(BaseDialog):
    def __init__(self, parent, topic=None):
        super().__init__(parent, "✏️  Topik", 520, 340)
        self._build(topic)
        self.wait_window()

    def _build(self, t):
        header = tk.Frame(self, bg=C["accent"], height=4)
        header.pack(fill="x")

        inner = tk.Frame(self, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=24, pady=16)

        Label(inner, "Tambah / Edit Topik", font=F["h1"]).pack(anchor="w", pady=(0,16))

        for lbl, key, val in [
            ("Judul Topik *", "title", t.get("title","") if t else ""),
            ("Deskripsi", "description", t.get("description","") if t else ""),
        ]:
            SLabel(inner, lbl).pack(anchor="w", pady=(8,2))
            v = tk.StringVar(value=val)
            setattr(self, f"_{key}", v)
            Entry(inner, textvariable=v).pack(fill="x")

        SLabel(inner, "Kelas").pack(anchor="w", pady=(12,4))
        gf = tk.Frame(inner, bg=C["bg"]); gf.pack(anchor="w")
        self._grades = {}
        curr = t.get("grade",[7]) if t else [7]
        for g in [7,8,9]:
            var = tk.BooleanVar(value=g in curr)
            self._grades[g] = var
            cb = tk.Checkbutton(gf, text=f"Kelas {g}", variable=var,
                                bg=C["bg"], fg=C["text2"], selectcolor=C["raised"],
                                activebackground=C["bg"], font=F["body"],
                                cursor="hand2")
            cb.pack(side="left", padx=10)

        self._footer(self._save)

    def _save(self):
        title = self._title.get().strip()
        if not title:
            messagebox.showwarning("Perhatian", "Judul wajib diisi!", parent=self)
            return
        self.result = {
            "id": slugify(title), "title": title,
            "description": self._description.get().strip(),
            "grade": [g for g,v in self._grades.items() if v.get()],
            "lessons": [], "flashcards": [], "quiz": {"questions": []}
        }
        self.destroy()


class SubjectInfoDialog(BaseDialog):
    def __init__(self, parent, data):
        super().__init__(parent, "⚙️  Info Pelajaran", 520, 380)
        self._build(data); self.wait_window()

    def _build(self, d):
        tk.Frame(self, bg=C["accent"], height=4).pack(fill="x")
        inner = tk.Frame(self, bg=C["bg"]); inner.pack(fill="both",expand=True,padx=24,pady=16)
        Label(inner, "Info Pelajaran", font=F["h1"]).pack(anchor="w", pady=(0,12))

        self._vars = {}
        for lbl, key, val in [
            ("Nama Pelajaran *", "name",        d.get("name","")),
            ("Deskripsi",        "description", d.get("description","")),
            ("Cover Image URL",  "image",       d.get("image","")),
        ]:
            SLabel(inner, lbl).pack(anchor="w", pady=(8,2))
            v = tk.StringVar(value=val)
            self._vars[key] = v
            Entry(inner, textvariable=v).pack(fill="x")

        SLabel(inner, "Tingkatan Kelas").pack(anchor="w", pady=(12,4))
        gf = tk.Frame(inner, bg=C["bg"]); gf.pack(anchor="w")
        self._grades = {}
        for g in [7,8,9]:
            var = tk.BooleanVar(value=g in d.get("grade",[7,8,9]))
            self._grades[g] = var
            tk.Checkbutton(gf, text=f"Kelas {g}", variable=var,
                           bg=C["bg"], fg=C["text2"], selectcolor=C["raised"],
                           activebackground=C["bg"], font=F["body"], cursor="hand2"
                           ).pack(side="left", padx=10)
        self._footer(self._save)

    def _save(self):
        name = self._vars["name"].get().strip()
        if not name: messagebox.showwarning("Perhatian","Nama wajib diisi!",parent=self); return
        self.result = {
            "name": name,
            "description": self._vars["description"].get().strip(),
            "image":       self._vars["image"].get().strip(),
            "grade":       [g for g,v in self._grades.items() if v.get()],
        }
        self.destroy()


class LessonDialog(BaseDialog):
    """Full-featured lesson editor with DSL + syntax highlighting."""
    def __init__(self, parent, lesson=None):
        super().__init__(parent, "📖  Editor Pelajaran", 680, 740)
        self._build(lesson); self.wait_window()

    def _build(self, lesson):
        # Top accent
        tk.Frame(self, bg=C["accent"], height=4).pack(fill="x")

        # Scrollable main area
        outer = tk.Frame(self, bg=C["bg"]); outer.pack(fill="both", expand=True)

        # ── Header
        hdr = tk.Frame(outer, bg=C["bg"]); hdr.pack(fill="x", padx=20, pady=(16,8))
        Label(hdr, "📖  Editor Pelajaran", font=F["h1"]).pack(anchor="w")

        inner = tk.Frame(outer, bg=C["bg"]); inner.pack(fill="both", expand=True, padx=20)

        # Basic fields row
        row1 = tk.Frame(inner, bg=C["bg"]); row1.pack(fill="x")
        left1 = tk.Frame(row1, bg=C["bg"]); left1.pack(side="left", fill="x", expand=True, padx=(0,12))
        right1 = tk.Frame(row1, bg=C["bg"]); right1.pack(side="left", fill="x")

        SLabel(left1, "Judul Pelajaran *").pack(anchor="w")
        self._title = tk.StringVar(value=lesson.get("title","") if lesson else "")
        Entry(left1, textvariable=self._title).pack(fill="x", pady=(2,0))

        SLabel(right1, "Estimasi (menit)").pack(anchor="w")
        self._mins = tk.StringVar(value=str(lesson.get("estMinutes",10)) if lesson else "10")
        Entry(right1, textvariable=self._mins, width=10).pack(fill="x", pady=(2,0))

        # DSL cheatsheet
        sheet = tk.Frame(inner, bg=C["surface"]); sheet.pack(fill="x", pady=(12,4))
        cheatsheet = [
            ("HEADING:", C["accent2"]),  ("H2:", C["blue"]),
            ("TEXT:", C["text2"]),       ("HIGHLIGHT:", C["pink"]),
            ("LIST:", C["green"]),       ("MATH:", C["yellow"]),
            ("TABLE_HEADER:", C["text3"]),("IMAGE:", C["yellow2"]),
        ]
        for i,(tag, color) in enumerate(cheatsheet):
            tk.Label(sheet, text=tag, bg=C["surface"], fg=color,
                     font=F["monos"], padx=4).grid(row=i//4, column=i%4, sticky="w", padx=2)

        # Content editor
        SLabel(inner, "Konten DSL (satu blok per baris)").pack(anchor="w", pady=(8,2))
        self._editor = Textbox(inner, font=F["mono"], height=18)
        self._editor.pack(fill="both", expand=True)
        self._editor.bind("<KeyRelease>", self._highlight)

        # Syntax tags
        self._editor.tag_configure("kw",     foreground=C["accent2"],  font=(F["mono"][0], F["mono"][1], "bold"))
        self._editor.tag_configure("heading",foreground=C["yellow"],   font=(F["mono"][0], F["mono"][1]+1, "bold"))
        self._editor.tag_configure("list",   foreground=C["green"])
        self._editor.tag_configure("hi",     foreground=C["pink"],     background="#3b0f2c")
        self._editor.tag_configure("math",   foreground=C["yellow2"])
        self._editor.tag_configure("image",  foreground=C["blue"])

        if lesson and lesson.get("content"):
            self._editor.insert("1.0", DSL.dumps(lesson["content"]))
            self._highlight()

        # Toolbar
        toolbar = tk.Frame(inner, bg=C["bg"]); toolbar.pack(fill="x", pady=(8,0))
        Btn(toolbar, "✨ Auto-Format", self._auto_format, "purple", px=10).pack(side="left", padx=2)
        Btn(toolbar, "👁 Preview",     self._preview,     "ghost",  px=10).pack(side="left", padx=2)

        label_info = tk.Label(toolbar, text="Tip: setiap baris = 1 blok konten",
                              bg=C["bg"], fg=C["text3"], font=F["small"])
        label_info.pack(side="right", padx=8)

        self._footer(self._save)

    def _highlight(self, event=None):
        t = self._editor
        for tag in ("kw","heading","list","hi","math","image"):
            t.tag_remove(tag, "1.0", "end")
        for i, line in enumerate(t.get("1.0","end-1c").split("\n")):
            row = i+1
            if ":" not in line: continue
            colon = line.index(":")
            p = line[:colon].strip().upper()
            end = f"{row}.{colon+1}"
            t.tag_add("kw", f"{row}.0", end)
            if any(x in p for x in ("HEADING","H1","H2","H3","H4")):
                t.tag_add("heading", end, f"{row}.end")
            elif "LIST" in p:      t.tag_add("list",  end, f"{row}.end")
            elif "HIGHLIGHT" in p: t.tag_add("hi",    end, f"{row}.end")
            elif "MATH" in p:      t.tag_add("math",  end, f"{row}.end")
            elif p in ("IMAGE","CAPTION"): t.tag_add("image", end, f"{row}.end")

    def _auto_format(self):
        raw = self._editor.get("1.0","end-1c")
        out = []
        for line in raw.split("\n"):
            s = line.strip()
            if not s: out.append(""); continue
            # Already has prefix
            if re.match(r"^[A-Z_]+\s*:", s): out.append(s); continue
            if s.startswith("# "): out.append(f"HEADING: {s[2:]}")
            elif s.startswith("## "): out.append(f"H2: {s[3:]}")
            elif s.startswith("### "): out.append(f"H3: {s[4:]}")
            elif re.match(r"^[-*]\s", s): out.append(f"LIST: {s[2:]}")
            elif re.match(r"^\d+\.\s", s): out.append(f"LIST: {re.sub(r'^\d+\.\s','',s)}")
            elif len(s) < 50 and not s.endswith((".",",","!","?")): out.append(f"H2: {s}")
            else: out.append(f"TEXT: {s}")
        self._editor.delete("1.0","end")
        self._editor.insert("1.0","\n".join(out))
        self._highlight()
        messagebox.showinfo("✨","Teks otomatis diformat ke DSL!", parent=self)

    def _preview(self):
        content = DSL.loads(self._editor.get("1.0","end-1c"))
        pw = tk.Toplevel(self); pw.title("Preview"); pw.geometry("520x600"); pw.configure(bg=C["bg"])
        tk.Frame(pw, bg=C["accent"], height=4).pack(fill="x")
        Label(pw, "📖 Preview Konten", font=F["h1"]).pack(pady=12)
        txt = Textbox(pw); txt.pack(fill="both", expand=True, padx=16, pady=8)
        txt.tag_configure("h1", foreground=C["accent2"], font=(F["body"][0], 14, "bold"))
        txt.tag_configure("h2", foreground=C["blue"],    font=(F["body"][0], 11, "bold"))
        txt.tag_configure("hi", foreground=C["pink"],    background="#2d0a22")
        txt.tag_configure("li", foreground=C["green"])
        for item in content:
            t = item.get("type","text")
            if t == "heading":
                lvl = item.get("level",1)
                tag = "h1" if lvl==1 else "h2"
                txt.insert("end", f"\n{'  '*(lvl-1)}{item.get('text','')}\n", tag)
            elif t == "text":
                txt.insert("end", f"\n{item.get('text','')}\n")
            elif t == "highlight":
                txt.insert("end", f"\n★ {item.get('text','')}\n", "hi")
            elif t == "list":
                for it in item.get("items",[]):
                    txt.insert("end", f"  • {it}\n", "li")
                txt.insert("end","\n")
            elif t == "table":
                txt.insert("end", f"┌ {' | '.join(item.get('headers',[]))} ┐\n")
                for row in item.get("rows",[]):
                    txt.insert("end", f"│ {' | '.join(str(c) for c in row)} │\n")
                txt.insert("end","\n")
            elif t == "math":
                txt.insert("end", f"\n∑ {item.get('tex','')}\n")
        txt.config(state="disabled")

    def _save(self):
        title = self._title.get().strip()
        if not title: messagebox.showwarning("Perhatian","Judul wajib diisi!",parent=self); return
        try: mins = int(self._mins.get())
        except: mins = 10
        self.result = {
            "id": slugify(title), "title": title,
            "estMinutes": mins,
            "content": DSL.loads(self._editor.get("1.0","end-1c"))
        }
        self.destroy()


class FlashcardDialog(BaseDialog):
    def __init__(self, parent, cards=None):
        super().__init__(parent, "🃏  Flashcard", 680, 640)
        self._cards = deep(cards) if cards else []
        self._build(); self.wait_window()

    def _build(self):
        tk.Frame(self, bg=C["green"], height=4).pack(fill="x")

        hdr = tk.Frame(self, bg=C["bg"]); hdr.pack(fill="x", padx=20, pady=12)
        Label(hdr, "🃏  Kelola Flashcard", font=F["h1"]).pack(side="left")
        self._count_lbl = Label(hdr, "0 kartu", fg=C["text3"], font=F["small"])
        self._count_lbl.pack(side="left", padx=10)

        # Scroll area for cards
        outer = tk.Frame(self, bg=C["bg"]); outer.pack(fill="both", expand=True, padx=16)
        canvas = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self._sf = tk.Frame(canvas, bg=C["bg"])
        self._sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self._sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._canvas = canvas

        self._refresh_cards()

        # Add panel
        add = Card(self); add.pack(fill="x", padx=16, pady=(4,0))
        tk.Frame(add, bg=C["card"]).pack(fill="x", padx=12, pady=(8,4))

        qrow = tk.Frame(add, bg=C["card"]); qrow.pack(fill="x", padx=12)
        Label(qrow, "Pertanyaan:", fg=C["text3"], font=F["small"]).pack(anchor="w")
        self._nq = Textbox(add, height=2); self._nq.pack(fill="x", padx=12, pady=2)
        Label(add, "Jawaban:", bg=C["card"], fg=C["text3"], font=F["small"]).pack(padx=12, anchor="w")
        self._na = Textbox(add, height=2); self._na.pack(fill="x", padx=12, pady=(2,4))

        btn_row = tk.Frame(add, bg=C["card"]); btn_row.pack(fill="x", padx=12, pady=8)
        Btn(btn_row, "⚡ Bulk Add", self._bulk, "purple", px=10).pack(side="left", padx=4)
        Btn(btn_row, "＋  Tambah Kartu", self._add_one, "green", px=10).pack(side="right", padx=4)

        self._footer(self._save)

    def _refresh_cards(self):
        for w in self._sf.winfo_children(): w.destroy()
        for i, card in enumerate(self._cards):
            self._card_row(i, card)
        self._count_lbl.config(text=f"{len(self._cards)} kartu")

    def _card_row(self, idx, card):
        row = Card(self._sf); row.pack(fill="x", pady=2, padx=2)
        hdr = tk.Frame(row, bg=C["card"]); hdr.pack(fill="x", padx=10, pady=(6,2))
        Label(hdr, f"#{idx+1}", bg=C["card"], fg=C["accent"], font=F["small"]).pack(side="left")
        Btn(hdr, "✕", lambda i=idx: self._del(i), "red", px=6, py=2).pack(side="right")
        Label(row, "Q:", bg=C["card"], fg=C["text3"], font=F["small"]).pack(padx=10, anchor="w")
        qw = Textbox(row, height=2, bg=C["raised"]); qw.pack(fill="x", padx=10, pady=2)
        qw.insert("1.0", card.get("question",""))
        Label(row, "A:", bg=C["card"], fg=C["text3"], font=F["small"]).pack(padx=10, anchor="w")
        aw = Textbox(row, height=2, bg=C["raised"]); aw.pack(fill="x", padx=10, pady=(2,8))
        aw.insert("1.0", card.get("answer",""))
        card["_q"] = qw; card["_a"] = aw

    def _add_one(self):
        q = self._nq.get("1.0","end-1c").strip()
        a = self._na.get("1.0","end-1c").strip()
        if not q or not a:
            messagebox.showwarning("Perhatian","Q dan A wajib diisi!",parent=self); return
        self._cards.append({"id":f"fc{len(self._cards)+1}","question":q,"answer":a})
        self._nq.delete("1.0","end"); self._na.delete("1.0","end")
        self._refresh_cards()
        self._canvas.update_idletasks(); self._canvas.yview_moveto(1.0)

    def _del(self, idx):
        del self._cards[idx]; self._refresh_cards()

    def _bulk(self):
        dlg = tk.Toplevel(self); dlg.title("Bulk Add"); dlg.geometry("480x420")
        dlg.configure(bg=C["bg"])
        tk.Frame(dlg, bg=C["green"], height=4).pack(fill="x")
        Label(dlg, "Format: Pertanyaan = Jawaban  (satu per baris)", fg=C["text3"], font=F["small"]
              ).pack(pady=10, padx=20, anchor="w")
        txt = Textbox(dlg, height=14); txt.pack(fill="both", expand=True, padx=20, pady=4)
        sample = "Apa itu sel? = Unit terkecil kehidupan\nRumus air = H₂O"
        Label(dlg, f"Contoh:\n{sample}", fg=C["text4"], font=F["monos"], justify="left"
              ).pack(padx=20, anchor="w", pady=4)

        def go():
            raw = txt.get("1.0","end-1c"); count = 0
            for line in raw.split("\n"):
                if "=" in line:
                    q,_,a = line.partition("=")
                    self._cards.append({"id":f"fc{len(self._cards)+1}",
                                        "question":q.strip(),"answer":a.strip()})
                    count += 1
            self._refresh_cards(); dlg.destroy()
            messagebox.showinfo("Bulk Add",f"✓ {count} kartu ditambahkan!",parent=self)
        Btn(dlg, f"Import", go, "green").pack(pady=12)

    def _save(self):
        saved = []
        for card in self._cards:
            q = card["_q"].get("1.0","end-1c").strip() if "_q" in card else card.get("question","")
            a = card["_a"].get("1.0","end-1c").strip() if "_a" in card else card.get("answer","")
            saved.append({"id":card.get("id",f"fc{len(saved)+1}"),
                          "question":q,"answer":a})
        self.result = saved; self.destroy()


class QuizDialog(BaseDialog):
    def __init__(self, parent, questions=None):
        super().__init__(parent, "📝  Editor Kuis", 740, 700)
        self._questions = deep(questions) if questions else []
        self._qframes = []
        self._build(); self.wait_window()

    def _build(self):
        tk.Frame(self, bg=C["yellow"], height=4).pack(fill="x")
        hdr = tk.Frame(self, bg=C["bg"]); hdr.pack(fill="x", padx=20, pady=12)
        Label(hdr, "📝  Editor Soal Kuis", font=F["h1"]).pack(side="left")
        self._count_lbl = Label(hdr, "0 soal", fg=C["text3"], font=F["small"])
        self._count_lbl.pack(side="left", padx=10)

        # Scroll area
        outer = tk.Frame(self, bg=C["bg"]); outer.pack(fill="both", expand=True, padx=16)
        canvas = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self._sf = tk.Frame(canvas, bg=C["bg"])
        self._sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self._sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set); canvas.pack(side="left",fill="both",expand=True); sb.pack(side="right",fill="y")
        self._canvas = canvas

        for i,q in enumerate(self._questions): self._q_row(i,q)
        Btn(self._sf, "＋  Tambah Soal Baru", self._add, "green").pack(pady=12, padx=8)
        self._update_count()
        self._footer(self._save)

    def _q_row(self, idx, q):
        card = Card(self._sf); card.pack(fill="x", pady=4, padx=4)
        hdr = tk.Frame(card, bg=C["card"]); hdr.pack(fill="x", padx=12, pady=(8,4))
        Label(hdr, f"Soal #{idx+1}", bg=C["card"], fg=C["yellow"], font=F["h2"]).pack(side="left")
        Btn(hdr, "✕ Hapus", lambda i=idx: self._del(i), "red", px=8, py=2).pack(side="right")

        Label(card, "Pertanyaan:", bg=C["card"], fg=C["text3"], font=F["small"]).pack(padx=12, anchor="w")
        qt = Textbox(card, height=3, bg=C["raised"]); qt.pack(fill="x", padx=12, pady=(2,6))
        qt.insert("1.0", q.get("question",""))

        opts = []
        for j in range(4):
            r = tk.Frame(card, bg=C["card"]); r.pack(fill="x", padx=12, pady=1)
            c = "ABCD"[j]
            lbl_color = [C["blue"], C["green"], C["yellow"], C["pink"]][j]
            tk.Label(r, text=c, bg=C["card"], fg=lbl_color, font=F["h2"], width=2).pack(side="left")
            e = Entry(r, bg=C["raised"]); e.pack(side="left", fill="x", expand=True)
            options = q.get("options",["","","",""])
            if j < len(options): e.insert(0, options[j])
            opts.append(e)

        meta = tk.Frame(card, bg=C["card"]); meta.pack(fill="x", padx=12, pady=(6,4))
        Label(meta, "Jawaban benar:", bg=C["card"], fg=C["text3"], font=F["small"]).pack(side="left")
        ans_v = tk.StringVar(value=str(q.get("answer",0)))
        combo = ttk.Combobox(meta, textvariable=ans_v,
                             values=["0 — A","1 — B","2 — C","3 — D"],
                             width=12, state="readonly")
        combo.pack(side="left", padx=8)
        Label(meta, "Penjelasan:", bg=C["card"], fg=C["text3"], font=F["small"]).pack(side="left", padx=(16,4))
        exp = Entry(meta, bg=C["raised"]); exp.pack(side="left", fill="x", expand=True)
        exp.insert(0, q.get("explanation",""))

        self._qframes.append({"qt":qt,"opts":opts,"ans":ans_v,"exp":exp,"id":q.get("id",f"q{idx+1}")})

    def _add(self):
        nq = {"id":f"q{len(self._questions)+1}","type":"multiple_choice",
              "question":"","options":["","","",""],"answer":0,"explanation":""}
        self._questions.append(nq)
        # Remove add button, add row, re-add button
        for w in self._sf.winfo_children():
            if isinstance(w, tk.Button): w.destroy()
        self._q_row(len(self._qframes)-1+1, nq)
        Btn(self._sf, "＋  Tambah Soal Baru", self._add, "green").pack(pady=12, padx=8)
        self._update_count()
        self._canvas.update_idletasks(); self._canvas.yview_moveto(1.0)

    def _del(self, idx):
        del self._questions[idx]; self._qframes = []
        for w in self._sf.winfo_children(): w.destroy()
        for i,q in enumerate(self._questions): self._q_row(i,q)
        Btn(self._sf,"＋  Tambah Soal Baru",self._add,"green").pack(pady=12,padx=8)
        self._update_count()

    def _update_count(self):
        self._count_lbl.config(text=f"{len(self._questions)} soal")

    def _save(self):
        saved = []
        for f in self._qframes:
            ans_raw = f["ans"].get().split(" ")[0]
            try: ans = int(ans_raw)
            except: ans = 0
            saved.append({"id":f["id"],"type":"multiple_choice",
                           "question":f["qt"].get("1.0","end-1c").strip(),
                           "options":[e.get().strip() for e in f["opts"]],
                           "answer":ans,"explanation":f["exp"].get().strip()})
        self.result = saved; self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  AI MODE WINDOW  (no API — pure prompt generator + paste-back parser)
# ══════════════════════════════════════════════════════════════════════════════
class AIModeWindow(tk.Toplevel):
    """
    Three-step workflow:
      1. Choose topic + action → Generate Prompt
      2. Copy prompt → paste into ChatGPT / Claude / Gemini
      3. Paste AI response back → Parse & Apply
    """
    def __init__(self, parent, data, apply_cb):
        super().__init__(parent)
        self.title("🤖  AI Content Studio")
        self.configure(bg=C["bg"])
        self.geometry("1180x860")
        self.minsize(900, 700)
        self._data = data
        self._apply_cb = apply_cb
        self._style_ttk()
        self._build()
        self.transient(parent)
        self.grab_set()

    def _style_ttk(self):
        s = ttk.Style(self)
        s.configure("TCombobox", fieldbackground=C["raised"], background=C["raised"],
                     foreground=C["text"])

    def _build(self):
        # Accent stripe
        tk.Frame(self, bg=C["accent"], height=4).pack(fill="x")

        # ── Title bar ──
        bar = tk.Frame(self, bg=C["surface"]); bar.pack(fill="x")
        tk.Label(bar, text="🤖  AI Content Studio", bg=C["surface"], fg=C["accent2"],
                 font=F["title"], pady=14, padx=24).pack(side="left")
        tk.Label(bar, text="No API key needed — copy prompt → paste into any AI → import result",
                 bg=C["surface"], fg=C["text3"], font=F["small"]).pack(side="left", padx=4)
        Btn(bar, "✕ Tutup", self.destroy, "ghost", px=10).pack(side="right", padx=16)

        # ── Body (3-column) ──
        body = tk.Frame(self, bg=C["bg"]); body.pack(fill="both", expand=True, padx=20, pady=16)

        # ── STEP 1 ──
        self._col1 = self._step_col(body, "1", "Setup & Generate Prompt", C["accent"])
        self._col1.pack(side="left", fill="both", expand=False, padx=(0,8), ipadx=4)
        self._build_step1()

        # ── Separator ──
        sep1 = tk.Frame(body, bg=C["border"], width=2); sep1.pack(side="left", fill="y", padx=4)

        # ── STEP 2 (prompt output) ──
        self._col2 = self._step_col(body, "2", "Generated Prompt", C["blue"])
        self._col2.pack(side="left", fill="both", expand=True, padx=4)
        self._build_step2()

        # ── Separator ──
        sep2 = tk.Frame(body, bg=C["border"], width=2); sep2.pack(side="left", fill="y", padx=4)

        # ── STEP 3 ──
        self._col3 = self._step_col(body, "3", "Paste AI Response & Apply", C["green"])
        self._col3.pack(side="left", fill="both", expand=True, padx=(8,0))
        self._build_step3()

    def _step_col(self, parent, num, label, color):
        """Returns the content frame of a step column."""
        outer = tk.Frame(parent, bg=C["surface"])
        # Colored top stripe
        tk.Frame(outer, bg=color, height=3).pack(fill="x")
        header = tk.Frame(outer, bg=C["surface"]); header.pack(fill="x", padx=12, pady=(10,6))
        circle = tk.Label(header, text=f" {num} ", bg=color, fg=C["white"],
                           font=F["h2"], padx=2)
        circle.pack(side="left")
        tk.Label(header, text=label, bg=C["surface"], fg=C["text"],
                 font=F["h2"]).pack(side="left", padx=8)
        content = tk.Frame(outer, bg=C["surface"]); content.pack(fill="both", expand=True, padx=12, pady=8)
        outer._content = content
        return outer

    def _build_step1(self):
        f = self._col1._content

        topics = self._data.get("topics", [])
        topic_names = [t.get("title","?") for t in topics]

        SLabel(f, "Topik").pack(anchor="w", pady=(4,2))
        self._topic_var = tk.StringVar(value=topic_names[0] if topic_names else "")
        ttk.Combobox(f, textvariable=self._topic_var, values=topic_names,
                     width=32, state="readonly").pack(fill="x")

        SLabel(f, "Aksi AI").pack(anchor="w", pady=(12,2))
        self._action_var = tk.StringVar()
        actions = [(v[0], k) for k,v in PromptKit.ACTIONS.items()]
        self._action_map = {v[0]: k for k,v in PromptKit.ACTIONS.items()}
        ttk.Combobox(f, textvariable=self._action_var,
                     values=[a[0] for a in actions],
                     width=32, state="readonly").pack(fill="x")
        self._action_var.set(actions[0][0])

        tk.Frame(f, bg=C["border"], height=1).pack(fill="x", pady=12)

        # Info panel
        info = Card(f, bg=C["card"]); info.pack(fill="x", pady=4)
        Label(info, "Cara Pakai:", fg=C["accent2"], font=F["h2"]).pack(anchor="w", padx=12, pady=(10,4))
        steps = [
            "① Pilih topik & aksi lalu klik Generate",
            "② Salin prompt ke ChatGPT / Claude / Gemini",
            "③ Tempel respons AI di kolom kanan",
            "④ Klik Apply — data otomatis tersimpan",
        ]
        for s in steps:
            Label(info, s, fg=C["text2"], font=F["small"]).pack(anchor="w", padx=16, pady=2)
        Label(info, "", bg=C["card"]).pack(pady=4)

        # AI suggestions
        Label(f, "Rekomendasi AI:", fg=C["text3"], font=F["small"]).pack(anchor="w", pady=(8,2))
        ais = [
            ("ChatGPT 4o",  C["green"]),
            ("Claude 3.7",  C["accent2"]),
            ("Gemini 1.5",  C["blue"]),
        ]
        row = tk.Frame(f, bg=C["surface"]); row.pack(fill="x")
        for name, color in ais:
            tk.Label(row, text=f"● {name}", bg=C["surface"], fg=color,
                     font=F["small"]).pack(side="left", padx=6)

        tk.Frame(f, bg=C["surface"]).pack(fill="both", expand=True)

        Btn(f, "🚀  Generate Prompt", self._generate, "primary").pack(fill="x", pady=(8,0))

    def _build_step2(self):
        f = self._col2._content
        SLabel(f, "Prompt siap-salin untuk AI").pack(anchor="w", pady=(4,2))
        self._prompt_out = Textbox(f, font=F["monos"], wrap="word")
        self._prompt_out.pack(fill="both", expand=True)

        # Placeholder
        self._prompt_out.insert("1.0", "← Klik 'Generate Prompt' untuk memulai...")
        self._prompt_out.config(fg=C["text4"])

        bar = tk.Frame(f, bg=C["surface"]); bar.pack(fill="x", pady=(8,0))
        Btn(bar, "📋 Salin Semua", self._copy_prompt, "outline").pack(side="left")
        self._char_lbl = Label(bar, "0 karakter", fg=C["text4"], font=F["small"])
        self._char_lbl.pack(side="right")

    def _build_step3(self):
        f = self._col3._content

        # Target selector
        top_row = tk.Frame(f, bg=C["surface"]); top_row.pack(fill="x")
        SLabel(top_row, "Terapkan ke Topik").pack(side="left", pady=(4,2))
        topics = self._data.get("topics", [])
        topic_names = [t.get("title","?") for t in topics]
        self._target_var = tk.StringVar(value=topic_names[0] if topic_names else "")
        ttk.Combobox(top_row, textvariable=self._target_var, values=topic_names,
                     width=22, state="readonly").pack(side="right", pady=(4,2))

        SLabel(f, "Tempel respons AI di sini (DSL format)").pack(anchor="w", pady=(8,2))
        self._resp_in = Textbox(f, font=F["monos"])
        self._resp_in.pack(fill="both", expand=True)
        self._resp_in.bind("<KeyRelease>", self._on_resp_change)

        # Parse preview
        self._parse_lbl = Label(f, "Menunggu input...", fg=C["text4"], font=F["small"])
        self._parse_lbl.pack(anchor="w", pady=(4,0))

        bar = tk.Frame(f, bg=C["surface"]); bar.pack(fill="x", pady=(8,0))
        Btn(bar, "🗑 Bersihkan",   self._clear_resp, "ghost",  px=8).pack(side="left", padx=2)
        Btn(bar, "🔍 Validasi DSL", self._validate,   "outline",px=8).pack(side="left", padx=2)
        Btn(bar, "⚡  Apply & Simpan", self._apply, "green").pack(side="right")

    # ── Step 1 actions ──
    def _generate(self):
        topic_name = self._topic_var.get()
        action_label = self._action_var.get()
        action_key = self._action_map.get(action_label, "enhance")
        subject = self._data.get("name", "IPA")

        topic = next((t for t in self._data.get("topics",[])
                      if t.get("title") == topic_name), None)

        if topic is None and action_key != "from_zero":
            messagebox.showerror("Error","Pilih topik terlebih dahulu!",parent=self); return

        if action_key == "from_zero":
            prompt = PromptKit.quick_build(topic_name or "Topik Baru", subject)
        else:
            prompt = PromptKit.build(action_key, topic, subject)

        # Update prompt output
        self._prompt_out.config(fg=C["text"])
        self._prompt_out.delete("1.0","end")
        self._prompt_out.insert("1.0", prompt)
        self._char_lbl.config(text=f"{len(prompt):,} karakter")

        # Auto-sync target
        if topic_name:
            self._target_var.set(topic_name)

        Toast.show(self.master, "Prompt siap! Salin ke AI kamu.", "ok")

    def _copy_prompt(self):
        txt = self._prompt_out.get("1.0","end-1c")
        if txt.startswith("←"): return
        self.clipboard_clear(); self.clipboard_append(txt)
        Toast.show(self.master, "Prompt disalin ke clipboard!", "ok")

    # ── Step 3 actions ──
    def _on_resp_change(self, event=None):
        raw = self._resp_in.get("1.0","end-1c").strip()
        if not raw:
            self._parse_lbl.config(text="Menunggu input...", fg=C["text4"]); return
        lines = raw.split("\n")
        has_lesson   = any("--- LESSON:" in l for l in lines)
        has_fc       = "=== FLASHCARDS ===" in raw
        has_quiz     = "=== QUIZ ===" in raw
        has_topic    = any("TOPIC_TITLE:" in l for l in lines)
        parts = []
        if has_topic:    parts.append("Topik")
        if has_lesson:   parts.append(f"{sum(1 for l in lines if '--- LESSON:' in l)} Pelajaran")
        if has_fc:       parts.append("Flashcard")
        if has_quiz:     parts.append("Quiz")
        if parts:
            self._parse_lbl.config(text="✓ Terdeteksi: " + ", ".join(parts), fg=C["green"])
        else:
            self._parse_lbl.config(text="⚠ Format belum dikenali — coba validasi", fg=C["yellow"])

    def _clear_resp(self):
        self._resp_in.delete("1.0","end")
        self._parse_lbl.config(text="Menunggu input...", fg=C["text4"])

    def _validate(self):
        raw = self._resp_in.get("1.0","end-1c").strip()
        if not raw: messagebox.showinfo("Validasi","Input kosong!",parent=self); return
        raw = self._clean_dsl(raw)
        try:
            result = TopicDSL.decode(raw)
            n_ls  = len(result.get("lessons",[]))
            n_fc  = len(result.get("flashcards",[]))
            n_q   = len(result.get("quiz",{}).get("questions",[]))
            msg = (f"✓ DSL valid!\n\n"
                   f"Topik: {result.get('title','?')}\n"
                   f"Pelajaran: {n_ls}\nFlashcard: {n_fc}\nSoal: {n_q}")
            messagebox.showinfo("Validasi DSL", msg, parent=self)
        except Exception as e:
            messagebox.showerror("Validasi Gagal", f"Gagal parse:\n{e}", parent=self)

    def _clean_dsl(self, raw: str) -> str:
        """Strip markdown fences, preamble, conversational text."""
        raw = re.sub(r"```[a-zA-Z]*\n?", "", raw)
        raw = raw.replace("```","")
        raw = re.sub(r"^DATA DSL:\s*\n?","", raw, flags=re.MULTILINE)
        # Try to find first DSL token
        known = ["TOPIC_TITLE:","--- LESSON:","=== FLASHCARDS ===","=== QUIZ ==="]
        start = -1
        for tok in known:
            idx = raw.find(tok)
            if idx != -1 and (start == -1 or idx < start):
                start = idx
        return raw[start:].strip() if start != -1 else raw

    def _apply(self):
        raw = self._resp_in.get("1.0","end-1c").strip()
        if not raw:
            messagebox.showwarning("Error","Tidak ada input untuk diproses!",parent=self); return

        raw = self._clean_dsl(raw)
        try:
            parsed = TopicDSL.decode(raw)
        except Exception as e:
            messagebox.showerror("Parse Error", f"Gagal memproses:\n{e}", parent=self); return

        if not parsed:
            messagebox.showerror("Error","Tidak ada data yang bisa diparsing!",parent=self); return

        target_name = self._target_var.get()
        topics = self._data.get("topics", [])
        target = next((t for t in topics if t.get("title") == target_name), None)

        if target:
            self._apply_cb("full_topic_update", target.get("id"), parsed)
            messagebox.showinfo("✓ Berhasil",
                                f"Topik '{target_name}' diperbarui & disimpan!\n"
                                f"({len(parsed.get('lessons',[]))} pelajaran, "
                                f"{len(parsed.get('flashcards',[]))} flashcard, "
                                f"{len(parsed.get('quiz',{}).get('questions',[]))} soal)",
                                parent=self)
        else:
            self._apply_cb("topic", None, parsed)
            messagebox.showinfo("✓ Berhasil",
                                f"Topik baru '{parsed.get('title','?')}' ditambahkan!",
                                parent=self)

        self._clear_resp()
        Toast.show(self.master, "AI content berhasil diapply!", "ok")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✏️  Subject JSON Editor  —  Polaris")
        self.geometry("1340x820")
        self.minsize(960, 600)
        self.configure(bg=C["bg"])

        self._data: dict = {"id":"subject","name":"Subject","description":"",
                            "grade":[7,8,9],"icon":"Book","color":"soft","topics":[]}
        self._filepath: str | None = None
        self._unsaved = False
        self._sel_idx: int | None = None
        self._undo = UndoStack()

        self._style_ttk()
        self._build_ui()
        self._setup_hotkeys()
        self._load_subject_list()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── TTK theme ─────────────────────────────────────────────────────────────
    def _style_ttk(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview", background=C["card"], fieldbackground=C["card"],
                     foreground=C["text"], font=F["body"], rowheight=38, borderwidth=0)
        s.configure("Treeview.Heading", background=C["surface"], foreground=C["text3"],
                     font=F["tiny"], borderwidth=0, relief="flat")
        s.map("Treeview",
              background=[("selected", C["accent"])],
              foreground=[("selected","#fff")])
        s.configure("TNotebook", background=C["bg"], borderwidth=0)
        s.configure("TNotebook.Tab", background=C["surface"], foreground=C["text3"],
                     font=F["small"], padding=[14,7])
        s.map("TNotebook.Tab",
              background=[("selected", C["card"])],
              foreground=[("selected", C["accent2"])])
        s.configure("TCombobox", fieldbackground=C["raised"], background=C["raised"],
                     foreground=C["text"])
        s.configure("Vertical.TScrollbar", background=C["surface"],
                     troughcolor=C["bg"], borderwidth=0, relief="flat")
        s.configure("Horizontal.TScrollbar", background=C["surface"],
                     troughcolor=C["bg"], borderwidth=0, relief="flat")
        s.configure("TSeparator", background=C["border"])

    # ── Keyboard shortcuts ───────────────────────────────────────────────────
    def _setup_hotkeys(self):
        self.bind("<Control-s>",      lambda e: self._save())
        self.bind("<Control-S>",      lambda e: self._save_as())
        self.bind("<Control-n>",      lambda e: self._add_topic())
        self.bind("<Control-f>",      lambda e: (self._search_var.set(""), self._search_ent.focus_set()))
        self.bind("<Control-z>",      lambda e: self._do_undo())
        self.bind("<Control-y>",      lambda e: self._do_redo())
        self.bind("<Control-d>",      lambda e: self._duplicate_topic())
        self.bind("<F5>",             lambda e: self._refresh_tree())

    # ── UI Layout ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Top accent stripe
        tk.Frame(self, bg=C["accent"], height=3).pack(fill="x")

        self._build_toolbar()

        main = tk.PanedWindow(self, orient="horizontal", bg=C["bg"],
                               sashwidth=5, sashrelief="flat", sashpad=0)
        main.pack(fill="both", expand=True)

        left = tk.Frame(main, bg=C["surface"], width=290)
        main.add(left, minsize=220)
        self._build_sidebar(left)

        right = tk.Frame(main, bg=C["bg"])
        main.add(right, minsize=600)
        self._build_detail(right)

        self._build_statusbar()

    # ── Toolbar ───────────────────────────────────────────────────────────────
    def _build_toolbar(self):
        tb = tk.Frame(self, bg=C["surface"], height=54)
        tb.pack(fill="x"); tb.pack_propagate(False)

        # Logo
        tk.Label(tb, text="✏️", bg=C["surface"], font=("Segoe UI", 18)).pack(side="left", padx=(16,4), pady=10)
        tk.Label(tb, text="JSON Editor", bg=C["surface"], fg=C["accent2"],
                 font=F["h1"]).pack(side="left", pady=10)

        tk.Frame(tb, bg=C["border"], width=1).pack(side="left", fill="y", pady=8, padx=12)

        # Subject selector
        tk.Label(tb, text="Pelajaran:", bg=C["surface"], fg=C["text3"], font=F["small"]).pack(side="left", padx=(0,4))
        self._subject_var = tk.StringVar()
        self._subject_cb  = ttk.Combobox(tb, textvariable=self._subject_var, width=18, state="readonly")
        self._subject_cb.pack(side="left", pady=14)
        self._subject_cb.bind("<<ComboboxSelected>>", self._on_subject_change)

        tk.Frame(tb, bg=C["border"], width=1).pack(side="left", fill="y", pady=8, padx=8)

        actions = [
            ("⚙️ Info",      self._edit_info,    "ghost"),
            ("🔍 Cari",      self._global_search,"ghost"),
            ("↩ Undo",       self._do_undo,       "ghost"),
            ("↪ Redo",       self._do_redo,       "ghost"),
            ("💾 Simpan",    self._save,          "outline"),
            ("🤖 AI Studio", self._open_ai,       "purple"),
        ]
        for lbl, cmd, sty in actions:
            Btn(tb, lbl, cmd, sty, py=4).pack(side="left", padx=3, pady=12)

        # File path label
        self._file_lbl = tk.Label(tb, text="Belum ada file", bg=C["surface"],
                                   fg=C["text4"], font=F["tiny"])
        self._file_lbl.pack(side="right", padx=16)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self, parent):
        # Header
        hdr = tk.Frame(parent, bg=C["surface"]); hdr.pack(fill="x", padx=12, pady=(10,6))
        Label(hdr, "📚  Topik", bg=C["surface"], font=F["h2"]).pack(side="left")
        self._topic_count = Label(hdr, "0 topik", bg=C["surface"],
                                   fg=C["text3"], font=F["small"])
        self._topic_count.pack(side="right")

        # Search
        sf = tk.Frame(parent, bg=C["surface"]); sf.pack(fill="x", padx=12, pady=(0,8))
        tk.Label(sf, text="🔍", bg=C["surface"], fg=C["text3"], font=F["small"]).pack(side="left")
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *a: self._refresh_tree())
        self._search_ent = Entry(sf, textvariable=self._search_var, width=22)
        self._search_ent.pack(side="left", fill="x", expand=True, padx=4)
        Btn(sf, "✕", lambda: self._search_var.set(""), "ghost", px=5, py=2).pack(side="left")

        # Treeview
        tree_f = tk.Frame(parent, bg=C["surface"]); tree_f.pack(fill="both", expand=True, padx=8)
        self._tree = ttk.Treeview(tree_f, show="tree", selectmode="browse")
        sb = ttk.Scrollbar(tree_f, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._tree.bind("<<TreeviewSelect>>", self._on_select)
        self._tree.bind("<Double-1>", lambda e: self._edit_topic())

        # Context menu
        self._ctx = tk.Menu(self, tearoff=0, bg=C["card"], fg=C["text"],
                             activebackground=C["accent"], activeforeground=C["white"],
                             font=F["body"], bd=0)
        self._ctx.add_command(label="✏️  Edit Topik",        command=self._edit_topic)
        self._ctx.add_command(label="📋  Duplikat Topik",    command=self._duplicate_topic)
        self._ctx.add_separator()
        self._ctx.add_command(label="⬆  Pindah ke Atas",    command=self._move_up)
        self._ctx.add_command(label="⬇  Pindah ke Bawah",   command=self._move_down)
        self._ctx.add_separator()
        self._ctx.add_command(label="🗑  Hapus Topik",       command=self._del_topic)
        self._tree.bind("<Button-3>", self._show_ctx)

        # Bottom buttons
        bot = tk.Frame(parent, bg=C["surface"]); bot.pack(fill="x", padx=10, pady=10)
        Btn(bot, "＋",     self._add_topic,      "green",   px=10, py=4).pack(side="left", padx=2)
        Btn(bot, "✏️",     self._edit_topic,     "ghost",   px=10, py=4).pack(side="left", padx=2)
        Btn(bot, "⬆",      self._move_up,        "ghost",   px=8,  py=4).pack(side="left", padx=2)
        Btn(bot, "⬇",      self._move_down,      "ghost",   px=8,  py=4).pack(side="left", padx=2)
        Btn(bot, "🗑",     self._del_topic,      "red",     px=10, py=4).pack(side="right", padx=2)

    # ── Detail panel ─────────────────────────────────────────────────────────
    def _build_detail(self, parent):
        self._nb = ttk.Notebook(parent)
        self._nb.pack(fill="both", expand=True, padx=6, pady=6)

        for tab_id, label, builder in [
            ("info",    "  ℹ️  Info  ",       self._build_tab_info),
            ("lesson",  "  📖  Pelajaran  ",  self._build_tab_lesson),
            ("fc",      "  🃏  Flashcard  ",  self._build_tab_fc),
            ("quiz",    "  📝  Kuis  ",       self._build_tab_quiz),
            ("raw",     "  { } Raw JSON  ",   self._build_tab_raw),
        ]:
            frame = tk.Frame(self._nb, bg=C["bg"])
            self._nb.add(frame, text=label)
            setattr(self, f"_tab_{tab_id}", frame)
            builder(frame)

    # ── Tab: Info ─────────────────────────────────────────────────────────────
    def _build_tab_info(self, parent):
        self._info_host = tk.Frame(parent, bg=C["bg"])
        self._info_host.pack(fill="both", expand=True)
        self._show_dashboard()

    def _show_dashboard(self):
        for w in self._info_host.winfo_children(): w.destroy()
        host = self._info_host

        # Header
        hdr = tk.Frame(host, bg=C["bg"]); hdr.pack(fill="x", padx=24, pady=(20,12))
        name = self._data.get("name","Dashboard")
        tk.Label(hdr, text=f"📊  {name}", bg=C["bg"], fg=C["accent2"],
                 font=F["title"]).pack(side="left")
        tk.Label(hdr, text=datetime.now().strftime("%A, %d %B %Y"),
                 bg=C["bg"], fg=C["text3"], font=F["small"]).pack(side="right")

        # Stats row
        topics = self._data.get("topics",[])
        n_ls  = sum(len(t.get("lessons",[])) for t in topics)
        n_fc  = sum(len(t.get("flashcards",[])) for t in topics)
        n_q   = sum(len(t.get("quiz",{}).get("questions",[])) for t in topics)

        stats_row = tk.Frame(host, bg=C["bg"]); stats_row.pack(fill="x", padx=24)
        stat_defs = [
            ("📚", len(topics), "Topik",       C["accent"]),
            ("📖", n_ls,        "Pelajaran",   C["blue"]),
            ("🃏", n_fc,        "Flashcard",   C["green"]),
            ("📝", n_q,         "Soal Kuis",   C["yellow"]),
        ]
        for icon, count, label, color in stat_defs:
            card = Card(stats_row); card.pack(side="left", padx=6, fill="both", expand=True)
            tk.Label(card, text=icon,  bg=C["card"], fg=color,   font=("Segoe UI",22)).pack(pady=(16,2))
            tk.Label(card, text=str(count), bg=C["card"], fg=C["text"], font=F["h1"]).pack()
            tk.Label(card, text=label, bg=C["card"], fg=C["text3"], font=F["small"]).pack(pady=(0,16))

        # Quick actions
        qa = tk.Frame(host, bg=C["bg"]); qa.pack(fill="x", padx=24, pady=20)
        Label(qa, "Aksi Cepat:", fg=C["text3"], font=F["small"]).pack(anchor="w", pady=(0,8))
        btns = tk.Frame(qa, bg=C["bg"]); btns.pack(anchor="w")
        Btn(btns, "＋ Topik Baru  (Ctrl+N)", self._add_topic, "green").pack(side="left", padx=4)
        Btn(btns, "🤖 AI Studio",            self._open_ai,  "purple").pack(side="left", padx=4)
        Btn(btns, "🔍 Global Search",         self._global_search, "ghost").pack(side="left", padx=4)

        # Recent topics list
        if topics:
            Label(host, "Semua Topik:", fg=C["text3"], font=F["small"]).pack(padx=24, anchor="w", pady=(8,4))
            for t in topics[:8]:
                row = tk.Frame(host, bg=C["bg"]); row.pack(fill="x", padx=24, pady=2)
                n_fc = len(t.get("flashcards",[]))
                n_q  = len(t.get("quiz",{}).get("questions",[]))
                tk.Label(row, text=f"  {t.get('title','?')}", bg=C["bg"],
                         fg=C["text"], font=F["body"]).pack(side="left")
                tk.Label(row, text=f"{n_fc}🃏  {n_q}📝",
                         bg=C["bg"], fg=C["text3"], font=F["small"]).pack(side="right")

    # ── Tab: Pelajaran ────────────────────────────────────────────────────────
    def _build_tab_lesson(self, parent):
        hdr = tk.Frame(parent, bg=C["bg"]); hdr.pack(fill="x", padx=16, pady=10)
        Label(hdr, "Daftar Pelajaran", font=F["h2"]).pack(side="left")
        btn_row = tk.Frame(hdr, bg=C["bg"]); btn_row.pack(side="right")
        Btn(btn_row, "＋ Tambah", self._add_lesson, "green",  px=10).pack(side="left", padx=2)
        Btn(btn_row, "✏️ Edit",   self._edit_lesson, "ghost", px=10).pack(side="left", padx=2)
        Btn(btn_row, "🗑 Hapus",  self._del_lesson,  "red",   px=10).pack(side="left", padx=2)

        cols = ("title","mins","items")
        self._lesson_tree = ttk.Treeview(parent, columns=cols, show="headings", height=10)
        for col,label,w,anchor in [
            ("title","Judul Pelajaran", 420,"w"),
            ("mins","Menit",80,"center"),
            ("items","Blok",80,"center"),
        ]:
            self._lesson_tree.heading(col, text=label)
            self._lesson_tree.column(col, width=w, anchor=anchor)
        self._lesson_tree.pack(fill="both", expand=True, padx=16, pady=4)
        self._lesson_tree.bind("<Double-1>", lambda e: self._edit_lesson())

    # ── Tab: Flashcard ────────────────────────────────────────────────────────
    def _build_tab_fc(self, parent):
        hdr = tk.Frame(parent, bg=C["bg"]); hdr.pack(fill="x", padx=16, pady=10)
        Label(hdr, "Flashcard", font=F["h2"]).pack(side="left")
        self._fc_count_lbl = Label(hdr, "0 kartu", fg=C["text3"], font=F["small"])
        self._fc_count_lbl.pack(side="left", padx=10)
        Btn(hdr, "✏️ Edit Semua", self._edit_flashcards, "ghost").pack(side="right")

        canvas = tk.Canvas(parent, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self._fc_host = tk.Frame(canvas, bg=C["bg"])
        self._fc_host.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self._fc_host, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(16,0))
        sb.pack(side="right", fill="y", pady=4)

    # ── Tab: Quiz ─────────────────────────────────────────────────────────────
    def _build_tab_quiz(self, parent):
        hdr = tk.Frame(parent, bg=C["bg"]); hdr.pack(fill="x", padx=16, pady=10)
        Label(hdr, "Soal Kuis", font=F["h2"]).pack(side="left")
        self._quiz_count_lbl = Label(hdr, "0 soal", fg=C["text3"], font=F["small"])
        self._quiz_count_lbl.pack(side="left", padx=10)
        Btn(hdr, "✏️ Edit Semua", self._edit_quiz, "ghost").pack(side="right")

        cols = ("no","question","ans","exp")
        self._quiz_tree = ttk.Treeview(parent, columns=cols, show="headings", height=16)
        for col,lbl,w,anchor in [
            ("no","#",40,"center"),
            ("question","Pertanyaan",500,"w"),
            ("ans","Jwb",50,"center"),
            ("exp","Penjelasan",200,"w"),
        ]:
            self._quiz_tree.heading(col, text=lbl)
            self._quiz_tree.column(col, width=w, anchor=anchor)
        self._quiz_tree.pack(fill="both", expand=True, padx=16, pady=4)

    # ── Tab: Raw JSON ─────────────────────────────────────────────────────────
    def _build_tab_raw(self, parent):
        hdr = tk.Frame(parent, bg=C["bg"]); hdr.pack(fill="x", padx=16, pady=10)
        Label(hdr, "Raw JSON", font=F["h2"]).pack(side="left")
        Btn(hdr, "📋 Salin Topik",  self._copy_topic_json, "ghost").pack(side="right", padx=4)
        Btn(hdr, "📋 Salin Penuh",  self._copy_full_json,  "ghost").pack(side="right", padx=4)
        Btn(hdr, "💾 Export Topik", self._export_topic,    "outline").pack(side="right", padx=4)

        self._raw_txt = Textbox(parent, font=F["mono"], state="disabled",
                                 bg=C["surface"])
        sb = ttk.Scrollbar(parent, orient="vertical", command=self._raw_txt.yview)
        self._raw_txt.configure(yscrollcommand=sb.set)
        self._raw_txt.pack(side="left", fill="both", expand=True, padx=(16,0), pady=4)
        sb.pack(side="right", fill="y", padx=(0,8), pady=4)

    def _build_statusbar(self):
        sb = tk.Frame(self, bg=C["surface"], height=28)
        sb.pack(fill="x", side="bottom"); sb.pack_propagate(False)

        self._status_lbl = tk.Label(sb, text="  Selamat datang di Subject JSON Editor  ★  Polaris",
                                     bg=C["surface"], fg=C["text3"], font=F["small"], anchor="w")
        self._status_lbl.pack(side="left", fill="x", expand=True)

        self._undo_lbl = tk.Label(sb, text="Ctrl+Z Undo  │  Ctrl+Y Redo  │  Ctrl+S Simpan",
                                   bg=C["surface"], fg=C["text4"], font=F["tiny"])
        self._undo_lbl.pack(side="right", padx=16)

    # ══════════════════════════════════════════════════════════════════════════
    #  FILE  OPERATIONS
    # ══════════════════════════════════════════════════════════════════════════
    def _load_subject_list(self):
        base = os.path.dirname(os.path.abspath(__file__))
        files = sorted(f for f in os.listdir(base) if f.endswith(".json"))
        self._subject_cb["values"] = files
        if "ipa.json" in files:
            self._subject_var.set("ipa.json")
            self._on_subject_change()
        elif files:
            self._subject_var.set(files[0])
            self._on_subject_change()

    def _on_subject_change(self, event=None):
        fname = self._subject_var.get()
        if not fname: return
        if self._unsaved:
            if not messagebox.askyesno("Konfirmasi","Ada perubahan belum disimpan. Lanjut?"):
                if self._filepath:
                    self._subject_var.set(os.path.basename(self._filepath))
                return
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
        self._load_path(path)

    def _load_path(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._push_undo()
            self._data = data
            self._filepath = path
            self._unsaved = False
            self._sel_idx = None
            self._refresh_tree()
            self._show_dashboard()
            self._update_title()
            self._status(f"✓ Dimuat: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error",f"Gagal memuat:\n{e}")

    def _save(self, event=None):
        if not self._filepath: self._save_as(); return
        self._write(self._filepath)

    def _save_as(self):
        p = filedialog.asksaveasfilename(
            title="Simpan File JSON", defaultextension=".json",
            filetypes=[("JSON","*.json")])
        if p: self._filepath = p; self._write(p); self._load_subject_list()

    def _write(self, path):
        try:
            clean = json.loads(json.dumps(self._data, ensure_ascii=False))
            with open(path,"w",encoding="utf-8") as f:
                json.dump(clean, f, ensure_ascii=False, indent=2)
            self._unsaved = False
            self._update_title()
            self._status(f"💾 Disimpan: {os.path.basename(path)}  [{datetime.now():%H:%M:%S}]")
            Toast.show(self, f"Disimpan: {os.path.basename(path)}", "ok", 2000)
        except Exception as e:
            messagebox.showerror("Error",f"Gagal simpan:\n{e}")

    # ══════════════════════════════════════════════════════════════════════════
    #  TOPIC CRUD
    # ══════════════════════════════════════════════════════════════════════════
    def _refresh_tree(self):
        self._tree.delete(*self._tree.get_children())
        q = self._search_var.get().lower().strip() if hasattr(self,"_search_var") else ""
        tokens = q.split()
        topics = self._data.get("topics",[])
        shown = 0
        for i,t in enumerate(topics):
            title = t.get("title",f"Topik {i+1}")
            if tokens and not all(tok in title.lower() for tok in tokens): continue
            n_fc = len(t.get("flashcards",[]))
            n_q  = len(t.get("quiz",{}).get("questions",[]))
            n_ls = len(t.get("lessons",[]))
            label = f"  {title}  ·  {n_ls}📖  {n_fc}🃏  {n_q}📝"
            self._tree.insert("", "end", iid=str(i), text=label, values=(i,))
            shown += 1
        if hasattr(self,"_topic_count"):
            self._topic_count.config(text=f"{shown}/{len(topics)}")

    def _on_select(self, event=None):
        sel = self._tree.selection()
        if not sel: return
        idx = int(sel[0])
        self._sel_idx = idx
        self._refresh_detail(idx)

    def _get_topic(self):
        if self._sel_idx is None: return None
        t = self._data.get("topics",[])
        return t[self._sel_idx] if self._sel_idx < len(t) else None

    def _add_topic(self):
        dlg = TopicDialog(self)
        if dlg.result:
            self._push_undo()
            self._data.setdefault("topics",[]).append(dlg.result)
            self._mark_dirty()
            self._refresh_tree()
            Toast.show(self, f"Topik '{dlg.result['title']}' ditambahkan", "ok")

    def _edit_topic(self):
        t = self._get_topic()
        if not t: messagebox.showinfo("Info","Pilih topik!"); return
        dlg = TopicDialog(self, t)
        if dlg.result:
            self._push_undo()
            dlg.result["lessons"]    = t.get("lessons",[])
            dlg.result["flashcards"] = t.get("flashcards",[])
            dlg.result["quiz"]       = t.get("quiz",{"questions":[]})
            self._data["topics"][self._sel_idx] = dlg.result
            self._mark_dirty()
            self._refresh_tree()
            self._refresh_detail(self._sel_idx)

    def _del_topic(self):
        t = self._get_topic()
        if not t: messagebox.showinfo("Info","Pilih topik!"); return
        if messagebox.askyesno("Konfirmasi",
                                f"Hapus '{t.get('title')}'?\nSemua data di dalamnya akan hilang."):
            self._push_undo()
            del self._data["topics"][self._sel_idx]
            self._sel_idx = None
            self._mark_dirty()
            self._refresh_tree()
            self._show_dashboard()

    def _duplicate_topic(self):
        t = self._get_topic()
        if not t: return
        self._push_undo()
        copy_t = deep(t)
        copy_t["id"]    = copy_t["id"] + "-copy"
        copy_t["title"] = copy_t["title"] + " (Salinan)"
        self._data["topics"].append(copy_t)
        self._mark_dirty()
        self._refresh_tree()
        Toast.show(self, f"Topik disalin!", "ok")

    def _move_up(self):
        if self._sel_idx is None or self._sel_idx == 0: return
        self._push_undo()
        t = self._data["topics"]
        t[self._sel_idx-1], t[self._sel_idx] = t[self._sel_idx], t[self._sel_idx-1]
        self._sel_idx -= 1
        self._mark_dirty()
        self._refresh_tree()
        self._tree.selection_set(str(self._sel_idx))

    def _move_down(self):
        if self._sel_idx is None: return
        t = self._data["topics"]
        if self._sel_idx >= len(t)-1: return
        self._push_undo()
        t[self._sel_idx], t[self._sel_idx+1] = t[self._sel_idx+1], t[self._sel_idx]
        self._sel_idx += 1
        self._mark_dirty()
        self._refresh_tree()
        self._tree.selection_set(str(self._sel_idx))

    def _show_ctx(self, event):
        row = self._tree.identify_row(event.y)
        if row: self._tree.selection_set(row)
        self._ctx.post(event.x_root, event.y_root)

    # ══════════════════════════════════════════════════════════════════════════
    #  DETAIL REFRESH
    # ══════════════════════════════════════════════════════════════════════════
    def _refresh_detail(self, idx):
        topics = self._data.get("topics",[])
        if idx >= len(topics): return
        t = topics[idx]

        # ── Info tab ──
        for w in self._info_host.winfo_children(): w.destroy()

        card = Card(self._info_host); card.pack(fill="x", padx=20, pady=16)

        # Topic header
        th = tk.Frame(card, bg=C["card"]); th.pack(fill="x", padx=16, pady=(16,4))
        tk.Label(th, text=t.get("title",""), bg=C["card"], fg=C["text"],
                 font=F["h1"]).pack(side="left")
        grades = t.get("grade",[])
        for g in grades:
            tk.Label(th, text=f" Kelas {g} ", bg=C["accent"], fg=C["white"],
                     font=F["tiny"]).pack(side="right", padx=2)

        if t.get("description"):
            tk.Label(card, text=t["description"], bg=C["card"], fg=C["text2"],
                     font=F["body"], wraplength=580, justify="left",
                     ).pack(padx=16, pady=(0,6), anchor="w")

        # Stats inside card
        s_row = tk.Frame(card, bg=C["card"]); s_row.pack(fill="x", padx=16, pady=(4,16))
        n_ls = len(t.get("lessons",[])); n_fc = len(t.get("flashcards",[])); n_q = len(t.get("quiz",{}).get("questions",[]))
        for icon, count, label, color in [
            ("📖", n_ls, "Pelajaran", C["blue"]),
            ("🃏", n_fc, "Flashcard", C["green"]),
            ("📝", n_q,  "Soal Kuis", C["yellow"]),
        ]:
            box = tk.Frame(s_row, bg=C["raised"]); box.pack(side="left", padx=6)
            tk.Label(box, text=f"{icon} {count}", bg=C["raised"], fg=color,
                     font=F["h1"]).pack(padx=14, pady=(10,2))
            tk.Label(box, text=label, bg=C["raised"], fg=C["text3"],
                     font=F["small"]).pack(padx=14, pady=(0,10))

        # Action row
        act = tk.Frame(self._info_host, bg=C["bg"]); act.pack(fill="x", padx=20, pady=8)
        Btn(act, "✏️ Edit Topik",       self._edit_topic,       "ghost", px=10).pack(side="left", padx=4)
        Btn(act, "📋 Duplikat",          self._duplicate_topic,  "ghost", px=10).pack(side="left", padx=4)
        Btn(act, "🤖 AI Studio",         self._open_ai,          "purple",px=10).pack(side="left", padx=4)
        Btn(act, "🗑 Hapus",             self._del_topic,        "red",   px=10).pack(side="right", padx=4)

        # ── Lessons tab ──
        self._lesson_tree.delete(*self._lesson_tree.get_children())
        for ls in t.get("lessons",[]):
            n_blk = len(ls.get("content",[]))
            self._lesson_tree.insert("","end",
                values=(ls.get("title",""), ls.get("estMinutes","?"), n_blk))

        # ── Flashcard tab ──
        for w in self._fc_host.winfo_children(): w.destroy()
        cards = t.get("flashcards",[])
        self._fc_count_lbl.config(text=f"{len(cards)} kartu")
        for i,card in enumerate(cards):
            row = Card(self._fc_host); row.pack(fill="x", pady=2, padx=4)
            rr = tk.Frame(row, bg=C["card"]); rr.pack(fill="x", padx=12, pady=6)
            tk.Label(rr, text=f"#{i+1}", bg=C["card"], fg=C["accent"], font=F["small"]).pack(side="left")
            tk.Label(rr, text=f"Q: {card.get('question','')[:60]}", bg=C["card"],
                     fg=C["text"], font=F["small"]).pack(side="left", padx=8, fill="x", expand=True)
            tk.Label(rr, text=f"A: {card.get('answer','')[:40]}", bg=C["card"],
                     fg=C["green"], font=F["small"]).pack(side="right")

        # ── Quiz tab ──
        self._quiz_tree.delete(*self._quiz_tree.get_children())
        qs = t.get("quiz",{}).get("questions",[])
        self._quiz_count_lbl.config(text=f"{len(qs)} soal")
        for i,q in enumerate(qs):
            ans = q.get("answer",0)
            ans_l = "ABCD"[ans] if ans < 4 else "?"
            self._quiz_tree.insert("","end",
                values=(i+1, q.get("question","")[:80], ans_l, q.get("explanation","")[:40]))

        # ── Raw tab ──
        self._raw_txt.config(state="normal")
        self._raw_txt.delete("1.0","end")
        clean = {k:v for k,v in t.items() if not k.startswith("_")}
        self._raw_txt.insert("1.0", json.dumps(clean, ensure_ascii=False, indent=2))
        self._raw_txt.config(state="disabled")

    # ══════════════════════════════════════════════════════════════════════════
    #  LESSON CRUD
    # ══════════════════════════════════════════════════════════════════════════
    def _add_lesson(self):
        t = self._get_topic()
        if not t: messagebox.showinfo("Info","Pilih topik!"); return
        dlg = LessonDialog(self)
        if dlg.result:
            self._push_undo()
            t.setdefault("lessons",[]).append(dlg.result)
            self._mark_dirty()
            self._refresh_detail(self._sel_idx)

    def _edit_lesson(self):
        t = self._get_topic()
        if not t: return
        sel = self._lesson_tree.selection()
        if not sel: messagebox.showinfo("Info","Pilih pelajaran!"); return
        idx = self._lesson_tree.index(sel[0])
        dlg = LessonDialog(self, t["lessons"][idx])
        if dlg.result:
            self._push_undo()
            t["lessons"][idx] = dlg.result
            self._mark_dirty()
            self._refresh_detail(self._sel_idx)

    def _del_lesson(self):
        t = self._get_topic()
        if not t: return
        sel = self._lesson_tree.selection()
        if not sel: return
        idx = self._lesson_tree.index(sel[0])
        if messagebox.askyesno("Konfirmasi",f"Hapus '{t['lessons'][idx].get('title','')}'?"):
            self._push_undo()
            del t["lessons"][idx]
            self._mark_dirty()
            self._refresh_detail(self._sel_idx)

    # ══════════════════════════════════════════════════════════════════════════
    #  FLASHCARD / QUIZ
    # ══════════════════════════════════════════════════════════════════════════
    def _edit_flashcards(self):
        t = self._get_topic()
        if not t: messagebox.showinfo("Info","Pilih topik!"); return
        dlg = FlashcardDialog(self, t.get("flashcards",[]))
        if dlg.result is not None:
            self._push_undo()
            t["flashcards"] = dlg.result
            self._mark_dirty()
            self._refresh_detail(self._sel_idx)

    def _edit_quiz(self):
        t = self._get_topic()
        if not t: messagebox.showinfo("Info","Pilih topik!"); return
        dlg = QuizDialog(self, t.get("quiz",{}).get("questions",[]))
        if dlg.result is not None:
            self._push_undo()
            t.setdefault("quiz",{})["questions"] = dlg.result
            self._mark_dirty()
            self._refresh_detail(self._sel_idx)

    # ══════════════════════════════════════════════════════════════════════════
    #  RAW JSON ACTIONS
    # ══════════════════════════════════════════════════════════════════════════
    def _copy_topic_json(self):
        t = self._get_topic()
        if not t: return
        clean = {k:v for k,v in t.items() if not k.startswith("_")}
        self.clipboard_clear(); self.clipboard_append(json.dumps(clean, ensure_ascii=False, indent=2))
        Toast.show(self,"JSON topik disalin!","ok")

    def _copy_full_json(self):
        self.clipboard_clear()
        self.clipboard_append(json.dumps(self._data, ensure_ascii=False, indent=2))
        Toast.show(self,"Full JSON disalin!","ok")

    def _export_topic(self):
        t = self._get_topic()
        if not t: return
        p = filedialog.asksaveasfilename(
            title="Export Topik", initialfile=f"{t.get('id','topic')}.json",
            defaultextension=".json", filetypes=[("JSON","*.json")])
        if p:
            clean = {k:v for k,v in t.items() if not k.startswith("_")}
            with open(p,"w",encoding="utf-8") as f:
                json.dump(clean, f, ensure_ascii=False, indent=2)
            Toast.show(self, f"Topik diekspor!", "ok")

    # ══════════════════════════════════════════════════════════════════════════
    #  GLOBAL SEARCH
    # ══════════════════════════════════════════════════════════════════════════
    def _global_search(self):
        dlg = tk.Toplevel(self); dlg.title("🔍 Global Search & Replace")
        dlg.geometry("640x520"); dlg.configure(bg=C["bg"])
        tk.Frame(dlg, bg=C["accent"], height=3).pack(fill="x")

        Label(dlg, "🔍  Global Search & Replace", font=F["h2"]).pack(pady=(16,0), padx=20, anchor="w")

        row = tk.Frame(dlg, bg=C["bg"]); row.pack(fill="x", padx=20, pady=8)
        SLabel(row, "Cari").pack(anchor="w")
        se = Entry(row); se.pack(fill="x")
        SLabel(row, "Ganti Dengan (kosongkan = hanya cari)").pack(anchor="w", pady=(8,2))
        re_e = Entry(row); re_e.pack(fill="x")

        res = tk.Listbox(dlg, bg=C["raised"], fg=C["text"], font=F["small"],
                          borderwidth=0, highlightthickness=1, highlightbackground=C["border"],
                          selectbackground=C["accent"])
        res.pack(fill="both", expand=True, padx=20, pady=8)

        def search():
            q = se.get().lower().strip()
            if not q: return
            res.delete(0,"end")
            for i,t in enumerate(self._data.get("topics",[])):
                if q in t.get("title","").lower():
                    res.insert("end", f"📚  Topik: {t['title']}")
                for ls in t.get("lessons",[]):
                    if q in ls.get("title","").lower():
                        res.insert("end", f"   📖  Pelajaran: {ls['title']}")
                    for item in ls.get("content",[]):
                        txt = item.get("text","") or ",".join(item.get("headers",[]))
                        if q in txt.lower():
                            res.insert("end", f"      · {txt[:60]}...")
                            break
                for fc in t.get("flashcards",[]):
                    if q in fc.get("question","").lower() or q in fc.get("answer","").lower():
                        res.insert("end", f"   🃏  {fc['question'][:50]}")
                for qq in t.get("quiz",{}).get("questions",[]):
                    if q in qq.get("question","").lower():
                        res.insert("end", f"   📝  {qq['question'][:50]}")

        def replace_all():
            q = se.get().strip(); r = re_e.get().strip()
            if not q or not r: return
            if not messagebox.askyesno("Replace","Lanjutkan replace all?",parent=dlg): return
            count = 0
            for t in self._data.get("topics",[]):
                if q in t.get("title",""):
                    t["title"] = t["title"].replace(q,r); count += 1
                for ls in t.get("lessons",[]):
                    if q in ls.get("title",""): ls["title"] = ls["title"].replace(q,r); count += 1
                    for item in ls.get("content",[]):
                        if "text" in item and q in item["text"]:
                            item["text"] = item["text"].replace(q,r); count += 1
            self._push_undo(); self._mark_dirty(); self._refresh_tree()
            messagebox.showinfo("Done",f"✓ {count} kemunculan diganti.",parent=dlg)
            dlg.destroy()

        btn_row = tk.Frame(dlg, bg=C["bg"]); btn_row.pack(pady=8)
        Btn(btn_row,"🔍 Cari",search,"primary").pack(side="left",padx=5)
        Btn(btn_row,"🔄 Replace All",replace_all,"yellow").pack(side="left",padx=5)
        se.focus_set()
        se.bind("<Return>", lambda e: search())

    # ══════════════════════════════════════════════════════════════════════════
    #  INFO EDIT / AI MODE
    # ══════════════════════════════════════════════════════════════════════════
    def _edit_info(self):
        dlg = SubjectInfoDialog(self, self._data)
        if dlg.result:
            self._push_undo()
            self._data.update(dlg.result)
            self._mark_dirty()
            self._show_dashboard()

    def _open_ai(self):
        AIModeWindow(self, self._data, self._ai_callback)

    def _ai_callback(self, kind, topic_id, payload):
        topics = self._data.get("topics",[])
        self._push_undo()
        if kind == "topic":
            topics.append(payload)
        elif kind == "full_topic_update":
            target = next((t for t in topics if t.get("id") == topic_id), None)
            if target:
                if payload.get("title"):       target["title"]       = payload["title"]
                if payload.get("description"): target["description"] = payload["description"]
                if payload.get("lessons"):     target["lessons"]     = payload["lessons"]
                if payload.get("flashcards"):  target["flashcards"]  = payload["flashcards"]
                if payload.get("quiz",{}).get("questions"):
                    target["quiz"] = payload["quiz"]
        self._mark_dirty()
        self._save()
        self._refresh_tree()
        if self._sel_idx is not None:
            self._refresh_detail(self._sel_idx)

    # ══════════════════════════════════════════════════════════════════════════
    #  UNDO / REDO
    # ══════════════════════════════════════════════════════════════════════════
    def _push_undo(self):
        self._undo.push(self._data)

    def _do_undo(self, event=None):
        if not self._undo.can_undo:
            Toast.show(self,"Tidak ada yang bisa di-undo","warn"); return
        self._data = self._undo.undo(self._data)
        self._unsaved = True
        self._refresh_tree()
        self._show_dashboard()
        self._update_title()
        Toast.show(self,"Undo ✓","info")

    def _do_redo(self, event=None):
        if not self._undo.can_redo:
            Toast.show(self,"Tidak ada yang bisa di-redo","warn"); return
        self._data = self._undo.redo(self._data)
        self._unsaved = True
        self._refresh_tree()
        self._show_dashboard()
        self._update_title()
        Toast.show(self,"Redo ✓","info")

    # ══════════════════════════════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════════════════════════════
    def _mark_dirty(self):
        self._unsaved = True
        self._update_title()

    def _update_title(self):
        fname = os.path.basename(self._filepath) if self._filepath else "Tanpa File"
        marker = " ●" if self._unsaved else ""
        self.title(f"✏️  JSON Editor  —  {fname}{marker}")
        self._file_lbl.config(
            text=self._filepath or "Belum ada file",
            fg=C["yellow"] if self._unsaved else C["text4"])

    def _status(self, msg):
        self._status_lbl.config(text=f"  {msg}")

    def _on_close(self):
        if self._unsaved:
            choice = messagebox.askyesnocancel("Keluar","Ada perubahan belum disimpan. Simpan dulu?")
            if choice is None: return
            if choice: self._save()
        self.destroy()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
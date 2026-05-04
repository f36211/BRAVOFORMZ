"""
IPA JSON Editor — Editor materi IPA SMP berbasis GUI
Dirancang untuk format JSON kurikulum IPA (topik, pelajaran, flashcard, kuis)
Fitur: Edit, Tambah, Hapus, Export, AI Mode (export ringkas untuk AI)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
import copy
import re
from datetime import datetime

# ─── Warna & Font ───────────────────────────────────────────────────────────
BG_DARK    = "#09090b"
BG_CARD    = "#18181b"
BG_PANEL   = "#121214"
BG_INPUT   = "#27272a"
ACCENT     = "#6366f1"
ACCENT2    = "#a855f7"
SUCCESS    = "#22c55e"
DANGER     = "#ef4444"
WARNING    = "#eab308"
TEXT_PRI   = "#fafafa"
TEXT_SEC   = "#a1a1aa"
TEXT_DIM   = "#52525b"
BORDER     = "#3f3f46"

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_HEAD  = ("Segoe UI", 13, "bold")
FONT_BODY  = ("Segoe UI", 10)
FONT_MONO  = ("Consolas", 10)
FONT_SMALL = ("Segoe UI", 9)


# ─── Helper ──────────────────────────────────────────────────────────────────
def make_id(title: str) -> str:
    """Buat ID slug dari judul."""
    s = title.lower().strip()
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s[:40]


def deep_copy(obj):
    return copy.deepcopy(obj)


# ─── Komponen UI Kustom ───────────────────────────────────────────────────────
class StyledButton(tk.Button):
    def __init__(self, parent, text, command=None, style="primary", **kw):
        colors = {
            "primary": (ACCENT, "#fff"),
            "success": (SUCCESS, "#000"),
            "danger":  (DANGER, "#fff"),
            "ghost":   (BG_INPUT, TEXT_SEC),
            "warning": (WARNING, "#000"),
            "purple":  (ACCENT2, "#fff"),
        }
        bg, fg = colors.get(style, (ACCENT, "#fff"))
        
        # Use defaults if not provided in kw
        px = kw.pop("padx", 14)
        py = kw.pop("pady", 7)
        
        super().__init__(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
            relief="flat", bd=0, padx=px, pady=py,
            font=FONT_BODY, cursor="hand2", **kw
        )
        self._bg = bg
        self.bind("<Enter>", lambda e: self.config(bg=self._darken(bg)))
        self.bind("<Leave>", lambda e: self.config(bg=bg))

    def _darken(self, hex_color):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return "#{:02x}{:02x}{:02x}".format(max(0, r-30), max(0, g-30), max(0, b-30))


class StyledEntry(tk.Entry):
    def __init__(self, parent, **kw):
        defaults = dict(
            bg=BG_INPUT, fg=TEXT_PRI, insertbackground=TEXT_PRI,
            relief="flat", bd=0, font=FONT_BODY,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT
        )
        defaults.update(kw)
        super().__init__(parent, **defaults)


class StyledText(tk.Text):
    def __init__(self, parent, **kw):
        defaults = dict(
            bg=BG_INPUT, fg=TEXT_PRI, insertbackground=TEXT_PRI,
            relief="flat", bd=0, font=FONT_BODY,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT, selectbackground=ACCENT,
            wrap="word"
        )
        defaults.update(kw)
        super().__init__(parent, **defaults)


class SectionLabel(tk.Label):
    def __init__(self, parent, text, **kw):
        super().__init__(
            parent, text=text, bg=BG_PANEL, fg=TEXT_SEC,
            font=FONT_SMALL, anchor="w", **kw
        )


class Card(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_CARD, relief="flat", bd=0, **kw)


# ─── Dialog Tambah Topik ─────────────────────────────────────────────────────
class TopicDialog(tk.Toplevel):
    def __init__(self, parent, topic=None):
        super().__init__(parent)
        self.result = None
        self.title("✏️  Tambah / Edit Topik")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.geometry("500x320")
        self._build(topic)
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def _build(self, topic):
        pad = dict(padx=20, pady=8)
        tk.Label(self, text="Tambah / Edit Topik", bg=BG_DARK, fg=TEXT_PRI,
                 font=FONT_HEAD).pack(**pad, anchor="w")

        fields = [
            ("Judul Topik *", "title", topic.get("title", "") if topic else ""),
            ("Deskripsi", "description", topic.get("description", "") if topic else ""),
        ]
        self._vars = {}
        for label, key, val in fields:
            SectionLabel(self, text=label).pack(padx=20, anchor="w", pady=(8, 2))
            v = tk.StringVar(value=val)
            self._vars[key] = v
            StyledEntry(self, textvariable=v, width=55).pack(padx=20, fill="x")

        # Grade checkboxes
        SectionLabel(self, text="Kelas yang Diajarkan").pack(padx=20, pady=(8, 2), anchor="w")
        grade_frame = tk.Frame(self, bg=BG_DARK)
        grade_frame.pack(padx=20, anchor="w")
        self._grades = {}
        curr_grades = topic.get("grade", [7, 8, 9]) if topic else [7]
        for g in [7, 8, 9]:
            var = tk.BooleanVar(value=g in curr_grades)
            self._grades[g] = var
            tk.Checkbutton(grade_frame, text=f"Kelas {g}", variable=var,
                           bg=BG_DARK, fg=TEXT_PRI, selectcolor=BG_INPUT,
                           activebackground=BG_DARK, font=FONT_BODY).pack(side="left", padx=10)

        # Buttons
        btn_frame = tk.Frame(self, bg=BG_DARK)
        btn_frame.pack(side="bottom", pady=16)
        StyledButton(btn_frame, "✓  Simpan", self._save, style="primary").pack(side="left", padx=6)
        StyledButton(btn_frame, "Batal", self.destroy, style="ghost").pack(side="left", padx=6)

    def _save(self):
        title = self._vars["title"].get().strip()
        if not title:
            messagebox.showwarning("Perhatian", "Judul topik wajib diisi!", parent=self)
            return
        self.result = {
            "id": make_id(title),
            "title": title,
            "description": self._vars["description"].get().strip(),
            "grade": [g for g, v in self._grades.items() if v.get()],
            "lessons": [],
            "flashcards": [],
            "quiz": {"questions": []}
        }
        self.destroy()


# ─── Dialog Edit Subject ────────────────────────────────────────────────────
class SubjectDialog(tk.Toplevel):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.result = None
        self.title("⚙️ Edit Info Pelajaran")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.geometry("500x420")
        self._build(data)
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def _build(self, data):
        pad = dict(padx=20, pady=8)
        tk.Label(self, text="⚙️ Edit Info Pelajaran", bg=BG_DARK, fg=TEXT_PRI,
                 font=FONT_HEAD).pack(**pad, anchor="w")

        fields = [
            ("Nama Pelajaran *", "name", data.get("name", "")),
            ("Deskripsi", "description", data.get("description", "")),
            ("URL Gambar (Cover)", "image", data.get("image", "")),
        ]
        self._vars = {}
        for label, key, val in fields:
            SectionLabel(self, text=label).pack(padx=20, anchor="w", pady=(8, 2))
            v = tk.StringVar(value=val)
            self._vars[key] = v
            StyledEntry(self, textvariable=v, width=55).pack(padx=20, fill="x")

        # Grade checkboxes
        SectionLabel(self, text="Tingkatan Kelas").pack(padx=20, pady=(8, 2), anchor="w")
        grade_frame = tk.Frame(self, bg=BG_DARK)
        grade_frame.pack(padx=20, anchor="w")
        self._grades = {}
        curr_grades = data.get("grade", [7, 8, 9])
        for g in [7, 8, 9]:
            var = tk.BooleanVar(value=g in curr_grades)
            self._grades[g] = var
            tk.Checkbutton(grade_frame, text=f"Kelas {g}", variable=var,
                           bg=BG_DARK, fg=TEXT_PRI, selectcolor=BG_INPUT,
                           activebackground=BG_DARK, font=FONT_BODY).pack(side="left", padx=10)

        # Buttons
        btn_frame = tk.Frame(self, bg=BG_DARK)
        btn_frame.pack(side="bottom", pady=20)
        StyledButton(btn_frame, "✓  Simpan Perubahan", self._save, style="primary").pack(side="left", padx=6)
        StyledButton(btn_frame, "Batal", self.destroy, style="ghost").pack(side="left", padx=6)

    def _save(self):
        name = self._vars["name"].get().strip()
        if not name:
            messagebox.showwarning("Perhatian", "Nama pelajaran wajib diisi!", parent=self)
            return
        self.result = {
            "name": name,
            "description": self._vars["description"].get().strip(),
            "image": self._vars["image"].get().strip(),
            "grade": [g for g, v in self._grades.items() if v.get()]
        }
        self.destroy()


# ─── Dialog Lesson ────────────────────────────────────────────────────────────
class LessonDialog(tk.Toplevel):
    def __init__(self, parent, lesson=None):
        super().__init__(parent)
        self.result = None
        self.title("📖  Edit Pelajaran")
        self.configure(bg=BG_DARK)
        self.geometry("640x700")
        self._content_items = []
        self._build(lesson)
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def _build(self, lesson):
        # Top
        top = tk.Frame(self, bg=BG_DARK)
        top.pack(fill="x", padx=20, pady=12)
        tk.Label(top, text="📖  Edit Pelajaran", bg=BG_DARK, fg=TEXT_PRI,
                 font=FONT_HEAD).pack(anchor="w")

        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=20)

        # Basic fields
        fields = [
            ("Judul Pelajaran *", "title", lesson.get("title", "") if lesson else ""),
            ("Estimasi Waktu (menit)", "estMinutes", str(lesson.get("estMinutes", 10)) if lesson else "10"),
        ]
        self._vars = {}
        for lbl, key, val in fields:
            SectionLabel(main, text=lbl).pack(anchor="w", pady=(8, 2))
            v = tk.StringVar(value=val)
            self._vars[key] = v
            StyledEntry(main, textvariable=v, width=60).pack(fill="x")

        # Content editor
        SectionLabel(main, text="Konten Materi (satu paragraf/poin per baris)").pack(
            anchor="w", pady=(12, 2))
        tk.Label(main, text="Format: HEADING: teks | H2: teks | LIST: poin | TABLE_HEADER: h1,h2 | TABLE_ROW: v1,v2 | HIGHLIGHT: teks",
                 bg=BG_DARK, fg=TEXT_DIM, font=("Segoe UI", 8)).pack(anchor="w")

        self._content_text = StyledText(main, height=14, width=70, font=FONT_MONO)
        self._content_text.pack(fill="both", expand=True, pady=(4, 8))
        
        # Configure syntax tags
        self._content_text.tag_configure("prefix", foreground=ACCENT, font=(FONT_MONO[0], FONT_MONO[1], "bold"))
        self._content_text.tag_configure("heading", foreground=WARNING, font=(FONT_MONO[0], FONT_MONO[1]+2, "bold"))
        self._content_text.tag_configure("math", foreground=ACCENT2)
        self._content_text.tag_configure("list", foreground=SUCCESS)
        self._content_text.tag_configure("highlight", foreground=ACCENT2, background="#2e1065")
        self._content_text.tag_configure("image", foreground="#fbbf24")
        self._content_text.bind("<KeyRelease>", self._apply_syntax)

        if lesson and lesson.get("content"):
            self._content_text.insert("1.0", self._content_to_text(lesson["content"]))
            self._apply_syntax()

        # Buttons
        btn_f = tk.Frame(self, bg=BG_DARK)
        btn_f.pack(pady=12, fill="x", padx=20)
        
        left_btns = tk.Frame(btn_f, bg=BG_DARK)
        left_btns.pack(side="left")
        StyledButton(left_btns, "✨ Magic DSL", self._magic_dsl, style="purple").pack(side="left", padx=4)
        StyledButton(left_btns, "📝 Preview", self._preview_content, style="ghost").pack(side="left", padx=4)

        right_btns = tk.Frame(btn_f, bg=BG_DARK)
        right_btns.pack(side="right")
        StyledButton(right_btns, "✓  Simpan", self._save, style="primary").pack(side="left", padx=6)
        StyledButton(right_btns, "Batal", self.destroy, style="ghost").pack(side="left", padx=6)

    def _magic_dsl(self):
        """Mencoba mengubah teks mentah menjadi format DSL secara otomatis."""
        raw = self._content_text.get("1.0", "end-1c").strip()
        if not raw: return
        
        lines = raw.split("\n")
        new_lines = []
        for line in lines:
            line = line.strip()
            if not line: 
                new_lines.append("")
                continue
            
            # Jika sudah ada prefix, biarkan
            if ":" in line[:15] and any(p in line.upper() for p in ["HEADING", "H2", "TEXT", "LIST", "TABLE", "HIGHLIGHT", "MATH"]):
                new_lines.append(line)
                continue
                
            # Heuristik sederhana
            if line.startswith(("# ", "## ", "### ")):
                level = line.count("#")
                new_lines.append(f"H{level}: {line.strip('# ')}")
            elif line.startswith(("- ", "* ", "1. ")):
                new_lines.append(f"LIST: {re.sub(r'^[-*1.]\s+', '', line)}")
            elif len(line) < 40 and not line.endswith((".", "!", "?")):
                new_lines.append(f"H2: {line}")
            else:
                new_lines.append(f"TEXT: {line}")
        
        self._content_text.delete("1.0", "end")
        self._content_text.insert("1.0", "\n".join(new_lines))
        self._apply_syntax()
        messagebox.showinfo("✨ Magic", "Teks telah diformat ke DSL!")

    def _preview_content(self):
        """Menampilkan preview sederhana dari konten."""
        raw = self._content_text.get("1.0", "end-1c")
        content = self._text_to_content(raw)
        
        pv = tk.Toplevel(self)
        pv.title("Materi Preview")
        pv.geometry("500x600")
        pv.configure(bg=BG_DARK)
        
        st = StyledText(pv, font=FONT_BODY)
        st.pack(fill="both", expand=True, padx=20, pady=20)
        
        for item in content:
            t = item.get("type", "text")
            if t == "heading":
                lvl = item.get("level", 1)
                st.insert("end", f"\n{'='*lvl} {item.get('text')}\n", "head")
            elif t == "text":
                st.insert("end", f"{item.get('text')}\n\n")
            elif t == "list":
                for it in item.get("items", []):
                    st.insert("end", f" • {it}\n")
                st.insert("end", "\n")
            elif t == "table":
                st.insert("end", f"[TABEL: {','.join(item.get('headers', []))}]\n", "table")
                for r in item.get("rows", []):
                    st.insert("end", f" - {','.join(str(x) for x in r)}\n")
                st.insert("end", "\n")
        
        st.tag_configure("head", foreground=ACCENT, font=FONT_HEAD)
        st.tag_configure("table", foreground=SUCCESS)
        st.config(state="disabled")

    def _apply_syntax(self, event=None):
        text = self._content_text
        text.tag_remove("prefix", "1.0", "end")
        text.tag_remove("heading", "1.0", "end")
        text.tag_remove("math", "1.0", "end")
        text.tag_remove("list", "1.0", "end")
        text.tag_remove("highlight", "1.0", "end")
        text.tag_remove("image", "1.0", "end")
        
        content = text.get("1.0", "end-1c")
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            line_idx = i + 1
            if ":" in line:
                idx = line.find(":")
                prefix = line[:idx+1]
                p_end = f"{line_idx}.{idx+1}"
                text.tag_add("prefix", f"{line_idx}.0", p_end)
                
                tag_type = None
                p_upper = prefix.upper()
                if any(x in p_upper for x in ["HEADING", "H1", "H2", "H3"]):
                    tag_type = "heading"
                elif "MATH" in p_upper:
                    tag_type = "math"
                elif "LIST" in p_upper:
                    tag_type = "list"
                elif "HIGHLIGHT" in p_upper:
                    tag_type = "highlight"
                elif "IMAGE" in p_upper or "CAPTION" in p_upper:
                    tag_type = "image"
                
                if tag_type:
                    text.tag_add(tag_type, p_end, f"{line_idx}.end")

    def _content_to_text(self, content):
        lines = []
        for item in content:
            t = item.get("type", "text")
            if t == "heading":
                lvl = item.get("level", 1)
                prefix = "HEADING" if lvl == 1 else f"H{lvl}"
                lines.append(f"{prefix}: {item.get('text', '')}")
            elif t == "text":
                lines.append(f"TEXT: {item.get('text', '')}")
            elif t == "highlight":
                lines.append(f"HIGHLIGHT: {item.get('text', '')}")
            elif t == "list":
                for it in item.get("items", []):
                    lines.append(f"LIST: {it}")
            elif t == "table":
                headers = ",".join(item.get("headers", []))
                lines.append(f"TABLE_HEADER: {headers}")
                for row in item.get("rows", []):
                    lines.append(f"TABLE_ROW: {','.join(str(c) for c in row)}")
            elif t == "math":
                lines.append(f"MATH: {item.get('tex', '')}")
            elif t == "image":
                lines.append(f"IMAGE: {item.get('url', '')}")
                if item.get("caption"):
                    lines.append(f"CAPTION: {item.get('caption', '')}")
        return "\n".join(lines)

    def _text_to_content(self, raw):
        content = []
        lines = raw.strip().split("\n")
        current_table = None

        def flush_table():
            nonlocal current_table
            if current_table:
                content.append(current_table)
                current_table = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if ":" not in line:
                flush_table()
                content.append({"type": "text", "text": line})
                continue

            prefix, _, rest = line.partition(":")
            prefix = prefix.strip().upper()
            rest = rest.strip()

            if prefix in ("HEADING", "H1"):
                flush_table()
                content.append({"type": "heading", "text": rest})
            elif prefix.startswith("H") and prefix[1:].isdigit():
                flush_table()
                content.append({"type": "heading", "level": int(prefix[1:]), "text": rest})
            elif prefix == "TEXT":
                flush_table()
                content.append({"type": "text", "text": rest})
            elif prefix == "HIGHLIGHT":
                flush_table()
                content.append({"type": "highlight", "text": rest})
            elif prefix == "LIST":
                flush_table()
                # Merge adjacent LIST items into one block
                if content and content[-1].get("type") == "list":
                    content[-1]["items"].append(rest)
                else:
                    content.append({"type": "list", "items": [rest]})
            elif prefix == "TABLE_HEADER":
                flush_table()
                current_table = {"type": "table", "headers": [h.strip() for h in rest.split(",")], "rows": []}
            elif prefix == "TABLE_ROW":
                if current_table is None:
                    current_table = {"type": "table", "headers": [], "rows": []}
                current_table["rows"].append([c.strip() for c in rest.split(",")])
            elif prefix == "MATH":
                flush_table()
                content.append({"type": "math", "tex": rest, "display": True})
            elif prefix == "IMAGE":
                flush_table()
                content.append({"type": "image", "url": rest, "caption": ""})
            elif prefix == "CAPTION":
                if content and content[-1]["type"] == "image":
                    content[-1]["caption"] = rest
            else:
                flush_table()
                content.append({"type": "text", "text": line})

        flush_table()
        return content

    def _save(self):
        title = self._vars["title"].get().strip()
        if not title:
            messagebox.showwarning("Perhatian", "Judul pelajaran wajib diisi!", parent=self)
            return
        try:
            est = int(self._vars["estMinutes"].get().strip())
        except ValueError:
            est = 10

        raw_content = self._content_text.get("1.0", "end-1c")
        content = self._text_to_content(raw_content)

        self.result = {
            "id": make_id(title),
            "title": title,
            "estMinutes": est,
            "content": content
        }
        self.destroy()


# ─── Dialog Flashcard ─────────────────────────────────────────────────────────
class FlashcardDialog(tk.Toplevel):
    def __init__(self, parent, cards=None):
        super().__init__(parent)
        self.result = None
        self.title("🃏  Edit Flashcard")
        self.configure(bg=BG_DARK)
        self.geometry("660x600")
        self._cards = deep_copy(cards) if cards else []
        self._build()
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def _build(self):
        tk.Label(self, text="🃏  Kelola Flashcard", bg=BG_DARK, fg=TEXT_PRI,
                 font=FONT_HEAD).pack(padx=20, pady=12, anchor="w")

        # List area
        list_frame = tk.Frame(self, bg=BG_DARK)
        list_frame.pack(fill="both", expand=True, padx=20)

        # Scrollable cards
        self._scroll_canvas = tk.Canvas(list_frame, bg=BG_DARK, highlightthickness=0)
        sb = tk.Scrollbar(list_frame, orient="vertical", command=self._scroll_canvas.yview)
        self._scroll_frame = tk.Frame(self._scroll_canvas, bg=BG_DARK)
        self._scroll_frame.bind("<Configure>",
            lambda e: self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all")))
        self._scroll_canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")
        self._scroll_canvas.configure(yscrollcommand=sb.set)
        self._scroll_canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._refresh_cards()

        # Add new card
        add_frame = Card(self)
        add_frame.pack(fill="x", padx=20, pady=8)
        tk.Label(add_frame, text="+ Tambah Kartu Baru", bg=BG_CARD, fg=ACCENT,
                 font=FONT_BODY).pack(padx=12, pady=4, anchor="w")

        q_frame = tk.Frame(add_frame, bg=BG_CARD)
        q_frame.pack(fill="x", padx=12, pady=4)
        tk.Label(q_frame, text="Pertanyaan:", bg=BG_CARD, fg=TEXT_SEC, font=FONT_SMALL).pack(anchor="w")
        self._new_q = StyledText(add_frame, height=2)
        self._new_q.pack(fill="x", padx=12, pady=2)
        tk.Label(add_frame, text="Jawaban:", bg=BG_CARD, fg=TEXT_SEC, font=FONT_SMALL).pack(padx=12, anchor="w")
        self._new_a = StyledText(add_frame, height=2)
        self._new_a.pack(fill="x", padx=12, pady=2)

        btn_row = tk.Frame(add_frame, bg=BG_CARD)
        btn_row.pack(padx=12, pady=8, anchor="e")
        StyledButton(btn_row, "⚡ Bulk Add", self._bulk_add_flashcards, style="purple").pack(side="left", padx=4)
        StyledButton(btn_row, "＋ Tambah", self._add_card, style="success").pack(side="left", padx=4)

    def _bulk_add_flashcards(self):
        """Menambah banyak flashcard sekaligus dari format Q: A: atau Baris1=Q, Baris2=A."""
        dlg = tk.Toplevel(self)
        dlg.title("Bulk Add Flashcards")
        dlg.geometry("500x500")
        dlg.configure(bg=BG_DARK)
        
        tk.Label(dlg, text="Format: Pertanyaan = Jawaban (satu per baris)", bg=BG_DARK, fg=TEXT_SEC, font=FONT_SMALL).pack(pady=10)
        txt = StyledText(dlg, height=15)
        txt.pack(fill="both", expand=True, padx=20, pady=10)
        
        def do_import():
            raw = txt.get("1.0", "end-1c").strip()
            if not raw: return
            lines = raw.split("\n")
            count = 0
            for line in lines:
                if "=" in line:
                    q, _, a = line.partition("=")
                    self._cards.append({
                        "id": f"fc{len(self._cards)+1}",
                        "question": q.strip(),
                        "answer": a.strip()
                    })
                    count += 1
            self._refresh_cards()
            dlg.destroy()
            messagebox.showinfo("Bulk Add", f"Berhasil menambah {count} flashcard!")

        StyledButton(dlg, "Import", do_import, style="success").pack(pady=10)

        # Bottom
        bot = tk.Frame(self, bg=BG_DARK)
        bot.pack(pady=12)
        StyledButton(bot, "✓  Simpan Semua", self._save, style="primary").pack(side="left", padx=6)
        StyledButton(bot, "Batal", self.destroy, style="ghost").pack(side="left", padx=6)

    def _refresh_cards(self):
        for w in self._scroll_frame.winfo_children():
            w.destroy()
        for i, card in enumerate(self._cards):
            self._make_card_row(i, card)

    def _make_card_row(self, idx, card):
        row = Card(self._scroll_frame)
        row.pack(fill="x", pady=3, padx=4)

        header = tk.Frame(row, bg=BG_CARD)
        header.pack(fill="x", padx=10, pady=(6, 2))
        tk.Label(header, text=f"#{idx+1}", bg=BG_CARD, fg=ACCENT, font=FONT_SMALL).pack(side="left")
        StyledButton(header, "🗑", lambda i=idx: self._delete_card(i),
                     style="danger", padx=6, pady=2).pack(side="right")

        tk.Label(row, text="Q:", bg=BG_CARD, fg=TEXT_SEC, font=FONT_SMALL).pack(padx=10, anchor="w")
        q_text = StyledText(row, height=2)
        q_text.pack(fill="x", padx=10, pady=2)
        q_text.insert("1.0", card.get("question", ""))

        tk.Label(row, text="A:", bg=BG_CARD, fg=TEXT_SEC, font=FONT_SMALL).pack(padx=10, anchor="w")
        a_text = StyledText(row, height=2)
        a_text.pack(fill="x", padx=10, pady=(2, 6))
        a_text.insert("1.0", card.get("answer", ""))

        # Save references
        card["_q_widget"] = q_text
        card["_a_widget"] = a_text

    def _add_card(self):
        q = self._new_q.get("1.0", "end-1c").strip()
        a = self._new_a.get("1.0", "end-1c").strip()
        if not q or not a:
            messagebox.showwarning("Perhatian", "Pertanyaan dan jawaban wajib diisi!", parent=self)
            return
        new_id = f"fc{len(self._cards)+1}"
        self._cards.append({"id": new_id, "question": q, "answer": a})
        self._new_q.delete("1.0", "end")
        self._new_a.delete("1.0", "end")
        self._refresh_cards()
        self._scroll_canvas.update_idletasks()
        self._scroll_canvas.yview_moveto(1.0)

    def _delete_card(self, idx):
        del self._cards[idx]
        self._refresh_cards()

    def _save(self):
        # Collect edits from widgets
        saved = []
        for card in self._cards:
            q_widget = card.get("_q_widget")
            a_widget = card.get("_a_widget")
            q = q_widget.get("1.0", "end-1c").strip() if q_widget else card.get("question", "")
            a = a_widget.get("1.0", "end-1c").strip() if a_widget else card.get("answer", "")
            saved.append({
                "id": card.get("id", f"fc{len(saved)+1}"),
                "question": q,
                "answer": a
            })
        self.result = saved
        self.destroy()


# ─── Dialog Quiz ──────────────────────────────────────────────────────────────
class QuizDialog(tk.Toplevel):
    def __init__(self, parent, questions=None):
        super().__init__(parent)
        self.result = None
        self.title("📝  Edit Kuis")
        self.configure(bg=BG_DARK)
        self.geometry("720x680")
        self._questions = deep_copy(questions) if questions else []
        self._build()
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def _build(self):
        tk.Label(self, text="📝  Kelola Soal Kuis", bg=BG_DARK, fg=TEXT_PRI,
                 font=FONT_HEAD).pack(padx=20, pady=12, anchor="w")

        # Scrollable
        self._scroll_canvas = tk.Canvas(self, bg=BG_DARK, highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=self._scroll_canvas.yview)
        self._sf = tk.Frame(self._scroll_canvas, bg=BG_DARK)
        self._sf.bind("<Configure>",
            lambda e: self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all")))
        self._scroll_canvas.create_window((0, 0), window=self._sf, anchor="nw")
        self._scroll_canvas.configure(yscrollcommand=sb.set)
        self._scroll_canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        sb.pack(side="right", fill="y", padx=(0, 10))

        self._q_frames = []
        for i, q in enumerate(self._questions):
            self._make_q_row(i, q)

        # Add new
        StyledButton(self._sf, "＋ Tambah Soal Baru", self._add_question,
                     style="success").pack(pady=12, padx=8)

        # Bottom
        bot = tk.Frame(self, bg=BG_DARK)
        bot.pack(side="bottom", pady=12)
        StyledButton(bot, "✓  Simpan", self._save, style="primary").pack(side="left", padx=6)
        StyledButton(bot, "Batal", self.destroy, style="ghost").pack(side="left", padx=6)

    def _make_q_row(self, idx, q):
        card = Card(self._sf)
        card.pack(fill="x", pady=4, padx=6)

        hdr = tk.Frame(card, bg=BG_CARD)
        hdr.pack(fill="x", padx=10, pady=(6, 2))
        tk.Label(hdr, text=f"Soal #{idx+1}", bg=BG_CARD, fg=ACCENT, font=FONT_SMALL).pack(side="left")
        StyledButton(hdr, "🗑", lambda i=idx: self._del_q(i),
                     style="danger", padx=6, pady=2).pack(side="right")

        tk.Label(card, text="Pertanyaan:", bg=BG_CARD, fg=TEXT_SEC, font=FONT_SMALL).pack(padx=10, anchor="w")
        q_text = StyledText(card, height=2)
        q_text.pack(fill="x", padx=10, pady=2)
        q_text.insert("1.0", q.get("question", ""))

        # 4 options
        opts_widgets = []
        for j in range(4):
            opt_row = tk.Frame(card, bg=BG_CARD)
            opt_row.pack(fill="x", padx=10, pady=1)
            lbl = "ABCD"[j]
            tk.Label(opt_row, text=f"{lbl}.", bg=BG_CARD, fg=TEXT_SEC,
                     font=FONT_SMALL, width=2).pack(side="left")
            oe = StyledEntry(opt_row)
            oe.pack(side="left", fill="x", expand=True)
            options = q.get("options", ["", "", "", ""])
            if j < len(options):
                oe.insert(0, options[j])
            opts_widgets.append(oe)

        # Correct answer
        ans_row = tk.Frame(card, bg=BG_CARD)
        ans_row.pack(fill="x", padx=10, pady=4)
        tk.Label(ans_row, text="Jawaban benar (0-3):", bg=BG_CARD, fg=TEXT_SEC,
                 font=FONT_SMALL).pack(side="left", padx=(0, 8))
        ans_var = tk.StringVar(value=str(q.get("answer", 0)))
        ans_combo = ttk.Combobox(ans_row, textvariable=ans_var, values=["0 (A)", "1 (B)", "2 (C)", "3 (D)"],
                                  width=10, state="readonly")
        ans_combo.pack(side="left")

        tk.Label(card, text="Penjelasan (opsional):", bg=BG_CARD, fg=TEXT_SEC,
                 font=FONT_SMALL).pack(padx=10, anchor="w")
        exp_text = StyledText(card, height=2)
        exp_text.pack(fill="x", padx=10, pady=(2, 8))
        exp_text.insert("1.0", q.get("explanation", ""))

        self._q_frames.append({
            "q_text": q_text,
            "opts": opts_widgets,
            "ans_var": ans_var,
            "exp_text": exp_text,
            "id": q.get("id", f"q{idx+1}")
        })

    def _add_question(self):
        new_q = {"id": f"q{len(self._questions)+1}", "type": "multiple_choice",
                 "question": "", "options": ["", "", "", ""], "answer": 0, "explanation": ""}
        self._questions.append(new_q)
        self._make_q_row(len(self._q_frames), new_q)
        self._scroll_canvas.update_idletasks()
        self._scroll_canvas.yview_moveto(1.0)

    def _del_q(self, idx):
        del self._questions[idx]
        # Rebuild
        for w in self._sf.winfo_children():
            w.destroy()
        self._q_frames = []
        for i, q in enumerate(self._questions):
            self._make_q_row(i, q)
        StyledButton(self._sf, "＋ Tambah Soal Baru", self._add_question,
                     style="success").pack(pady=12, padx=8)

    def _save(self):
        saved = []
        for i, frame in enumerate(self._q_frames):
            ans_raw = frame["ans_var"].get().split(" ")[0]
            try:
                ans = int(ans_raw)
            except ValueError:
                ans = 0
            saved.append({
                "id": frame["id"],
                "type": "multiple_choice",
                "question": frame["q_text"].get("1.0", "end-1c").strip(),
                "options": [e.get().strip() for e in frame["opts"]],
                "answer": ans,
                "explanation": frame["exp_text"].get("1.0", "end-1c").strip()
            })
        self.result = saved
        self.destroy()


# ─── DSL Translator ──────────────────────────────────────────────────────────
class DSLTranslator:
    """
    Mengonversi JSON ke bahasa kustom (DSL) untuk efisiensi token AI.
    """
    @staticmethod
    def to_dsl(topic_data):
        lines = []
        lines.append(f"TOPIC_TITLE: {topic_data.get('title', '')}")
        lines.append(f"TOPIC_DESC: {topic_data.get('description', '')}")
        
        # Lessons
        for lesson in topic_data.get("lessons", []):
            lines.append(f"\nLESSON_START: {lesson.get('id', 'new-lesson')}")
            lines.append(f"LESSON_TITLE: {lesson.get('title', '')}")
            lines.append(f"LESSON_TIME: {lesson.get('estMinutes', 10)}")
            
            for item in lesson.get("content", []):
                t = item.get("type", "text")
                if t == "heading":
                    lvl = item.get("level", 1)
                    prefix = "HEADING" if lvl == 1 else f"H{lvl}"
                    lines.append(f"{prefix}: {item.get('text', '')}")
                elif t == "text":
                    lines.append(f"TEXT: {item.get('text', '')}")
                elif t == "highlight":
                    lines.append(f"HIGHLIGHT: {item.get('text', '')}")
                elif t == "list":
                    for it in item.get("items", []):
                        lines.append(f"LIST: {it}")
                elif t == "table":
                    headers = ",".join(item.get("headers", []))
                    lines.append(f"TABLE_HEADER: {headers}")
                    for row in item.get("rows", []):
                        lines.append(f"TABLE_ROW: {','.join(str(c) for c in row)}")
                elif t == "math":
                    lines.append(f"MATH: {item.get('tex', '')}")
            lines.append("LESSON_END")

        # Flashcards
        if topic_data.get("flashcards"):
            lines.append("\nFLASHCARDS_START")
            for fc in topic_data.get("flashcards", []):
                lines.append(f"FC_Q: {fc.get('question', '')}")
                lines.append(f"FC_A: {fc.get('answer', '')}")
            lines.append("FLASHCARDS_END")

        # Quiz
        quiz = topic_data.get("quiz", {})
        if quiz.get("questions"):
            lines.append("\nQUIZ_START")
            for q in quiz.get("questions", []):
                lines.append(f"Q_TEXT: {q.get('question', '')}")
                opts = q.get("options", ["", "", "", ""])
                for i, opt in enumerate(opts):
                    lines.append(f"Q_OPT: {'ABCD'[i]}) {opt}")
                lines.append(f"Q_ANS: {q.get('answer', 0)}")
                if q.get("explanation"):
                    lines.append(f"Q_EXP: {q.get('explanation')}")
            lines.append("QUIZ_END")
            
        return "\n".join(lines)

    @staticmethod
    def to_dsl(topic_data):
        lines = []
        lines.append(f"TOPIC_TITLE: {topic_data.get('title', '')}")
        lines.append(f"TOPIC_DESC: {topic_data.get('description', '')}")
        
        # Lessons
        for lesson in topic_data.get("lessons", []):
            lines.append(f"\n--- LESSON: {lesson.get('title', 'Untitled')} [{lesson.get('id', 'new')}] ---")
            lines.append(f"EST_TIME: {lesson.get('estMinutes', 10)}")
            
            for item in lesson.get("content", []):
                t = item.get("type", "text")
                if t == "heading":
                    lvl = item.get("level", 1)
                    prefix = "HEADING" if lvl == 1 else f"H{lvl}"
                    lines.append(f"{prefix}: {item.get('text', '')}")
                elif t == "text":
                    lines.append(f"TEXT: {item.get('text', '')}")
                elif t == "highlight":
                    lines.append(f"HIGHLIGHT: {item.get('text', '')}")
                elif t == "list":
                    lines.append("LIST_START")
                    for it in item.get("items", []):
                        lines.append(f"  • {it}")
                    lines.append("LIST_END")
                elif t == "table":
                    headers = " | ".join(item.get("headers", []))
                    lines.append(f"TABLE_START: {headers}")
                    for row in item.get("rows", []):
                        lines.append(f"  ROW: {' | '.join(str(c) for c in row)}")
                    lines.append("TABLE_END")
                elif t == "math":
                    lines.append(f"MATH: {item.get('tex', '')}")
                elif t == "chart":
                    data_str = json.dumps(item.get("data", []))
                    lines.append(f"CHART: {item.get('chartType', 'bar')} {data_str}")
                elif t == "simulation":
                    lines.append(f"SIMULATION: {item.get('simType', 'atom')}")
                elif t == "image":
                    lines.append(f"IMAGE: {item.get('url', '')}")
                    if item.get("caption"):
                        lines.append(f"CAPTION: {item.get('caption', '')}")
            lines.append("--- END_LESSON ---")

        # Flashcards
        if topic_data.get("flashcards"):
            lines.append("\n=== FLASHCARDS ===")
            for fc in topic_data.get("flashcards", []):
                lines.append(f"Q: {fc.get('question', '')}")
                lines.append(f"A: {fc.get('answer', '')}")
            lines.append("=== END_FLASHCARDS ===")

        # Quiz
        quiz = topic_data.get("quiz", {})
        if quiz.get("questions"):
            lines.append("\n=== QUIZ ===")
            for q in quiz.get("questions", []):
                lines.append(f"QUESTION: {q.get('question', '')}")
                opts = q.get("options", ["", "", "", ""])
                for i, opt in enumerate(opts):
                    lines.append(f"  {'ABCD'[i]}) {opt}")
                lines.append(f"CORRECT: {q.get('answer', 0)}")
                if q.get("explanation"):
                    lines.append(f"EXP: {q.get('explanation')}")
            lines.append("=== END_QUIZ ===")
            
        return "\n".join(lines)

    @staticmethod
    def from_dsl(dsl_text):
        topic = {}
        lines = dsl_text.strip().split("\n")
        
        current_lesson = None
        current_table = None
        current_list = None
        in_flashcards = False
        in_quiz = False
        current_q = None

        def flush_all():
            nonlocal current_lesson, current_table, current_list, current_q
            if current_lesson:
                if current_table: 
                    current_lesson["content"].append(current_table)
                    current_table = None
                if current_list:
                    current_lesson["content"].append(current_list)
                    current_list = None
                # Check if this lesson is already in topic
                if not any(l.get("id") == current_lesson["id"] for l in topic.get("lessons", [])):
                    topic.setdefault("lessons", []).append(current_lesson)
            
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Smart Block Detection
            if "--- LESSON:" in line:
                flush_all()
                topic.setdefault("lessons", [])
                try:
                    title_part = line.split(":")[1].split("[")[0].strip()
                    id_part = line.split("[")[1].split("]")[0].strip() if "[" in line else make_id(title_part)
                except:
                    title_part = "Untitled"; id_part = "new"
                current_lesson = {"id": id_part, "title": title_part, "estMinutes": 10, "content": []}
                continue
            elif "--- END_LESSON ---" in line:
                flush_all()
                current_lesson = None
                continue
            elif "=== FLASHCARDS ===" in line:
                flush_all()
                topic.setdefault("flashcards", [])
                in_flashcards = True; continue
            elif "=== END_FLASHCARDS ===" in line:
                in_flashcards = False; continue
            elif "=== QUIZ ===" in line:
                flush_all()
                topic.setdefault("quiz", {"questions": []})
                in_quiz = True; continue
            elif "=== END_QUIZ ===" in line:
                in_quiz = False; continue

            # Block Markers
            u_line = line.upper()
            if u_line.startswith("LIST_START"):
                if current_list and current_lesson: current_lesson["content"].append(current_list)
                current_list = {"type": "list", "items": []}
                continue
            elif u_line.startswith("LIST_END"):
                if current_lesson and current_list: current_lesson["content"].append(current_list)
                current_list = None
                continue
            elif u_line.startswith("TABLE_START"):
                if current_table and current_lesson: current_lesson["content"].append(current_table)
                # Parse headers from TABLE_START: H1 | H2
                headers = []
                if ":" in line:
                    headers = [h.strip() for h in line.partition(":")[2].split("|")]
                current_table = {"type": "table", "headers": headers, "rows": []}
                continue
            elif u_line.startswith("TABLE_END"):
                if current_lesson and current_table: current_lesson["content"].append(current_table)
                current_table = None
                continue

            # Item Detection (Bullets)
            if line.startswith("•") or line.startswith("- "):
                it = line.lstrip("•- ").strip()
                if not current_list: current_list = {"type": "list", "items": []}
                current_list["items"].append(it)
                continue

            # Prefix-based Parsing
            if ":" in line:
                prefix, _, rest = line.partition(":")
                prefix = prefix.strip().upper()
                rest = rest.strip()

                # Global Meta
                if prefix == "TOPIC_TITLE": topic["title"] = rest; topic["id"] = make_id(rest)
                elif prefix == "TOPIC_DESC": topic["description"] = rest

                # Lesson Context
                elif current_lesson:
                    if prefix == "EST_TIME": 
                        try: current_lesson["estMinutes"] = int(re.search(r"\d+", rest).group())
                        except: pass
                    elif prefix in ("HEADING", "H1"): current_lesson["content"].append({"type": "heading", "text": rest})
                    elif prefix.startswith("H") and prefix[1:].isdigit():
                        current_lesson["content"].append({"type": "heading", "level": int(prefix[1:]), "text": rest})
                    elif prefix == "TEXT": current_lesson["content"].append({"type": "text", "text": rest})
                    elif prefix == "HIGHLIGHT": current_lesson["content"].append({"type": "highlight", "text": rest})
                    elif prefix == "ROW":
                        if current_table: current_table["rows"].append([c.strip() for c in rest.split("|")])
                    elif prefix == "MATH": current_lesson["content"].append({"type": "math", "tex": rest, "display": True})
                    elif prefix == "CHART":
                        try:
                            parts = rest.split(" ", 1)
                            ctype = parts[0] if parts else "bar"
                            data = json.loads(parts[1]) if len(parts) > 1 else []
                            current_lesson["content"].append({"type": "chart", "chartType": ctype, "data": data})
                        except: pass
                    elif prefix == "SIMULATION":
                        current_lesson["content"].append({"type": "simulation", "simType": rest if rest in ["atom", "cells", "newton", "circuit", "magnet", "wave", "piston", "geometry"] else "atom"})
                    elif prefix == "IMAGE":
                        current_lesson["content"].append({"type": "image", "url": rest, "caption": ""})
                    elif prefix == "CAPTION":
                        if current_lesson["content"] and current_lesson["content"][-1]["type"] == "image":
                            current_lesson["content"][-1]["caption"] = rest
                    else:
                        if current_list: current_list["items"].append(line)
                        else: current_lesson["content"].append({"type": "text", "text": line})

                # Flashcards Context
                elif in_flashcards:
                    if prefix == "Q": topic["flashcards"].append({"id": f"fc{len(topic['flashcards'])+1}", "question": rest, "answer": ""})
                    elif prefix == "A" and topic["flashcards"]: topic["flashcards"][-1]["answer"] = rest

                # Quiz Context
                elif in_quiz:
                    if prefix == "QUESTION":
                        current_q = {"id": f"q{len(topic['quiz']['questions'])+1}", "type": "multiple_choice", "question": rest, "options": [], "answer": 0, "explanation": ""}
                        topic["quiz"]["questions"].append(current_q)
                    elif prefix.startswith("Q_OPT") or (re.match(r"^[A-D]$|^(OPTION|OPT)$", prefix)):
                        if current_q: current_q["options"].append(rest)
                    elif prefix == "CORRECT":
                        if current_q:
                            try: 
                                if rest.isdigit(): current_q["answer"] = int(rest)
                                else: current_q["answer"] = ord(rest.upper()[0]) - 65
                            except: pass
                    elif prefix == "EXP":
                        if current_q: current_q["explanation"] = rest
            else:
                if current_lesson:
                    if current_list: current_list["items"].append(line)
                    else:
                        current_lesson["content"].append({"type": "text", "text": line})
                elif current_q and in_quiz:
                    # Fix: Correctly handle options without prefix in AI response
                    if re.match(r"^[A-D]\)", line):
                        current_q["options"].append(line[2:].strip())
                    elif re.match(r"^[A-D]\.", line):
                        current_q["options"].append(line[2:].strip())
        
        flush_all()
        return topic


# ─── Prompt Generator ────────────────────────────────────────────────────────
class PromptGenerator:
    @staticmethod
    def get_system_prompt(subject="IPA"):
        return f"""Kamu adalah asisten pengembang konten edukasi {subject} tingkat SMP (Sekolah Menengah Pertama). 
Tugasmu adalah memproses materi dalam bahasa kustom (DSL) yang efisien token.

TARGET AUDIENS: Siswa SMP (Kelas 7, 8, dan 9). 
KONTEN: Pastikan materi sesuai dengan kurikulum SMP. Gunakan bahasa yang mudah dipahami remaja, berikan contoh yang relevan dengan kehidupan sehari-hari, dan HINDARI materi tingkat SMA/Perguruan Tinggi yang terlalu kompleks.

ATURAN BAHASA (DSL) - VERSI ADVANCE:
Struktur Utama:
- TOPIC_TITLE: [judul]
- TOPIC_DESC: [deskripsi]

Blok Pelajaran:
--- LESSON: [Judul] [id] ---
EST_TIME: [menit]
HEADING: [teks]
H2: [teks]
TEXT: [paragraf]
HIGHLIGHT: [teks penting]
LIST_START
  • [item 1]
  • [item 2]
LIST_END
TABLE_START: Header1 | Header2
  ROW: Kolom1 | Kolom2
TABLE_END
MATH: [Latex]
CHART: bar | line | area [data json: {{name, value}}[]]
SIMULATION: atom | cells | newton | circuit | magnet | wave | piston | geometry
IMAGE: [url]
CAPTION: [deskripsi gambar]
--- END_LESSON ---

Blok Flashcards:
=== FLASHCARDS ===
Q: [Pertanyaan]
A: [Jawaban]
=== END_FLASHCARDS ===

Blok Kuis:
=== QUIZ ===
QUESTION: [Soal]
  A) [opsi A]
  B) [opsi B]
  C) [opsi C]
  D) [opsi D]
CORRECT: [0-3]
EXP: [Penjelasan]
=== END_QUIZ ===

PENTING: Selalu balas HANYA dengan kode DSL tersebut tanpa penjelasan tambahan. Kamu bebas mengekspresikan materi sekreatif mungkin selama mengikuti struktur DSL di atas."""

    @staticmethod
    def get_user_prompt(action, target_topic, subject="IPA"):
        prompts = {
            "generate_lesson": f"Buatlah 1 pelajaran baru untuk topik '{target_topic}' ({subject}) tingkat SMP menggunakan format DSL.",
            "add_flashcards": f"Tambahkan 5 flashcard baru untuk topik '{target_topic}' ({subject}) tingkat SMP menggunakan format DSL (FC_Q dan FC_A).",
            "add_quiz": f"Tambahkan 5 soal kuis pilihan ganda baru untuk topik '{target_topic}' ({subject}) tingkat SMP menggunakan format DSL.",
            "improve_content": f"Perbaiki dan lengkapi materi pada topik '{target_topic}' ({subject}) tingkat SMP berikut agar lebih mendalam namun tetap ringkas.",
            "summarize": f"Buat ringkasan materi untuk topik '{target_topic}' ({subject}) tingkat SMP dalam format DSL yang padat."
        }
        return prompts.get(action, f"Proses topik '{target_topic}' ({subject}) tingkat SMP ini.")


# ─── AI Mode Window ───────────────────────────────────────────────────────────
class AIModeWindow(tk.Toplevel):
    """
    Advanced Zen AI Mode: Real-time, minimalist, and high-automation flow.
    """
    def __init__(self, parent, data, on_import_callback):
        super().__init__(parent)
        self.title("🤖 Zen AI Assistant")
        self.configure(bg=BG_DARK)
        self.geometry("1100x850")
        self._data = data
        self._callback = on_import_callback
        self._build()
        self.transient(parent)
        self.grab_set()

    def _build(self):
        # Top Header (Minimal)
        hdr = tk.Frame(self, bg=BG_PANEL, height=70)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        
        tk.Label(hdr, text="Zen AI Content Flow", bg=BG_PANEL, fg=ACCENT,
                 font=FONT_TITLE).pack(side="left", padx=25)
        
        # Action Center (Floating look)
        center_f = tk.Frame(self, bg=BG_DARK)
        center_f.pack(fill="both", expand=True, padx=30, pady=20)

        # Left Column: Configuration & Prompt
        left_col = tk.Frame(center_f, bg=BG_DARK)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 15))

        # Config Card
        cfg_card = Card(left_col)
        cfg_card.pack(fill="x", pady=(0, 15))
        
        tk.Label(cfg_card, text="1. Set Your Goal", bg=BG_CARD, fg=TEXT_SEC, font=FONT_SMALL).pack(anchor="w", padx=15, pady=(15, 5))
        
        topics = self._data.get("topics", [])
        topic_names = [f"📚 {t.get('title', '?')}" for t in topics]
        self._topic_var = tk.StringVar(value=topic_names[0] if topic_names else "")
        topic_combo = ttk.Combobox(cfg_card, textvariable=self._topic_var, values=topic_names, width=35, state="readonly")
        topic_combo.pack(padx=15, pady=5, fill="x")
        
        # AUTO-SYNC: When you change the goal topic, the import target updates automatically and inputs reset
        topic_combo.bind("<<ComboboxSelected>>", self._on_goal_change)
        
        self._ai_action = tk.StringVar(value="improve_content")
        actions = [
            ("🧠 Enhance Depth (Advance)", "improve_content"),
            ("📖 Generate New Lesson", "generate_lesson"),
            ("🃏 Add Pro Flashcards", "add_flashcards"),
            ("📝 Create HOTS Quiz", "add_quiz"),
            ("📊 Material Summary", "summarize")
        ]
        ttk.Combobox(cfg_card, textvariable=self._ai_action, values=[a[0] for a in actions], state="readonly", width=35).pack(padx=15, pady=10, fill="x")
        self._action_map = {a[0]: a[1] for a in actions}
        
        StyledButton(cfg_card, "🚀 Generate & Copy Prompt", self._auto_export, style="primary").pack(fill="x", padx=15, pady=(5, 20))

        # Guide/Status Card
        guide_card = Card(left_col)
        guide_card.pack(fill="both", expand=True)
        tk.Label(guide_card, text="Pro Tips:", bg=BG_CARD, fg=WARNING, font=FONT_HEAD).pack(anchor="w", padx=15, pady=(15, 5))
        
        tips = [
            "• AI results are real-time synced to your JSON.",
            "• Use GPT-4 or Claude 3.5 for best DSL parsing.",
            "• No manual formatting needed, just paste & go.",
            "• Multi-topic updates are supported via DSL."
        ]
        for tip in tips:
            tk.Label(guide_card, text=tip, bg=BG_CARD, fg=TEXT_SEC, font=FONT_SMALL, justify="left").pack(anchor="w", padx=20, pady=2)

        # Right Column: The Input Zone
        right_col = tk.Frame(center_f, bg=BG_DARK)
        right_col.pack(side="left", fill="both", expand=True, padx=(15, 0))

        # Import Card
        imp_card = Card(right_col)
        imp_card.pack(fill="both", expand=True)
        
        tk.Label(imp_card, text="2. Paste AI Response Below", bg=BG_CARD, fg=SUCCESS, font=FONT_HEAD).pack(anchor="w", padx=15, pady=(15, 5))
        
        self._import_in = StyledText(imp_card, font=FONT_MONO)
        self._import_in.pack(fill="both", expand=True, padx=15, pady=5)
        
        bot_f = tk.Frame(imp_card, bg=BG_CARD)
        bot_f.pack(fill="x", padx=15, pady=15)
        
        tk.Label(bot_f, text="Sync Target:", bg=BG_CARD, fg=TEXT_SEC, font=FONT_SMALL).pack(side="left")
        self._import_target_var = tk.StringVar(value=topic_names[0] if topic_names else "")
        ttk.Combobox(bot_f, textvariable=self._import_target_var, values=topic_names, width=30, state="readonly").pack(side="left", padx=10)
        
        StyledButton(bot_f, "⚡ Fast Sync & Auto-Save", self._do_import, style="success").pack(side="right")

    def _on_goal_change(self, event=None):
        """Update sync target and clear inputs when goal changes."""
        self._import_target_var.set(self._topic_var.get())
        if hasattr(self, "_import_in"):
            self._import_in.delete("1.0", "end")

    def _auto_export(self):
        """Otomatis generate prompt + DSL dan salin ke clipboard."""
        if not hasattr(self, "_prompt_out"):
            self._prompt_out = tk.Text()
            self._dsl_out = tk.Text()
            
        self._do_export()
        combined = f"{self._prompt_out.get('1.0', 'end-1c')}\n\nDATA DSL:\n{self._dsl_out.get('1.0', 'end-1c')}"
        self.clipboard_clear()
        self.clipboard_append(combined)
        messagebox.showinfo("🤖 Zen AI", "AI Prompt & Material Data Copied!\nPaste it into your AI assistant.")

    def _do_export(self):
        sel_topic_name = self._topic_var.get().replace("📚 ", "")
        sel_action_label = self._ai_action.get()
        action_key = self._action_map.get(sel_action_label, "improve_content")
        
        topics = self._data.get("topics", [])
        topic = next((t for t in topics if t.get("title") == sel_topic_name), None)
        
        if not topic:
            messagebox.showerror("Error", "Topik tidak ditemukan!")
            return

        # Generate DSL
        dsl = DSLTranslator.to_dsl(topic)
        
        # Subject Name
        subject = self._data.get("name", "IPA")
        
        # Generate Prompts
        sys_p = PromptGenerator.get_system_prompt(subject)
        usr_p = PromptGenerator.get_user_prompt(action_key, sel_topic_name, subject)
        
        full_prompt = f"SYSTEM PROMPT:\n{sys_p}\n\nUSER PROMPT:\n{usr_p}"
        
        self._prompt_out.delete("1.0", "end")
        self._prompt_out.insert("1.0", full_prompt)
        
        self._dsl_out.delete("1.0", "end")
        self._dsl_out.insert("1.0", dsl)

    def _copy_text(self, widget):
        text = widget.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("✓", "Teks berhasil disalin!")

    def _do_import(self):
        raw_input = self._import_in.get("1.0", "end-1c").strip()
        if not raw_input:
            messagebox.showwarning("Error", "Tidak ada DSL untuk diimport!")
            return

        # Try to find the DSL block if AI added conversational text
        # Look for the first recognized DSL header
        known_headers = ["TOPIC_TITLE:", "LESSON_START:", "FLASHCARDS_START", "QUIZ_START"]
        start_idx = -1
        for header in known_headers:
            idx = raw_input.find(header)
            if idx != -1 and (start_idx == -1 or idx < start_idx):
                start_idx = idx
        
        if start_idx != -1:
            raw_dsl = raw_input[start_idx:].strip()
        else:
            raw_dsl = raw_input

        # Clean markdown if AI wrapped it
        raw_dsl = re.sub(r"```[a-zA-Z]*\n", "", raw_dsl)
        raw_dsl = raw_dsl.replace("```", "")
        # Remove any "DATA DSL:" line if it exists
        raw_dsl = re.sub(r"^DATA DSL:\s*\n?", "", raw_dsl, flags=re.MULTILINE)

        try:
            # Parse DSL to JSON
            new_topic_data = DSLTranslator.from_dsl(raw_dsl)
            
            if not new_topic_data:
                messagebox.showerror("Error", "Gagal mengenali format DSL. Pastikan format benar.")
                return

            sel_target = self._import_target_var.get().replace("📚 ", "")
            topics = self._data.get("topics", [])
            target_topic = next((t for t in topics if t.get("title") == sel_target), None)
            
            if target_topic:
                topic_id = target_topic.get("id")
                self._callback("full_topic_update", topic_id, new_topic_data)
                messagebox.showinfo("✓", f"Topik '{sel_target}' berhasil diperbarui dan disimpan!")
            else:
                self._callback("topic", None, new_topic_data)
                messagebox.showinfo("✓", f"Topik baru '{new_topic_data.get('title')}' berhasil ditambahkan!")
                
        except Exception as e:
            messagebox.showerror("DSL Error", f"Gagal memproses DSL:\n{str(e)}")


PROMPT_GUIDE = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PANDUAN PROMPT UNTUK AI — HEMAT TOKEN                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 PRINSIP UTAMA: Jangan paste seluruh JSON ke AI!
   → Export HANYA bagian yang mau diedit (flashcard / quiz / satu topik)
   → Minta AI balas HANYA JSON, tanpa penjelasan tambahan

═══════════════════════════════════════════════════════════════════════════════
📝 TEMPLATE PROMPT — TAMBAH FLASHCARD
───────────────────────────────────────────────────────────────────────────────
[Paste hasil export flashcard di sini]

Tambahkan 4 flashcard baru tentang topik ini yang belum ada di daftar.
Format SAMA PERSIS dengan yang sudah ada.
BALAS HANYA dengan JSON array lengkap (termasuk yang lama + yang baru).
Jangan tambahkan penjelasan, markdown, atau teks lain.

═══════════════════════════════════════════════════════════════════════════════
📝 TEMPLATE PROMPT — PERBAIKI SOAL KUIS
───────────────────────────────────────────────────────────────────────────────
[Paste hasil export quiz di sini]

Perbaiki soal-soal kuis di atas:
- Pastikan semua soal HOCA (Higher Order Thinking)
- Tambahkan explanation untuk soal yang belum ada
- Tambahkan 2 soal baru tentang [topik spesifik]
BALAS HANYA dengan JSON array questions yang sudah diperbarui.

═══════════════════════════════════════════════════════════════════════════════
📝 TEMPLATE PROMPT — BUAT TOPIK BARU
───────────────────────────────────────────────────────────────────────────────
Buat topik IPA SMP baru tentang [nama topik].
Gunakan format JSON berikut PERSIS:
{
  "id": "slug-topik",
  "title": "Judul Topik",
  "description": "Deskripsi singkat",
  "lessons": [{"id": "...", "title": "...", "estMinutes": 10, "content": [...]}],
  "flashcards": [{"id": "fc1", "question": "...", "answer": "..."}],
  "quiz": {"questions": [{"id": "q1", "type": "multiple_choice", 
            "question": "...", "options": ["A","B","C","D"], 
            "answer": 0, "explanation": "..."}]}
}
Buat minimal 6 flashcard dan 5 soal kuis.
BALAS HANYA dengan JSON (tanpa ```json atau penjelasan).

═══════════════════════════════════════════════════════════════════════════════
💡 TIPS
───────────────────────────────────────────────────────────────────────────────
✅ Export mode "Flashcard saja" = ~200-400 token (vs seluruh topik = 2000+ token)
✅ Selalu minta AI balas JSON saja tanpa markdown
✅ Gunakan mode Import > "Flashcard" atau "Quiz" untuk merge otomatis
✅ Backup file JSON sebelum import besar-besaran

"""


# ─── Aplikasi Utama ────────────────────────────────────────────────────────────
class SubjectEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✏️  Subject JSON Editor")
        self.geometry("1280x780")
        self.configure(bg=BG_DARK)
        self.minsize(900, 600)

        self._data = {"id": "subject", "name": "Subject Name",
                      "description": "", "grade": [7, 8, 9],
                      "icon": "Book", "color": "soft", "topics": []}
        self._filepath = None
        self._selected_topic_idx = None
        self._unsaved = False

        self._style_ttk()
        self._build_ui()
        self._setup_shortcuts()
        self._update_title()
        self._load_subject_list()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_shortcuts(self):
        self.bind("<Control-s>", lambda e: self._save_file())
        self.bind("<Control-o>", lambda e: self._subject_combo.focus_set())
        self.bind("<Control-n>", lambda e: self._add_topic())
        self.bind("<Control-f>", lambda e: self._focus_search())
        self.bind("<Control-Shift-S>", lambda e: self._save_as())
        self.bind("<Control-q>", lambda e: self._on_close())

    def _focus_search(self):
        self._search_var.set("")
        self._search_entry.focus_set()

    # ── Styling ─────────────────────────────────────────────────────────────
    def _style_ttk(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background=BG_CARD, fieldbackground=BG_CARD,
                        foreground=TEXT_PRI, font=FONT_BODY, rowheight=36,
                        borderwidth=0)
        style.configure("Treeview.Heading", background=BG_PANEL, foreground=TEXT_SEC,
                        font=FONT_SMALL, borderwidth=0, relief="flat")
        style.map("Treeview", background=[("selected", ACCENT)],
                  foreground=[("selected", "#fff")])
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_PANEL, foreground=TEXT_SEC,
                        font=FONT_SMALL, padding=[12, 6])
        style.map("TNotebook.Tab", background=[("selected", BG_CARD)],
                  foreground=[("selected", ACCENT)])
        style.configure("TCombobox", fieldbackground=BG_INPUT, background=BG_INPUT,
                        foreground=TEXT_PRI, selectbackground=ACCENT)
        style.configure("Vertical.TScrollbar", background=BG_PANEL,
                        troughcolor=BG_DARK, borderwidth=0)

    # ── Layout Utama ─────────────────────────────────────────────────────────
    def _build_ui(self):
        # Toolbar
        self._build_toolbar()

        # Main pane
        paned = tk.PanedWindow(self, orient="horizontal", bg=BG_DARK,
                                sashwidth=4, sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=0, pady=0)

        # Left: Topic list
        left = tk.Frame(paned, bg=BG_PANEL, width=300)
        paned.add(left, minsize=220)
        self._build_left(left)

        # Right: Detail panel
        right = tk.Frame(paned, bg=BG_DARK)
        paned.add(right, minsize=500)
        self._build_right(right)

        # Status bar
        self._build_statusbar()

    def _build_toolbar(self):
        tb = tk.Frame(self, bg=BG_PANEL, height=52)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        # Logo
        tk.Label(tb, text="✏️ Editor", bg=BG_PANEL, fg=TEXT_PRI,
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=18)

        # Subject Selector
        tk.Label(tb, text="Pilih Pelajaran:", bg=BG_PANEL, fg=TEXT_SEC, font=FONT_SMALL).pack(side="left", padx=(10, 5))
        self._subject_var = tk.StringVar()
        self._subject_combo = ttk.Combobox(tb, textvariable=self._subject_var, width=20, state="readonly")
        self._subject_combo.pack(side="left", padx=5, pady=10)
        self._subject_combo.bind("<<ComboboxSelected>>", self._on_subject_change)

        # Buttons
        btns = [
            ("⚙️ Info", self._edit_subject_info, "ghost"),
            ("🔍 Global Search", self._global_search, "ghost"),
            ("💾 Export As", self._save_as, "ghost"),
            ("🤖 AI Mode", self._open_ai_mode, "purple"),
        ]
        for lbl, cmd, sty in btns:
            StyledButton(tb, lbl, cmd, style=sty).pack(side="left", padx=4, pady=10)

        # Info
        self._file_label = tk.Label(tb, text="Belum ada file", bg=BG_PANEL,
                                     fg=TEXT_DIM, font=FONT_SMALL)
        self._file_label.pack(side="left", padx=12)

    def _load_subject_list(self):
        """Muat daftar file JSON dari folder data/subjects."""
        subjects_dir = os.path.dirname(os.path.abspath(__file__))
        files = [f for f in os.listdir(subjects_dir) if f.endswith(".json")]
        self._subject_combo["values"] = files
        
        # Cari file yang sedang dibuka atau default ke ipa.json jika ada
        if self._filepath:
            fname = os.path.basename(self._filepath)
            if fname in files:
                self._subject_var.set(fname)
        elif "ipa.json" in files:
            self._subject_var.set("ipa.json")
            self._on_subject_change()

    def _on_subject_change(self, event=None):
        fname = self._subject_var.get()
        if not fname: return
        
        # Check if unsaved
        if self._unsaved:
            if not messagebox.askyesno("Konfirmasi", "Ada perubahan yang belum disimpan. Pindah pelajaran?"):
                # Reset combo to current file
                if self._filepath:
                    self._subject_var.set(os.path.basename(self._filepath))
                return

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
        self._load_file_path(path)

    def _edit_subject_info(self):
        """Edit metadata pelajaran (nama, deskripsi, image, grade)."""
        if not self._data: return
        dlg = SubjectDialog(self, self._data)
        if dlg.result:
            self._data.update(dlg.result)
            self._mark_unsaved()
            self._update_title()
            messagebox.showinfo("✓", "Informasi pelajaran berhasil diperbarui!")

    def _load_file_path(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._data = data
            self._filepath = path
            self._unsaved = False
            self._selected_topic_idx = None
            self._refresh_tree()
            self._clear_detail()
            self._update_title()
            self._set_status(f"✓ Berhasil memuat: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat file:\n{e}")

    def _global_search(self):
        """Mencari teks di seluruh topik dan pelajaran."""
        dlg = tk.Toplevel(self)
        dlg.title("Global Search & Replace")
        dlg.geometry("600x500")
        dlg.configure(bg=BG_DARK)
        
        tk.Label(dlg, text="Cari Teks:", bg=BG_DARK, fg=TEXT_SEC, font=FONT_SMALL).pack(pady=(20, 5), padx=20, anchor="w")
        search_ent = StyledEntry(dlg)
        search_ent.pack(fill="x", padx=20)
        
        tk.Label(dlg, text="Ganti Dengan (Opsional):", bg=BG_DARK, fg=TEXT_SEC, font=FONT_SMALL).pack(pady=(15, 5), padx=20, anchor="w")
        replace_ent = StyledEntry(dlg)
        replace_ent.pack(fill="x", padx=20)
        
        res_list = tk.Listbox(dlg, bg=BG_INPUT, fg=TEXT_PRI, font=FONT_SMALL, borderwidth=0, highlightthickness=0)
        res_list.pack(fill="both", expand=True, padx=20, pady=20)
        
        def do_search():
            q = search_ent.get().lower()
            if not q: return
            res_list.delete(0, "end")
            for i, topic in enumerate(self._data.get("topics", [])):
                if q in topic.get("title", "").lower():
                    res_list.insert("end", f"Topik: {topic.get('title')}")
                for j, lesson in enumerate(topic.get("lessons", [])):
                    if q in lesson.get("title", "").lower():
                        res_list.insert("end", f"  Pelajaran: {lesson.get('title')}")
                    # Check content
                    for item in lesson.get("content", []):
                        txt = item.get("text", "") or ",".join(item.get("headers", []))
                        if q in txt.lower():
                            res_list.insert("end", f"    Konten: {txt[:50]}...")
                            break

        def do_replace():
            q = search_ent.get()
            r = replace_ent.get()
            if not q: return
            if not messagebox.askyesno("Replace All", f"Ganti semua '{q}' dengan '{r}'?"): return
            
            count = 0
            for topic in self._data.get("topics", []):
                if q in topic["title"]:
                    topic["title"] = topic["title"].replace(q, r)
                    count += 1
                for lesson in topic.get("lessons", []):
                    if q in lesson["title"]:
                        lesson["title"] = lesson["title"].replace(q, r)
                        count += 1
                    for item in lesson.get("content", []):
                        if "text" in item and q in item["text"]:
                            item["text"] = item["text"].replace(q, r)
                            count += 1
            self._mark_unsaved()
            self._refresh_tree()
            messagebox.showinfo("Replace", f"Berhasil mengganti {count} kemunculan.")
            dlg.destroy()

        btn_f = tk.Frame(dlg, bg=BG_DARK)
        btn_f.pack(pady=10)
        StyledButton(btn_f, "Cari", do_search, style="primary").pack(side="left", padx=5)
        StyledButton(btn_f, "Ganti Semua", do_replace, style="danger").pack(side="left", padx=5)

    def _build_left(self, parent):
        # Header
        hdr = tk.Frame(parent, bg=BG_PANEL)
        hdr.pack(fill="x", padx=12, pady=10)
        tk.Label(hdr, text="📚  Daftar Topik", bg=BG_PANEL, fg=TEXT_PRI,
                 font=FONT_HEAD).pack(side="left")

        # Search
        search_frame = tk.Frame(parent, bg=BG_PANEL)
        search_frame.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(search_frame, text="🔍", bg=BG_PANEL, fg=TEXT_SEC).pack(side="left")
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._filter_topics)
        self._search_entry = StyledEntry(search_frame, textvariable=self._search_var, width=24)
        self._search_entry.pack(side="left", fill="x", expand=True, padx=4)

        # Tree
        tree_frame = tk.Frame(parent, bg=BG_PANEL)
        tree_frame.pack(fill="both", expand=True, padx=8)
        self._tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse")
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._tree.bind("<<TreeviewSelect>>", self._on_topic_select)

        # Bottom buttons
        bot = tk.Frame(parent, bg=BG_PANEL)
        bot.pack(fill="x", padx=12, pady=10)
        StyledButton(bot, "＋ Topik", self._add_topic, style="success").pack(side="left", padx=2)
        StyledButton(bot, "✏️ Edit", self._edit_topic, style="ghost").pack(side="left", padx=2)
        StyledButton(bot, "🗑 Hapus", self._delete_topic, style="danger").pack(side="left", padx=2)

        # Count label
        self._count_lbl = tk.Label(parent, text="", bg=BG_PANEL, fg=TEXT_DIM,
                                    font=FONT_SMALL)
        self._count_lbl.pack(pady=(0, 6))

    def _build_right(self, parent):
        # Action Bar at Top
        self._action_bar = tk.Frame(parent, bg=BG_PANEL, height=45)
        self._action_bar.pack(fill="x", side="top")
        self._action_bar.pack_propagate(False)
        
        tk.Label(self._action_bar, text="Opsi Topik:", bg=BG_PANEL, fg=TEXT_SEC, font=FONT_SMALL).pack(side="left", padx=(15, 5))
        StyledButton(self._action_bar, "✏️ Edit Topik", self._edit_topic, style="ghost", pady=2).pack(side="left", padx=2)
        StyledButton(self._action_bar, "🗑 Hapus Topik", self._delete_topic, style="danger", pady=2).pack(side="left", padx=2)
        
        # Tabs
        self._nb = ttk.Notebook(parent)
        self._nb.pack(fill="both", expand=True, padx=8, pady=8)

        # Tab: Info
        self._tab_info = tk.Frame(self._nb, bg=BG_DARK)
        self._nb.add(self._tab_info, text="  ℹ️  Info  ")
        self._build_info_tab(self._tab_info)

        # Tab: Pelajaran
        self._tab_lesson = tk.Frame(self._nb, bg=BG_DARK)
        self._nb.add(self._tab_lesson, text="  📖  Pelajaran  ")
        self._build_lesson_tab(self._tab_lesson)

        # Tab: Flashcard
        self._tab_fc = tk.Frame(self._nb, bg=BG_DARK)
        self._nb.add(self._tab_fc, text="  🃏  Flashcard  ")
        self._build_flashcard_tab(self._tab_fc)

        # Tab: Quiz
        self._tab_quiz = tk.Frame(self._nb, bg=BG_DARK)
        self._nb.add(self._tab_quiz, text="  📝  Kuis  ")
        self._build_quiz_tab(self._tab_quiz)

        # Tab: JSON Raw
        self._tab_raw = tk.Frame(self._nb, bg=BG_DARK)
        self._nb.add(self._tab_raw, text="  { } Raw JSON  ")
        self._build_raw_tab(self._tab_raw)

    def _build_info_tab(self, parent):
        self._info_frame = tk.Frame(parent, bg=BG_DARK)
        self._info_frame.pack(fill="both", expand=True, padx=20, pady=16)
        
        # Initial Dashboard view
        self._show_dashboard()

    def _show_dashboard(self):
        """Menampilkan ringkasan subject sebagai dashboard awal."""
        for w in self._info_frame.winfo_children(): w.destroy()
        
        tk.Label(self._info_frame, text=f"📊 {self._data.get('name', 'Dashboard')}", 
                 bg=BG_DARK, fg=ACCENT, font=FONT_TITLE).pack(pady=(10, 20), anchor="w")
        
        stats_f = tk.Frame(self._info_frame, bg=BG_DARK)
        stats_f.pack(fill="x", pady=10)
        
        topics = self._data.get("topics", [])
        n_lessons = sum(len(t.get("lessons", [])) for t in topics)
        n_flash = sum(len(t.get("flashcards", [])) for t in topics)
        n_quiz = sum(len(t.get("quiz", {}).get("questions", [])) for t in topics)
        
        for icon, count, label in [
            ("📚", len(topics), "Topik"),
            ("📖", n_lessons, "Pelajaran"),
            ("🃏", n_flash, "Flashcards"),
            ("📝", n_quiz, "Soal Kuis")
        ]:
            card = Card(stats_f)
            card.pack(side="left", padx=10, pady=10, fill="both", expand=True)
            tk.Label(card, text=f"{icon} {count}", bg=BG_CARD, fg=TEXT_PRI, font=FONT_HEAD).pack(pady=(15, 5))
            tk.Label(card, text=label, bg=BG_CARD, fg=TEXT_SEC, font=FONT_SMALL).pack(pady=(0, 15))

        tk.Label(self._info_frame, text="Quick Actions:", bg=BG_DARK, fg=TEXT_DIM, font=FONT_SMALL).pack(pady=(30, 10), anchor="w")
        qa_f = tk.Frame(self._info_frame, bg=BG_DARK)
        qa_f.pack(fill="x")
        
        StyledButton(qa_f, "＋ Tambah Topik Baru (Ctrl+N)", self._add_topic, style="success").pack(side="left", padx=5)
        StyledButton(qa_f, "🔍 Global Search", self._global_search, style="ghost").pack(side="left", padx=5)

    def _build_lesson_tab(self, parent):
        hdr = tk.Frame(parent, bg=BG_DARK)
        hdr.pack(fill="x", padx=16, pady=8)
        tk.Label(hdr, text="Daftar Pelajaran", bg=BG_DARK, fg=TEXT_PRI,
                 font=FONT_HEAD).pack(side="left")
        
        btn_row = tk.Frame(hdr, bg=BG_DARK)
        btn_row.pack(side="right")
        StyledButton(btn_row, "＋ Pelajaran", self._add_lesson, style="success").pack(side="left", padx=2)
        StyledButton(btn_row, "✏️ Edit", self._edit_lesson, style="ghost").pack(side="left", padx=2)
        StyledButton(btn_row, "🗑 Hapus", self._del_lesson, style="danger").pack(side="left", padx=2)

        self._lesson_list = ttk.Treeview(parent, columns=("title", "minutes"),
                                          show="headings", height=8)
        self._lesson_list.heading("title", text="Judul Pelajaran")
        self._lesson_list.heading("minutes", text="Menit")
        self._lesson_list.column("title", width=400)
        self._lesson_list.column("minutes", width=80, anchor="center")
        self._lesson_list.pack(fill="both", expand=True, padx=16, pady=4)
        self._lesson_list.bind("<Double-1>", lambda e: self._edit_lesson())

    def _build_flashcard_tab(self, parent):
        hdr = tk.Frame(parent, bg=BG_DARK)
        hdr.pack(fill="x", padx=16, pady=8)
        tk.Label(hdr, text="Flashcard", bg=BG_DARK, fg=TEXT_PRI,
                 font=FONT_HEAD).pack(side="left")
        self._fc_count = tk.Label(hdr, text="0 kartu", bg=BG_DARK, fg=TEXT_DIM,
                                   font=FONT_SMALL)
        self._fc_count.pack(side="left", padx=10)
        StyledButton(hdr, "✏️ Edit Semua Flashcard", self._edit_flashcards, style="ghost").pack(side="right")

        # Preview cards
        canvas = tk.Canvas(parent, bg=BG_DARK, highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self._fc_frame = tk.Frame(canvas, bg=BG_DARK)
        self._fc_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._fc_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=16)
        sb.pack(side="right", fill="y", pady=4)

    def _build_quiz_tab(self, parent):
        hdr = tk.Frame(parent, bg=BG_DARK)
        hdr.pack(fill="x", padx=16, pady=8)
        tk.Label(hdr, text="Soal Kuis", bg=BG_DARK, fg=TEXT_PRI,
                 font=FONT_HEAD).pack(side="left")
        self._quiz_count = tk.Label(hdr, text="0 soal", bg=BG_DARK, fg=TEXT_DIM,
                                     font=FONT_SMALL)
        self._quiz_count.pack(side="left", padx=10)
        StyledButton(hdr, "✏️ Edit Semua Soal", self._edit_quiz, style="ghost").pack(side="right")

        self._quiz_list = ttk.Treeview(parent, columns=("no", "question", "answer"),
                                        show="headings", height=16)
        self._quiz_list.heading("no", text="#")
        self._quiz_list.heading("question", text="Pertanyaan")
        self._quiz_list.heading("answer", text="Jwb")
        self._quiz_list.column("no", width=40, anchor="center")
        self._quiz_list.column("question", width=500)
        self._quiz_list.column("answer", width=60, anchor="center")
        self._quiz_list.pack(fill="both", expand=True, padx=16, pady=4)

    def _build_raw_tab(self, parent):
        hdr = tk.Frame(parent, bg=BG_DARK)
        hdr.pack(fill="x", padx=16, pady=8)
        tk.Label(hdr, text="Raw JSON (read-only preview)", bg=BG_DARK, fg=TEXT_PRI,
                 font=FONT_HEAD).pack(side="left")
        StyledButton(hdr, "📋 Salin JSON Topik", self._copy_raw, style="ghost").pack(side="right")
        StyledButton(hdr, "📋 Salin JSON Penuh", self._copy_full_json, style="ghost").pack(
            side="right", padx=6)

        self._raw_text = StyledText(parent, font=FONT_MONO, state="disabled")
        sb = ttk.Scrollbar(parent, orient="vertical", command=self._raw_text.yview)
        self._raw_text.configure(yscrollcommand=sb.set)
        self._raw_text.pack(side="left", fill="both", expand=True, padx=(16, 0), pady=4)
        sb.pack(side="right", fill="y", padx=(0, 10), pady=4)

    def _build_statusbar(self):
        self._status = tk.Label(self, text="Selamat datang di IPA Editor",
                                 bg=BG_PANEL, fg=TEXT_DIM, font=FONT_SMALL,
                                 anchor="w")
        self._status.pack(fill="x", side="bottom", padx=12, pady=4)

    # ── File Operations ──────────────────────────────────────────────────────
    def _save_file(self):
        if not self._filepath:
            self._save_as()
            return
        self._write_json(self._filepath)

    def _save_as(self):
        path = filedialog.asksaveasfilename(
            title="Simpan File JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if not path:
            return
        self._filepath = path
        self._write_json(path)

    def _write_json(self, path):
        try:
            # Clean internal widget keys
            clean = json.loads(json.dumps(self._data, ensure_ascii=False))
            with open(path, "w", encoding="utf-8") as f:
                json.dump(clean, f, ensure_ascii=False, indent=2)
            self._unsaved = False
            self._update_title()
            self._set_status(f"✓ Disimpan: {os.path.basename(path)}  [{datetime.now().strftime('%H:%M:%S')}]")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan:\n{e}")

    # ── Topic CRUD ────────────────────────────────────────────────────────────
    def _refresh_tree(self):
        self._tree.delete(*self._tree.get_children())
        query = self._search_var.get().lower() if hasattr(self, "_search_var") else ""
        query_tokens = query.split()
        topics = self._data.get("topics", [])
        shown = 0
        for i, t in enumerate(topics):
            title = t.get("title", f"Topik {i+1}")
            title_lower = title.lower()
            
            if query_tokens and not all(tok in title_lower for tok in query_tokens):
                continue
                
            n_fc = len(t.get("flashcards", []))
            n_q  = len(t.get("quiz", {}).get("questions", []))
            label = f"  {title}   [{n_fc}🃏 {n_q}📝]"
            self._tree.insert("", "end", iid=str(i), text=label, values=(i,))
            shown += 1
        if hasattr(self, "_count_lbl"):
            self._count_lbl.config(text=f"{shown}/{len(topics)} topik")

    def _filter_topics(self, *args):
        self._refresh_tree()

    def _on_topic_select(self, event):
        sel = self._tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        self._selected_topic_idx = idx
        self._refresh_detail(idx)

    def _get_selected_topic(self):
        if self._selected_topic_idx is None:
            return None
        topics = self._data.get("topics", [])
        if self._selected_topic_idx >= len(topics):
            return None
        return topics[self._selected_topic_idx]

    def _add_topic(self):
        dlg = TopicDialog(self)
        if dlg.result:
            self._data.setdefault("topics", []).append(dlg.result)
            self._mark_unsaved()
            self._refresh_tree()
            self._set_status(f"✓ Topik '{dlg.result['title']}' ditambahkan")

    def _edit_topic(self):
        topic = self._get_selected_topic()
        if not topic:
            messagebox.showinfo("Info", "Pilih topik terlebih dahulu!")
            return
        dlg = TopicDialog(self, topic)
        if dlg.result:
            # Preserve existing lessons/flashcards/quiz
            dlg.result["lessons"] = topic.get("lessons", [])
            dlg.result["flashcards"] = topic.get("flashcards", [])
            dlg.result["quiz"] = topic.get("quiz", {"questions": []})
            self._data["topics"][self._selected_topic_idx] = dlg.result
            self._mark_unsaved()
            self._refresh_tree()
            self._refresh_detail(self._selected_topic_idx)

    def _delete_topic(self):
        topic = self._get_selected_topic()
        if not topic:
            messagebox.showinfo("Info", "Pilih topik terlebih dahulu!")
            return
        if messagebox.askyesno("Konfirmasi",
                                f"Hapus topik '{topic.get('title')}'?\nSemua data di dalamnya akan hilang."):
            del self._data["topics"][self._selected_topic_idx]
            self._selected_topic_idx = None
            self._mark_unsaved()
            self._refresh_tree()
            self._clear_detail()
            self._set_status("🗑 Topik dihapus")

    # ── Detail Refresh ─────────────────────────────────────────────────────────
    def _refresh_detail(self, idx):
        topics = self._data.get("topics", [])
        if idx >= len(topics):
            return
        t = topics[idx]

        # Info tab
        for w in self._info_frame.winfo_children():
            w.destroy()

        info_card = Card(self._info_frame)
        info_card.pack(fill="x", pady=8)

        title_row = tk.Frame(info_card, bg=BG_CARD)
        title_row.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(title_row, text=t.get("title", ""), bg=BG_CARD, fg=TEXT_PRI,
                 font=("Segoe UI", 16, "bold")).pack(side="left")

        desc = tk.Label(info_card, text=t.get("description", "—"), bg=BG_CARD,
                        fg=TEXT_SEC, font=FONT_BODY, wraplength=550, justify="left")
        desc.pack(padx=16, pady=4, anchor="w")

        stats = tk.Frame(info_card, bg=BG_CARD)
        stats.pack(fill="x", padx=16, pady=8)
        n_ls = len(t.get("lessons", []))
        n_fc = len(t.get("flashcards", []))
        n_q  = len(t.get("quiz", {}).get("questions", []))
        for icon, count, label, color in [
            ("📖", n_ls, "Pelajaran", ACCENT),
            ("🃏", n_fc, "Flashcard", SUCCESS),
            ("📝", n_q, "Soal Kuis", WARNING),
        ]:
            box = tk.Frame(stats, bg=BG_INPUT, padx=16, pady=8)
            box.pack(side="left", padx=8, pady=4)
            tk.Label(box, text=f"{icon} {count}", bg=BG_INPUT, fg=color,
                     font=("Segoe UI", 20, "bold")).pack()
            tk.Label(box, text=label, bg=BG_INPUT, fg=TEXT_DIM,
                     font=FONT_SMALL).pack()

        # Lessons
        self._lesson_list.delete(*self._lesson_list.get_children())
        for ls in t.get("lessons", []):
            self._lesson_list.insert("", "end",
                values=(ls.get("title", ""), str(ls.get("estMinutes", "?"))))

        # Flashcards
        for w in self._fc_frame.winfo_children():
            w.destroy()
        cards = t.get("flashcards", [])
        self._fc_count.config(text=f"{len(cards)} kartu")
        for i, card in enumerate(cards):
            row = Card(self._fc_frame)
            row.pack(fill="x", pady=3, padx=4)
            num = tk.Label(row, text=f"#{i+1}", bg=BG_CARD, fg=ACCENT, font=FONT_SMALL)
            num.pack(side="left", padx=(10, 4), pady=6)
            q_lbl = tk.Label(row, text=f"Q: {card.get('question', '')}", bg=BG_CARD,
                              fg=TEXT_PRI, font=FONT_SMALL, wraplength=350, justify="left")
            q_lbl.pack(side="left", fill="x", expand=True, pady=4)
            a_lbl = tk.Label(row, text=f"A: {card.get('answer', '')}", bg=BG_CARD,
                              fg=SUCCESS, font=FONT_SMALL, wraplength=250, justify="left")
            a_lbl.pack(side="right", padx=10)

        # Quiz
        self._quiz_list.delete(*self._quiz_list.get_children())
        questions = t.get("quiz", {}).get("questions", [])
        self._quiz_count.config(text=f"{len(questions)} soal")
        for i, q in enumerate(questions):
            opts = q.get("options", [])
            ans = q.get("answer", 0)
            ans_letter = "ABCD"[ans] if ans < 4 else "?"
            self._quiz_list.insert("", "end",
                values=(i+1, q.get("question", "")[:80], ans_letter))

        # Raw JSON
        self._raw_text.config(state="normal")
        self._raw_text.delete("1.0", "end")
        clean = {k: v for k, v in t.items() if not k.startswith("_")}
        self._raw_text.insert("1.0", json.dumps(clean, ensure_ascii=False, indent=2))
        self._raw_text.config(state="disabled")

    def _clear_detail(self):
        self._show_dashboard()

    # ── Lesson CRUD ────────────────────────────────────────────────────────────
    def _add_lesson(self):
        topic = self._get_selected_topic()
        if not topic:
            messagebox.showinfo("Info", "Pilih topik terlebih dahulu!")
            return
        dlg = LessonDialog(self)
        if dlg.result:
            topic.setdefault("lessons", []).append(dlg.result)
            self._mark_unsaved()
            self._refresh_detail(self._selected_topic_idx)

    def _edit_lesson(self):
        topic = self._get_selected_topic()
        if not topic:
            return
        sel = self._lesson_list.selection()
        if not sel:
            messagebox.showinfo("Info", "Pilih pelajaran yang ingin diedit!")
            return
        idx = self._lesson_list.index(sel[0])
        lesson = topic["lessons"][idx]
        dlg = LessonDialog(self, lesson)
        if dlg.result:
            topic["lessons"][idx] = dlg.result
            self._mark_unsaved()
            self._refresh_detail(self._selected_topic_idx)

    def _del_lesson(self):
        topic = self._get_selected_topic()
        if not topic:
            return
        sel = self._lesson_list.selection()
        if not sel:
            return
        idx = self._lesson_list.index(sel[0])
        title = topic["lessons"][idx].get("title", "")
        if messagebox.askyesno("Konfirmasi", f"Hapus pelajaran '{title}'?"):
            del topic["lessons"][idx]
            self._mark_unsaved()
            self._refresh_detail(self._selected_topic_idx)

    # ── Flashcard ─────────────────────────────────────────────────────────────
    def _edit_flashcards(self):
        topic = self._get_selected_topic()
        if not topic:
            messagebox.showinfo("Info", "Pilih topik terlebih dahulu!")
            return
        dlg = FlashcardDialog(self, topic.get("flashcards", []))
        if dlg.result is not None:
            topic["flashcards"] = dlg.result
            self._mark_unsaved()
            self._refresh_detail(self._selected_topic_idx)

    # ── Quiz ──────────────────────────────────────────────────────────────────
    def _edit_quiz(self):
        topic = self._get_selected_topic()
        if not topic:
            messagebox.showinfo("Info", "Pilih topik terlebih dahulu!")
            return
        dlg = QuizDialog(self, topic.get("quiz", {}).get("questions", []))
        if dlg.result is not None:
            topic.setdefault("quiz", {})["questions"] = dlg.result
            self._mark_unsaved()
            self._refresh_detail(self._selected_topic_idx)

    # ── Raw JSON ──────────────────────────────────────────────────────────────
    def _copy_raw(self):
        topic = self._get_selected_topic()
        if not topic:
            return
        clean = {k: v for k, v in topic.items() if not k.startswith("_")}
        self.clipboard_clear()
        self.clipboard_append(json.dumps(clean, ensure_ascii=False, indent=2))
        self._set_status("📋 JSON topik disalin ke clipboard")

    def _copy_full_json(self):
        self.clipboard_clear()
        self.clipboard_append(json.dumps(self._data, ensure_ascii=False, indent=2))
        self._set_status("📋 JSON penuh disalin ke clipboard")

    # ── AI Mode ───────────────────────────────────────────────────────────────
    def _open_ai_mode(self):
        AIModeWindow(self, self._data, self._ai_import_callback)

    def _ai_import_callback(self, import_type, topic_id, payload):
        topics = self._data.get("topics", [])
        if import_type == "full":
            self._data = payload
        elif import_type == "topic":
            topics.append(payload)
        elif import_type == "full_topic_update":
            target = next((t for t in topics if t.get("id") == topic_id), None)
            if target:
                # Update ONLY if present in payload to avoid accidental deletions
                if "title" in payload: target["title"] = payload["title"]
                if "description" in payload: target["description"] = payload["description"]
                if "lessons" in payload and payload["lessons"]: target["lessons"] = payload["lessons"]
                if "flashcards" in payload and payload["flashcards"]: target["flashcards"] = payload["flashcards"]
                if "quiz" in payload and payload["quiz"].get("questions"): 
                    target["quiz"] = payload["quiz"]
        elif import_type in ("flashcards", "quiz"):
            target = next((t for t in topics if t.get("id") == topic_id), None)
            if not target:
                return
            if import_type == "flashcards":
                target["flashcards"] = payload
            else:
                target.setdefault("quiz", {})["questions"] = payload
        
        # UI Update
        self._refresh_tree()
        if self._selected_topic_idx is not None:
            self._refresh_detail(self._selected_topic_idx)
            
        # Auto-Save to disk (User said it doesn't change, so let's make it real)
        self._mark_unsaved()
        self._save_file()
        self._set_status(f"✓ AI Import Berhasil & Otomatis Disimpan")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _mark_unsaved(self):
        """Mark as dirty and trigger immediate real-time save."""
        self._unsaved = True
        self._update_title()
        if self._filepath:
            # REAL-TIME SYNC: Save immediately to disk
            self._write_json(self._filepath)
            self._set_status(f"⚡ Live Synced: {os.path.basename(self._filepath)}")

    def _update_title(self):
        fname = os.path.basename(self._filepath) if self._filepath else "File Baru"
        marker = " ●" if self._unsaved else ""
        self.title(f"✏️  Editor — {fname}{marker}")
        self._file_label.config(
            text=self._filepath or "Belum disimpan",
            fg=WARNING if self._unsaved else TEXT_DIM
        )

    def _set_status(self, msg):
        self._status.config(text=f"  {msg}")

    def _on_close(self):
        # Real-time save is already active, so just exit
        self.destroy()


# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = SubjectEditor()
    app.mainloop()
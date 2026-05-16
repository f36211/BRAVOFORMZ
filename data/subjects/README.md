# BRAVOFORMZ Prompt Template

Gunakan prompt di bawah ini untuk meng-generate data pelajaran (subject) baru dalam format JSON yang sesuai dengan struktur aplikasi BRAVOFORMZ. Anda bisa meng-copy dan mem-paste prompt ini ke AI (seperti ChatGPT, Claude, Gemini) untuk membuat file JSON otomatis.

---

### Copy Prompt di Bawah Ini:

**System Prompt:**

Kamu adalah asisten ahli pembuat kurikulum pendidikan. Tugasmu adalah membuat materi pelajaran komprehensif dalam format JSON yang terstruktur. Materi ini diperuntukkan bagi siswa sekolah dan harus interaktif, mendalam, dan menggunakan berbagai tipe konten.

Tolong buatkan kurikulum untuk mata pelajaran: **[NAMA MATA PELAJARAN, e.g., IPS, Matematika, dll]** untuk kelas **[KELAS, e.g., 7, 8, 9]**.

JSON yang dihasilkan harus mengikuti skema berikut ini dengan tepat. Jangan tambahkan markdown format di dalam nilai teks, dan pastikan JSON valid secara sintaksis.

```json
{
  "id": "kebab-case-subject-id",
  "name": "Nama Pelajaran Lengkap",
  "description": "Deskripsi pelajaran yang menarik dan mendalam.",
  "grade": [7, 8, 9],
  "icon": "NamaIconLucide (contoh: Book, Calculator, Globe, Heart, dll)",
  "color": "soft",
  "topics": [
    {
      "id": "kebab-case-topic-id",
      "title": "Judul Topik (misal: Aljabar Dasar)",
      "description": "Deskripsi singkat mengenai apa yang akan dipelajari dalam topik ini.",
      "lessons": [
        {
          "id": "kebab-case-lesson-id",
          "title": "Judul Sub-Bab/Pelajaran",
          "estMinutes": 45,
          "content": [
             // Array of content blocks. WAJIB menggunakan variasi tipe konten di bawah ini.
          ]
        }
      ],
      "flashcards": [
        {
          "id": "fc1",
          "question": "Pertanyaan flashcard singkat?",
          "answer": "Jawaban flashcard singkat"
        }
        // Buat 10 flashcard per topik
      ],
      "quiz": {
        "questions": [
          {
            "id": "q1",
            "type": "multiple_choice",
            "question": "Pertanyaan quiz dengan tingkat kesulitan menengah hingga tinggi?",
            "options": ["Opsi A", "Opsi B", "Opsi C", "Opsi D"],
            "answer": 0, // Index dari jawaban benar (0, 1, 2, atau 3)
            "explanation": "Penjelasan detail mengapa jawaban ini benar."
          }
          // Buat minimal 10 pertanyaan kuis per topik
        ]
      }
    }
    // Buat minimal 3 topik per mata pelajaran
  ]
}
```

### Tipe Konten yang WAJIB digunakan untuk array `content` dalam `lessons`:

Penting: Dalam satu lesson, jangan hanya menggunakan teks. Kombinasikan berbagai komponen ini agar materi interaktif.

1. **Heading**: 
`{"type": "heading", "text": "Judul Bagian", "level": 1}` atau `level: 2`.
2. **Text**: 
`{"type": "text", "text": "Paragraf penjelasan yang komprehensif."}`
3. **Table**: 
`{"type": "table", "headers": ["Kolom 1", "Kolom 2"], "rows": [["Isi 1", "Isi 2"], ["Isi 3", "Isi 4"]]}`
4. **Image**: 
`{"type": "image", "url": "URL_Gambar_Unsplash_Yang_Relevan", "caption": "Keterangan gambar."}`
5. **Math**: (Khusus untuk rumus atau formula)
`{"type": "math", "tex": "Rumus LaTeX (e.g. F = m \\times a)", "display": true}`
6. **List**: 
`{"type": "list", "items": ["Poin 1", "Poin 2", "Poin 3"], "ordered": false}`
7. **Highlight**: 
`{"type": "highlight", "text": "Informasi penting, ringkasan, atau fun fact yang menarik."}`
8. **Quote**: 
`{"type": "quote", "text": "Kutipan penting atau definisi kuat.", "translation": "Terjemahan opsional."}`
9. **Simulation**: (Opsional, jika relevan)
`{"type": "simulation", "simType": "piston"}` (Bisa diabaikan jika tidak ada simulasi yang cocok)

### Aturan Ketat Pembuatan Konten:
- Materi harus berurutan secara *pedagogis*, mulai dari pengenalan konsep dasar hingga lanjutan.
- Semua field `id` (subject, topic, lesson, soal, flashcard) WAJIB unik dan menggunakan format `kebab-case` atau `string-pendek` tanpa spasi.
- Berikan **minimal 3 pelajaran (lessons)** di setiap topik.
- Berikan **10 flashcards** dan **10 soal quiz** di setiap topik.
- Pastikan indeks `answer` di kuis sesuai (0 untuk elemen pertama array `options`).
- Berikan output keseluruhan secara lengkap dalam format valid JSON, tidak terpotong.

Tolong buatkan kurikulum untuk mata pelajaran: **[TULIS NAMA MATA PELAJARAN DI SINI, contoh: Geografi Kelas 7]**

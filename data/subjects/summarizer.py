import json
import os

# ===== PATH HANDLING =====
def get_parent_dir():
    return os.path.dirname(os.path.abspath(__file__))


# ===== LIST JSON FILES =====
def list_json_files():
    parent_dir = get_parent_dir()
    files = [f for f in os.listdir(parent_dir) if f.endswith(".json")]

    if not files:
        print("❌ No JSON files found in parent folder.")
        return []

    print("\n📂 Available JSON files:")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")

    return files


# ===== LOAD JSON =====
def load_json(filename):
    parent_dir = get_parent_dir()
    file_path = os.path.join(parent_dir, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ===== VALIDATE STRUCTURE =====
def validate_structure(data):
    required_keys = ["name", "topics"]

    for key in required_keys:
        if key not in data:
            print(f"⚠️ Warning: Missing key '{key}'")

    if not isinstance(data.get("topics", []), list):
        raise ValueError("❌ 'topics' should be a list")

    print("✅ JSON structure looks OK\n")


# ===== SUMMARIZE TO TEXT =====
def summarize_to_text(data):
    output = []

    output.append(f"=== {data.get('name', 'Unknown Subject')} ===\n")

    for topic in data.get("topics", []):
        output.append(f"\n## TOPIK: {topic.get('title', 'No Title')}\n")

        # --- MATERI ---
        output.append(">> MATERI:")
        for lesson in topic.get("lessons", []):
            output.append(f"\n- {lesson.get('title', 'No Lesson Title')}:")

            for item in lesson.get("content", []):
                t = item.get("type")

                if t == "text":
                    output.append(f"  {item.get('text')}")
                elif t == "highlight":
                    output.append(f"  [INTI] {item.get('text')}")
                elif t == "quote":
                    output.append(f"  (Dalil) {item.get('translation')}")
                elif t == "list":
                    for i in item.get("items", []):
                        output.append(f"  - {i}")
                elif t == "table":
                    output.append("  [Tabel]")
                    for row in item.get("rows", []):
                        output.append(f"    - {' | '.join(row)}")

        # --- FLASHCARDS ---
        output.append("\n>> FLASHCARDS:")
        for fc in topic.get("flashcards", []):
            output.append(f"  Q: {fc.get('question')}")
            output.append(f"  A: {fc.get('answer')}")

        # --- QUIZ ---
        output.append("\n>> QUIZ:")
        for q in topic.get("quiz", {}).get("questions", []):
            options = q.get("options", [])
            answer_index = q.get("answer", 0)

            answer_text = (
                options[answer_index]
                if 0 <= answer_index < len(options)
                else "Invalid Answer"
            )

            output.append(f"  Q: {q.get('question')}")
            output.append(f"  A: {answer_text}")

            if q.get("explanation"):
                output.append(f"  Penjelasan: {q.get('explanation')}")

    return "\n".join(output)


# ===== SAVE OUTPUT =====
def save_output(text, filename="summary.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\n💾 Saved to {filename}")


# ===== MAIN PROGRAM =====
def main():
    try:
        files = list_json_files()
        if not files:
            return

        choice = input("\nSelect file number OR type filename: ").strip()

        # If user enters number
        if choice.isdigit():
            index = int(choice) - 1
            if index < 0 or index >= len(files):
                print("❌ Invalid selection.")
                return
            filename = files[index]
        else:
            filename = choice

        print(f"\n📥 Loading: {filename}")
        data = load_json(filename)

        validate_structure(data)

        print("🧠 Generating summary...")
        summary = summarize_to_text(data)

        print("\n===== PREVIEW =====\n")
        print(summary[:1000])  # preview first part

        save_output(summary)

    except Exception as e:
        print(f"❌ Error: {e}")


# ===== RUN =====
if __name__ == "__main__":
    main()
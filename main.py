from aqt import gui_hooks, mw
from aqt.utils import tooltip, showInfo
from aqt.qt import QAction, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
import requests
import json
import re
import random
import os

# ========== CẤU HÌNH MẶC ĐỊNH ==========
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
DEFAULT_CONFIG = {
    "enabled": True,
    "api_key": "AIzaSyCTHLa6IeIaPSD8kkrswsM_Mt5zEUhGWJQ",
    "model": "gemini-2.0-flash"
}

# ====== ĐỌC / GHI CẤU HÌNH ==========
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_CONFIG.copy()

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

CONFIG = load_config()
API_KEY = CONFIG["api_key"]
MODEL = CONFIG["model"]
ENABLED = CONFIG["enabled"]

def get_url():
    return f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

# =====================================

FIELD_MAP = {
    "Phonetic": r"Phonetic:\s*(.+)",
    "Part of speech": r"Part of speech:\s*(.+)",
    "Meaning": r"Meaning:\s*(.+)",
    "Synonyms": r"Synonyms:\s*(.+)",
    "Example": r"Example:\s*(.+)",
    "Example meaning": r"Example meaning:\s*(.+)"
}

def log_error(msg):
    with open("gemini_error_log.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def generate_hint(vocab):
    words = vocab.split(" ")
    hint = ""
    for word in words:
        masked_word = word[0]
        if len(word) >= 6:
            rand_index = random.randint(1, len(word) - 1)
            for i in range(1, len(word)):
                if i == rand_index:
                    masked_word += word[i]
                else:
                    masked_word += "_"
        else:
            masked_word += "_" * (len(word) - 1)
        hint += masked_word + " "
    return hint.strip()

def on_card_shown(card):
    if not CONFIG.get("enabled", True):
        return
    try:
        note = card.note()
        print("📌 Hook chạy OK")

        if "Vocabulary" not in note:
            tooltip("❌ Model không có trường 'Vocabulary'")
            log_error("❌ Lỗi: Model không có trường 'Vocabulary'")
            return

        vocab = note["Vocabulary"].strip()
        if not vocab:
            tooltip("⚠️ Trường Vocabulary đang trống.")
            log_error("⚠️ Vocabulary rỗng")
            return

        if "Hint" in note and not note["Hint"].strip():
            note["Hint"] = generate_hint(vocab)
            print("✅ Đã tạo Hint:", note["Hint"])

        need_update = any(field in note and not note[field].strip() for field in FIELD_MAP)
        if not need_update:
            note.flush()
            mw.requireReset()
            print("✅ Hint đã tạo, không cần gọi Gemini.")
            return

        prompt = f"""Hãy phân tích từ "{vocab}" thành các phần sau, mỗi phần bắt đầu bằng tên trường in hoa và dấu hai chấm:
Phonetic: 
Part of speech:
Meaning:
Synonyms:
Example:
Example meaning:
Trả lời bằng tiếng Việt, giữ nguyên thứ tự trường như yêu cầu."""

        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": CONFIG["api_key"]
        }

        response = requests.post(
            get_url(),
            headers=headers,
            data=json.dumps(payload)
        )

        if response.status_code != 200:
            tooltip(f"❌ Gemini lỗi: {response.status_code}")
            log_error(f"[HTTP {response.status_code}]\n{response.text}")
            return

        data = response.json()
        try:
            content = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            tooltip("⚠️ Lỗi khi xử lý dữ liệu Gemini.")
            log_error(f"❌ JSON parsing: {str(e)}\n↩ {json.dumps(data, indent=2)}")
            return

        
        # Tách từng trường rõ ràng
        lines = content.splitlines()
        current_field = None
        field_data = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue
            for field in FIELD_MAP:
                if line.lower().startswith(field.lower() + ":"):
                    current_field = field
                    value = line.split(":", 1)[1].strip()
                    field_data[current_field] = value
                    break
            else:
                if current_field:
                    field_data[current_field] += " " + line

        def clean_field(text):
            text = text.strip()
            text = re.sub(r"^\*+", "", text)                    # Bỏ dấu sao đầu dòng
            text = re.sub(r"\(Câu \d+\)", "", text)             # Bỏ (Câu 1)
            text = re.sub(r"\s{2,}", " ", text)                 # Bỏ khoảng trắng thừa
            text = re.sub(r"\*\s*", "", text)                   # Bỏ dấu sao còn dư giữa dòng
    # Nếu có nhiều định nghĩa loại từ, tách dòng cho rõ
            parts = re.split(r"(?=\([Tt]ính từ\)|\([Dd]anh từ\)|\([Đđ]ộng từ\))", text)
            return "\n".join([p.strip() for p in parts if p.strip()])


        def parse_synonyms(text):
            pairs = re.findall(r"(\w+)\s*\(([^)]+)\)", text)
            if pairs:
                return ", ".join(f"{w} ({m})" for w, m in pairs)
            return text.strip()

        updated = []
        for field in FIELD_MAP:
            if field in note and not note[field].strip() and field in field_data:
                raw = field_data[field]
                cleaned = parse_synonyms(raw) if field == "Synonyms" else clean_field(raw)
                note[field] = cleaned
                updated.append(field)

        if updated or "Hint" in note:
            note.flush()
            mw.requireReset()
            tooltip(f"✅ Ghi: {', '.join(updated + (['Hint'] if 'Hint' in note else []))}")
        else:
            tooltip("⚠️ Không cập nhật được trường nào.")

    except Exception as e:
        tooltip("❌ Lỗi hệ thống trong addon.")
        log_error(f"❌ Exception toàn cục: {str(e)}")
        print("❌ Exception:", e)

# ========== CÀI ĐẶT MENU ==========
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Cài đặt Gemini Flashcard Generator")
        layout = QVBoxLayout()

        self.enable_checkbox = QCheckBox("✅ Tự động thêm các trường còn thiếu (Tick để bật)")
        self.enable_checkbox.setChecked(CONFIG["enabled"])

        self.api_input = QLineEdit(CONFIG["api_key"])
        self.model_input = QLineEdit(CONFIG["model"])

        layout.addWidget(self.enable_checkbox)
        layout.addWidget(QLabel("🔑 API Key:"))
        layout.addWidget(self.api_input)
        layout.addWidget(QLabel("📦 Model Gemini:"))
        layout.addWidget(self.model_input)

        save_btn = QPushButton("💾 Lưu cài đặt")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save_settings(self):
        CONFIG["enabled"] = self.enable_checkbox.isChecked()
        CONFIG["api_key"] = self.api_input.text().strip()
        CONFIG["model"] = self.model_input.text().strip()
        save_config(CONFIG)
        showInfo("✅ Đã cập nhật cấu hình. Có hiệu lực ngay!")
        global API_KEY, MODEL, ENABLED
        API_KEY = CONFIG["api_key"]
        MODEL = CONFIG["model"]
        ENABLED = CONFIG["enabled"]
        self.close()

def show_settings_dialog():
    dlg = SettingsDialog(mw)
    dlg.exec()

def setup_menu():
    action = QAction("🧠 Gemini Flashcard Settings", mw)
    action.triggered.connect(show_settings_dialog)
    mw.form.menuTools.addAction(action)

# ========== KÍCH HOẠT ==========
gui_hooks.main_window_did_init.append(setup_menu)
gui_hooks.reviewer_did_show_question.append(on_card_shown)

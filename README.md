# 🧠 Gemini Flashcard Generator for Anki

**Tự động tạo nội dung thẻ ghi nhớ (flashcard) từ một từ vựng duy nhất – chỉ cần nhập "Vocabulary", phần còn lại Gemini sẽ lo!**

---

## ✨ Tính năng chính

- 🔑 **Tự động phân tích từ vựng** bằng AI Gemini:
  - Phiên âm (Phonetic)
  - Loại từ (Part of speech)
  - Nghĩa (Meaning)
  - Từ đồng nghĩa (Synonyms)
  - Ví dụ minh họa (Example)
  - Giải nghĩa ví dụ (Example meaning)
  - Gợi ý đoán từ (Hint)

- ✅ **Tùy chọn bật/tắt tự động điền các trường còn thiếu.**
- 🛠️ **Tuỳ chỉnh API Key và Model Gemini** ngay trong giao diện Anki.
- 🔍 **Log lỗi chi tiết** nếu có vấn đề từ hệ thống hoặc phản hồi Gemini.

---

## 📦 Cách sử dụng

1. Vào **Tools → Gemini Flashcard Settings**.
2. Điền **API Key** và chọn **Model Gemini**:
   - `gemini-pro`, `gemini-1.5-pro-latest`, hoặc `gemini-2.0-flash`.
3. Tạo thẻ mới với trường "Vocabulary" chứa 1 từ vựng bất kỳ.
4. Khi bạn xem thẻ lần đầu, addon sẽ tự động gọi Gemini API để điền các trường còn lại.

---

## 🧩 Yêu cầu

- Anki 2.1.65 trở lên.
- Kết nối internet.
- Tài khoản Google đã tạo API Key tại [makersuite.google.com](https://makersuite.google.com/app/apikey).

---

## 🔗 Hướng dẫn chi tiết

Xem thêm tại:  
👉 [❓ Hướng dẫn lấy API Key & chọn Model Gemini](http://nguyenphanvn95.github.io/Anki/Gemini.html)

---

## 💡 Ví dụ

Chỉ cần nhập:

```
Vocabulary: implement
```

Addon sẽ tự động điền vào các trường:

```
Phonetic: /ˈɪmplɪˌmɛnt/
Part of speech: (Động từ)
Meaning: thực hiện, thi hành
Synonyms: carry out, execute, apply
Example: The company implemented a new strategy.
Example meaning: Công ty đã thực hiện một chiến lược mới.
Hint: i_____t
```

---

## 🚨 Ghi chú

- Addon **không lưu API Key lên mạng**, chỉ lưu cục bộ trên máy.
- Nên sử dụng tài khoản phụ để lấy API Key vì quota giới hạn.

<<<<<<< HEAD
---
=======
---
>>>>>>> 7e7f08166ced9192b74a38eb4e535844d27a1f10

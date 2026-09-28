# Thư mục Mã nguồn thô & Công cụ xử lý dữ liệu (_tools_and_sources)

Thư mục này lưu trữ toàn bộ các file nguồn, file cài đặt APK, bảng tính Excel, tài liệu PDF và các script Python dùng để trích xuất & đóng gói dữ liệu bài hát Karaoke. Các file này không cần thiết để chạy web và đã được tách riêng để thư mục gốc web app gọn gàng, sẵn sàng triển khai lên GitHub Pages hoặc hosting tĩnh.

## Danh sách các tệp & thư mục:

### 1. File ứng dụng Android (APK)
- `Mã+số+Karaoke+Vietnam_2.1.6_APKPure.apk`: APK ứng dụng Karaoke Vietnam (chứa SQLite database của Arirang, California, Việt KTV, MusicCore).
- `Vitek List_3.25062020.apk`: APK danh mục bài hát Vitek VTB.
- `tKaraokeList+🎤+Mã+số+Karaoke+_2.4_APKPure.apk`: APK danh mục bài hát Arirang / Paramax.

### 2. Danh mục bài hát Excel (.xlsx)
- `Danh mục bài hát MusicCore (cập nhật tới vol 102).xlsx`
- `Danh mục bài hát Paramax (cập nhật tới vol 52).xlsx`
- `Danh mục bài hát tiếng Anh (Paramax) (cập nhật tới vol 52).xlsx`

### 3. Danh mục Acnos Soncamedia (.pdf)
- Thư mục `PDF/`: Chứa các file PDF danh mục Vol 58, 60, 62 của hãng Sơn Ca Media (MIDI, KTV, Remix, Cổ nhạc).

### 4. File trích xuất & OCR
- `arirang_ocr_lines.json`: Dữ liệu phân tích OCR các trang bài hát Arirang Vol 66.
- `arirang_ocr_results.json`: Kết quả trích xuất các bài hát Vocal & Chorus từ Vol 66.

### 5. Script Python xử lý & đóng gói dữ liệu
- `build_all_data.py`: Script tổng hợp toàn bộ bài hát từ APK, Excel và xuất ra JSON/JS.
- `build_acnos_data.py`: Script phân tích PDF Acnos và sinh `data/acnos.js`.
- `build_arirang_vocal_chorus.py`: Script gắn nhãn Vocal & Chorus cho Arirang Vol 66.
- `export_data.py`: Script trích xuất SQLite từ APK.

# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Văn Duy | 2A202602729 | Cài harness, chạy thí nghiệm, phân tích và báo cáo |

- Nhà cung cấp và mô hình của thí nghiệm chính: Google Gemini `google_genai:gemini-3.1-flash-lite`; `LAB_TEMPERATURE=0`, `recursion_limit=60`. Đã thử Gemini 3.5 Flash-Lite trước đó, nhưng một lần chạy subagent kéo dài quá 5 phút và bị ngắt kết nối; dữ liệu thử được giữ riêng ở `pilot35/`, không trộn vào bảng chính.
- Deep Agents `0.7.21`; Python 3.12 trong Docker Linux trên Windows.
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): Dự đoán **không tăng điểm đánh giá một cách nhất quán**. Hai subagent được giới hạn ở đọc/kiểm tra, tác tử chính vẫn ghi file. Trên `data-learn`, điểm tăng từ 3/8 lên 5/8 dù `subagent_calls=0`, nên không thể quy thay đổi đó cho cơ chế đa tác tử. Chi phí ngữ cảnh và thời gian có thể vẫn tăng. Nghiên cứu của [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) cho thấy đa tác tử có thể tốn nhiều token; lợi ích phụ thuộc khả năng chia việc độc lập.
- H2 (skills-auto so với baseline): Dự đoán skill quy trình có thể giảm lỗi bỏ qua kiểm tra dữ liệu (nhóm D), nhưng **khó giải đúng quy ước mới chưa có trong phản hồi tập học**. [SkillsBench](https://arxiv.org/abs/2602.12670) cho thấy skill tự sinh không bảo đảm tăng chất lượng; giả thuyết cần đối chiếu với `skills_read` và check kỹ thuật/quy ước.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán hiệu quả của skill trên tập học cao hơn tập đánh giá nếu skill học quá sát 9 phản hồi quy ước cụ thể của tập học. [SkillEvolBench](https://arxiv.org/abs/2605.24117) xem khả năng chuyển từ kinh nghiệm sang kỹ năng dùng cho tác vụ mới là điều cần kiểm chứng; chênh lệch cũng có thể do nhiễu vì mỗi cấu hình chỉ chạy một lần.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định thấy 9 công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. `execute` chạy lệnh shell.
2. Mô tả `task` cho biết `general-purpose` là subagent xử lý việc nhiều bước, có các công cụ như tác tử chính. Mỗi lần gọi là phiên độc lập, chỉ thấy prompt giao việc và trả về một báo cáo cuối; tác tử chính phải gửi đủ quy tắc và đường dẫn.
3. System prompt mặc định rỗng. Mô tả `task` hướng dẫn: “Put full detail in the prompt and state exactly what it should return”. Mô tả `execute` hướng dẫn: “Use read_file rather than cat/head/tail”. Các dòng này được ghi từ đầu ra thật của `python scripts/tour.py`.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `rule_type_hints` | E | `RULE: every public function ... has type annotations on all parameters and on the return value` |
| `code-learn` | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py ... at least 3` |
| `code-learn` | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md under ... ## Unreleased` |
| `data-learn` | `north_q1_revenue` | D | `wrong value (got 2314.87)`; bước chuẩn hóa dữ liệu cho tổng doanh thu chưa đúng |
| `data-learn` | `north_q1_orders` | D | `wrong value (got 9)`; đếm đơn hàng sau làm sạch chưa đúng |
| `data-learn` | `rule_money_in_cents` | E | `RULE: money values in answer.json are integer cents` |
| `data-learn` | `rule_meta_block` | E | `RULE: answer.json has an object meta` với `source`, `rows_in`, `rows_used` |
| `data-learn` | `rule_clean_csv` | E | `RULE: write workspace/clean.csv` với cột và định dạng quy định |
| `logs-learn` | `rule_service_names` | E | `RULE: service names ... lower-case with '-' replaced by '_'` |
| `logs-learn` | `rule_sorted_errors` | E | `RULE: errors is sorted by service, then by timestamp_utc` |
| `logs-learn` | `rule_schema_header` | E | `RULE: ... schema_version: 2 and generated_by: log-triage` |

Chín trong 11 lỗi thuộc nhóm E (quy ước tổ chức không có trong đề tác vụ), hai lỗi thuộc nhóm D (làm sạch/tính toán dữ liệu). Có 16/18 check kỹ thuật đạt: `code-learn` 7/7, `data-learn` 3/5, `logs-learn` 6/6. Một skill tổng quát có thể nhắc tác tử kiểm tra dữ liệu bẩn và tự xác minh đầu ra, nhưng không thể biết trước chính xác quy ước chưa được cung cấp của tác vụ đánh giá; đây là giả thuyết cần thử sau khi đóng băng skill.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa: `explorer` chỉ đọc nhiều nguồn để lập báo cáo bằng chứng trước khi tác tử chính sửa; `reviewer` chỉ kiểm tra độc lập sau khi có đầu ra. Tác tử chính là người duy nhất ghi file, tránh hai tác tử sửa cùng một workspace. Cách chia này thay cho bản thử ban đầu có cả `implementer`, vì bản đó làm phát sinh vòng giao việc dài và lỗi đệ quy (dữ liệu thử giữ riêng, không đưa vào bảng chính).
- Trong ba tác vụ học của cấu hình chính thức, `subagent_calls=0` ở cả `code-learn`, `data-learn`, `logs-learn`. Đây là quyết định của tác tử chính: các mô tả subagent chỉ phù hợp với bước đọc/kiểm tra độc lập, còn tác vụ yêu cầu tạo đầu ra một mạch. Không được nói đa tác tử gây ra phần tăng điểm khi không có lời gọi nào.
- Thông tin thiếu hoặc thừa khi giao việc: không có lời giao việc trong vết chính thức để đánh giá nội dung bàn giao. Bản thử có `implementer` từng giao toàn bộ tác vụ cho một subagent, làm ngữ cảnh và số bước phình lớn; đã bỏ cấu hình đó trước khi chốt thí nghiệm.
- Ảnh hưởng đo được trên tập học: `data-learn` 3/8 → 5/8 nhưng token 48.602 → 86.656 (+78%) và 0 lời gọi subagent; `logs-learn` giữ 6/9, token 56.031 → 96.546 (+72%), 0 lời gọi. `code-learn` ở điều kiện subagent chạm giới hạn 80 bước sau khi lặp cùng lệnh `edit_file` không đổi nội dung; điểm 6/10, 310.233 token. Không thể quy các chênh lệch này cho lợi ích của thực thi đa tác tử. Vết của lần lỗi được giữ trong `results/subagents/code-learn/trace.md`.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Chạy curator 2 lần. Lần đầu sinh 2 skill rồi loại cả hai vì chúng chép tên file, số test, phiên bản schema và giá trị metadata của tập học; SHA-256 lần lượt là `30DEED41AB897B2B8A4293E44C0960E28BA13ABB63A90B8F689E6164C491C3BB` và `731D7B29A330B89C09FCAE1B79E82EEECDB55C0032057A77957CD9940180FD09`. Lần hai siết prompt để yêu cầu chỉ dẫn quy trình tổng quát, sinh 3 skill hiện có. Không sửa tay nội dung của bất kỳ skill nào.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `verify-code-standards` | Phần lớn là quy trình chung cho sửa Python, nhưng `fix(...)` trong changelog lấy từ tập học. | Đúng nếu dự án áp dụng quy ước đó; có thể gây sai cho dự án mới. | 9 dòng; `description` kích hoạt khi nộp sửa code; `skills_read=0` ở `code-learn` Phần 3.4. |
| `validate-data-output` | Kiểm tra schema đầu ra là chung, nhưng giả định tiền luôn là cent và luôn có khối metadata là quá hẹp. | Có hại nếu đầu ra mới dùng đơn vị khác; giữ nguyên để đo khả năng chuyển giao, không sửa tay. | 9 dòng; `description` dành cho báo cáo dữ liệu; `skills_read=0` ở `data-learn` Phần 3.4. |
| `normalize-log-output` | Có bước kiểm tra log tổng quát, nhưng quy tắc gạch nối → gạch dưới và sắp theo service lấy từ tập học. | Đúng trên `logs-learn`, chưa biết có đúng ở tác vụ mới. | 9 dòng; `description` dành cho parse log; `skills_read=1` ở `logs-learn` Phần 3.4. |

Ở Phần 3.4, `skills-auto`: `code-learn` 7/10 (lỗi đệ quy, không đọc skill), `data-learn` 4/8 (không đọc skill), `logs-learn` 8/9 (đọc `normalize-log-output`). So với baseline `logs-learn` 6/9, hai check `rule_service_names` và `rule_sorted_errors` chuyển sang đạt; vết có lệnh `read_file skills/normalize-log-output/SKILL.md`. Chênh lệch này **chỉ** chứng minh skill được dùng trong ca học đó; chưa chứng minh chuyển sang ca đánh giá.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1. **Chỉ sáu tác vụ ở ba họ:** mỗi họ chỉ có một tác vụ học và một tác vụ đánh giá. Một chênh lệch điểm ở đây có thể do cấu tạo riêng của tác vụ; không suy rộng thành mức cải thiện của mọi hệ đa tác tử.
2. **Mỗi điều kiện chỉ chạy chính thức một lần:** Gemini vẫn có biến thiên đầu ra dù đặt `LAB_TEMPERATURE=0`. Chênh lệch giữa bản `skills-auto` phát triển và bản sau đóng băng cho cùng tập học sẽ được dùng như dấu hiệu nhiễu, không phải chứng minh nguyên nhân.
3. **Tác vụ và quy ước do giảng viên thiết kế:** các check `rule_` không nằm trong đề giao cho tác tử. Skill học từ phản hồi có thể chép quy ước của tập học mà không chuyển được sang tập đánh giá; điểm tốt trên tập học chưa chứng minh khả năng tổng quát hóa.
4. **Chỉ một model trong bảng chính:** Gemini 3.1 Flash-Lite có hành vi gọi công cụ riêng; các kết luận về `skills_read` hoặc vòng lặp `edit_file` không tự động đúng với model khác. Những lần thử Gemini 3.5 được tách riêng, không trộn số liệu.
5. **Giới hạn thời gian/đệ quy và hạ tầng:** một lần chạy có thể dừng trước khi tác tử hoàn thiện. Báo cáo nêu riêng `error` và số check đã đạt khi dừng, tránh diễn giải lỗi quota hoặc kết nối thành năng lực của kiến trúc.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:

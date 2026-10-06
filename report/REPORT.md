# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin sinh viên và cấu hình

- Họ tên: Nguyễn Văn Duy
- Mã sinh viên: 2A202602729

- Nhà cung cấp và mô hình: OpenAI API, `openai:gpt-4o-mini`; `LAB_TEMPERATURE=0`; `recursion_limit=60`; trần 4.096 token đầu ra mỗi lượt mô hình và 120.000 token mỗi tác vụ. Khóa API chỉ nằm trong tệp môi trường không theo dõi bởi Git.
- Deep Agents `0.7.21`, Python 3.12 trong Docker Linux trên Windows.
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): Dự đoán **không cải thiện điểm đánh giá một cách nhất quán** và tốn thêm token. Tập học chỉ có một lời giao việc tới subagent mặc định, kết quả 0/8; hai ca còn lại không gọi subagent. Việc tách chỉ có lợi nếu phần việc độc lập và bàn giao đủ quy tắc; [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) cũng ghi nhận chi phí token của hệ đa tác tử cao hơn hội thoại thường.
- H2 (skills-auto so với baseline): Dự đoán skill `requirement-discovery` và `testing-and-validation` có thể giúp tác tử hoàn thiện/kiểm tra file đầu ra, nhưng lợi ích trên tập đánh giá có thể nhỏ nếu model không đọc skill. [SkillsBench](https://arxiv.org/abs/2602.12670) cho thấy skill tự sinh không bảo đảm cải thiện; cần đo `skills_read` và check đạt thay vì chỉ kiểm tra skill tồn tại.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm tăng trên tập học, nếu có, không chuyển nguyên vẹn sang tập đánh giá vì tập đánh giá có quy ước mới. [SkillEvolBench](https://arxiv.org/abs/2605.24117) nhấn mạnh việc kiểm tra khả năng chuyển từ kinh nghiệm sang tác vụ chưa thấy; so sánh còn chịu nhiễu vì mỗi ca chỉ chạy một lần.

## 3. Làm quen Deep Agents (Phần 0.3)

1. `scripts/tour.py` in 9 công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. `execute` chạy lệnh shell.
2. `task` mở subagent `general-purpose` cho việc nhiều bước. Subagent có công cụ như tác tử chính nhưng mỗi lần gọi là một phiên độc lập; nó chỉ thấy prompt bàn giao và trả về một báo cáo cuối. Vì vậy prompt giao việc phải đủ quy tắc và đường dẫn.
3. System prompt mặc định của Deep Agents rỗng. Mô tả `task` ghi “Put full detail in the prompt and state exactly what it should return”; mô tả `execute` ghi “Use read_file rather than cat/head/tail”. Đây là chữ thực tế từ `python scripts/tour.py`.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `csv_quoting_follows_docstring` | A | Check ghi `to_csv_row returned 'Desk, large "oak",10.00,2'`: đầu ra chưa đặt dấu nháy/escape theo docstring. |
| `code-learn` | `rule_type_hints` | E | `RULE: every public function ... has type annotations on all parameters and on the return value`. |
| `code-learn` | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py ... at least 3`; chưa có bộ kiểm tra hồi quy theo quy ước. |
| `code-learn` | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md under ... ## Unreleased`. |
| `logs-learn` | `valid_structure` cùng 8 check khác | B | `FileNotFoundError: .../workspace/errors.json`; lần chạy không tạo tệp kết quả để xác minh. Không suy từ 9 check này thành 9 nguyên nhân độc lập. |

Trong 4 lỗi của `code-learn`, nhóm E chiếm 3/4; đây là những quy ước không có trong đề nhưng được phản hồi `detail` nêu ra. `logs-learn` không tạo tệp, nên 9 check trượt có cùng gốc (nhóm B). `data-learn` chạm trần token và không tạo `answer.json`; 8 check trượt của ca này được ghi là **bị chặn bởi giới hạn thử nghiệm**, không gán cả 8 thành lỗi suy luận độc lập. Curator có thể nhắc tác tử đọc đặc tả và xác minh file đầu ra; nó không thể tự suy ra quy ước mới chưa được phản hồi.

## 5. Điều kiện `subagents` (Phần 2.3)

- Định nghĩa hai subagent: `explorer` đọc nhiều nguồn và trả bằng chứng trước khi sửa; `reviewer` kiểm tra độc lập tệp đã làm. Cả hai chỉ đọc; tác tử chính giữ quyền ghi để tránh xung đột trong cùng workspace.
- `subagent_calls`: `code-learn=0`, `data-learn=1`, `logs-learn=0`. Lời gọi duy nhất ở `data-learn` dùng subagent mặc định `general-purpose`, không phải hai vai trò tùy biến. Vì vậy không thể quy chất lượng của ba ca này cho chuyên môn hóa subagent tùy biến.
- Prompt bàn giao `data-learn` có các chỉ số, tên file và quy tắc làm sạch chính, nhưng không nêu đủ quy ước Acme về `meta`, `clean.csv` và tiền theo cent. Vết chính chỉ thấy lời giao việc và báo cáo cuối, không thấy các bước bên trong subagent.
- Kết quả và chi phí: `code-learn` 6/10 → 5/10, 52.400 → 60.003 token; `data-learn` đều 0/8, baseline bị trần 131.664 token trong khi subagents dùng 49.428; `logs-learn` 0/9 → 1/9, 16.852 → 20.020 token. Chênh lệch nhỏ trên một lần chạy không đủ chứng minh lợi ích đa tác tử.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Chạy curator **một lần** trên phản hồi/vết `baseline` của tác vụ học. Sinh 3 skill hợp lệ; không xóa và không sửa tay skill nào.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `requirement-discovery` | Tổng quát: đọc đề, xác định đầu ra, định dạng và quy tắc. | Đúng nhưng bước xác nhận với stakeholder không khả thi trong một lab chạy tự động; không chứa đáp án. | 10 dòng; `description` kích hoạt khi bắt đầu tác vụ mới; `skills_read=0` ở cả ba ca học. |
| `error-handling` | Tổng quát: lưu lỗi, xác định loại và thử sửa từng bước. | Đúng ở mức quy trình; bước thêm logging có thể không cần cho tác vụ nhỏ. | 10 dòng; `description` cho lỗi thực thi; `skills_read=0` ở cả ba ca học. |
| `testing-and-validation` | Tổng quát: chạy test và kiểm tra định dạng đầu ra. | Đúng; không nêu tên file/tác vụ riêng, nhưng chỉ dẫn khá rộng. | 10 dòng; `description` cho bước xác minh; `skills_read=0` ở cả ba ca học. |

Lần chạy phát triển `skills-auto` trên tập học đạt `code-learn` 5/10, `data-learn` 0/8 (chạm trần token), `logs-learn` 1/9. Vì `skills_read=0` cả ba ca, không có bằng chứng rằng skill đã tác động tới điểm. Kết quả được giữ riêng tại `results/skills-auto-dev/` trước khi chốt `freeze`.

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
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Bạn đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:

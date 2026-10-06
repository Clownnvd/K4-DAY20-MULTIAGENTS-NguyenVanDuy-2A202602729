# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin sinh viên và cấu hình

- Họ tên: Nguyễn Văn Duy
- Mã sinh viên: 2A202602729

- Nhà cung cấp và mô hình: OpenAI API, `openai:gpt-4o-mini`; `LAB_TEMPERATURE=0`; `recursion_limit=60`; trần 4.096 token đầu ra mỗi lượt mô hình và 120.000 token mỗi tác vụ. Khóa API chỉ nằm trong tệp môi trường không theo dõi bởi Git.
- Deep Agents `0.7.21`, Python 3.12 trong Docker Linux trên Windows.
- Số lần chạy: 18 ca chính thức (3 điều kiện × 6 tác vụ) và 3 ca phát triển `skills-auto-dev`; mỗi ca OpenAI chạy đúng một lần. Trần 120.000 token/tác vụ được áp dụng như nhau, nên một số ca dừng sớm và được ghi `error`.
- Commit của tag `freeze`: `1fd406c` (bộ skill OpenAI); mốc Gemini tạm trước đó được giữ riêng ở tag `freeze-gemini-interim` và không trộn vào bảng.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Dự đoán **không cải thiện điểm đánh giá một cách nhất quán** và tốn thêm token. Tập học chỉ có một lời giao việc tới subagent mặc định, kết quả 0/8; hai ca còn lại không gọi subagent. Việc tách chỉ có lợi nếu phần việc độc lập và bàn giao đủ quy tắc; [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) cũng ghi nhận chi phí token của hệ đa tác tử cao hơn hội thoại thường.
- H2 (skills-auto so với baseline): Dự đoán skill `requirement-discovery` và `testing-and-validation` có thể giúp tác tử hoàn thiện/kiểm tra file đầu ra, nhưng lợi ích trên tập đánh giá có thể nhỏ nếu model không đọc skill. [SkillsBench](https://arxiv.org/abs/2602.12670) cho thấy skill tự sinh không bảo đảm cải thiện; cần đo `skills_read` và check đạt thay vì chỉ kiểm tra skill tồn tại.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm tăng trên tập học, nếu có, không chuyển nguyên vẹn sang tập đánh giá vì tập đánh giá có quy ước mới. [SkillEvolBench](https://arxiv.org/abs/2605.24117) nhấn mạnh việc kiểm tra khả năng chuyển từ kinh nghiệm sang tác vụ chưa thấy; so sánh còn chịu nhiễu vì mỗi ca chỉ chạy một lần.

## 3. Làm quen Deep Agents (Phần 0.3)

1. `scripts/tour.py` in 9 công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. `execute` chạy lệnh shell.
2. `task` mở subagent `general-purpose` cho việc nhiều bước. Subagent có công cụ như tác tử chính nhưng mỗi lần gọi là một phiên độc lập; nó chỉ thấy prompt bàn giao và trả về một báo cáo cuối. Vì vậy prompt giao việc phải đủ quy tắc và đường dẫn.
3. System prompt mặc định của Deep Agents rỗng. Mô tả `task` ghi “Put full detail in the prompt and state exactly what it should return”; mô tả `execute` ghi “Use read_file rather than cat/head/tail”. Đây là chữ thực tế từ `python scripts/tour.py`.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

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

Bảng dưới đây do `python -m lab.compare` sinh vào `report/table.md`, không sửa tay số liệu:

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 5/10 | 3/10 |
| data-learn | 0/8 | 0/8 | 1/8 |
| logs-learn | 0/9 | 1/9 | 0/9 |
| code-eval | 2/11 | 1/11 | 3/11 |
| data-eval | 0/9 | 0/9 | 0/9 |
| logs-eval | 2/10 | 2/10 | 1/10 |
| **Mean score - learning tasks** | 0.20 | 0.20 | 0.14 |
| **Mean score - evaluation tasks** | 0.13 | 0.10 | 0.12 |
| **Mean tokens per run** | 77,914 | 63,988 | 59,767 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

`python scripts/check_breakdown.py` cho kết quả:

| Điều kiện | Tập | Check kỹ thuật | Check quy ước | Token trung bình | Lượt đọc skill |
|---|---|---:|---:|---:|---:|
| baseline | đánh giá | 3/18 | 1/12 | 88.856 | 0/3 |
| baseline | học | 6/18 | 0/9 | 66.972 | 0/3 |
| subagents | đánh giá | 2/18 | 1/12 | 84.827 | 0/3 |
| subagents | học | 6/18 | 0/9 | 43.150 | 0/3 |
| skills-auto | đánh giá | 4/18 | 0/12 | 90.008 | 0/3 |
| skills-auto | học | 4/18 | 0/9 | 29.526 | 0/3 |

Các ca chạm trần 120.000 token được ghi `error` trong `run.json`: `baseline/data-learn`, `baseline/code-eval`, `baseline/data-eval`, `subagents/code-eval`, `skills-auto/code-eval`, `skills-auto/data-eval`; lượt phát triển `skills-auto-dev/data-learn` cũng chạm trần. Không chạy lại để chọn điểm tốt hơn. `scripts/verify_freeze.py` báo `checked 6 runs of skill conditions: OK`; không có ca chính thức nào sửa skill.

## 8. Phân tích

1. **Điểm học và đánh giá.** Điểm trung bình tập học: `baseline=0,20`, `subagents=0,20`, `skills-auto=0,14`. Tập đánh giá: `0,13`, `0,10`, `0,12` theo cùng thứ tự. Không điều kiện nào cải thiện điểm đánh giá so với baseline. `data-learn` tăng từ 0/8 lên 1/8 trong `skills-auto`, nhưng `data-eval` vẫn 0/9 cả ba điều kiện và `skills_read=0`, nên không thể gọi đây là lợi ích chuyển giao của skill.
2. **Check kỹ thuật và quy ước.** Trên tập đánh giá, check kỹ thuật đạt `3/18` (baseline), `2/18` (subagents), `4/18` (skills-auto); check `rule_` đạt lần lượt `1/12`, `1/12`, `0/12`. Tập học cũng không có check quy ước nào đạt (`0/9` ở cả ba điều kiện). Skill chưa giúp nhóm quy ước mới; model không đọc skill trong cả 6 lượt `skills-auto` và skill tổng quát không chứa thông tin về quy ước chưa từng được cung cấp.
3. **Cơ chế nhìn từ vết.** Không có check nào có thể quy là “skill giúp đạt”, vì `skills_read=0/6`. Ví dụ, `top_region` ở `data-learn` chuyển từ trượt sang đạt trong `skills-auto`, nhưng vết không có lệnh đọc `SKILL.md`; đây chỉ là chênh lệch giữa hai lượt chạy. Ngược lại, `visible_suite_passes` ở `code-learn` chuyển từ đạt sang trượt, cũng khi không đọc skill. Hai ví dụ cho thấy việc *có file skill* chưa đồng nghĩa tác tử dùng hoặc làm theo skill.
4. **Chi phí và hiệu quả.** Token trung bình mỗi lượt: baseline `77.914`, subagents `63.988`, skills-auto `59.767`. Trên riêng tập đánh giá: `88.856`, `84.827`, `90.008`. Baseline có điểm đánh giá cao nhất (`0,13`) và hiệu quả điểm/token tốt nhất trong ba điều kiện; subagents đạt `0,10` dù còn tốn nhiều bước trong ca code. Tổng 18 lượt ghi nhận 1.174.050 token đầu vào và 35.971 token đầu ra; theo [giá `gpt-4o-mini` của OpenAI](https://developers.openai.com/api/docs/models/gpt-4o-mini), chi phí **ước tính** khoảng 0,198 USD, chưa gồm các lượt kiểm tra cấu hình hoặc sai khác hóa đơn. Token thấp hơn ở một số điều kiện có thể do kết thúc sớm hoặc chạm trần, không phải tự động là tối ưu hơn.
5. **Rò rỉ và quá khớp.** Curator chỉ đọc `baseline` của vai trò `learn`; `validate_skill` loại tên/định danh thuộc tác vụ đánh giá. Ba skill do curator sinh không chứa tên file hoặc đáp án riêng của tập đánh giá, không sửa tay và đã được đóng băng; `verify_freeze.py` báo OK cho 6 lượt chính thức. Không thấy bằng chứng rò rỉ. Nguy cơ còn lại là skill quá chung nên không được đọc, hoặc quy tắc học từ một họ tác vụ không đúng cho ca mới; số liệu hiện tại ủng hộ nhận xét “chưa có tác dụng”, không chứng minh mọi skill tự sinh đều vô ích.
6. **Nhiễu trên cùng bộ skill.** Lượt phát triển trước `freeze` so với lượt chính thức sau `freeze`: `code-learn` 5/10 → 3/10 (−0,20), `data-learn` 0/8 → 1/8 (+0,125), `logs-learn` 1/9 → 0/9 (−0,111). Trung bình khoảng 0,20 → 0,14. Cùng bộ skill vẫn cho chênh lệch khi `skills_read=0` ở cả hai lượt; vì thế những khoảng cách 0,01–0,03 giữa điều kiện trên tập đánh giá quá nhỏ để khẳng định có hiệu ứng thật từ kiến trúc.

## 9. Hạn chế và tính hợp lệ

1. **Mẫu nhỏ:** chỉ sáu tác vụ thuộc ba họ. Một thay đổi điểm có thể do một file hoặc quy tắc riêng của ca đó, nên không suy rộng sang mọi hệ đa tác tử.
2. **Mỗi ca chạy một lần:** dù `LAB_TEMPERATURE=0`, kết quả mô hình có thể thay đổi theo provider và ngữ cảnh. Chênh lệch giữa `skills-auto-dev` và bản sau `freeze` trên cùng tác vụ học là dấu hiệu nhiễu; không tự xem đó là tác dụng của skill.
3. **Quy ước do giảng viên đặt:** tác vụ đánh giá có quy ước mới không hiện trong đề. Skill học từ phản hồi tập học có thể không chuyển sang tập đánh giá; điểm tập học không đủ chứng minh tổng quát hóa.
4. **Một mô hình:** bảng chính chỉ dùng `gpt-4o-mini`. Hành vi gọi công cụ, bỏ qua skill hoặc kết thúc sớm có thể khác với model khác; số liệu Gemini/Groq thử trước được tách khỏi bảng chính.
5. **Giới hạn tài nguyên:** trần 4.096 token mỗi phản hồi và 120.000 token mỗi tác vụ ngăn chi phí tăng vô hạn, nhưng có thể dừng tác vụ trước khi hoàn thành. Báo cáo nêu riêng các lần chạy có `error`; không diễn giải lỗi giới hạn thành kết quả chất lượng bình thường.

## 10. Kết luận

Harness chạy được và đạt 32/32 kiểm thử ngoại tuyến; 18 lượt chính thức và quy trình đóng băng đều được lưu, `verify_freeze.py` báo OK. Trong sáu tác vụ đánh giá, baseline có điểm trung bình 0,13, subagents 0,10 và skills-auto 0,12; không có bằng chứng cải thiện từ hai điều kiện thêm vào. Curator sinh ba skill hợp lệ nhưng tác tử không đọc chúng (`skills_read=0/6`), còn nhiều ca chạm trần token, nên thí nghiệm chưa đo được tác dụng khi skill thực sự được sử dụng. Bước tiếp theo là buộc kiểm tra việc đọc skill như một tiêu chí thực thi, sửa vòng lặp công cụ và lặp lại phép đo nhiều lần dưới cùng ngân sách.

## Phụ lục

- Lệnh chính theo thứ tự: `python scripts/tour.py`; `pytest tests/ -q`; `python -m lab.runner --condition baseline --tasks learn`; `python -m lab.runner --condition subagents --tasks learn`; `python -m lab.curator`; `python -m lab.runner --condition skills-auto --tasks learn`; lưu kết quả này thành `results/skills-auto-dev/`; commit giả thuyết và tag `freeze`; `python -m lab.runner --condition baseline --tasks eval`; `python -m lab.runner --condition subagents --tasks eval`; `python -m lab.runner --condition skills-auto --tasks all`; `python scripts/verify_freeze.py`; `python -m lab.compare > report/table.md`; `python scripts/check_breakdown.py`. Các lệnh mô hình chạy tuần tự trong Docker Linux với tệp `.env` cục bộ do người chạy tự cung cấp; `.env` không nằm trong Git.
- Thử thách mở rộng: không thực hiện để giữ cùng ngân sách và tập trung phân tích kết quả chính.
- Ghi chú: ước tính chi phí ở mục 8 chỉ dựa trên token của 18 ca chính thức; không gồm ca thử kết nối, curator hoặc mọi sai khác về giảm giá/cache trên hóa đơn. Bản Gemini nộp tạm trước đây là thí nghiệm riêng, được lưu trong Git history và tag `freeze-gemini-interim`.

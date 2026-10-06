"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use only when a task needs independent inspection of several "
                "instructions, data formats, or code files before the main agent "
                "makes a change. Return a short evidence report; do not implement."
            ),
            "system_prompt": (
                "Read the smallest relevant set of files, normally within six tool "
                "calls. Report concrete facts, paths, and uncertainty. Do not edit "
                "files or solve the whole task; the main agent is the only writer."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use only after the main agent has produced files and needs an "
                "independent read-only check against task rules or edge cases."
            ),
            "system_prompt": (
                "Review only the supplied requirements and produced files, normally "
                "within six tool calls. Do not edit files or take over implementation. "
                "Report precise discrepancies and evidence to the main agent."
            ),
        },
    ]

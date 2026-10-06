"""GUIDE Phần 1 - Chạy một tác vụ (task) và ghi kết quả.   >>> SINH VIÊN CÀI ĐẶT run_task <<<

Pseudo-code: guides/pseudocode/03_runner.md
Kiểm tra:    pytest tests/test_03_runner.py
Chạy thật:   python -m lab.runner --condition baseline --tasks learn
"""
import argparse
import json
import os
import re
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.callbacks import UsageMetadataCallbackHandler
from langchain_core.messages import AIMessage, ToolMessage

from .agent import build_agent
from .grading import grade                                                      # có sẵn
from .tasks import ROOT, get_task, hash_dir, list_tasks, prepare_sandbox         # có sẵn

# Ba điều kiện thí nghiệm (condition). `skills_dir` là thư mục skill nguồn (tính từ thư mục gốc của lab).
CONDITIONS = {
    "baseline": {"mode": "single", "skills_dir": None},
    "subagents": {"mode": "subagents", "skills_dir": None},
    "skills-auto": {"mode": "single", "skills_dir": "skills/auto"},
}


def render_trace(messages) -> str:
    """CÓ SẴN, KHÔNG SỬA. Chuyển danh sách message của luồng chính thành Markdown (vết - trace).

    Lưu ý: chỉ gồm luồng chính. Việc subagent làm bên trong KHÔNG hiện trong vết;
    chỉ thấy lệnh gọi `task` và báo cáo cuối của subagent.
    """
    home = str(Path.home())

    def clean(text) -> str:
        return str(text).replace(home, "~")[:1500]

    parts = []
    for m in messages:
        if isinstance(m, AIMessage):
            if m.content:
                parts.append(f"### Assistant\n{clean(m.content)}")
            for tc in m.tool_calls:
                parts.append(f"### Tool call: {tc['name']}\n{clean(json.dumps(tc['args'], ensure_ascii=False))}")
        elif isinstance(m, ToolMessage):
            parts.append(f"### Tool result\n{clean(m.content)}")
        else:
            parts.append(f"### {m.type.capitalize()}\n{clean(m.content)}")
    return "\n\n".join(parts)


def run_task(task_id: str, condition: str, results_dir="results", model=None, recursion_limit: int = 60) -> dict:
    """Chạy MỘT tác vụ dưới MỘT điều kiện, chấm điểm, ghi kết quả, và trả về bản ghi (record).

    Ghi vào: <results_dir>/<condition>/<task_id>/run.json và trace.md  (trace.md = render_trace(messages)).
    Bản ghi `run.json` phải có các khóa:
      task, condition, role, score, passed, total, checks,
      tokens {input, output, total}       - cộng dồn mọi lần gọi LLM, kể cả subagent (dùng UsageMetadataCallbackHandler)
      tool_calls                          - số tool call trong các AIMessage của luồng chính (không gồm việc bên trong subagent)
      subagent_calls                      - số tool call có tên "task" (giao việc cho subagent)
      skills_read                         - số skill KHÁC NHAU đã được đọc: với mỗi tool call "read_file" có file_path chứa
                                            "skills/", lấy tên thư mục ngay sau "skills/" rồi đếm các tên khác nhau
                                            (đọc lại cùng một skill chỉ tính một lần)
      skills_modified (bool)              - thư mục skills trong sandbox bị đổi trong lúc chạy (so hash_dir trước/sau)
      skills_sha256                       - hash_dir(sandbox/"skills") TRƯỚC khi chạy (để đối chiếu với skill đã đóng băng)
      timestamp                           - thời điểm bắt đầu, UTC, dạng ISO-8601
      seconds, final_message, error (None nếu không lỗi)
    Lỗi khi chạy tác tử KHÔNG được làm chương trình dừng: ghi vào `error` và vẫn chấm điểm.
    Sandbox là thư mục tạm NGOÀI kho mã nguồn và phải được xóa sau khi chạy.
    """
    cfg = CONDITIONS[condition]
    task = get_task(task_id)
    skills_dir = ROOT / cfg["skills_dir"] if cfg["skills_dir"] else None
    out = Path(results_dir) / condition / task_id
    out.mkdir(parents=True, exist_ok=True)
    record = {
        "task": task.id,
        "condition": condition,
        "role": task.role,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": None,
        "seconds": 0.0,
        "tokens": {"input": 0, "output": 0, "total": 0},
        "tool_calls": 0,
        "subagent_calls": 0,
        "skills_read": 0,
        "skills_modified": False,
        "skills_sha256": "",
        "final_message": "",
    }
    messages = []
    trace_text = ""
    with tempfile.TemporaryDirectory(prefix="day20-agent-") as tmp:
        sandbox = Path(tmp)
        started = time.perf_counter()
        try:
            prepare_sandbox(task, sandbox, skills_dir)
            skills_before = hash_dir(sandbox / "skills")
            record["skills_sha256"] = skills_before
            usage = UsageMetadataCallbackHandler()
            agent = build_agent(
                sandbox, mode=cfg["mode"], use_skills=skills_dir is not None, model=model
            )
            try:
                token_budget = int(os.getenv("LAB_TASK_TOKEN_BUDGET", "0"))
                for state in agent.stream(
                    {"messages": [{"role": "user", "content": task.instruction}]},
                    config={"callbacks": [usage], "recursion_limit": recursion_limit},
                    stream_mode="values",
                ):
                    messages = state.get("messages", messages)
                    consumed = sum(
                        int(value.get("total_tokens", 0))
                        for value in usage.usage_metadata.values()
                    )
                    if token_budget and consumed >= token_budget:
                        raise RuntimeError(
                            f"task token budget reached: {consumed} >= {token_budget}"
                        )
                if messages:
                    record["final_message"] = str(messages[-1].content)
            except Exception as exc:  # record failures instead of aborting the experiment
                record["error"] = f"{type(exc).__name__}: {exc}"
                if messages:
                    record["final_message"] = str(messages[-1].content)

            for value in usage.usage_metadata.values():
                record["tokens"]["input"] += int(value.get("input_tokens", 0))
                record["tokens"]["output"] += int(value.get("output_tokens", 0))
                record["tokens"]["total"] += int(value.get("total_tokens", 0))

            calls = [call for msg in messages if isinstance(msg, AIMessage)
                     for call in msg.tool_calls]
            record["tool_calls"] = len(calls)
            record["subagent_calls"] = sum(call.get("name") == "task" for call in calls)
            skills_read = set()
            for call in calls:
                if call.get("name") != "read_file":
                    continue
                path = str(call.get("args", {}).get("file_path", "")).replace("\\", "/")
                match = re.search(r"(?:^|/)skills/([^/]+)/SKILL\.md$", path)
                if match:
                    skills_read.add(match.group(1))
            record["skills_read"] = len(skills_read)
            record["skills_modified"] = hash_dir(sandbox / "skills") != skills_before
        except Exception as exc:  # also record setup failures
            record["error"] = f"{type(exc).__name__}: {exc}"
        finally:
            record["seconds"] = round(time.perf_counter() - started, 1)
            result = grade(task, sandbox / "workspace")
            record.update({k: result.get(k) for k in ("score", "passed", "total", "checks")})
            if result.get("error") and record["error"] is None:
                record["error"] = result["error"]
            trace_text = render_trace(messages)

    # Provider exceptions can include a credential; never persist one in a run artifact.
    for key in ("LAB_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"):
        secret = os.getenv(key)
        if secret and len(secret) >= 8:
            trace_text = trace_text.replace(secret, "[REDACTED]")
            for field in ("error", "final_message"):
                if record[field]:
                    record[field] = record[field].replace(secret, "[REDACTED]")
    (out / "trace.md").write_text(trace_text, encoding="utf-8")
    (out / "run.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return record


def main(argv=None):
    """CÓ SẴN, KHÔNG SỬA. Giao diện dòng lệnh (CLI): --condition, --tasks (id... | all | learn | eval), --results, --recursion-limit.

    In mỗi lần chạy một dòng: điều kiện, id, passed/total, token, số tool call, số giây, lỗi (nếu có).
    """
    ap = argparse.ArgumentParser(description="Run tasks under one condition.")
    ap.add_argument("--condition", required=True, choices=sorted(CONDITIONS))
    ap.add_argument("--tasks", nargs="+", default=["all"], help="task ids, or 'all', 'learn', 'eval'")
    ap.add_argument("--results", default="results")
    ap.add_argument("--recursion-limit", type=int, default=60)
    args = ap.parse_args(argv)
    if args.tasks == ["all"]:
        ids = [t.id for t in list_tasks()]
    elif args.tasks in (["learn"], ["eval"]):
        ids = [t.id for t in list_tasks(args.tasks[0])]
    else:
        ids = args.tasks
    for tid in ids:
        try:
            r = run_task(tid, args.condition, args.results, recursion_limit=args.recursion_limit)
        except Exception as exc:  # noqa: BLE001
            print(f"{args.condition:13s} {tid:11s} CRASH {type(exc).__name__}: {exc}", flush=True)
            continue
        print(f"{args.condition:13s} {tid:11s} score={r['passed']}/{r['total']} tokens={r['tokens']['total']} "
              f"calls={r['tool_calls']} {r['seconds']}s" + (f" ERROR={r['error']}" if r["error"] else ""), flush=True)


if __name__ == "__main__":
    main()

"""ETL 表血缘分析工具"""

import argparse
import json
import re
import smtplib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from email.message import EmailMessage
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    ETL_GRAPH_FILE,
    ETL_INDEX_FILE,
    ETL_SQL_DIR,
    IGNORE_DAVINCI,
    IGNORE_DIRS,
    IGNORE_PATTERNS,
    MAIL_CONFIG,
    OUTPUT_DIR,
)


TARGET_TABLE_PATTERN = re.compile(r"([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)_etl\.sql$")


@dataclass
class LineageResult:
    sources: list[str] = field(default_factory=list)
    target: str = ""
    etl_path: str = ""


def should_parse(file_path: Path) -> bool:
    """判断文件是否需要解析血缘"""
    relative = file_path.relative_to(ETL_SQL_DIR)

    if relative.parts[0] in IGNORE_DIRS:
        return False

    for pattern in IGNORE_PATTERNS:
        if str(relative).startswith(pattern):
            return False

    if relative.parts[0].startswith("davinci-"):
        for suffix in IGNORE_DAVINCI:
            if relative.parts[0].endswith(f"-{suffix}"):
                return False

    return file_path.name.endswith("_etl.sql")


def extract_target_table(file_path: Path) -> str | None:
    """从文件名提取 Target Table，如 cdm_abite.dim_shop_etl.sql -> cdm_abite.dim_shop"""
    match = TARGET_TABLE_PATTERN.search(file_path.name)
    if match:
        return f"{match.group(1)}.{match.group(2)}"
    return None


def parse_etl_file(file_path: Path) -> LineageResult | None:
    """调用 sqllineage 解析单个 ETL 文件"""
    try:
        result = subprocess.run(
            ["sqllineage", "-f", str(file_path), "--dialect=hive"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout + result.stderr

        sources = []
        in_sources = False
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("Source Tables:"):
                in_sources = True
                continue
            if line.startswith("Target Tables:"):
                in_sources = False
                continue
            if in_sources and line and not line.startswith("("):
                sources.append(line.rstrip(",").strip())

        target = extract_target_table(file_path)
        if not target:
            return None

        return LineageResult(sources=sources, target=target, etl_path=str(file_path))
    except Exception:
        return None


def generate_index(tables: dict):
    lines = []
    for table, data in sorted(tables.items()):
        upstreams_str = ", ".join(data["upstreams"]) if data["upstreams"] else ""
        etl_str = ", ".join(data["source_of_etl"]) if data["source_of_etl"] else ""

        if upstreams_str:
            lines.append(f"{table} — 上游: {upstreams_str} — ETL: {etl_str}")
        elif etl_str:
            lines.append(f"{table} — 上游: (无) — ETL: {etl_str}")
        else:
            lines.append(f"{table} — 上游: (无) — ETL: (无)")

    with open(ETL_INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def send_failure_email(failed_files: list[tuple[str, str]]):
    if not MAIL_CONFIG["enabled"]:
        return

    msg = EmailMessage()
    msg["Subject"] = f"ETL 血缘解析失败：{len(failed_files)} 个文件"
    msg["From"] = MAIL_CONFIG["from_addr"]
    msg["To"] = ", ".join(MAIL_CONFIG["to_addrs"])

    body = "解析失败的文件：\n\n"
    for path, reason in failed_files[:50]:
        body += f"- {path}: {reason}\n"
    if len(failed_files) > 50:
        body += f"\n... 共 {len(failed_files)} 个文件\n"

    msg.set_content(body)

    with smtplib.SMTP(MAIL_CONFIG["smtp_host"], MAIL_CONFIG["smtp_port"]) as server:
        server.starttls()
        server.send_message(msg)


def run_all():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_results: list[LineageResult] = []
    failed_files: list[tuple[str, str]] = []

    etl_files = [f for f in ETL_SQL_DIR.rglob("*_etl.sql") if should_parse(f)]

    print(f"Found {len(etl_files)} ETL files to parse")

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(parse_etl_file, f): f for f in etl_files}
        for future in as_completed(futures):
            result = future.result()
            if result:
                all_results.append(result)
            else:
                failed_files.append((str(futures[future]), "sqllineage parse failed"))

    tables: dict[str, dict] = {}

    for r in all_results:
        if r.target not in tables:
            tables[r.target] = {"source_of_etl": [], "upstreams": [], "downstreams": []}
        tables[r.target]["source_of_etl"].append(r.etl_path)

    source_to_etls: dict[str, list[str]] = {}
    for r in all_results:
        for source in r.sources:
            if source not in source_to_etls:
                source_to_etls[source] = []
            source_to_etls[source].append(r.etl_path)

    for r in all_results:
        tables[r.target]["upstreams"] = r.sources

    for source, etl_list in source_to_etls.items():
        if source not in tables:
            tables[source] = {"source_of_etl": [], "upstreams": [], "downstreams": []}
        tables[source]["downstreams"] = list(set(etl_list))

    for table_data in tables.values():
        table_data["source_of_etl"] = list(set(table_data["source_of_etl"]))
        table_data["downstreams"] = list(set(table_data["downstreams"]))

    output = {"tables": tables}
    with open(ETL_GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    generate_index(tables)

    print(f"Success: {len(all_results)}, Failed: {len(failed_files)}")

    if failed_files:
        send_failure_email(failed_files)


def main():
    parser = argparse.ArgumentParser(description="ETL 表血缘分析工具")
    parser.add_argument("--all", action="store_true", help="全量解析")
    args = parser.parse_args()

    if args.all:
        run_all()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

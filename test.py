"""
pathlib 实战演练
目标：对根目录下的 sample_data.txt 及相关文件进行完整的 pathlib 操作
"""

from pathlib import Path
import shutil
import json


def main():
    # 定位项目根目录和样本文件
    current_file = Path(__file__).resolve()
    project_root = current_file.parent
    sample_file = project_root / "sample_data.txt"

    print("=" * 50)
    print("pathlib 实战演练")
    print("=" * 50)

    # 1. 基础信息查看
    print("\n【1】样本文件基础信息")
    print(f"  文件路径: {sample_file}")
    print(f"  绝对路径: {sample_file.absolute()}")
    print(f"  文件名: {sample_file.name}")
    print(f"  无后缀名: {sample_file.stem}")
    print(f"  后缀: {sample_file.suffix}")
    print(f"  是否存在: {sample_file.exists()}")
    print(f"  是否文件: {sample_file.is_file()}")
    print(f"  文件大小: {sample_file.stat().st_size} 字节")

    # 2. 读取并分析内容
    print("\n【2】读取并分析 sample_data.txt 内容")
    content = sample_file.read_text(encoding="utf-8")  
    lines = content.splitlines()

    print(f"  总行数: {len(lines)}")
    print(f"  总字符数: {len(content)}")

    # 3. 提取特定信息
    print("\n【3】提取团队成员列表")
    team_lines = [line for line in lines if line.strip().startswith("- ")]
    team_members = [line.strip()[2:] for line in team_lines]
    print(f"  成员: {team_members}")

    print("\n【4】提取待办事项")
    todo_lines = [line.strip() for line in lines if line.strip() and line.strip()[0].isdigit() and ". " in line]
    for todo in todo_lines:
        print(f"  {todo}")

    print("\n【5】提取日志记录")
    log_lines = [line for line in lines if line.strip().startswith("[")]
    for log in log_lines:
        print(f"  {log.strip()}")

    # 4. 创建处理结果目录
    print("\n【6】创建处理结果目录")
    result_dir = project_root / "processed_results"
    result_dir.mkdir(exist_ok=True)
    print(f"  创建目录: {result_dir}")

    # 5. 备份原文件
    print("\n【7】备份原文件")
    backup_dir = result_dir / "backup"
    backup_dir.mkdir(exist_ok=True)
    backup_file = backup_dir / f"{sample_file.stem}_backup{sample_file.suffix}"
    shutil.copy(sample_file, backup_file)
    print(f"  备份至: {backup_file}")
    print(f"  备份文件大小: {backup_file.stat().st_size} 字节")

    # 6. 将提取的数据写入 JSON
    print("\n【8】将提取的数据导出为 JSON")
    data = {
        "project_name": "MyFastAPI App",
        "team_members": team_members,
        "todos": [line.split(". ", 1)[1] for line in todo_lines],
        "logs": [line.strip() for line in log_lines]
    }
    json_file = result_dir / "extracted_data.json"
    json_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  导出至: {json_file}")

    # 7. 生成处理报告
    print("\n【9】生成处理报告")
    report_file = result_dir / "report.txt"
    report_lines = [
        "处理报告",
        "=" * 30,
        f"源文件: {sample_file.name}",
        f"源文件大小: {sample_file.stat().st_size} 字节",
        f"总行数: {len(lines)}",
        f"团队成员数: {len(team_members)}",
        f"待办事项数: {len(todo_lines)}",
        f"日志条数: {len(log_lines)}",
        "",
        "团队成员:",
    ]
    for member in team_members:
        report_lines.append(f"  - {member}")
    report_lines.append("")
    report_lines.append("待办事项:")
    for todo in todo_lines:
        report_lines.append(f"  {todo}")
    report_lines.append("")
    report_lines.append("日志记录:")
    for log in log_lines:
        report_lines.append(f"  {log}")

    report_file.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"  报告路径: {report_file}")

    # 8. 查找项目下所有 .py 文件
    print("\n【10】查找项目根目录下所有 Python 文件")
    py_files = list(project_root.glob("*.py"))
    print(f"  共找到 {len(py_files)} 个 .py 文件:")
    for pf in py_files:
        print(f"    - {pf.name}")

    # 9. 重命名报告文件
    print("\n【11】重命名报告文件")
    final_report = result_dir / "final_report.txt"
    report_file.rename(final_report)
    print(f"  重命名为: {final_report.name}")

    # 10. 列出处理结果目录
    print("\n【12】处理结果目录结构")
    for item in result_dir.rglob("*"):
        depth = len(item.relative_to(result_dir).parts) - 1
        indent = "  " * depth
        if item.is_dir():
            print(f"{indent}[DIR]  {item.name}/")
        else:
            print(f"{indent}[FILE] {item.name} ({item.stat().st_size} bytes)")

    print("\n" + "=" * 50)
    print("实战演练完成！")
    print(f"请查看目录: {result_dir}")
    print("=" * 50)
    print("=" * 50)
    print("=" * 50)


if __name__ == "__main__":
    main()

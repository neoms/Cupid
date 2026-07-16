"""将 user_data.json 中的数据逐条导入到 API

用法: uv run python test/import_users.py [--base-url http://localhost:8000]
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Generator

import httpx

# 并发数，避免打爆服务
CONCURRENCY = 5
API_BASE = "http://localhost:8000"


def iter_users(filepath: str) -> Generator[dict, None, None]:
    """
    逐条迭代 JSON 数组中的对象，避免一次性加载整个文件到内存。

    使用两层策略：
    1. 文件较小时（< 1MB）直接 json.load 后逐个 yield
    2. 文件较大时，使用 JSONDecoder.raw_decode 流式解析
    """
    file_size = Path(filepath).stat().st_size
    if file_size < 1_000_000:
        # 小文件：一次性解析，通过 yield from 保持迭代器语义
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        yield from data
        return

    # 大文件：流式解析
    decoder = json.JSONDecoder()
    with open(filepath, encoding="utf-8") as f:
        buf = ""
        started = False
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            buf += chunk
            if not started:
                # 跳过开头的 [
                idx = buf.find("[")
                if idx == -1:
                    continue
                buf = buf[idx + 1:]
                started = True

            # 逐条解析
            while True:
                trimmed = buf.lstrip()
                if not trimmed:
                    break
                if trimmed[0] == "]":
                    return
                try:
                    obj, end = decoder.raw_decode(trimmed)
                    yield obj
                    buf = trimmed[end:].lstrip()
                    if buf.startswith(","):
                        buf = buf[1:]
                except json.JSONDecodeError:
                    # 当前 buf 不足以解析完整对象，继续读取
                    buf = trimmed
                    break


async def import_user(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    user: dict,
    index: int,
    total: int,
) -> tuple[int, bool, str]:
    """导入单个用户，返回 (序号, 成功, 信息)"""
    async with semaphore:
        try:
            resp = await client.post(
                f"{API_BASE}/api/profiles",
                json=user,
                timeout=60.0,  # 包含 embedding 调用的时间
            )
            if resp.status_code == 201:
                data = resp.json()
                return (index, True, f"{data['nickname']} (user_id={data['user_id']})")
            else:
                return (index, False, f"HTTP {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            return (index, False, str(e))


async def main():
    # 解析命令行参数
    base_url = API_BASE
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--base-url" and i + 1 < len(args):
            base_url = args[i + 1]

    data_file = Path(__file__).parent / "user_data.json"
    if not data_file.exists():
        print(f"✗ 文件不存在: {data_file}")
        sys.exit(1)

    # 先遍历计数（JSON 数组无法直接获取长度，需要完整解析）
    print(f"读取数据文件: {data_file}")
    users = list(iter_users(str(data_file)))
    total = len(users)
    print(f"共 {total} 条数据，并发数: {CONCURRENCY}")
    print(f"目标服务: {base_url}\n")

    semaphore = asyncio.Semaphore(CONCURRENCY)
    success = 0
    fail = 0

    async with httpx.AsyncClient(base_url=base_url) as client:
        tasks = [
            import_user(client, semaphore, user, i + 1, total)
            for i, user in enumerate(users)
        ]

        # 逐个获取结果，按完成顺序打印进度
        for coro in asyncio.as_completed(tasks):
            idx, ok, msg = await coro
            if ok:
                success += 1
                print(f"[{idx:3d}/{total}] ✓ {msg}")
            else:
                fail += 1
                print(f"[{idx:3d}/{total}] ✗ {msg}")

    print(f"\n{'='*40}")
    print(f"完成: 成功 {success} 条, 失败 {fail} 条")


if __name__ == "__main__":
    asyncio.run(main())

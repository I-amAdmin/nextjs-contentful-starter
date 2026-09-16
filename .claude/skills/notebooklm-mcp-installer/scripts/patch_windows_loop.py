#!/usr/bin/env python3
"""
תיקון קריסת login על Windows.

הבעיה: החבילה notebooklm-py קובעת WindowsSelectorEventLoopPolicy באופן גלובלי
(תיקון לבאג נישתי #79 של Sandboxie). אבל Playwright חייב את ProactorEventLoop
כדי להפעיל תת-תהליך על Windows — זו הדרך היחידה שם להריץ תהליך חיצוני מ-asyncio.

התוצאה: הפקודה `notebooklm login` קורסת מיד עם

    NotImplementedError
      File "...\\asyncio\\base_events.py", line 539, in _make_subprocess_transport

בלי לפתוח בכלל חלון דפדפן — המשתמש חושב שהתוכנה "לא עושה כלום".

הסקריפט מנטרל את שתי הקריאות ל-set_event_loop_policy בקובץ notebooklm_cli.py,
ומשאיר את ברירת המחדל של Windows (ProactorEventLoop), שתומכת גם בהפעלת
תת-תהליך וגם בתקשורת רשת רגילה.

**רלוונטי ל-Windows בלבד.** על Mac/Linux הקוד עטוף ב-if sys.platform == "win32"
ולא רץ — אפשר להריץ את הסקריפט בכל מקרה, הוא פשוט לא ישנה דבר מהותי.

קרדיט לאיתור ולאבחון: אליאור שימנוב, ספטמבר 2026.

הרצה:
    python patch_windows_loop.py                 # תיקון
    python patch_windows_loop.py --check         # בדיקה בלבד
    python patch_windows_loop.py --restore       # שחזור מהגיבוי
"""

import argparse
import shutil
import sys
from pathlib import Path

TARGET = "asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())"

REPLACEMENT = (
    "# DISABLED by notebooklm-mcp-installer:\n"
    "    # SelectorEventLoopPolicy שובר את הפעלת התת-תהליך של Playwright על Windows\n"
    "    # (NotImplementedError ב-login). ProactorEventLoop — ברירת המחדל — תומך\n"
    "    # גם בתת-תהליך וגם ב-I/O רשת. ה-policy נדרש רק למקרה הקצה של issue #79.\n"
    "    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())"
)


def find_cli(start: Path) -> Path | None:
    """מאתר את notebooklm_cli.py בתוך ה-venv (Mac/Linux/Windows)."""
    for venv in (start / ".venv", start / "venv"):
        if not venv.exists():
            continue
        for pattern in ("lib/python*/site-packages", "Lib/site-packages"):
            for sp in venv.glob(pattern):
                cli = sp / "notebooklm" / "notebooklm_cli.py"
                if cli.is_file():
                    return cli
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="בדיקה בלבד")
    ap.add_argument("--restore", action="store_true", help="שחזור מהגיבוי")
    ap.add_argument("--dir", default=".", help="תיקיית הפרויקט")
    args = ap.parse_args()

    root = Path(args.dir).expanduser().resolve()
    cli = find_cli(root)

    if cli is None:
        print("❌ לא נמצא notebooklm_cli.py.")
        print(f"   חיפשתי תחת: {root}")
        print("   ודאו שאתם בתיקיית notebooklm-mcp ושהרצתם 'uv sync'.")
        return 1

    backup = cli.with_suffix(".py.bak_pre_loop_patch")

    if args.restore:
        if not backup.exists():
            print(f"❌ לא נמצא גיבוי ב-{backup}")
            return 1
        shutil.copy2(backup, cli)
        print(f"✅ שוחזר מהגיבוי: {backup}")
        return 0

    text = cli.read_text(encoding="utf-8")

    # שורות פעילות בלבד — לא כאלה שכבר מנוטרלות בהערה
    active = [
        ln
        for ln in text.splitlines()
        if TARGET in ln and not ln.lstrip().startswith("#")
    ]

    if not active:
        print("✅ התיקון כבר מוחל — אין מה לעשות.")
        return 0

    print(f"📄 קובץ: {cli}")
    print(f"🔧 קריאות פעילות שיש לנטרל: {len(active)}")

    if args.check:
        print("\n(מצב בדיקה — לא בוצע שינוי. הריצו בלי --check כדי לתקן.)")
        return 0

    if not backup.exists():
        shutil.copy2(cli, backup)
        print(f"💾 גיבוי נשמר: {backup}")

    out = []
    patched = 0
    for line in text.splitlines():
        if TARGET in line and not line.lstrip().startswith("#"):
            indent = line[: len(line) - len(line.lstrip())]
            out.append(indent + REPLACEMENT)
            patched += 1
        else:
            out.append(line)

    cli.write_text("\n".join(out) + "\n", encoding="utf-8")

    print(f"   ✓ נוטרלו {patched} קריאות")
    print("\n✅ התיקון הוחל.")
    print("   בדיקה: uv run notebooklm login")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
תיקון דומיין NotebookLM.

גוגל העבירה את השירות מ-notebooklm.google.com ל-notebook.google.com
(המותג החדש: "Gemini Notebook"). הספרייה notebooklm-py עדיין מקודדת
את הדומיין הישן, ולכן כל קריאה נכשלת עם
"Authentication expired or invalid".

הסקריפט:
  1. מאתר את חבילת notebooklm בתוך ה-venv (Mac/Linux/Windows)
  2. מגבה אותה
  3. מחליף את כתובות ה-API לדומיין החדש
  4. מוסיף את הדומיין החדש לרשימת דומייני הקוקיז המורשים

הרצה:
    python patch_domain.py                 # תיקון
    python patch_domain.py --check         # בדיקה בלבד, בלי שינוי
    python patch_domain.py --restore       # שחזור מהגיבוי

הסקריפט אידמפוטנטי: הרצה חוזרת לא תזיק.
"""

import argparse
import shutil
import sys
from pathlib import Path

OLD = "https://notebooklm.google.com"
NEW = "https://notebook.google.com"

COOKIE_OLD = '''    ".google.com",
    "notebooklm.google.com",
    ".googleusercontent.com",'''

COOKIE_NEW = '''    ".google.com",
    "notebooklm.google.com",
    "notebook.google.com",
    ".notebook.google.com",
    ".googleusercontent.com",'''


def find_package(start: Path) -> Path | None:
    """מאתר את תיקיית חבילת notebooklm בתוך ה-venv.

    תומך גם ב-Mac/Linux (lib/pythonX.Y/site-packages)
    וגם ב-Windows (Lib/site-packages).
    """
    for venv in (start / ".venv", start / "venv"):
        if not venv.exists():
            continue
        for pattern in ("lib/python*/site-packages", "Lib/site-packages"):
            for sp in venv.glob(pattern):
                pkg = sp / "notebooklm"
                if pkg.is_dir():
                    return pkg
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="בדיקה בלבד")
    ap.add_argument("--restore", action="store_true", help="שחזור מהגיבוי")
    ap.add_argument("--dir", default=".", help="תיקיית הפרויקט (ברירת מחדל: הנוכחית)")
    args = ap.parse_args()

    root = Path(args.dir).expanduser().resolve()
    pkg = find_package(root)

    if pkg is None:
        print("❌ לא נמצאה חבילת notebooklm.")
        print(f"   חיפשתי תחת: {root}")
        print("   ודאו שאתם בתיקיית notebooklm-mcp ושהרצתם 'uv sync'.")
        return 1

    backup = pkg.parent / "notebooklm_backup_pre_domain_patch"

    if args.restore:
        if not backup.exists():
            print(f"❌ לא נמצא גיבוי ב-{backup}")
            return 1
        shutil.rmtree(pkg)
        shutil.copytree(backup, pkg)
        print(f"✅ שוחזר מהגיבוי: {backup}")
        return 0

    py_files = sorted(pkg.rglob("*.py"))
    need_url = [f for f in py_files if OLD in f.read_text(encoding="utf-8")]

    auth = pkg / "auth.py"
    need_cookie = auth.exists() and COOKIE_OLD in auth.read_text(encoding="utf-8")

    if not need_url and not need_cookie:
        print("✅ התיקון כבר מוחל — אין מה לעשות.")
        return 0

    print(f"📁 חבילה: {pkg}")
    print(f"🔗 קבצים עם הדומיין הישן: {len(need_url)}")
    print(f"🍪 צריך עדכון דומייני קוקיז: {'כן' if need_cookie else 'לא'}")

    if args.check:
        print("\n(מצב בדיקה — לא בוצע שינוי. הריצו בלי --check כדי לתקן.)")
        return 0

    if not backup.exists():
        shutil.copytree(pkg, backup)
        print(f"💾 גיבוי נשמר: {backup}")

    for f in need_url:
        text = f.read_text(encoding="utf-8")
        f.write_text(text.replace(OLD, NEW), encoding="utf-8")
        print(f"   ✓ {f.relative_to(pkg)}")

    if need_cookie:
        text = auth.read_text(encoding="utf-8")
        auth.write_text(text.replace(COOKIE_OLD, COOKIE_NEW), encoding="utf-8")
        print("   ✓ auth.py (דומייני קוקיז)")

    print("\n✅ התיקון הוחל.")
    print("   בדיקה: uv run notebooklm list")
    return 0


if __name__ == "__main__":
    sys.exit(main())

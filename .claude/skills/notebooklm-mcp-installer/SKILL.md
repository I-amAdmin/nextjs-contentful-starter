---
name: notebooklm-mcp-installer
description: 'התקנה מלווה שלב-אחר-שלב של חיבור NotebookLM (Gemini Notebook) לקלוד קוד דרך MCP — כולל התחברות לגוגל, תיקון הדומיין שגוגל שינתה, רישום ה-MCP ובדיקת תקינות. השתמש כשמשתמש מבקש: "תתקין לי נוטבוק", "חבר את NotebookLM לקלוד", "התקנת MCP של נוטבוק", "install notebooklm mcp", "connect notebooklm". גם כשמשתמש כבר התקין ונתקל בשגיאה — "Authentication expired or invalid", "notebooklm לא עובד", "הסקיל של נוטבוק נשבר", "Executable does not exist", "Opening in existing browser session", "NotImplementedError", "login לא פותח דפדפן" — הפעל את הסקיל ולך לפרק פתרון תקלות. גם כשמבקשים לעדכן/לתקן התקנה קיימת אחרי uv sync.'
---

# התקנת NotebookLM MCP לקלוד קוד

## מטרה

לחבר את NotebookLM (שנקרא היום **Gemini Notebook**) לקלוד קוד, כך שאפשר יהיה
ליצור נוטבוקים, להוסיף מקורות, לתשאל, ולייצר פודקאסטים / מצגות / כרטיסיות —
הכל משורת הפקודה, בלי לגעת בדפדפן.

## לפני שמתחילים — מה חשוב שהמשתמש ידע

אמור את זה למשתמש בפתיחה, בקצרה. עדיף שישמע מראש מאשר שיגלה באמצע:

1. **אין ל-NotebookLM API רשמי.** הכלי מתחזה לדפדפן ומשתמש בקוקיז של החשבון.
   ההערה בקוד עצמו אומרת "reverse-engineered from network traffic analysis".
2. **המשמעות:** גוגל יכולה לשבור את זה בלי הודעה מראש. זה קרה כבר — ראו פרק התיקון.
   זה כנראה מנוגד לתנאי השימוש של גוגל; לא מומלץ לשימוש בנפח גדול או עסקי-קריטי.
3. **ההתקנה דורשת סבלנות** — כ-15 דקות, וכוללת שלב תיקון קוד (אוטומטי).
4. **לא להסתמך על זה בהדגמה חיה.** ראו "כללי אצבע להדגמה" בסוף.

אם המשתמש לא בסדר עם אלה — עצור והצע לו לעבוד עם NotebookLM בדפדפן.

## זרימת ההתקנה

בצע את השלבים לפי הסדר. **אל תדלג** — כל שלב מאמת את הקודם.
אחרי כל שלב, ודא הצלחה לפני המעבר הלאה.

---

### שלב 0 — לזהות מערכת הפעלה

שאל או זהה: **Mac או Windows?** הפקודות שונות.
בכל השלבים מופיעים שני מסלולים — השתמש רק בזה שרלוונטי.

---

### שלב 1 — דרישות קדם

בדוק מה כבר מותקן:

**Mac:**
```bash
which uv; python3 --version; git --version
```

**Windows (PowerShell):**
```powershell
where.exe uv; python --version; git --version
```

אם `uv` חסר:

**Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

אחרי התקנת uv — צריך לפתוח טרמינל חדש כדי שייכנס ל-PATH.

**גרסאות שנבדקו ועובדות:** Python 3.13, uv 0.7.13, notebooklm-py 0.3.1.

---

### שלב 2 — הורדה והתקנת תלויות

**Mac:**
```bash
mkdir -p ~/mcp-servers && cd ~/mcp-servers && git clone https://github.com/alfredang/notebooklm-mcp.git && cd notebooklm-mcp && uv sync
```

**Windows (PowerShell):**
```powershell
mkdir "$HOME\mcp-servers" -Force; cd "$HOME\mcp-servers"; git clone https://github.com/alfredang/notebooklm-mcp.git; cd notebooklm-mcp; uv sync
```

**אימות:** התיקייה מכילה `server.py`, `pyproject.toml`, ותיקיית `.venv`.

---

### שלב 3 — התקנת דפדפן ל-Playwright

**זהו שלב שנשכח והוא הכשל הראשון הנפוץ.** בלעדיו תתקבל השגיאה
`Executable doesn't exist at ... chrome-mac-arm64`.

```bash
uv run playwright install chromium
```

(אותה פקודה בשתי המערכות, מתוך תיקיית הפרויקט.)

השלב הזה מוריד כ-90MB — ייקח דקה או שתיים.

---

### שלב 3.5 — תיקון event loop (Windows בלבד — חובה)

**דלג על השלב הזה ב-Mac ו-Linux.**

ב-Windows, `notebooklm login` **קורס מיד** בלי לפתוח דפדפן, עם:

```
NotImplementedError
  File "...\asyncio\base_events.py", line 539, in _make_subprocess_transport
```

**הסיבה:** החבילה `notebooklm-py` קובעת `WindowsSelectorEventLoopPolicy` גלובלית
(תיקון לבאג נישתי של Sandboxie, issue #79). אבל Playwright חייב את
`ProactorEventLoop` כדי להפעיל תת-תהליך ב-Windows — זו הדרך היחידה שם.
התוצאה: תיקון לבאג נדיר שובר את `login` אצל **כל** משתמש Windows.

חשוב לומר למשתמש: **זה לא נראה כמו שגיאה** — נדמה שהתוכנה פשוט לא עושה כלום.

```powershell
python "$HOME\.claude\skills\notebooklm-mcp-installer\scripts\patch_windows_loop.py"
```

הסקריפט מגבה, מנטרל את שתי הקריאות, ואידמפוטנטי. יש גם `--check` ו-`--restore`.

*אותרה ואובחנה על ידי אליאור שימנוב, ספטמבר 2026.*

---

### שלב 4 — התחברות לחשבון גוגל

```bash
uv run notebooklm login
```

**מה קורה:** נפתח חלון דפדפן. המשתמש מתחבר לגוגל בעצמו.
**אתה לא מזין סיסמאות ולא נוגע בפרטי ההתחברות** — זו פעולה של המשתמש בלבד.

הנחיות שצריך למסור למשתמש **לפני** שהוא מריץ:

- להתחבר בחלון שנפתח, ולחכות שייטען דף הנוטבוקים.
- **לא לסגור את החלון ידנית.**
- אם גוגל מפנה למסך "בדיקת אבטחה" או "שינוי סיסמה" — לדלג עליו ("לא עכשיו" / ביטול).
- כשהדף נטען, לחזור לטרמינל וללחוץ ENTER.
- אם מופיעה אזהרה `Current URL is https://notebook.google.com/` — **לענות Y**.
  זו לא שגיאה; זה בדיוק הדומיין החדש של גוגל.

**אימות:** נוצר הקובץ
`~/.notebooklm/storage_state.json` (Mac) או `%USERPROFILE%\.notebooklm\storage_state.json` (Windows).

---

### שלב 5 — תיקון הדומיין (חובה)

**זה השלב הקריטי.** בלעדיו כל פקודה תיכשל עם
`Authentication expired or invalid`.

**הרקע:** גוגל העבירה את השירות מ-`notebooklm.google.com` ל-`notebook.google.com`
(מיתוג מחדש ל-"Gemini Notebook"). הספרייה `notebooklm-py` עדיין מקודדת את הדומיין
הישן בשבעה קבצים, כולל בכתובות ה-API עצמן.

הרץ את סקריפט התיקון מתיקיית הפרויקט:

```bash
python3 ~/.claude/skills/notebooklm-mcp-installer/scripts/patch_domain.py
```

**Windows:**
```powershell
python "$HOME\.claude\skills\notebooklm-mcp-installer\scripts\patch_domain.py"
```

הסקריפט מגבה את הספרייה לפני שינוי, מתקן 7 קבצים, ומוסיף את הדומיין החדש
לרשימת דומייני הקוקיז. הוא אידמפוטנטי — הרצה חוזרת בטוחה.

אפשרויות נוספות:
- `--check` — בדיקה בלבד, בלי לשנות
- `--restore` — שחזור מהגיבוי
- `--dir <path>` — אם לא מריצים מתיקיית הפרויקט

**אימות — זו בדיקת האמת של כל ההתקנה:**
```bash
uv run notebooklm list
```

צריכה להופיע טבלה עם הנוטבוקים של המשתמש. אם כן — ההתקנה עובדת.

---

### שלב 6 — רישום ה-MCP בקלוד קוד

צריך **נתיבים מלאים**, לא יחסיים.

**Mac:**
```bash
claude mcp add notebooklm -s user -- $HOME/.local/bin/uv --directory $HOME/mcp-servers/notebooklm-mcp run python server.py
```

**Windows (PowerShell):**
```powershell
claude mcp add notebooklm -s user -- "$HOME\.local\bin\uv.exe" --directory "$HOME\mcp-servers\notebooklm-mcp" run python server.py
```

**אימות:**
```bash
claude mcp list
```

יש לוודא ש-`notebooklm` מופיע. **צריך להפעיל מחדש את הסשן** כדי שהכלים ייטענו.

---

### שלב 7 — הגדרת שפה (למשתמשים בעברית)

```bash
uv run notebooklm language set iw
```

**חשוב לומר למשתמש:** זו הגדרה **גלובלית לכל החשבון** — היא משפיעה על כל
הנוטבוקים, גם אלה שנוצרים בממשק הרגיל.

---

### שלב 8 — בדיקת קצה-לקצה

הצע למשתמש לוודא שהכל עובד:

```bash
uv run notebooklm create "בדיקה"
uv run notebooklm source add "https://example.com" -n <ID>
uv run notebooklm ask -n <ID> "על מה המקור הזה?"
```

---

## פתרון תקלות

| השגיאה | הסיבה | הפתרון |
|---|---|---|
| `Authentication expired or invalid` | הדומיין לא תוקן, או שהתיקון נמחק | הרץ שוב את שלב 5 |
| `Executable doesn't exist at ...` | דפדפן Playwright לא הותקן | `uv run playwright install chromium` |
| `NotImplementedError` ב-`_make_subprocess_transport` בזמן `login` (Windows) | `notebooklm-py` קובעת `WindowsSelectorEventLoopPolicy` גלובלית ושוברת את הפעלת התת-תהליך של Playwright | הרץ את שלב 3.5 — `patch_windows_loop.py` |
| `login` לא פותח דפדפן וכאילו "לא קורה כלום" (Windows) | אותו באג — הקריסה מתרחשת לפני פתיחת הדפדפן | הרץ את שלב 3.5 |
| `Opening in existing browser session` | Chrome פתוח ותופס את הפרופיל | סגור את Chrome לגמרי ונסה שוב |
| `Server error 500 calling LIST_ARTIFACTS` | תקלה זמנית בצד גוגל | היצירה בדרך כלל ממשיכה ברקע — בדוק עם `artifact list` |
| הכל הפסיק לעבוד פתאום אחרי עדכון | `uv sync` דרס את התיקון | הרץ שוב את שלב 5 |
| `Unknown artifact type` | סוג תוצר חדש שהספרייה לא מכירה | אזהרה בלבד, לא שגיאה — אפשר להתעלם |

### סגירת Chrome

**Mac:**
```bash
osascript -e 'quit app "Google Chrome"'
```

**Windows (PowerShell):**
```powershell
Stop-Process -Name chrome -Force -ErrorAction SilentlyContinue
```

### האזהרה החשובה ביותר

**כל `uv sync` או עדכון חבילה ימחק את התיקונים.** אם משהו עבד והפסיק —
זו הסיבה הראשונה לבדוק. הפתרון: להריץ שוב את שלב 5, וב-Windows גם את שלב 3.5.

בדיקה מהירה ששני התיקונים במקומם:

```bash
python3 ~/.claude/skills/notebooklm-mcp-installer/scripts/patch_domain.py --check
python3 ~/.claude/skills/notebooklm-mcp-installer/scripts/patch_windows_loop.py --check
```

---

## אחרי ההתקנה — מה אפשר לעשות

| פעולה | פקודה |
|---|---|
| רשימת נוטבוקים | `notebooklm list` |
| יצירת נוטבוק | `notebooklm create "שם"` |
| הוספת מקור | `notebooklm source add <URL או קובץ> -n <ID>` |
| שאלה | `notebooklm ask -n <ID> "שאלה"` |
| פודקאסט | `notebooklm generate audio -n <ID> --wait` |
| מצגת | `notebooklm generate slide-deck -n <ID> --wait` |
| כרטיסיות / מבחן | `notebooklm generate flashcards\|quiz -n <ID> --wait` |
| הורדת תוצר | `notebooklm download <סוג> <נתיב-קובץ> -n <ID>` |

שים לב: ב-`download`, הארגומנט הראשון הוא **נתיב הקובץ** ולא מזהה —
טעות נפוצה שיוצרת תיקייה בשם ה-ID.

---

## כללי אצבע להדגמה מול קהל

מבוסס על ניסיון מהתקנה אמיתית:

1. **אל תייצר מצגת או פודקאסט בשידור חי.** לוקח 5-10 דקות ולפעמים נכשל.
   הכן מראש והצג את התוצר.
2. **מה כן להדגים חי:** `list` ו-`ask` — מהירים ומרשימים.
3. **הכן תוכנית גיבוי** — צילומי מסך או קבצים מוכנים.
4. **אל תבטיח יציבות.** זה כלי מבוסס reverse-engineering.

---

## מגבלות ידועות

- לא ניתן להוסיף מקורות לנוטבוק ש**שותף** איתך — רק לנוטבוקים בבעלותך.
  הפתרון: ליצור נוטבוק משלך ולהוסיף את אותם מקורות.
- יצירת תוצרים כבדים (מצגת, וידאו) לוקחת דקות ולעיתים מחזירה 500 בבדיקת הסטטוס
  בזמן שהיצירה עצמה מצליחה ברקע.
- הגדרת השפה גלובלית לחשבון, לא פר-נוטבוק.

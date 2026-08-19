import os
import time
import glob
from datetime import datetime

from orchestrator import Orchestrator

# --- הגדרות, ניתנות לשינוי דרך .env בהמשך אם נרצה ---
WATCH_DIR = "sample_code"       # התיקייה שהסוכן סורק
REPORTS_DIR = "reports"          # לאן כותבים את הדוחות
CHECK_INTERVAL_SECONDS = 120     # כל כמה זמן בודקים שוב (2 דקות)

# יוצר את תיקיית הדוחות אם היא לא קיימת עדיין
os.makedirs(REPORTS_DIR, exist_ok=True)

orch = Orchestrator()

# הזיכרון של הסוכן: לכל קובץ, מתי הוא נסרק לאחרונה (mtime)
# {filepath: last_seen_mtime}
known_mtimes = {}


def scan_and_review():
    """
    סורק את WATCH_DIR, מוצא קבצי .py ששונו מאז הסריקה הקודמת,
    שולח אותם לביקורת קוד, וכותב דוח לכל קובץ ששונה.
    """
    py_files = glob.glob(os.path.join(WATCH_DIR, "*.py"))

    for filepath in py_files:
        current_mtime = os.path.getmtime(filepath)
        last_seen = known_mtimes.get(filepath)

        # אם ראינו את הקובץ בעבר ושום דבר לא השתנה — מדלגים
        if last_seen is not None and current_mtime == last_seen:
            continue

        # קובץ חדש (לא היה ב-known_mtimes) או שהשתנה (mtime גדול יותר)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] שינוי זוהה: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()

        # שולח לביקורת קוד דרך אותו orchestrator שהטלגרם בוט משתמש בו
        result = orch.route("review", {"code": code})

        # כותב דוח לקובץ עם timestamp בשם, כדי לא לדרוס דוחות קודמים
        report_name = f"{os.path.basename(filepath)}_{int(time.time())}.md"
        report_path = os.path.join(REPORTS_DIR, report_name)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Review: {filepath}\n")
            f.write(f"Scanned at: {datetime.now().isoformat()}\n\n")
            f.write(result)

        print(f"  → דוח נכתב: {report_path}")

        # מעדכן את הזיכרון, כדי שלא נסרוק את אותו קובץ שוב בסבב הבא
        known_mtimes[filepath] = current_mtime


def main():
    print(f"🔎 Watcher פעיל. סורק את '{WATCH_DIR}' כל {CHECK_INTERVAL_SECONDS} שניות.")
    print("לחץ Ctrl+C כדי לעצור.\n")

    # לולאה אינסופית — זה מה שהופך אותו לסוכן "אוטונומי":
    # הוא לא מחכה לפקודה, הוא בודק ביוזמתו כל X זמן
    while True:
        scan_and_review()
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
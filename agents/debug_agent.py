# טוען את המפתח הסודי מקובץ .env
from dotenv import load_dotenv
load_dotenv()

# מייבא את ChatAnthropic לחיבור לקלוד — אותו ייבוא בדיוק כמו בשני הסוכנים האחרים
from langchain_anthropic import ChatAnthropic

# מייבא את סוגי ההודעות — אותו דפוס כמו בכל הסוכנים במערכת
from langchain_core.messages import SystemMessage, HumanMessage

# מייבא את ה-prompt הספציפי לסוכן הזה מתוך הקובץ המרכזי
from agents.prompts import DEBUG_SYSTEM_PROMPT


class DebugAgent:
    """
    סוכן דיבאגינג.
    מקבל קוד + הודעת שגיאה, מחזיר אבחון + הצעת תיקון.
    Stateless — בדיוק כמו ReviewAgent ו-ArchitectureAgent.

    שים לב: ל-review() כאן יש שני פרמטרים (code, error) ולא אחד —
    כי דיבאגינג תמיד צריך גם את הקוד וגם את השגיאה כדי לאבחן נכון.
    זה ההבדל היחיד במבנה מול שני הסוכנים האחרים.
    """

    def __init__(self):
        # יוצר חיבור ל-Claude — אותה מחלקה כמו בסוכנים האחרים
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-5",
            # נמוך, כמו review (0.2) — גם כאן רוצים דיוק עובדתי, לא "יצירתיות"
            temperature=0.2
        )

        # ההוראות הקבועות לסוכן — מיובאות מ-prompts.py, עטופות כ-SystemMessage
        self.system_prompt = SystemMessage(content=DEBUG_SYSTEM_PROMPT)

    def review(self, code: str, error: str) -> str:
        """
        מריץ אבחון דיבאג על קוד + שגיאה שהתקבלו.
        code = מחרוזת עם הקוד
        error = מחרוזת עם הודעת השגיאה / traceback
        מחזיר: מחרוזת עם האבחון וההצעה לתיקון
        """

        # בונה בקשה אחת שמשלבת גם את הקוד וגם את השגיאה יחד —
        # כי אי אפשר לאבחן נכון עם חלק אחד בלבד מהמידע
        request = HumanMessage(
            content=f"Code:\n{code}\n\nError:\n{error}\n\nDiagnose and fix this."
        )

        # שולח ל-Claude: system prompt + הבקשה (בלי היסטוריה, כי stateless)
        messages = [self.system_prompt, request]
        response = self.llm.invoke(messages)

        return response.content
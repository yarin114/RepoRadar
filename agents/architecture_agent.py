# טוען את המפתח הסודי מקובץ .env
from dotenv import load_dotenv
load_dotenv()

# מייבא את ChatAnthropic לחיבור לקלוד — אותו ייבוא בדיוק כמו ב-ReviewAgent
from langchain_anthropic import ChatAnthropic

# מייבא את סוגי ההודעות — אותו דפוס כמו בכל הסוכנים במערכת
from langchain_core.messages import SystemMessage, HumanMessage

# מייבא את ה-prompt הספציפי לסוכן הזה מתוך הקובץ המרכזי
from agents.prompts import ARCHITECTURE_SYSTEM_PROMPT


class ArchitectureAgent:
    """
    סוכן ביקורת ארכיטקטורה.
    מקבל קטע קוד או שאלת עיצוב, מחזיר הצעות לשיפור ארכיטקטוני.
    Stateless — בדיוק כמו ReviewAgent: כל בקשה עצמאית, בלי זיכרון שיחה.
    """

    def __init__(self):
        # יוצר חיבור ל-Claude — אותה מחלקה כמו ב-ReviewAgent, אבל temperature שונה
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-5",
            # מעט יותר גבוה מ-review (0.2) — כאן יש מקום ליותר "שיקול דעת" עיצובי,
            # לא רק זיהוי עובדתי של באג קיים או לא-קיים
            temperature=0.3
        )

        # ההוראות הקבועות לסוכן — מיובאות מ-prompts.py, עטופות כ-SystemMessage
        self.system_prompt = SystemMessage(content=ARCHITECTURE_SYSTEM_PROMPT)

    def review(self, code: str) -> str:
        """
        מריץ ביקורת ארכיטקטורה על הקוד/העיצוב שהתקבל.
        code = מחרוזת עם הקוד או תיאור העיצוב
        מחזיר: מחרוזת עם ההמלצות הארכיטקטוניות
        """

        # בונה את הבקשה — הקוד עטוף בהודעת אדם, עם ניסוח שמכוון לארכיטקטורה
        # ולא לביקורת קוד כללית (שם ההבדל בין review-agent ל-architecture-agent)
        request = HumanMessage(content=f"Review the architecture of this:\n\n{code}")

        # שולח ל-Claude: system prompt + הבקשה (בלי היסטוריה, כי stateless)
        messages = [self.system_prompt, request]
        response = self.llm.invoke(messages)

        return response.content
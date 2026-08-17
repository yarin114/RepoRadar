# מייבא את שלושת הסוכנים כדי שה-orchestrator יוכל ליצור ולהפעיל אותם
from agents.review_agent import ReviewAgent
from agents.architecture_agent import ArchitectureAgent
from agents.debug_agent import DebugAgent


class Orchestrator:
    """
    מנתב בקשות לסוכן הנכון לפי task_type.
    זו נקודת הכניסה היחידה שהטלגרם בוט וה-watcher ישתמשו בה בהמשך —
    הם לא יכירו את שלושת הסוכנים ישירות, רק את ה-Orchestrator.
    """

    def __init__(self):
        # יוצר את שלושת הסוכנים פעם אחת, בזמן האתחול —
        # לא בכל בקשה מחדש, כדי לא ליצור חיבור חדש ל-Claude כל פעם
        self.agents = {
            "review": ReviewAgent(),
            "architecture": ArchitectureAgent(),
            "debug": DebugAgent(),
        }

    def route(self, task_type: str, payload: dict) -> str:
        """
        מנתב בקשה לסוכן המתאים.
        task_type = "review" / "architecture" / "debug"
        payload = dict עם המידע לסוכן. תמיד כולל "code".
                  לדיבאג בלבד: כולל גם "error".

        למה dict ולא פרמטרים נפרדים? כי ל-DebugAgent.review() יש חתימה
        שונה (code, error) לעומת שני האחרים (code בלבד). עם dict אחיד,
        route() יכולה לקבל את אותה צורת קלט לכל סוג בקשה, ורק כאן,
        במקום אחד, מחליטים איך לפרק אותו לפרמטרים של כל סוכן.
        """

        # בדיקה שסוג המשימה בכלל קיים — אם לא, שגיאה ברורה במקום קריסה מוזרה
        if task_type not in self.agents:
            raise ValueError(
                f"Unknown task_type: '{task_type}'. "
                f"Valid options: {list(self.agents.keys())}"
            )

        agent = self.agents[task_type]

        # כאן קורה הפירוק: debug צריך שני ארגומנטים, השאר צריכים רק code
        if task_type == "debug":
            return agent.review(payload["code"], payload["error"])
        else:
            return agent.review(payload["code"])
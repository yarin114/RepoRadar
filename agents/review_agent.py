from dotenv import load_dotenv
load_dotenv()


#מייבא את ChatAntropic לחיבור של קלוד במקום ChatOpenAI שהיה מ-learning-agents
from langchain_anthropic import ChatAnthropic

#אותו הדפוס כמו בסוכן המפקח מפרוייקט learning-agents  , מייבא את סוגי ההודעות 
from langchain_core.messages import SystemMessage, HumanMessage

from agents.prompts import REVIEW_SYSTEM_PROMPT


class ReviewAgent:
    """
    סוכן ביקורת קוד 
    מקבל קטע קוד, מחזיר ניתוח : באגים, סגנון, סיכונים 

    בניגוד לסוכן המפקח מפרוייקט learning-agents הסוכן הזה הוא STATELESS 
    כל ביקורת היא בקשה עצמאית, בלי היסטוריית שיחה בין הקריאות 
    """

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-5",
            temperature=0.2 # טמפרטורה נמוכה בשביל תשובות עקביות ופחות יצירתיות 
        )

        # ההוראות הקבועות לסוכן מיובאות מ- prompts.py 
        self.system_prompt = SystemMessage(content=REVIEW_SYSTEM_PROMPT)
        
    def review(self, code:str)-> str:
        """
        מריץ ביקורת קוד על הקטע קוד שהתקבל 
        code= מחרוזת עם הקוד לבדיקה
        מחזיר - מחרוזת עם הביקורת 
        """

        # בונה את הבקשה - קוד המשתמש עטוף בהודעת בן אדם 
        request = HumanMessage(content=f"Review this code:\n\n{code}")

        #שולח ל claude: system prompt +הבקשה 

        messages = [self.system_prompt, request]
        response = self.llm.invoke(messages)


        return response.content

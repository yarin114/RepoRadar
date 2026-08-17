from orchestrator import Orchestrator

# יוצר את ה-orchestrator פעם אחת — הוא כבר יוצר בפנים את שלושת הסוכנים
orch = Orchestrator()

# --- בדיקה 1: review ---
sample_code = """
def add(a, b):
    result = a + b
    print(result)
"""

print("=== REVIEW ===")
print(orch.route("review", {"code": sample_code}))

# --- בדיקה 2: architecture ---
print("\n=== ARCHITECTURE ===")
print(orch.route("architecture", {"code": sample_code}))

# --- בדיקה 3: debug ---
sample_error = "TypeError: unsupported operand type(s) for +: 'int' and 'str'"

print("\n=== DEBUG ===")
print(orch.route("debug", {"code": sample_code, "error": sample_error}))

# --- בדיקה 4: task_type לא קיים — אמור לזרוק שגיאה ברורה ---
print("\n=== INVALID TASK (אמור לזרוק שגיאה) ===")
try:
    orch.route("translate", {"code": sample_code})
except ValueError as e:
    print(f"תפסנו את השגיאה כמו שציפינו: {e}")
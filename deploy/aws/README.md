# פריסה ל-AWS EC2

## שלב 1 — יצירת instance
1. היכנס ל-AWS Console → EC2 → Launch Instance
2. שם: `reporadar-server`
3. AMI: **Ubuntu 24.04 LTS**
4. Instance type: **t2.micro** (או t3.micro) — זמין ב-Free Tier
5. Key pair: צור חדש, שם למשל `reporadar-key`, הורד את קובץ ה-`.pem` ושמור אותו במקום בטוח (**אי אפשר להוריד אותו שוב אחרי היצירה**)
6. Security group — חשוב:
   - **Inbound rules: רק SSH (port 22)**, מקור: My IP
   - **אין צורך בשום port אחר פתוח לעולם** — הבוט והwatcher עושים רק חיבורים יוצאים (outbound) לטלגרם ול-Anthropic API, הם לא מקבלים חיבורים נכנסים. זו נקודה טובה להסביר בראיון: "לא חשפתי שום port מיותר כי השירות לא מקשיב לכלום מבחוץ."
7. Launch Instance

## שלב 2 — התחברות לשרת

```bash
chmod 400 reporadar-key.pem
ssh -i reporadar-key.pem ubuntu@<PUBLIC_IP>
```
(את ה-`<PUBLIC_IP>` מוצאים בדף ה-instance ב-Console, שדה "Public IPv4 address")

## שלב 3 — התקנת Docker על השרת

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker ubuntu
```
אחרי הפקודה האחרונה — **התנתק והתחבר שוב** (`exit`, ואז `ssh` מחדש), כדי שהרשאת ה-docker group תיכנס לתוקף.

## שלב 4 — הבאת הקוד לשרת

```bash
git clone https://github.com/yarin114/RepoRadar.git
cd RepoRadar
```

## שלב 5 — הגדרת הסודות

בשרת אין `.env` (הוא לא ב-git, בכוונה). יוצרים אותו ידנית:
```bash
nano .env
```
מדביקים בפנים:
```
ANTHROPIC_API_KEY=המפתח-האמיתי
TELEGRAM_BOT_TOKEN=הטוקן-האמיתי
TELEGRAM_AUTHORIZED_CHAT_ID=המזהה-שלך
```
שומרים: `Ctrl+O`, `Enter`, `Ctrl+X`.

## שלב 6 — הרצה

```bash
docker compose up -d
```
(`-d` = detached — רץ ברקע, לא תלוי בחיבור ה-SSH שלך פתוח)

## שלב 7 — אימות

```bash
docker compose ps
docker compose logs -f
```
בדוק בטלגרם שהבוט מגיב. אם כן — **כבה את המחשב האישי שלך** ובדוק שהבוט עדיין מגיב. זו ההוכחה שהמערכת רצה בענן, לא אצלך.

## עדכון גרסה בעתיד

אחרי push חדש ל-GitHub:
```bash
cd RepoRadar
git pull
docker compose up -d --build
```

## עצירה

```bash
docker compose down
```
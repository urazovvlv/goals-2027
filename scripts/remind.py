"""Daily reminders for the 2027 goals mini app.

Runs from GitHub Actions. Needs two repository secrets:
  BOT_TOKEN - token from @BotFather
  CHAT_ID   - your Telegram user id (the bot can only message you after you press Start)
Usage: python scripts/remind.py morning|evening
"""
import datetime as dt
import json
import os
import sys
import urllib.request

APP_URL = "https://urazovvlv.github.io/goals-2027/"
TZ = dt.timezone(dt.timedelta(hours=5))  # Tashkent
YEAR = 2027

# Same checkpoints as the app's defaults (the bot cannot read the app's storage).
CHECKPOINTS = [
    ("2027-01-10", "IELTS imtihoni"),
    ("2027-01-31", "Ko'mak savollari aniqlangan bo'lsin"),
    ("2027-02-28", "Bank qarzi yopilgan, Ko'mak arizasi topshirilgan"),
    ("2027-03-31", "1-chorak: vazn ~70.5 kg"),
    ("2027-05-31", "Grit ochilishi"),
    ("2027-06-30", "2-chorak: vazn ~73 kg, bitiruv"),
    ("2027-09-30", "3-chorak: ~75.5 kg, Grit ≥ $2000 tekshiruvi"),
    ("2027-12-31", "Yil yakuni: 78 kg, Grit $3000"),
]

HAFTA = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]


def year_line(today: dt.date) -> str:
    start, end = dt.date(YEAR, 1, 1), dt.date(YEAR, 12, 31)
    if today < start:
        return f"2027-yilgacha <b>{(start - today).days}</b> kun qoldi — tayyorgarlik davri."
    if today > end:
        return "2027-yil yakunlandi. Natijalaringni ko'rib chiq!"
    n = (today - start).days + 1
    return f"2027-yilning <b>{n}-kuni</b> · {(end - today).days} kun qoldi."


def next_checkpoint(today: dt.date) -> str:
    for d, title in CHECKPOINTS:
        day = dt.date.fromisoformat(d)
        if day >= today:
            left = (day - today).days
            when = "bugun" if left == 0 else f"{left} kun qoldi"
            return f"🎯 Keyingi nazorat: <b>{title}</b> ({when})"
    return ""


def build(kind: str, today: dt.date) -> str:
    wd = today.weekday()  # Mon=0
    lines = []
    if kind == "morning":
        lines.append(f"☀️ <b>Xayrli tong!</b> {HAFTA[wd]}")
        lines.append(year_line(today))
        if wd == 4:
            lines.append("🕌 Bugun <b>juma</b> — juma namozini unutma.")
        if wd == 6:
            lines.append("⚖️ Yakshanba: ertalab <b>vazningni o'lchab</b>, ilovaga yozib qo'y.")
        if today.day == 1:
            lines.append("💰 Yangi oy: o'tgan oydagi <b>daromadlaringni</b> (Grit, targeting) yozib qo'y.")
        cp = next_checkpoint(today)
        if cp:
            lines.append(cp)
        lines.append("\nBugungi niyat: 5 mahal namoz, bir oz kitob va o'z maqsading sari bitta qadam.")
    else:
        lines.append("🌙 <b>Kun yakuni</b>")
        lines.append("Bugungi namozlar, zal, kitob, Qur'on va til mashg'ulotlarini belgilab qo'y.")
        if wd == 6:
            lines.append("\n📋 Hafta yakuni: qaysi maqsadda olg'a siljiding, qayerda orqada qolding?")
        lines.append("\nErtaga yangi kun. Yaxshi dam ol 🤍")
    return "\n".join(lines)


def send(text: str) -> None:
    token = os.environ["BOT_TOKEN"].strip()
    chat_id = os.environ["CHAT_ID"].strip()
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {"inline_keyboard": [[{"text": "📱 Ilovani ochish", "web_app": {"url": APP_URL}}]]},
    }
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        body = json.loads(r.read())
        if not body.get("ok"):
            raise SystemExit(f"Telegram error: {body}")
    print("sent")


if __name__ == "__main__":
    kind = sys.argv[1] if len(sys.argv) > 1 else "morning"
    today = dt.datetime.now(TZ).date()
    text = build(kind, today)
    if os.environ.get("DRY_RUN"):
        print(text)
    else:
        send(text)

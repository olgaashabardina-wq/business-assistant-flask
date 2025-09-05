import os
from dotenv import load_dotenv
from flask import Flask, request, render_template_string, jsonify
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "Ты вежливый бизнес-ассистент. Отвечай кратко и по делу, "
    "предлагай понятные следующие шаги. Если вопрос не по теме — скажи об этом."
)

HTML = """
<!doctype html>
<title>Business Assistant</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<div style="max-width:720px;margin:40px auto;font-family:system-ui;">
  <h1>💼 Business Assistant</h1>
  <form method="post" action="/" style="display:flex;gap:.5rem">
    <input name="q" placeholder="Сформулируй задачу…" style="flex:1;padding:.6rem"/>
    <button type="submit" style="padding:.6rem 1rem">Спросить</button>
  </form>
  {% if a %}
  <div style="margin-top:1rem;padding:1rem;border:1px solid #ddd;border-radius:12px;">
    <b>Ответ:</b><br>{{ a }}
  </div>
  {% endif %}
  <p style="color:#777;margin-top:1rem">
    Подсказка: «Составь план запуска Telegram-бота для магазина украшений»
  </p>
</div>
"""

app = Flask(__name__)

def llm_answer(q: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return "Нет ключа OPENAI_API_KEY. Создайте .env из .env.example."
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": q},
        ],
        temperature=0.3,
        max_tokens=400,
    )
    return resp.choices[0].message.content.strip()

@app.get("/")
def index_get():
    return render_template_string(HTML, a=None)

@app.post("/")
def index_post():
    q = request.form.get("q", "").strip()
    a = llm_answer(q) if q else "Введите вопрос."
    return render_template_string(HTML, a=a)

@app.post("/api/ask")
def api_ask():
    data = request.get_json(silent=True) or {}
    q = (data.get("q") or "").strip()
    return jsonify({"answer": llm_answer(q) if q else ""})

if __name__ == "__main__":
    app.run(debug=True)

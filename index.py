from flask import Flask, request, redirect, url_for, render_template_string, session
import json
import os

app = Flask(__name__)
app.secret_key = 'segredo_seguro_chatbot'  # Ideal: usar variável de ambiente
FAQ_FILE = 'faq.json'

def load_faq():
    if not os.path.exists(FAQ_FILE):
        return {}
    with open(FAQ_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_faq(faq):
    with open(FAQ_FILE, 'w', encoding='utf-8') as f:
        json.dump(faq, f, ensure_ascii=False, indent=2)

@app.route('/', methods=['GET', 'POST'])
def chat():
    faq = load_faq()
    resposta = ''
    exemplos = list(faq.keys())

    # Paginação
    page = request.args.get('page', 1)
    try:
        page = int(page)
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    per_page = 5
    total = len(exemplos)
    total_pages = (total - 1) // per_page + 1 if total > 0 else 1
    start = (page - 1) * per_page
    end = start + per_page
    exemplos_paginados = exemplos[start:end]
    exemplos_indexados = [f"{start + i + 1}. {ex}" for i, ex in enumerate(exemplos_paginados)]

    if request.method == 'POST':
        pergunta = request.form['mensagem'].lower().strip()
        resposta = "Desculpe, ainda não sei responder isso."
        palavras_pergunta = pergunta.split()
        for pergunta_faq, resposta_faq in faq.items():
            palavras_faq = pergunta_faq.lower().split()
            if any(p in palavras_faq for p in palavras_pergunta):
                resposta = resposta_faq
                break

    return render_template_string(CHAT_TEMPLATE, resposta=resposta, exemplos=exemplos_indexados, page=page, total_pages=total_pages)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    erro = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'vitor' and password == 'helena':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            erro = 'Usuário ou senha inválidos.'
    return render_template_string(ADMIN_LOGIN_TEMPLATE, erro=erro)

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    faq = load_faq()
    mensagem = ''
    if request.method == 'POST':
        pergunta = request.form.get('pergunta', '').lower().strip()
        resposta = request.form.get('resposta', '').strip()
        if pergunta and resposta:
            faq[pergunta] = resposta
            save_faq(faq)
            mensagem = 'FAQ atualizado com sucesso!'
        else:
            mensagem = 'Por favor, preencha pergunta e resposta.'

    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, faq=faq, mensagem=mensagem)

@app.route('/admin/delete')
def delete_topic():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    pergunta = request.args.get('pergunta', '').lower().strip()
    if pergunta:
        faq = load_faq()
        if pergunta in faq:
            del faq[pergunta]
            save_faq(faq)
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


# Templates (mantidos, com a alteração na lista FAQ do dashboard)
ADMIN_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Login Admin</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f8f9fa; padding: 20px; }
    .container { max-width: 400px; margin:auto; background:#fff; padding:30px; border-radius:8px; box-shadow:0 0 10px #ccc; }
    h1 { color:#333; text-align:center; }
    input[type=text], input[type=password] {
      width: 100%; padding:10px; margin:10px 0; border:1px solid #ccc; border-radius:4px;
      box-sizing: border-box;
    }
    button {
      width: 100%; padding:10px; background:#007BFF; color:#fff; border:none; border-radius:4px; cursor:pointer;
      font-size: 1em;
    }
    button:hover { background:#0056b3; }
    .error { color: red; text-align:center; margin-bottom:15px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Login Administrador</h1>
    {% if erro %}
      <p class="error">{{ erro }}</p>
    {% endif %}
    <form method="POST">
      <input type="text" name="username" placeholder="Usuário" required autofocus>
      <input type="password" name="password" placeholder="Senha" required>
      <button type="submit">Entrar</button>
    </form>
  </div>
</body>
</html>
"""

ADMIN_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Dashboard Admin</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f8f9fa; padding: 20px; }
    .container { max-width: 700px; margin:auto; background:#fff; padding:30px; border-radius:8px; box-shadow:0 0 10px #ccc; }
    h1, h2 { color:#333; }
    a.logout {
      display: inline-block; margin-bottom: 20px; color:#007BFF; text-decoration:none;
      font-weight:bold;
    }
    a.logout:hover { text-decoration: underline; }
    form input[type=text], form textarea {
      width: 100%; padding:10px; margin:10px 0; border:1px solid #ccc; border-radius:4px;
      box-sizing: border-box;
      font-size: 1em;
    }
    form textarea {
      resize: vertical;
    }
    button {
      padding:10px 20px; background:#007BFF; color:#fff; border:none; border-radius:4px; cursor:pointer;
      font-size: 1em;
    }
    button:hover { background:#0056b3; }
    .message {
      background:#d4edda; color:#155724; border:1px solid #c3e6cb; padding:10px; border-radius:4px;
      margin-bottom:20px;
    }
    ul.faq-list {
      list-style:none; padding:0;
    }
    ul.faq-list li {
      margin-bottom: 10px;
      border-bottom: 1px solid #ddd;
      padding-bottom: 5px;
    }
    ul.faq-list li strong {
      color:#007BFF;
    }
    ul.faq-list li a {
      color: red;
      margin-left: 10px;
      text-decoration: none;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Área do Administrador</h1>
    <a href="{{ url_for('logout') }}" class="logout">Sair</a>

    {% if mensagem %}
      <div class="message">{{ mensagem }}</div>
    {% endif %}

    <h2>Adicionar ou atualizar pergunta</h2>
    <form method="POST">
      <input type="text" name="pergunta" placeholder="Pergunta" required autofocus>
      <textarea name="resposta" placeholder="Resposta" rows="4" required></textarea>
      <button type="submit">Salvar</button>
    </form>

    <h2>FAQ Atual</h2>
    <ul class="faq-list">
      {% for p, r in faq.items() %}
        <li><strong>{{ p }}</strong>: {{ r }} 
          <a href="{{ url_for('delete_topic', pergunta=p) }}" onclick="return confirm('Confirma exclusão?');">[Excluir]</a>
        </li>
      {% endfor %}
    </ul>
  </div>
</body>
</html>
"""

CHAT_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Chatbot Vitória ES</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f8f9fa; padding: 20px; }
    .container { max-width: 600px; margin:auto; background:#fff; padding:30px;
      border-radius:8px; box-shadow:0 0 10px #ccc; }
    h1 { color:#333; }
    .exemplos ol { padding-left:20px; margin-bottom:20px; }
    .exemplos li { margin-bottom:5px; }
    input[type=text] { width:100%; padding:10px; margin:10px 0; border:1px solid #ccc; border-radius:4px; }
    button { padding:10px 20px; background:#007BFF; color:#fff; border:none; border-radius:4px; cursor:pointer; }
    button:hover { background:#0056b3; }
    .resposta { background:#e9ecef; padding:10px; border-radius:5px; margin-top:10px; }
    footer { text-align:center; margin-top:30px; font-size:0.9em; }
    .pagination { text-align:center; margin-top:20px; }
    .pagination a { margin: 0 5px; text-decoration:none; color:#007BFF; }
    .pagination a.disabled { color:#ccc; pointer-events:none; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🤖 BEM-VINDO</h1>
    <div class="exemplos"><h2>❓ Exemplos de perguntas:</h2>
      <ol>
      {% for ex in exemplos %}
        <li>{{ ex }}</li>
      {% endfor %}
      </ol>
    </div>
    <form method="POST">
      <input type="text" name="mensagem" placeholder="Digite sua pergunta..." required autofocus>
      <button type="submit">Enviar</button>
    </form>
    {% if resposta %}
      <div class="resposta"><strong>Resposta:</strong> {{ resposta }}</div>
    {% endif %}
    <div class="pagination">
      {% if page > 1 %}
        <a href="/?page={{ page - 1 }}">« Anterior</a>
      {% else %}
        <span class="disabled">« Anterior</span>
      {% endif %}
      Página {{ page }} de {{ total_pages }}
      {% if page < total_pages %}
        <a href="/?page={{ page + 1 }}">Próxima »</a>
      {% else %}
        <span class="disabled">Próxima »</span>
      {% endif %}
    </div>
    <footer><p><a href="/admin">Área do administrador</a></p></footer>
  </div>
</body>
</html>
"""

if __name__ == '__main__':
    if not os.path.exists(FAQ_FILE):
        save_faq({
            "oi": "Olá! Como posso ajudar?",
            "qual seu nome": "Sou um chatbot criado com Flask.",
            "tchau": "Até logo!",
            "como funciona": "Eu respondo perguntas frequentes cadastradas.",
            "quem é você": "Sou um assistente virtual."
        })
    app.run(debug=True)

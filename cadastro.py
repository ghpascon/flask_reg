from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

#local True or False
local_app=False


DB_NAME = 'cadastro.db'

def create_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, email TEXT)''')
    conn.commit()
    conn.close()

def reset_ids():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM usuarios')
    conn.commit()
    c.execute("DELETE FROM sqlite_sequence WHERE name='usuarios'")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']

        if not nome or not email:
            flash('Por favor, preencha todos os campos.', 'error')
            return redirect(url_for('cadastro'))

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        c.execute('SELECT * FROM usuarios WHERE nome = ?', (nome,))
        if c.fetchone():
            flash('Nome já cadastrado. Escolha outro nome.', 'error')
            conn.close()
            return redirect(url_for('cadastro'))

        c.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        if c.fetchone():
            flash('Email já cadastrado. Escolha outro email.', 'error')
            conn.close()
            return redirect(url_for('cadastro'))

        c.execute('INSERT INTO usuarios (nome, email) VALUES (?, ?)', (nome, email))
        conn.commit()
        conn.close()

        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('lista_usuarios'))
    return render_template('cadastro.html')

@app.route('/lista_usuarios')
def lista_usuarios():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM usuarios')
    usuarios = c.fetchall()
    conn.close()
    return render_template('lista_usuarios.html', usuarios=usuarios)

@app.route('/apagar_usuario/<int:id>', methods=['POST'])
def apagar_usuario(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM usuarios WHERE id = ?', (id,))
    conn.commit()
    c.execute('UPDATE usuarios SET id = id - 1 WHERE id > ?', (id,))
    conn.commit()
    conn.close()
    flash('Usuário apagado com sucesso!', 'success')
    return redirect(url_for('lista_usuarios'))

@app.route('/apagar_todos', methods=['POST'])
def apagar_todos():
    reset_ids()
    flash('Todos os usuários foram apagados!', 'success')
    return redirect(url_for('lista_usuarios'))

if __name__ == '__main__':
    create_table()
    if local_app:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', port=8080, debug=True)
import sqlite3
from flask import Flask, jsonify, request
import sqlite3

conn = sqlite3.connect('clinica.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS pacientes (
                    id INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    idade INTEGER NOT NULL,
                    sexo TEXT NOT NULL,
                    data_nascimento TEXT,
                    status TEXT NOT NULL,
                    data_criacao TEXT)''')

conn.commit()
conn.close()
print("Banco de dados configurado!")

def cadastrar_paciente(nome, idade, sexo, data_nascimento, status):
    conn = sqlite3.connect('clinica.db')
    cursor = conn.cursor()
    
    cursor.execute('''INSERT INTO pacientes (nome, idade, sexo, data_nascimento, status, data_criacao)
                      VALUES (?, ?, ?, ?, ?, ?)''', 
                      (nome, idade, sexo, data_nascimento, status, '2025-01-07'))  # Data de criação fixada por enquanto
    
    conn.commit()
    conn.close()
    print(f"Paciente {nome} cadastrado com sucesso!")

def buscar_pacientes(clinica_id=None):
    conn = sqlite3.connect('clinica.db')
    cursor = conn.cursor()
    
    if clinica_id:
        cursor.execute('''SELECT * FROM pacientes WHERE clinica_id = ?''', (clinica_id,))
    else:
        cursor.execute('''SELECT * FROM pacientes''')  # Busca todos os pacientes
    
    pacientes = cursor.fetchall()
    conn.close()
    return pacientes

app = Flask(__name__)

# Rota para buscar pacientes
@app.route('/pacientes', methods=['GET'])
def get_pacientes():
    pacientes = buscar_pacientes()  # Função que cria a consulta ao banco de dados
    return jsonify(pacientes)

# Rota para cadastrar paciente
@app.route('/pacientes', methods=['POST'])
def post_paciente():
    data = request.get_json()
    nome = data['nome']
    idade = data['idade']
    sexo = data['sexo']
    data_nascimento = data['data_nascimento']
    status = data['status']
    
    cadastrar_paciente(nome, idade, sexo, data_nascimento, status)  # Chama a função para cadastrar paciente
    return jsonify({'message': 'Paciente cadastrado com sucesso'}), 201

if __name__ == '__main__':
    app.run(debug=True)
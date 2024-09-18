// Script de inicialização do MongoDB para criar um usuário e uma coleção
db = db.getSiblingDB('spc');

db.createUser({
    user: "spcFlask",
    pwd: "admin",
    roles: [{ role: "readWrite", db: "spc" }]
  });

// Criar coleção e inserir dados iniciais
db.termos.insertOne({
  'nome_termo': 'termo_inicial',
  'descricao': 'Este é um termo inicial',
  'prioridade': 1,
  'data_cadastro': new Date(),
  'versao': 1.0
});

db.usuario.insertOne({
    "nome": 'teste',
    "email": 'teste@teste.com',
    "cpf_cnpj": '122112211/0001',
    "telefone": 129820500,
    "celular": 1298208004,
    "endereco": 'rua teste',
    "termo_status": {
        "nome_termo": "termo_inicial",
        "versao": 1.0,
        "status": "pendente", // Status inicial
        "data_aceite": null
    }
})

// // Script de inicialização do MongoDB uma coleção
// db = db.getSiblingDB('spc');

// // db.createUser({
// //     user: "spcFlask",
// //     pwd: "admin",
// //     roles: [{ role: "readWrite", db: "spc" }]
// //   });

// // Criar coleção e inserir dados iniciais
// db.termo.insertOne({
//   'nome_termo': 'termo_inicial',
//   'descricao': 'Este é um termo inicial',
//   'prioridade': 1,
//   'data_cadastro': new Date(),
//   'versao': 1.0
// });

// db.usuario.insertOne({
//     "nome": 'teste',
//     "email": 'teste@teste.com',
//     "cpf_cnpj": '1234560001',
//     "telefone": 129820500,
//     "celular": 1298208004,
//     "endereco": 'rua teste',
//     "termo_status": {
//         "nome_termo": "termo_inicial",
//         'prioridade': 2,
//         "versao": 1.0,
//         'aceite': True,
//         "data_aceite": null,
//         'descricao': 'testee',
//         'data_update': null
//     }
// })

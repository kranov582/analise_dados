import numpy as np
from dash import Dash, html, dcc, dash_table
import plotly.express as px
import pandas as pd
from pymongo import MongoClient

#criação do dash
app = Dash(__name__)

#Coneção ao mongodb

cluster = "mongodb+srv://root:reQOHe2iCebJdbvi@agenda.tflxj.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(cluster)

db = client.agenda

#DICIONARIO -------
lugares = {}
pessoas = {}
profissionais = {}

def dicionario(array, nome_dicionario):
    for element in range(len(array)):
        nome_dicionario['{}'.format(array[element][0])] = array[element][1]
    return nome_dicionario

#Dicionario de categorias
agendaShop = db.agendaShop
category = db.category
categorias = pd.DataFrame(list(category.find()), columns = ['_id', 'name'])
categorias = categorias.values
lugares = dicionario(categorias, lugares)

#Dicionario de pessoas
person = db.person
personid = pd.DataFrame(list(person.find()), columns = ['_id', 'fullName'])
personid = personid.values
pessoas = dicionario(personid, pessoas)

#Dicionario de estabelecimentos
professional = db.professional
prof = pd.DataFrame(list(professional.find()), columns = ['_id', 'name'])
prof = prof.values
profissionais = dicionario(prof, profissionais)

#Primeira tarefa
lojas = db.agendaShop

data_lojas = pd.DataFrame(list(lojas.find()), columns = ['name', 'categoryId'])

data_lojas.rename(columns={'name': 'Quantidade', 'categoryId': 'Categoria'}, inplace = True)
data_lojas.replace(lugares, inplace= True)
data_category = data_lojas.groupby(['Categoria']).count().reset_index()

lojas_graph = px.bar(data_category, x = 'Categoria', y = 'Quantidade')

#Segunda Tarefa

appointment = db.appointment

transacao = pd.DataFrame(list(appointment.find()), columns = ['totalPrice'])
transacao['totalPrice'] = pd.to_numeric(transacao['totalPrice'])
descricao = transacao.describe()

#terceira tarefa

porcliente = pd.DataFrame(list(appointment.find()), columns = ['personId'])
porcliente.rename(columns={'personId': 'Nome do cliente'}, inplace= True)
porcliente.replace(pessoas, inplace= True)
usuario = porcliente.drop_duplicates(ignore_index=True)
usuario.insert(1, 'Quantidade', porcliente.value_counts().values)


porcliente_graph = px.bar(usuario, x = 'Nome do cliente', y= 'Quantidade')

#quarta tarefa

porestabe = pd.DataFrame(list(appointment.find()), columns = ['professionalId'])
porestabe.rename(columns={'professionalId': 'Nome do Profissional'}, inplace= True)
porestabe.replace(profissionais, inplace= True)
estabe = porestabe.drop_duplicates(ignore_index=True)
estabe.insert(1, 'Quantidade', porestabe.value_counts().values)

porestabe_graph = px.bar(estabe, x = 'Nome do Profissional', y= 'Quantidade')

app.layout = html.Div(children=[
    html.H1(children='Numero de estabelecimentos e suas categorias'),

    dcc.Graph(
        id='1',
        figure=lojas_graph
    ),
    html.H1(children='Numero médio de ticket'),
    html.H2(children='{}'.format(transacao['totalPrice'].mean())),
    html.H1(children='Numero de appointment por cliente'),
    dcc.Graph(
        id='2',
        figure= porcliente_graph
    ),
    html.H2(children='Numero de appointment total por cliente'),
    html.H2(children='{}'.format(usuario['Quantidade'].sum())),

    html.H1(children='Numero de appointment por estabelecimento'),
    dcc.Graph(
        id='3',
        figure= porestabe_graph
    ),
    html.H2(children='Numero de appointement total por estabelecimento'),
    html.H2(children='{}'.format(estabe['Quantidade'].sum())),

    html.H2(children='Numero de profissionais ativos: '),
    html.H2(children='{}'.format(estabe['Nome do Profissional'].value_counts().sum())),

])

if __name__ == '__main__':
    app.run_server(debug=True)
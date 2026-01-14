
<div align="center"><img width="324" height="324" alt="Hephislog_icon" src="https://github.com/user-attachments/assets/69655ad8-ee6a-44d2-9657-15db7d7d60d1" /></div>
<br>
<div align:center><h3>PT-BR 🇧🇷</h3></div>

## O que é o HEPHISLOGº❓
<br>
<div style="text-align: justified"> O Hephislog é um sistema modular orientado a fluxos, criado para transformar dados brutos em informação estruturada através de etapas bem definidas, independentes e substituíveis.</div>
<br>
Ele não é uma pipeline rígida.<br>
Ele é um ecossistema de módulos que cooperam por papéis.<br>
<br>
A ideia central é simples:<br> 
<br>

<div style="text-align: center">"Em vez de o núcleo saber quem são os módulos, os módulos se anunciam dizendo o que sabem fazer."</div>

<br>

## 🧠 Como ele pensa ❓

<br>

O Hephislog organiza o processamento como uma história:

<br>

- Algo cria um fato (Source)
- Algo observa ou analisa (Advisor)
- Algo limpa ou transforma (Cleaner)
- Algo decide caminhos (Decider)
- Algo salva ou exporta (Sink)
  
<br>

Esses papéis não são classes fixas, são capacidades.
Qualquer módulo pode assumir um ou mais desses papéis, desde que declare isso ao sistema.

<br>

## Por que ele existe ❓

<br>

O Hephislog nasce de três dores comuns:

<br>

- Pipelines rígidas que quebram quando crescem
- **Import hell** com arquivos centrais cheios de mapeamento manual
- Sistemas que funcionam, mas são difíceis de entender e estender
  
<br>

## 💰 Ele aposta que ❓

<br>

- Sistemas crescem melhor por adição, não por reescrita
- Extensão deve ser barata
- Clareza mental é tão importante quanto performance

<br>
  
## ✅ Por isso ele é:

<br>

- Modular
- Auto-registrável
- Orientado a fluxos
- Pensado para evoluir sem perder a forma

<br>

---

> 1. 📐 [Diagramas](docs/diagrams/)
> 2. 🔀 [About Data Flows](flows/README.md)

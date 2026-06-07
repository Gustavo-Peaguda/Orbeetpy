# ORBEET — Plataforma de Monitoramento e Previsão de Risco à Polinização

## Equipe de Desenvolvimento

**Enzo Fernandes Ramos — RM: 563705**
**Felipe Henrique de Souza Cerazi — RM: 562746**
**Gustavo Peaguda de Castro — RM: 562923**
**Lorenzo Andolfatto Coque — RM: 563385**

---

## 1. Visão Geral

O ORBEET é uma plataforma desenvolvida em Python com o objetivo de monitorar condições ambientais e prever riscos associados à redução da atividade de polinização em áreas agrícolas. A solução foi concebida para apoiar produtores rurais e apicultores na tomada de decisão, por meio da análise de dados climáticos e geração de recomendações práticas.

O sistema integra informações provenientes de APIs meteorológicas e aplica um modelo de avaliação de risco que transforma dados ambientais em indicadores claros e acionáveis. Dessa forma, o ORBEET atua como uma ferramenta de suporte à gestão agrícola, com foco em sustentabilidade e eficiência produtiva.

---

## 2. Contextualização do Problema

A polinização por insetos, especialmente por abelhas, é um elemento essencial para a manutenção dos ecossistemas e para a produtividade agrícola. Estima-se que uma parcela significativa das culturas destinadas à alimentação humana dependa, em maior ou menor grau, da polinização animal.

Entretanto, fatores ambientais adversos podem comprometer a atividade das abelhas. Entre os principais fatores destacam-se variações extremas de temperatura, baixa umidade relativa do ar, ocorrência de chuvas intensas e ventos fortes. Esses elementos influenciam diretamente o comportamento das abelhas, podendo causar redução da atividade de forrageamento ou até migração das colônias.

Apesar da disponibilidade de dados climáticos, produtores rurais geralmente não dispõem de ferramentas capazes de interpretar essas informações sob a ótica da polinização. Essa lacuna dificulta a adoção de medidas preventivas e contribui para perdas produtivas.

---

## 3. Proposta da Solução

O ORBEET propõe uma abordagem baseada na coleta, processamento e interpretação de dados climáticos para identificar riscos à polinização. A plataforma realiza a integração com serviços externos de previsão do tempo e utiliza esses dados como base para cálculos e análises.

A partir dessa integração, o sistema é capaz de:

* Monitorar continuamente variáveis ambientais relevantes
* Identificar padrões e condições críticas
* Classificar o nível de risco associado à polinização
* Gerar recomendações para mitigação de impactos

O principal diferencial da solução está na transformação de dados técnicos em informações acessíveis e úteis para o usuário final.

---

## 4. Índice de Risco de Redução da Polinização (IRRP)

O IRRP é o principal indicador utilizado pelo sistema para avaliar o risco de impacto negativo na polinização. Trata-se de um índice calculado com base em quatro variáveis ambientais:

* Temperatura máxima
* Precipitação
* Umidade relativa do ar
* Velocidade do vento

Cada uma dessas variáveis é analisada individualmente e convertida em um valor de risco. O sistema considera o fator mais crítico como determinante para o resultado final, garantindo que situações adversas não sejam mascaradas por condições favoráveis em outros parâmetros.

O resultado do cálculo é apresentado como um percentual entre 0 e 100, acompanhado de uma classificação qualitativa:

* 0 a 30: risco baixo
* 31 a 60: risco moderado
* 61 a 100: risco alto

Além disso, o sistema identifica o fator predominante responsável pelo risco, permitindo maior clareza na interpretação dos resultados.

---

## 5. Funcionalidades do Sistema

### 5.1 Gestão de Usuários

O sistema permite o cadastro e autenticação de usuários, diferenciando dois perfis principais: fazendeiros e apicultores. Essa distinção possibilita a personalização das informações e recomendações apresentadas.

### 5.2 Gestão de Propriedades

Os usuários podem registrar suas propriedades, informando localização e características relevantes, como culturas plantadas ou espécies de abelhas. Esses dados são utilizados para contextualizar as análises realizadas pelo sistema.

### 5.3 Monitoramento Climático

O ORBEET integra-se à API Open-Meteo para obtenção de dados climáticos. As informações coletadas incluem temperatura, precipitação, umidade e velocidade do vento, sendo utilizadas tanto para previsões quanto para análises históricas.

### 5.4 Previsões e Histórico

O sistema disponibiliza dados referentes aos próximos 15 dias (previsão) e aos 15 dias anteriores (histórico). Essa abordagem permite ao usuário acompanhar tendências e identificar padrões ao longo do tempo.

### 5.5 Análise de Risco

Com base nos dados coletados, o sistema realiza o cálculo do IRRP para cada período analisado, classificando o nível de risco e identificando o fator dominante.

### 5.6 Geração de Recomendações

O sistema fornece recomendações práticas para mitigação dos riscos identificados. Essas recomendações podem ser geradas de duas formas:

* Por meio de integração com a API da OpenAI, produzindo sugestões mais elaboradas e contextualizadas
* Por meio de um mecanismo interno de regras (fallback), garantindo funcionamento mesmo sem integração externa

### 5.7 Interface Gráfica

A interface do sistema foi desenvolvida com a biblioteca Tkinter, oferecendo uma experiência visual organizada e interativa. O usuário pode acessar diferentes módulos, visualizar dados e acompanhar indicadores de forma intuitiva.

---

## 6. Arquitetura do Projeto

O projeto foi estruturado de forma modular, separando a interface gráfica da lógica de negócio.

```
/orbeet
 ├── interface.py          # Interface gráfica (Tkinter)
 ├── orbeet.py            # Lógica do sistema e integrações
 └── README.md
```

A lógica principal, incluindo cálculo do IRRP, integração com APIs e manipulação de dados, está concentrada no módulo `orbeet.py`. A interface e interação com o usuário são gerenciadas pelo arquivo `interface.py`.

---

## 7. Tecnologias Utilizadas

O desenvolvimento do ORBEET envolveu as seguintes tecnologias:

* Linguagem Python
* Biblioteca Tkinter para interface gráfica
* API Open-Meteo para dados climáticos
* API OpenAI para geração de recomendações (opcional)
* Formato JSON para armazenamento local de dados

---

## 8. Execução do Projeto

Para executar o sistema, siga os passos abaixo:

1. Clonar o repositório
2. Acessar o diretório do projeto
3. Instalar as dependências necessárias
4. Executar o arquivo principal `(interface.py)`

Exemplo de comandos:

```bash
git clone https://github.com/Gustavo-Peaguda/Orbeetpy.git
pip install pillow requests openai
pip install requests
python interface.py
```

---

## 9. Considerações sobre Integração com OpenAI

A integração com a API da OpenAI é opcional e utilizada para enriquecer as recomendações fornecidas pelo sistema. Caso não seja configurada, o sistema permanece totalmente funcional, utilizando um conjunto de regras internas para geração de sugestões.

Caso queira usar, terá que configurar a Api Key na aba de Configurações dentro do Tkinter

### Caso nao tenha a APIKEY:

Video de execução com a IA: https://youtu.be/-W2-XUJsc3k?si=Z_4vavQKwkkPh0LV

---

## 10. Impacto e Relevância

O ORBEET contribui para a redução de riscos na produção agrícola ao permitir a antecipação de condições ambientais adversas. A solução promove a sustentabilidade ao incentivar práticas que preservam as populações de abelhas e, consequentemente, a eficiência da polinização.

Além disso, o sistema demonstra a aplicabilidade de conceitos de ciência de dados e integração de APIs na resolução de problemas reais do agronegócio.

---

## 11. Conclusão

O ORBEET apresenta uma abordagem estruturada para o monitoramento ambiental aplicado à agricultura. Ao transformar dados climáticos em indicadores e recomendações, o sistema possibilita decisões mais informadas e estratégicas.

Trata-se de uma solução que evidencia o potencial da tecnologia no apoio à sustentabilidade e à produtividade no setor agrícola.

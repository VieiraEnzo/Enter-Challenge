# Projeto de Extração de Documentos (ENTER AI Fellowship)

Este projeto implementa um pipeline de extração de dados otimizado para PDFs, capaz de aprender com as requisições para reduzir custos e aumentar a velocidade.

A solução utiliza um sistema híbrido:
* **Heurísticas (Regex):** Um banco de dados `SQLite` armazena regras de Regex aprendidas. Se uma regra existe para um campo, ela é aplicada localmente (Custo Zero).
* **Filtro de Relevância:** O sistema pré-processa o PDF para identificar campos que são impossíveis de encontrar, marcando-os como `null` sem gastar tempo de processamento.
* **Fallback de LLM:** Campos que não puderam ser resolvidos por heurísticas são enviados (em lote e com contexto otimizado) para o `gpt-5-mini`.
* **Aprendizado (Learner):** As respostas da LLM são analisadas para identificar novos padrões de Regex, que são salvos no banco de dados para uso futuro.

O projeto pode ser executado como uma Aplicação Web (via Flask) ou como um Script de Linha de Comando (CLI).

## Como Rodar:

Este projeto foi construído para rodar com Python 3.11+ e um ambiente virtual (`venv`).

### 1. Preparação do Ambiente

1.  **Clone o Repositório**
    ```bash
    git clone https://github.com/VieiraEnzo/Enter-Challenge
    cd Enter-Challenge
    ```

2.  **Crie e Ative o Ambiente Virtual**
    ```bash
    # No macOS/Linux
    python -m venv venv
    source venv/bin/activate
    
    # No Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instale as Dependências**
    O projeto usa `python-dotenv` para gerenciar chaves de API.
    ```bash
    pip install -r requirements.txt
    ```

### 2. Configuração da API Key

1.  **Crie seu arquivo `.env`**
    ```bash
    # No macOS/Linux (copia o exemplo)
    cp .env.example .env
    
    # No Windows (copia o exemplo)
    copy .env.example .env
    
    ```

2.  **Adicione sua Chave**
    Abra o arquivo `.env` (que você acabou de criar) em um editor de texto e adicione sua chave:
    ```
    OPENAI_API_KEY="sk-sua-chave-secreta-aqui"
    ```

### 3. Executando a Aplicação

Você pode rodar este projeto de duas formas:

---

#### Opção A: Aplicação Web Interativa (Recomendado)

Esta opção inicia um servidor local que permite processar arquivos através de uma interface gráfica e acompanhar o progresso em tempo real.

1.  **Inicie o Servidor Flask**
    (Certifique-se de que seu `venv` está ativado)
    ```bash
    python3 -m src.webapp --output resultados.json
    ```

2.  **Acesse a Aplicação**
    Abra seu navegador e acesse:
    **`http://localhost:5000`**

3.  **Inicie o Processamento**
    * No campo de texto, insira o **caminho absoluto** para a pasta que contém os arquivos PDF que você deseja processar.
    * Exemplo (Linux/macOS): `/home/usuario/documentos/pdfs_para_teste`
    * Exemplo (Windows): `C:\Usuarios\SeuNome\Documentos\pdfs_para_teste`
    * Clique em "Extrair" e acompanhe o progresso.
    * Baixe o arquivo resultados.json utilizando o botão "Baixar resultados"

---

#### Opção B: Script de Linha de Comando (CLI)

Esta opção é ideal para testes em lote ou para integração com outros scripts. Ela processará todos os arquivos em um diretório de entrada e salvará um único `resultados.json`.

1.  **Execute o Módulo `main`**
    (Certifique-se de que seu `venv` está ativado)
    ```bash
    python -m src.main test/ --output resultados.json
    ```

    * `test/`: O diretório de **entrada** (substitua pelo seu, se necessário). Este projeto já inclui a pasta `test/` com os arquivos de exemplo.
    * `--output resultados.json`: O arquivo de **saída** onde o JSON final será salvo.


### 4. Trabalhos futuros

Durante o desafio, explorei uma abordagem de heurísticas baseadas na localização que, embora eu não tenha tido tempo de implementar de forma satisfatória, acredito ter grande potencial para identificar campos de maneira ainda mais eficaz.

A ideia central é esta: após identificar um campo "âncora" (por exemplo, com a LLM), podemos inferir a posição de outros campos com base em sua posição relativa.

Para layouts fixos, a lógica é simples. No entanto, como expandir isso para layouts variantes? A minha hipótese é que um layout variante raramente é caótico; ele é, na verdade, um conjunto de blocos de layout menores que são internamente fixos.

Por exemplo, o bloco "Endereço" pode mudar de lugar na fatura, mas dentro desse bloco, o campo "CEP" e "Estado" sempre terão a mesma disposição e distância relativa entre si.

Minha ideia era implementar um sistema que calculasse a distância de uma palavra-candidata para suas vizinhas, criando um "vetor de características espaciais". Ao analisar PDFs anteriores, o sistema poderia aprender esses padrões e prever a identidade de um campo com base nesse "fingerprint" espacial.

No entanto, devido ao tempo limitado e à necessidade de entregar um produto funcional com a acurácia exigida, optei por focar na arquitetura atual, que foi mais rápida de implementa, validar e debugar.
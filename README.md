# YouTube Downloader Web App
Uma aplicação web simples, robusta e eficiente para baixar múltiplos vídeos do YouTube, construída com Python (Flask) e otimizada para rodar em um container Docker.

(Esta é uma imagem de exemplo, substitua por um screenshot real da sua aplicação em funcionamento)

### Principais Funcionalidades
* **Download em Lote**: Cole múltiplos links de vídeos do YouTube e baixe-os em uma única operação.

* **Progresso em Tempo Real**: Acompanhe o status de cada download individualmente através de barras de progresso e logs detalhados.

* **Fila de Tarefas Otimizada**: Utiliza um sistema de "workers" com fila para processar um número fixo de downloads simultaneamente, evitando a sobrecarga de recursos do servidor.

* **Limpeza Automática de Arquivos**: Os vídeos são salvos em uma pasta temporária do sistema e são automaticamente excluídos após o download pelo usuário, mantendo o servidor sempre limpo.

* **Interface Web Moderna**: Interface limpa e reativa, que guia o usuário durante todo o processo.

* **Pronto para Docker**: Totalmente "containerizado" para uma implantação fácil, rápida e consistente em qualquer ambiente.

* **Reativação Automática**: O botão de download é reativado automaticamente ao final de um lote, pronto para novos vídeos.

### Tecnologias Utilizadas
* **Backend:**

    * [Python 3](https://www.python.org/)

    * [Flask](https://flask.palletsprojects.com/) (Micro-framework web)

    * [yt-dlp](https://github.com/yt-dlp/yt-dlp) (A engine principal para o download dos vídeos)

* **Frontend:**

    * HTML5   

    * CSS3

    * JavaScript (Vanilla)

* **Comunicação em Tempo Real:**

    * Server-Sent Events (SSE)

* **Containerização:**

    * [Docker](https://www.docker.com/)

### Estrutura do Projeto
```
.
├── static/
│   └── style.css       # Folha de estilos da aplicação
├── templates/
│   └── index.html      # Estrutura HTML da interface
├── app.py              # O servidor Flask e toda a lógica do backend
├── Dockerfile          # Receita para construir a imagem Docker
├── requirements.txt    # Lista de dependências Python
└── README.md           # Este arquivo
```

### Instalação e Execução
Existem duas maneiras de rodar esta aplicação:

**Método 1: Usando Docker (Recomendado)**
Este é o método mais simples e garante que o ambiente seja sempre o mesmo.

1. **Pré-requisitos:** Tenha o Docker instalado em sua máquina.

2. **Construa a imagem Docker:**
No terminal, na raiz do projeto, execute:

```
docker build -t youtube-downloader .
```
3. **Execute o container:**
```
docker run -d -p 5000:5000 --name meu-downloader --volume ~/Downloads:/downloads youtube-downloader
```
* `d`: Roda o container em segundo plano.

* `-p 5000:5000`: Mapeia a porta 5000 do seu computador para a porta 5000 do container.

* `--name meu-downloader`: Dá um nome ao container para fácil gerenciamento.

* `--volume ~/Downloads:/downloads`: **Importante!** Mapeia a pasta `Downloads` do seu computador para a pasta usada para salvar os vídeos dentro do container. **É aqui que seus vídeos aparecerão**. (No Windows, substitua `~/Downloads` por um caminho como `C:\Users\SeuUsuario\Downloads`).

4. Acesse a aplicação: Abra seu navegador e vá para http://localhost:5000.

**Método 2: Execução Local (Para Desenvolvimento)**
1. Pré-requisitos:

    * [Python 3.8+](https://www.python.org/downloads/)

    * [FFmpeg](https://ffmpeg.org/download.html) (essencial para o `yt-dlp` juntar áudio e vídeo)

        * No Linux (Ubuntu/Debian), instale com: `sudo apt update && sudo apt install ffmpeg`

2. **Crie e ative um ambiente virtual:**
```
python3 -m venv venv
source venv/bin/activate  # No Linux/macOS
# venv\Scripts\activate   # No Windows
```

3. **Instale as dependências:**
```
pip install -r requirements.txt
```
4. **Execute a aplicação:**
```
python3 app.py
```
5. **Acesse a aplicação**: Abra seu navegador e vá para http://localhost:5000.

### Como Usar
1. Abra a interface no seu navegador.

2. Cole um ou mais links de vídeos do YouTube na área de texto (um por linha).

3. Clique no botão "Baixar Vídeos".

4. Acompanhe o progresso de cada download na lista que aparecerá. A barra de progresso e os logs mostrarão o status em tempo real.

5. Quando um vídeo estiver pronto, seu status mudará para "✅ Pronto para Salvar: [nome do vídeo]".

6. Clique no link do vídeo pronto. Seu navegador abrirá a janela "Salvar Como...", permitindo que você escolha onde salvar o arquivo em seu computador.

### Configuração
Dentro do arquivo `app.py`, você pode ajustar a seguinte variável para otimizar o uso de recursos:

* `WORKER_COUNT`: Define o número de downloads que podem ocorrer simultaneamente. O padrão é 3, um valor seguro para a maioria dos containers. Aumente este número se estiver rodando em uma máquina com mais núcleos de CPU.

### Licença
Este projeto está sob a licença MIT.
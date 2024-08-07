# Rede Anel - Jogo "Fodina"

Este projeto implementa o jogo "fodinha" de cartas em uma rede anel, onde cada jogador está conectado em uma topologia de rede circular. O objetivo principal do jogo é permitir que jogadores possam participar de partidas seguindo as regras estabelecidas, utilizando uma comunicação distribuída entre os jogadores.

## Estrutura Geral

### 1. Arquivos e Diretórios Principais

- `config.json`: Contém a configuração inicial da rede e dos jogadores, incluindo o endereço IP, porta e status de dealer para cada jogador.
- `main.py`: Arquivo principal que inicializa o jogo e gerencia o ciclo principal de execução.
- `network.py`: Define a classe e métodos para o gerenciamento da rede entre os jogadores.
- `player.py`: Contém a classe que representa cada jogador, com suas respectivas ações e atributos.
- `message.py`: Define as mensagens trocadas entre os jogadores, como comandos e respostas durante o jogo.
- `utils.py`: Contém funções auxiliares que suportam as operações principais, como manipulação de dados, validações e funções utilitárias usadas em diferentes partes do código.
- `Dockerfile`: Configuração do Docker para containerizar o jogo.
- `run_dockers.sh`: Script para executar os containers Docker configurados para o jogo.

### 2. Ciclo de Jogo

O ciclo de jogo é gerenciado pelo arquivo `main.py`, onde a sequência de ações ocorre da seguinte maneira:

1. **Inicialização**: Configura a rede de acordo com as especificações em `config.json`, instancia os objetos necessários e carrega as configurações iniciais, como os jogadores e suas respectivas posições na rede.
2. **Distribuição de Papéis**: Um jogador é designado como dealer (atributo usado como bastão), que é o responsável por gerencias as rodadas. Este status de dealer é definido no arquivo `config.json` e pode eh passado ao proximo jogador em relacao ao dealer ainda com vida ao fim de cada rodada

3. **Ciclo de Rodadas**: O jogo é dividido em rodadas, onde cada jogador realiza sua jogada de acordo com suas cartas e pontos de vida. Durante as rodadas:

   - **Comportamento dos Jogadores**: Dentro de cada ciclo, o comportamento de uma máquina varia dependendo de seu jogador local ser o dealer ou não. Somente o dealer insere mensagens na rede, enquanto os outros jogadores apenas escutam e respondem ao dealer quando necessário. O dealer tem a responsabilidade de coletar as jogadas, calcular os resultados das jogadas, rodadas e atualizar os pontos de vida dos jogadores ao fim de cada rodada. Ele então envia esses resultados para todos os jogadores, garantindo que a rede permaneça sincronizada ao passar a função de dealer para o próximo jogador, que deverá assumir essas responsabilidades na rodada seguinte.

     3.1. **Distribuição de Cartas**:

   - Apenas o dealer envia as mensagens do tipo "shuffle" para distribuir as cartas aos jogadores.
   - Os outros jogadores aguardam as mensagens. Se forem destinatários, salvam a carta recebida através da mensagem do tipo "shuffle", onde a carta está no campo play da mensagem, e enviam uma resposta "shuffle" com `confirm="true"` para o dealer, indicando que ele pode enviar a próxima carta. Cada carta é enviada separadamente para o jogador correspondente.
   - Quando todas as cartas são distribuídas, o dealer envia uma mensagem "end_shuffle" para todos os jogadores, permitindo que saiam da rotina de escuta das mensagens de "shuffle" e comecem a escutar a próxima fase do jogo.

     3.2. **Coleta de Palpites**:

   - Novamente, apenas o dealer envia as mensagens do tipo "bid" para cada jogador.
   - Os outros jogadores aguardam a mensagem do tipo "bid", enviada individualmente pelo dealer. Se forem destinatários, respondem inserindo seu palpite na mensagem com `confirm=true`, e enviam de volta para o dealer. O dealer então salva o palpite inicial de cada jogador em sua rede local, que será usado ao final da rodada para calcular as novas vidas de cada jogador.
   - Quando todos os jogadores enviam seus palpites, o dealer transmite uma mensagem "end_bid" para todos, permitindo que saiam dessa rotina e retornem à função principal, sincronizando-se para o próximo ciclo de escuta.

     3.3. **Rodada**:

   - O dealer gerencia cada jogada da rodada. Para cada carta jogada, o dealer envia uma mensagem do tipo "play" para cada jogador, que responde com sua jogada/carta e `confirm=true`. Ao receber a jogada, o dealer retransmite a jogada do jogador na rede através de uma mensagem do tipo "ack_play", garantindo que a mensagem percorra todo o anel e que todos os jogadores possam ver as jogadas de seus rivais.
   - Ao final de cada jogada (uma carta por jogador), o dealer verifica quem ganhou ou se houve empate e transmite uma mensagem do tipo "round_won" na rede. Esta mensagem pode conter "draw" no campo play se houve empate, ou o IP do ganhador, para que cada jogador receba a informação sobre quem ganhou a jogada. O dealer também salva o ganhador para que a próxima jogada comece a partir do vencedor da rodada atual. É também neste momento que o dealer incrementa o número de jogadas vencidas de um jogador, o que será usado posteriormente para calcular quantas vidas ele perdeu na rodada. Após a conclusão de todas as jogadas da rodada, o dealer envia uma mensagem do tipo "end_play" para todos os jogadores, que retornam à rotina principal e entram no último passo do round.

     3.4. **Finalização da Rodada**:

   - Assim que todas as jogadas de uma rodada são concluídas, o dealer é responsável por calcular a vida de cada jogador utilizando os atributos `player.hp`, `player.round_wins` e `player.bid`. As novas vidas são salvas localmente e transmitidas para toda a rede através de uma mensagem do tipo "update_hp", garantindo que todas as máquinas da rede estejam sincronizadas quanto às vidas dos jogadores. Como o número exato de mensagens enviadas na rede é conhecido, não é necessária uma mensagem específica de finalização da rodada; em vez disso, é utilizado um contador que vai de 0 até o número de jogadores. Quando cada jogador tiver sua mensagem "update_hp" enviada e confirmada pelo dealer, todos retornam uma última vez para a função principal.

     3.5. **Último Passo**:

   - Agora que todos os jogadores estão sincronizados, cada máquina localmente passará o papel de dealer para o próximo jogador com vida restante, antes de remover os jogadores da rede (para evitar erros caso o dealer da rodada seja excluído). Em seguida, verifica-se se o jogador local perdeu todas as suas vidas. Se ele perdeu, a máquina local encerra o processo e informa ao jogador que ele perdeu. Caso o jogador local ainda tenha pontos de vida, ele removerá da rede os jogadores com HP igual a 0 e reorganizará a rede em formato de anel com os jogadores restantes. Aqui também é feita a verificação se há um ganhador. Se houver, o jogador local é informado de sua vitória e o processo é encerrado. Por último, é executada uma rotina de reset para o próximo round, onde cada jogador tem os seguintes atributos resetados: `self.cards = []`, `self.plays = []`, `self.bid = 0`, `self.round_wins = 0`. Com os jogadores restantes reorganizados em formato de anel, um novo dealer e cada jogador com seus atributos de rodada zerados, o jogo pode prosseguir para o próximo round do loop.

### 3. Classes

- **`Network` (`network.py`)**: Gerencia a comunicação entre os jogadores na rede. Esta classe é responsável por transmitir e receber mensagens, sincronizar o estado do jogo entre os participantes e gerenciar as conexões de rede entre os jogadores. Cada máquina mantém uma versão local da rede, contendo todos os jogadores ativos. Essas versões locais são sincronizadas através da rede durante o jogo, garantindo que todas as máquinas tenham uma visão consistente dos jogadores participantes.

- **`Player` (`player.py`)**: Representa cada jogador no jogo. Armazena informações como pontos de vida (`hp`), cartas na mão e se o jogador é o dealer ou não. Também possui métodos para realizar jogadas, receber cartas e executar outras ações durante o jogo, conforme as regras estabelecidas.

- **`Message` (`message.py`)**: Define a estrutura das mensagens trocadas entre os jogadores, incluindo o tipo de mensagem, remetente, destinatário e conteúdo. As mensagens são o principal meio de comunicação e coordenação entre os jogadores durante o jogo, permitindo a troca de informações essenciais como jogadas, resultados e atualizações de status.

### 5. Docker e Execução

O projeto inclui um `Dockerfile` para facilitar a containerização do jogo, permitindo que o ambiente de execução seja configurado e gerenciado de forma consistente e replicável. O script `run_dockers.sh` pode ser utilizado para iniciar os containers necessários e executar o jogo em um ambiente Dockerizado.

Para configurar a rede fora de um ambiente Docker, é necessário descobrir o IP e a porta ativa de 4 máquinas na mesma rede. Essas informações devem ser substituídas manualmente no arquivo `config.json` para cada máquina, garantindo que todas estejam corretamente configuradas para participar do jogo em rede. Este procedimento assegura que as conexões de rede sejam estabelecidas corretamente entre os jogadores, permitindo a execução do jogo sem problemas em um ambiente não Dockerizado.

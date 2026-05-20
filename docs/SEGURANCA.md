# Segurança — Defesas contra Prompt Injection

Aplicações que expõem LLMs a usuários finais estão sujeitas a **prompt injection**: tentativas do usuário de sobrescrever o comportamento do modelo via instruções no input (*"ignore as regras anteriores e…"*, *"você agora é…"*, etc.).

O **ChatCapitu** aplica defesas em três camadas.

## Camada 1 — Sanitização de entrada

Implementada em [`query.py`](../query.py) na função `sanitizar_pergunta()`:

```python
def sanitizar_pergunta(pergunta: str) -> str:
    pergunta = pergunta[:500]                            # limita o comprimento
    pergunta = re.sub(r"\n+", " ", pergunta)             # neutraliza quebras
    pergunta = re.sub(r"\s{2,}", " ", pergunta).strip()
    if _INJECTION_PATTERNS.search(pergunta):
        raise ValueError(
            "Sua pergunta contém termos não permitidos. Por favor, reformule."
        )
    return pergunta
```

**Padrões bloqueados** (regex case-insensitive):

- `ignore as instruções/regras/sistema`
- `novo sistema`
- `você agora é …`
- `atue como …`, `finja ser/que …`
- `esqueça as regras`
- `modo dev`, `jailbreak`
- Tentativas de injetar tags delimitadoras (`<sistema>`, `</contexto>`, etc.)

Em caso de match, a função lança `ValueError`, que sobe até a UI Streamlit e é exibida ao usuário como aviso amigável — sem revelar quais padrões foram detectados.

## Camada 2 — Estrutura do prompt

O prompt final é montado em formato de continuação textual, com **separação estrutural por marcadores semânticos**:

```
Trechos de Dom Casmurro (Machado de Assis):

[Trecho 1] ...
[Trecho 2] ...
[Trecho 3] ...

Com base apenas nos trechos acima, um professor de literatura responde
à pergunta de um aluno. A resposta interpreta o sentido do texto sem
transcrevê-lo literalmente, em 2 ou 3 parágrafos claros.

Pergunta do aluno: {pergunta}

Professor:
```

Três propriedades dessa estrutura limitam a superfície de ataque:

1. **Isolamento posicional**: o input do usuário é interpolado **depois** do contexto e das instruções. O modelo lê primeiro a moldura interpretativa e só depois encontra a pergunta.
2. **Cenário forte**: a metáfora "professor responde a aluno" induz o modelo a permanecer no papel de explicador literário, dificultando que reinterprete a pergunta como nova instrução.
3. **Marcadores fixos**: as palavras-âncora (`Trechos de Dom Casmurro`, `Pergunta do aluno`, `Professor:`) também funcionam como **stop tokens** na geração — o modelo é interrompido se tentar gerar nova seção (`\n\nPergunta:`, `\n\nProfessor:`, etc.).

> **Nota sobre o design iterativo**: uma versão anterior do prompt usava tags XML explícitas (`<sistema>`, `<contexto>`, `<pergunta>`) com regras inegociáveis declaradas. Essa abordagem foi abandonada porque o Sabiá-7B (modelo base, não instruct) ecoava as tags na resposta, contaminando a saída. O formato de continuação atual oferece isolamento estrutural equivalente sem o problema do eco — uma decisão pragmática que privilegia o que funciona com o modelo escolhido.

## Camada 3 — Pós-processamento

Mesmo que uma injeção bem-sucedida passe pelas duas primeiras camadas, três filtros são aplicados a cada sentença da resposta:

- **Anti-loop**: regex `(.{4,50}?)\1{3,}` detecta padrões repetidos 3+ vezes consecutivas e trunca a resposta antes do loop. Pega o caso clássico do modelo travar em *"de idem, de idem, de idem…"*.
- **Anti-eco do prompt**: bloqueia sentenças que repetem expressões da framing (`um professor de literatura responde`, `leitura crítica`, etc.).
- **Anti-quase-duplicata**: Jaccard de palavras > 0.7 contra os trechos recuperados, descartando cópias quase-literais do contexto.
- **Anti-prefixo truncado**: se a última sentença é prefixo de uma anterior, é descartada (caso comum quando `max_tokens` corta a geração no meio).

## Ameaças NÃO totalmente cobertas

Limitações conscientes do projeto, explicitadas para honestidade técnica:

- **Injeção semântica criativa**: variações linguísticas, sinônimos e construções perífrase dos padrões bloqueados podem escapar do regex. Uma defesa mais robusta usaria um classificador de intenção treinado especificamente.
- **Adversarial multi-turn**: o sistema é stateless (uma pergunta por vez), o que neutraliza ataques que dependem de acúmulo de contexto entre turnos. Em um chatbot conversacional, seria um risco a tratar.
- **Data poisoning**: como o corpus é curado manualmente pela autora, ataques via dados não se aplicam neste cenário.
- **Exfiltração via resposta**: sem mecanismo formal de auditoria de saída — uma resposta indevida não é automaticamente detectada além dos filtros pós-processamento.

## Auditoria e observabilidade

A versão atual loga via `logging.INFO`:

- Backend de LLM em uso (`Ollama local` ou `Maritaca API`).
- Carregamento do índice vetorial (uma única vez por sessão).
- Tamanho do contexto recuperado (chars + k).
- Erros durante a consulta ao LLM.

Tentativas de injeção bloqueadas pela sanitização **lançam exceção**, mas não são registradas — o usuário recebe mensagem genérica para evitar revelar quais padrões são detectados, e a equipe não monitora frequência de tentativas.

Telemetria mais rica (tempo de resposta, contagem de bloqueios, distribuição de erros) seria um próximo passo natural para um deploy em produção.

---

> **Disclaimer**: este é um trabalho acadêmico, não um sistema de produção endurecido. As defesas implementadas são adequadas para uma aplicação demonstrativa de TCC, mas um deploy em produção exigiria revisão por especialista em segurança de aplicações LLM e ferramentas dedicadas (Lakera Guard, Rebuff, etc.).

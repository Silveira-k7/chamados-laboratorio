# 3. Arquitetura

## Plano macro

O sistema é um monólito em camadas. Um comando executa interface, casos de uso e persistência local no mesmo processo.

| Critério do capítulo de estilo | Aplicação ao projeto |
| --- | --- |
| Quando adotar | Um grupo mantém o sistema, o fluxo é curto e os componentes precisam da mesma transação. |
| Quando evitar | A implantação precisaria mudar diante de operação por várias equipes remotas ou escalabilidade independente da leitura e da escrita. |
| Custo real | Uma mudança em qualquer camada exige atualizar a aplicação toda. O arquivo local e a capacidade de escrita do SQLite limitam a concorrência. |

Consideramos **microsserviços**, que introduziriam pelo menos outra implantação e comunicação de rede onde uma chamada local é suficiente, e **arquitetura orientada a eventos**, que adicionaria entrega e deduplicação de mensagens a um fluxo que precisa mostrar o resultado da gravação imediatamente. Ver [ADR 0001](../adrs/0001-monolito.md).

```python
with closing(sqlite3.connect(args.banco, timeout=5.0)) as connection:
    run_command(args, SqliteTickets(connection))
```

[Ver código em `chamados/cli.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/cli.py#L81-L82).

## Plano interno

A CLI compõe a aplicação com um adaptador SQLite. O serviço realiza os casos de uso, o domínio controla as transições e o adaptador traduz as operações de persistência.

| Parte | Pasta e arquivo |
| --- | --- |
| Interface e composição | [chamados/cli.py](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/cli.py) |
| Aplicação e portas | [chamados/application.py](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/application.py) |
| Domínio | [chamados/domain.py](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/domain.py) |
| Persistência | [chamados/storage.py](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/storage.py) |

```python
def run_command(args: Namespace, repository: SqliteTickets) -> None:
    service = TicketService(repository, repository, lambda: datetime.now(UTC))
```

[Ver código em `chamados/cli.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/cli.py#L45-L46).

- [Organização interna](../diagrams/camadas.md)
- [C4 nível 1 · Contexto](../diagrams/c4-contexto.md)
- [C4 nível 2 · Contêineres](../diagrams/c4-conteineres.md)
- [C4 nível 3 · Componentes](../diagrams/c4-componentes.md)
- [Sequência · Abertura de chamado](../diagrams/sequencia-abertura.md)

A obra integral indicada pela disciplina precisa ser consultada pelo grupo para conferir o capítulo do estilo e o Apêndice B.4. Os diagramas registram a estrutura implementada e usam rótulos de tipo nos conectores.

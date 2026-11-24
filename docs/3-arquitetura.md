# 3. Arquitetura

## Plano macro

O sistema é um monólito em camadas. Um comando executa interface, casos de uso e persistência local no mesmo processo. A decisão segue os critérios das seções 5.5 a 5.7 de [Abreu (2026)](8-conclusao.md#referências), nas páginas 40 a 42.

| Critério do capítulo de estilo | Aplicação ao projeto |
| --- | --- |
| Quando adotar | Um grupo mantém o sistema, o fluxo é curto e os componentes precisam da mesma transação. |
| Quando evitar | A implantação precisaria mudar diante de operação por várias equipes remotas ou escalabilidade independente da leitura e da escrita. |
| Custo real | Operar um processo e um banco reduz a infraestrutura. Uma mudança que afete várias camadas exige coordenar código e testes na mesma implantação. O arquivo local e a capacidade de escrita do SQLite limitam a concorrência. |

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

Os diagramas seguem as seções 3.5 e 3.6 e os modelos do Apêndice B.4 de [Abreu (2026)](8-conclusao.md#referências). A aplicação Python é a unidade de implantação. O SQLite é um contêiner C4 de armazenamento, acessado como arquivo no mesmo posto de atendimento.

## Verificação das dependências

A função de aptidão analisa os imports em Python. Ela confere as dependências internas permitidas por módulo e limita o uso de `sqlite3` ao adaptador e ao ponto de composição. O CI roda essa verificação junto dos testes de fluxo.

```python
def test_application_and_domain_do_not_depend_on_adapters(self):
    source_files = sorted(PACKAGE.glob("*.py"))
    self.assertEqual({file.stem for file in source_files}, ALLOWED_INTERNAL_IMPORTS.keys())
    for source in source_files:
        with self.subTest(module=source.stem):
            imports = imported_modules(source)
            internal = {name.split(".")[1] for name in imports if name.startswith("chamados.")}
            self.assertLessEqual(internal, ALLOWED_INTERNAL_IMPORTS[source.stem])
            if source.stem not in SQLITE_MODULES:
                self.assertFalse(any(name.split(".")[0] == "sqlite3" for name in imports))
```

[Ver código em `tests/test_architecture.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/dde43c9ca02c4584e898e59234092ab0829e34d2/tests/test_architecture.py#L35-L44).

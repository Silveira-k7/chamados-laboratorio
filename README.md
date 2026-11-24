# Chamados de Laboratório

Sistema para registrar incidentes de TI, priorizar a fila pelo prazo de solução e acompanhar cada chamado até a resolução ou reabertura.

## Integrantes

- [@Silveira-k7](https://github.com/Silveira-k7)
- [@GabrielFreire05](https://github.com/GabrielFreire05)
- [@CaueFeliciano](https://github.com/CaueFeliciano)
- [@NicolasDM22](https://github.com/NicolasDM22)

## Instalação e execução

Requer Python 3.11 ou superior com SQLite, que já integra a biblioteca padrão. A aplicação roda na pasta do repositório sem dependências externas.

```bash
git clone https://github.com/Silveira-k7/chamados-laboratorio.git
cd chamados-laboratorio
python -m chamados --help
python -m chamados abrir "Lab 3" "Projetor sem imagem" alta --politica prova
python -m chamados fila
```

Copie o identificador mostrado na abertura e substitua `ID` nos exemplos.

```bash
python -m chamados iniciar ID
python -m chamados resolver ID --nota "Cabo HDMI substituído"
python -m chamados reabrir ID --nota "A imagem voltou a falhar"
python -m chamados historico ID
```

Use `--banco caminho.db` antes do comando para escolher outro banco. O arquivo padrão é `chamados.db`.

## Verificações

```bash
python -m venv .venv
```

Ative o ambiente com `source .venv/bin/activate` no Linux/macOS ou `.venv\Scripts\Activate.ps1` no PowerShell.

```bash
python -m pip install -r requirements-dev.txt
ruff check .
ruff format --check .
python -m unittest discover -s tests -v
```

## Documentação

| Item | Documento |
| --- | --- |
| 1 | [Contexto](docs/1-contexto.md) |
| 2 | [Atributos de qualidade](docs/2-qualidade.md) |
| 3 | [Arquitetura](docs/3-arquitetura.md) |
| 4 | [Decisões de arquitetura (ADRs)](adrs/) |
| 5 | [SOLID](docs/4-solid.md) |
| 6 | [Clean Code](docs/5-clean-code.md) |
| 7 | [Padrões GoF](docs/6-gof.md) |
| 8 | [Padrão transversal](docs/7-transversal.md) |
| 9 | [Conclusão e referências](docs/8-conclusao.md) |

[Diagramas Mermaid](diagrams/) · [Modelo de pull request](.github/pull_request_template.md) · [GitHub Actions](https://github.com/Silveira-k7/chamados-laboratorio/actions)

## Colaboração

Abra uma branch descritiva por mudança, por exemplo `feat/filtrar-fila` ou `docs/adr-0006`. Faça commits com mensagens claras conforme o trabalho avança e abra um PR pequeno, explicando o que mudou, por quê e como testar. Cada integrante deve abrir PRs e revisar os dos colegas. O `main` exige PR e aprovação de outro integrante. Faça o squash pelo GitHub após a aprovação e as verificações.

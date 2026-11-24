# 9. Conclusão

- **O que funcionou.** A política por chamado preserva a ordem de prioridade. A transição e o histórico ficam consistentes quando ocorre uma tentativa de gravar com versão antiga.
- **O que não funcionou no uso de teste.** A operação de resolver sem anotar a solução foi rejeitada. A CLI recebe a nota por argumento, o que exige que o operador corrija e repita o comando.
- **O que faríamos diferente.** Experimentaríamos uma entrada interativa para as notas na CLI e mediríamos a fila usando arquivos em disco e dois processos, antes de considerar implantação para mais de uma equipe.

```python
def test_stale_update_leaves_history_untouched(self):
    stale = self.ticket.advance(Action.START, "")
    self.service.advance(self.ticket.id, Action.START, "Visita")
    with self.assertRaisesRegex(TicketError, "mudou"):
        self.storage.update(stale, HistoryEntry(stale.id, stale.status, self.now, "Duplicado"))
    self.assertEqual(len(self.storage.history(self.ticket.id)), 2)
```

[Ver código em `tests/test_chamados.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/tests/test_chamados.py#L47-L52).

## Referências

- Livro da disciplina **Padrões e Arquitetura de Software**. O [enunciado da disciplina](https://puc-campinas.instructure.com/courses/94516/assignments/286802) remete aos capítulos 2–5, 17–19 e ao Apêndice B.4. Título bibliográfico, autoria, ano e link da obra ficam pendentes de confirmação no material da turma.
- Refactoring Guru. *Padrões de Projeto* (s.d.). [Catálogo](https://refactoring.guru/pt-br/design-patterns/catalog).
- Refactoring Guru. *Refatoração* (s.d.). [Catálogo de code smells e técnicas](https://refactoring.guru/pt-br/refactoring).
- ISO e IEC. *ISO/IEC 25010:2023 — Product quality model* (2023). [Norma](https://www.iso.org/standard/78176.html).
- Python Software Foundation. *The Python Standard Library — sqlite3* (Python 3.11). [Documentação](https://docs.python.org/3.11/library/sqlite3.html).
- Simon Brown. *The C4 model for visualising software architecture* (s.d.). [Modelo C4](https://c4model.com/).

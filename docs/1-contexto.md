# 1. Contexto

Quando vários incidentes interrompem atividades de laboratório, a equipe de suporte precisa decidir a ordem de atendimento e registrar como cada caso foi resolvido. Uma mesma falha pode ter um prazo mais curto durante uma prova.

O projeto novo atende equipes pequenas de suporte por uma interface de linha de comando. O operador registra laboratório, descrição, gravidade e política de prazo, acompanha uma fila ordenada e consulta o histórico. Pode iniciar o atendimento, resolver com registro da solução e reabrir com justificativa.

```python
def triage_queue(reader: QueueReader) -> list[Ticket]:
    return sorted(
```

[Ver código em `chamados/application.py`](https://github.com/Silveira-k7/chamados-laboratorio/blob/cbc225cc7836fbd98740b3a7da5c3ec48d43230f/chamados/application.py#L85-L86).

Ficam fora do escopo a gestão de inventário, autenticação por operador, portal web, notificações, escalonamento automático e integração com sistemas da universidade.

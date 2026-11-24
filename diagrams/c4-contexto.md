# C4 nível 1 · Contexto

```mermaid
C4Context
Person(operador, "Operador de TI", "Registra e trata incidentes de laboratório")
System(chamados, "Chamados de Laboratório", "Calcula prazos e mantém histórico de atendimento")
Rel(operador, chamados, "chamada: opera por CLI")
```

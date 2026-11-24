import json
import logging
import sqlite3
import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from chamados.application import ExamDeadline, RegularDeadline, TicketService, triage_queue
from chamados.domain import Action, Severity, Ticket, TicketError
from chamados.storage import SqliteTickets

POLICIES = {policy.name: policy for policy in (RegularDeadline(), ExamDeadline())}
LOGGER = logging.getLogger(__name__)


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Triagem de chamados de laboratório")
    parser.add_argument("--banco", type=Path, default=Path("chamados.db"))
    commands = parser.add_subparsers(dest="command", required=True)
    open_ticket = commands.add_parser("abrir", help="Registrar um incidente")
    open_ticket.add_argument("laboratorio")
    open_ticket.add_argument("descricao")
    open_ticket.add_argument("gravidade", choices=list(Severity), type=Severity)
    open_ticket.add_argument("--politica", choices=POLICIES, default="regular")
    for action in Action:
        command = commands.add_parser(action.value)
        command.add_argument("id")
        command.add_argument("--nota", default="")
    commands.add_parser("fila", help="Exibir pendências em ordem de prazo")
    history = commands.add_parser("historico", help="Exibir as transições de um chamado")
    history.add_argument("id")
    return parser


def print_ticket(ticket: Ticket) -> None:
    print(
        f"{ticket.id} | {ticket.room} | {ticket.status} | {ticket.severity} "
        f"| prazo {ticket.due_at.isoformat()} | {ticket.title}"
    )


def run_command(args: Namespace, repository: SqliteTickets) -> None:
    service = TicketService(repository, repository, lambda: datetime.now(UTC))
    match args.command:
        case "abrir":
            print_ticket(
                service.open(
                    args.laboratorio, args.descricao, args.gravidade, POLICIES[args.politica]
                )
            )
        case "fila":
            for ticket in triage_queue(repository):
                print_ticket(ticket)
        case "historico":
            for entry in repository.history(args.id):
                print(f"{entry.at.isoformat()} | {entry.status} | {entry.note}")
        case _:
            print_ticket(service.advance(args.id, Action(args.command), args.nota))


def log_event(command: str, outcome: str, *, error_type: str | None = None) -> None:
    event = {
        "event": "ticket_command",
        "timestamp": datetime.now(UTC).isoformat(),
        "command": command,
        "outcome": outcome,
    }
    if error_type:
        event["error_type"] = error_type
    level = logging.ERROR if error_type else logging.INFO
    LOGGER.log(level, "%s", json.dumps(event))


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        with closing(sqlite3.connect(args.banco, timeout=5.0)) as connection:
            run_command(args, SqliteTickets(connection))
    except (TicketError, sqlite3.Error) as error:
        log_event(args.command, "error", error_type=type(error).__name__)
        print(f"Erro: {error}", file=sys.stderr)
        return 1
    log_event(args.command, "ok")
    return 0

from collections.abc import Callable, Sequence
from datetime import datetime, timedelta
from typing import ClassVar, Protocol
from uuid import uuid4

from chamados.domain import (
    Action,
    DeadlinePolicy,
    HistoryEntry,
    Severity,
    Status,
    Ticket,
    TicketError,
)


class TicketWriter(Protocol):
    def insert(self, ticket: Ticket, entry: HistoryEntry) -> None: ...

    def update(self, ticket: Ticket, entry: HistoryEntry) -> None: ...


class TicketReader(Protocol):
    def get(self, ticket_id: str) -> Ticket: ...


class QueueReader(Protocol):
    def pending(self) -> Sequence[Ticket]: ...


class RegularDeadline:
    name: ClassVar[str] = "regular"
    hours: ClassVar[dict[Severity, int]] = {
        Severity.HIGH: 4,
        Severity.MEDIUM: 12,
        Severity.LOW: 24,
    }

    def deadline(self, severity: Severity, opened_at: datetime) -> datetime:
        return opened_at + timedelta(hours=self.hours[severity])


class ExamDeadline:
    name: ClassVar[str] = "prova"

    def deadline(self, severity: Severity, opened_at: datetime) -> datetime:
        if severity is Severity.HIGH:
            return opened_at + timedelta(minutes=30)
        if severity is Severity.MEDIUM:
            return opened_at + timedelta(hours=3)
        return opened_at + timedelta(hours=24)


class TicketService:
    def __init__(self, reader: TicketReader, writer: TicketWriter, now: Callable[[], datetime]):
        self.reader = reader
        self.writer = writer
        self.now = now

    def open(self, room: str, title: str, severity: Severity, policy: DeadlinePolicy) -> Ticket:
        room, title = room.strip(), title.strip()
        if not room or not title:
            raise TicketError("Informe o laboratório e a descrição do incidente.")
        opened_at = self.now()
        ticket = Ticket(
            id=str(uuid4()),
            room=room,
            title=title,
            severity=severity,
            status=Status.OPEN,
            policy=policy.name,
            created_at=opened_at,
            due_at=policy.deadline(severity, opened_at),
        )
        self.writer.insert(ticket, HistoryEntry(ticket.id, ticket.status, opened_at, "Abertura"))
        return ticket

    def advance(self, ticket_id: str, action: Action, note: str) -> Ticket:
        ticket = self.reader.get(ticket_id).advance(action, note)
        entry = HistoryEntry(ticket.id, ticket.status, self.now(), note.strip())
        self.writer.update(ticket, entry)
        return ticket


def triage_queue(reader: QueueReader) -> list[Ticket]:
    return sorted(
        reader.pending(), key=lambda ticket: (ticket.due_at, ticket.created_at, ticket.id)
    )

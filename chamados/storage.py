from datetime import datetime
from sqlite3 import Connection, Row

from chamados.domain import HistoryEntry, Severity, Status, Ticket, TicketError

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    id TEXT PRIMARY KEY,
    room TEXT NOT NULL,
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    policy TEXT NOT NULL,
    created_at TEXT NOT NULL,
    due_at TEXT NOT NULL,
    version INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY,
    ticket_id TEXT NOT NULL REFERENCES tickets(id),
    status TEXT NOT NULL,
    at TEXT NOT NULL,
    note TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS history_ticket ON history(ticket_id, id);
"""


class SqliteTickets:
    def __init__(self, connection: Connection):
        self.connection = connection
        self.connection.row_factory = Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(SCHEMA)

    def insert(self, ticket: Ticket, entry: HistoryEntry) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO tickets
                (id, room, title, severity, status, policy, created_at, due_at, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket.id,
                    ticket.room,
                    ticket.title,
                    ticket.severity,
                    ticket.status,
                    ticket.policy,
                    ticket.created_at.isoformat(),
                    ticket.due_at.isoformat(),
                    ticket.version,
                ),
            )
            self._append(entry)

    def update(self, ticket: Ticket, entry: HistoryEntry) -> None:
        with self.connection:
            # A versão impede sobrescrever uma transição feita por outro operador.
            updated = self.connection.execute(
                "UPDATE tickets SET status = ?, version = ? WHERE id = ? AND version = ?",
                (ticket.status, ticket.version, ticket.id, ticket.version - 1),
            )
            if updated.rowcount != 1:
                raise TicketError(
                    "O chamado mudou durante a operação. Consulte-o e tente novamente."
                )
            self._append(entry)

    def _append(self, entry: HistoryEntry) -> None:
        self.connection.execute(
            "INSERT INTO history (ticket_id, status, at, note) VALUES (?, ?, ?, ?)",
            (entry.ticket_id, entry.status, entry.at.isoformat(), entry.note),
        )

    def get(self, ticket_id: str) -> Ticket:
        row = self.connection.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if row is None:
            raise TicketError("Chamado não encontrado.")
        return self._ticket_from_row(row)

    def pending(self) -> list[Ticket]:
        rows = self.connection.execute(
            "SELECT * FROM tickets WHERE status != ?", (Status.RESOLVED,)
        )
        return [self._ticket_from_row(row) for row in rows]

    def history(self, ticket_id: str) -> list[HistoryEntry]:
        self.get(ticket_id)
        rows = self.connection.execute(
            "SELECT * FROM history WHERE ticket_id = ? ORDER BY id", (ticket_id,)
        )
        return [
            HistoryEntry(
                row["ticket_id"],
                Status(row["status"]),
                datetime.fromisoformat(row["at"]),
                row["note"],
            )
            for row in rows
        ]

    @staticmethod
    def _ticket_from_row(row: Row) -> Ticket:
        return Ticket(
            id=row["id"],
            room=row["room"],
            title=row["title"],
            severity=Severity(row["severity"]),
            status=Status(row["status"]),
            policy=row["policy"],
            created_at=datetime.fromisoformat(row["created_at"]),
            due_at=datetime.fromisoformat(row["due_at"]),
            version=row["version"],
        )

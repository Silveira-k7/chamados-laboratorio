import sqlite3
import unittest
from datetime import UTC, datetime, timedelta

from chamados.application import ExamDeadline, RegularDeadline, TicketService, triage_queue
from chamados.domain import Action, HistoryEntry, Severity, Status, TicketError
from chamados.storage import SqliteTickets


class TicketFlowTest(unittest.TestCase):
    def setUp(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        self.storage = SqliteTickets(connection)
        self.now = datetime(2026, 11, 24, 12, tzinfo=UTC)
        self.service = TicketService(self.storage, self.storage, lambda: self.now)
        self.ticket = self.service.open(
            "Lab 3", "Projetor sem imagem", Severity.HIGH, ExamDeadline()
        )

    def test_queue_prioritizes_deadline(self):
        regular = self.service.open("Lab 4", "Falha no projetor", Severity.HIGH, RegularDeadline())
        self.assertEqual(self.ticket.due_at, self.now + timedelta(minutes=30))
        self.assertEqual(regular.due_at, self.now + timedelta(hours=4))
        self.assertEqual(triage_queue(self.storage), [self.ticket, regular])

    def test_state_journey_and_history(self):
        ticket_id = self.ticket.id
        self.service.advance(ticket_id, Action.START, "")
        with self.assertRaisesRegex(TicketError, "solução"):
            self.service.advance(ticket_id, Action.RESOLVE, " ")
        self.service.advance(ticket_id, Action.RESOLVE, "Cabo trocado")
        self.assertEqual(triage_queue(self.storage), [])
        reopened = self.service.advance(ticket_id, Action.REOPEN, "Falha retornou")
        self.assertEqual(reopened.due_at, self.ticket.due_at)
        self.assertEqual(
            [entry.status for entry in self.storage.history(ticket_id)],
            [Status.OPEN, Status.IN_PROGRESS, Status.RESOLVED, Status.OPEN],
        )

    def test_invalid_transition_leaves_history_untouched(self):
        with self.assertRaises(TicketError):
            self.service.advance(self.ticket.id, Action.RESOLVE, "Troca de equipamento")
        self.assertEqual(self.storage.get(self.ticket.id), self.ticket)
        self.assertEqual(len(self.storage.history(self.ticket.id)), 1)

    def test_stale_update_leaves_history_untouched(self):
        stale = self.ticket.advance(Action.START, "")
        self.service.advance(self.ticket.id, Action.START, "Visita")
        with self.assertRaisesRegex(TicketError, "mudou"):
            self.storage.update(stale, HistoryEntry(stale.id, stale.status, self.now, "Duplicado"))
        self.assertEqual(len(self.storage.history(self.ticket.id)), 2)


if __name__ == "__main__":
    unittest.main()

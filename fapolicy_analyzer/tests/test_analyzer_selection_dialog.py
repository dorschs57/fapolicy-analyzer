import context  # noqa: F401
import gi
import pytest

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from helpers import delayed_gui_action
from ui.analyzer_selection_dialog import AnalyzerSelectionDialog, ANALYZER_SELECTION


@pytest.fixture
def widget():
    return AnalyzerSelectionDialog(Gtk.Window())


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Dialog


def test_adds_dialog_to_parent():
    parent = Gtk.Window()
    widget = AnalyzerSelectionDialog(parent)
    assert widget.get_ref().get_transient_for() == parent


def test_trust_database_admin_selection(widget):
    trustAdminBtn = widget.get_object("adminTrustDatabasesBtn")
    delayed_gui_action(trustAdminBtn.clicked)
    result = widget.get_selection()
    assert result == ANALYZER_SELECTION.TRUST_DATABASE_ADMIN


def test_analyze_from_audit(widget):
    widget.get_object("auditLogTxt").set_text("foo")
    delayed_gui_action(widget.get_object("analyzeAuditBtn").clicked)
    result = widget.get_selection()
    assert result == ANALYZER_SELECTION.ANALYZE_FROM_AUDIT
    assert widget.get_data() == "foo"


def test_set_audit_file_from_dialog(widget, mocker):
    mocker.patch(
        "ui.analyzer_selection_dialog.Gtk.FileChooserDialog.run",
        return_value=Gtk.ResponseType.OK,
    )
    mocker.patch(
        "ui.analyzer_selection_dialog.Gtk.FileChooserDialog.get_filename",
        return_value="foo",
    )
    mocker.patch("ui.analyzer_selection_dialog.path.isfile", return_value=True)
    auditLogTxt = widget.get_object("auditLogTxt")
    auditLogTxt.emit("icon_press", Gtk.EntryIconPosition.SECONDARY, Gdk.Event())
    assert auditLogTxt.get_text() == "foo"


def test_does_nothing_on_primary_icon(widget):
    auditLogTxt = widget.get_object("auditLogTxt")
    auditLogTxt.set_text("foo")
    assert auditLogTxt.get_text() == "foo"
    auditLogTxt.emit("icon_press", Gtk.EntryIconPosition.PRIMARY, Gdk.Event())
    assert auditLogTxt.get_text() == "foo"
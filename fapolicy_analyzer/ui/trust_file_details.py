from .ui_widget import UIWidget


class TrustFileDetails(UIWidget):
    def clear(self):
        self.set_in_database_view("")
        self.set_on_file_system_view("")
        self.set_trust_status("")

    def set_in_database_view(self, text):
        self.get_object("inDatabaseView").get_buffer().set_text(text)

    def set_on_file_system_view(self, text):
        self.get_object("onFileSystemView").get_buffer().set_text(text)

    def set_trust_status(self, text):
        self.get_object("fileTrustStatusView").get_buffer().set_text(text)
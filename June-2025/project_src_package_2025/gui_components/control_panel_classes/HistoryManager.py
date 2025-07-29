from PyQt5.QtWidgets import QComboBox


class HistoryDropDown(QComboBox):

    def __init__(self):
        super().__init__()


"""

    Separated into two buttons.

    GUI components attributed to the history.

    history dropdown

    self.history_dropdown = QComboBox()
    self.history_dropdown.addItem()
    self.history_dropdown.currentIndexChanged.connect()
    self.left_panel.addWidget()

    clear history button


    functions:

    updating the history dropdown visibility:

    self.update_history_dropdown_visibility()
    
    Add this button onto the appropriate widget location.


"""


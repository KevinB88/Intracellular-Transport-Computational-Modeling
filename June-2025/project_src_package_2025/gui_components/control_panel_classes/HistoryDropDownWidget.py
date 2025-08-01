from PyQt5.QtWidgets import QWidget, QComboBox
from project_src_package_2025.gui_components import history_cache


class HistoryDropDownWidget(QWidget):
    #
    # '''
    #     HistoryDropDownWidget will be instantiated in views.py
    #     (The parent class)
    #     This will included onto the main panel established in views.
    #     Example:
    #     self.left_panel.addWidget(self.history_dropdown)
    # '''

    def __init__(self, parent=None):
        super().__init__(parent)

        self.history_dropdown = QComboBox()
        self.history_dropdown.addItem("Select Previous Computation")
        self.history_dropdown.currentIndexChanged.connect(self.load_history_entry)

        # Depends on history_cache
        for label in history_cache.cache.get_labels():
            self.history_dropdown.addItem(label)

    # Single responsibility functionality
    # This method should only load the contents
    # Content visualization, positioning, resulting labels should be implemented into separate functions
    def load_history_entry(self, index):
        if index == 0:
            return  # Ignore placeholder

        # Access the history_cache
        entry = history_cache.cache.get_entry(index - 1)
        if not entry:
            return

        # Setting the computation and parameters
        self.set_computation(entry.comp_type)
        self.set_parameters(entry.params)

        # Displayed onto the output_display
        if entry.mfpt is not None:
            self.output_display.append(
                f"<RESTORED> MFPT : {entry.mfpt:.6f}        [{self.produce_timestamp()}]")
        if entry.duration is not None:
            # self.duration_label.setText(f"Duration: {entry.duration:.6f} seconds")
            self.output_display.append(
                f"<RESTORED> Dimensionless time: {entry.duration:.6f}     [{self.produce_timestamp()}]")

        # Updating the output_files_widget display
        self.output_files_widget.update_display(entry.csv_files or [ ], entry.png_files or [ ])
        self.output_files_widget.show()

        # Displays a label
        self.show_restored_message(entry)

        # Displays the PNG files
        self.png_preview_widget.update_png_list(entry.png_files or [ ])
        self.png_preview_widget.show()

        self.update_history_dropdown_visibility()

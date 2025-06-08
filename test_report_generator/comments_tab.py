from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QGroupBox, QPushButton, QFrame)
from PySide6.QtCore import Qt

class CommentsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 5)

        comments_frame = QFrame()
        comments_frame.setObjectName("sectionFrame")
        comments_layout = QVBoxLayout(comments_frame)
        comments_layout.setContentsMargins(15, 10, 15, 5)

        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Enter notes here...")
        self.notes_text.setToolTip("Enter additional notes")
        self.notes_text.setFixedHeight(150)
        notes_layout.addWidget(self.notes_text)
        comments_layout.addWidget(notes_group)

        recommendations_group = QGroupBox("Remarks")
        recommendations_layout = QVBoxLayout(recommendations_group)
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setPlaceholderText("Enter remarks here...")
        self.recommendations_text.setToolTip("Remarks")
        self.recommendations_text.setFixedHeight(150)
        recommendations_layout.addWidget(self.recommendations_text)
        comments_layout.addWidget(recommendations_group)

        conclusion_group = QGroupBox("Conclusion")
        conclusion_layout = QVBoxLayout(conclusion_group)
        self.conclusion_text = QTextEdit()
        self.conclusion_text.setPlaceholderText("Enter conclusion here...")
        self.conclusion_text.setToolTip("Enter the conclusion")
        self.conclusion_text.setFixedHeight(150)
        conclusion_layout.addWidget(self.conclusion_text)
        comments_layout.addWidget(conclusion_group)

        generate_btn = QPushButton("Generate Report")
        generate_btn.setToolTip("Generate and open the test report")
        generate_btn.clicked.connect(self.parent().generate_report)
        self.parent().animate_button(generate_btn)
        comments_layout.addWidget(generate_btn, alignment=Qt.AlignRight)

        main_layout.addWidget(comments_frame)
        main_layout.addStretch()
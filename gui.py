"""
GUI interface for ImgExecutor.
Browse PNG files, view decoded Python code, and execute them in an embedded terminal.
"""

import sys
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QTextEdit, QLabel, QSplitter, QStatusBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor
from imgexecutor import image_to_python


class ExecutionThread(QThread):
    """Thread for running Python code without blocking the GUI."""
    output_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, image_file: str):
        super().__init__()
        self.image_file = image_file
    
    def run(self):
        try:
            self.output_signal.emit("🔄 Decoding image...\n")
            
            # Decode the image
            from imgexecutor import image_to_python
            from PIL import Image
            from pathlib import Path
            
            image_path = Path(self.image_file)
            image = Image.open(image_path)
            
            # Extract data
            pixels = list(image.getdata())
            data_bytes = bytearray()
            for r, g, b in pixels:
                data_bytes.append(r)
                data_bytes.append(g)
                data_bytes.append(b)
            
            # Trim padding
            original_size_str = image.info.get('original_size', None)
            if original_size_str:
                try:
                    original_size = int(original_size_str)
                    data_bytes = data_bytes[:original_size]
                except ValueError:
                    pass
            else:
                while data_bytes and data_bytes[-1] == 0:
                    data_bytes.pop()
            
            # Decode
            try:
                source_code = data_bytes.decode('utf-8')
            except UnicodeDecodeError:
                source_code = data_bytes.decode('latin-1')
            
            self.output_signal.emit("✓ Decoded successfully!\n\n")
            self.output_signal.emit("--- Python Output ---\n")
            
            # Execute the code
            try:
                exec(source_code, {'__file__': str(image_path)})
                self.output_signal.emit("\n--- Execution completed successfully ---\n")
            except Exception as e:
                self.error_signal.emit(f"\n❌ Execution error: {e}\n")
        
        except Exception as e:
            self.error_signal.emit(f"❌ Error: {e}\n")
        
        finally:
            self.finished_signal.emit()


class ImgExecutorGUI(QMainWindow):
    """Main GUI application for ImgExecutor."""
    
    def __init__(self):
        super().__init__()
        self.current_image = None
        self.execution_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("ImgExecutor - Run Python from Images")
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # File selection layout
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No image selected")
        file_layout.addWidget(self.file_label)
        
        browse_btn = QPushButton("📁 Browse PNG")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        
        main_layout.addLayout(file_layout)
        
        # Code and terminal splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Code display
        code_layout = QVBoxLayout()
        code_label = QLabel("Decoded Python Code:")
        code_label.setFont(QFont("Courier", 10))
        code_layout.addWidget(code_label)
        
        self.code_display = QTextEdit()
        self.code_display.setReadOnly(True)
        self.code_display.setFont(QFont("Courier", 9))
        self.code_display.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        code_layout.addWidget(self.code_display)
        
        code_widget = QWidget()
        code_widget.setLayout(code_layout)
        splitter.addWidget(code_widget)
        
        # Terminal output
        term_layout = QVBoxLayout()
        term_label = QLabel("Terminal Output:")
        term_label.setFont(QFont("Courier", 10))
        term_layout.addWidget(term_label)
        
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont("Courier", 9))
        self.terminal_output.setStyleSheet("background-color: #000000; color: #00ff00;")
        term_layout.addWidget(self.terminal_output)
        
        term_widget = QWidget()
        term_widget.setLayout(term_layout)
        splitter.addWidget(term_widget)
        
        splitter.setSizes([400, 400])
        main_layout.addWidget(splitter)
        
        # Control buttons layout
        control_layout = QHBoxLayout()
        
        run_btn = QPushButton("▶ Run Image as Python")
        run_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; font-weight: bold; padding: 10px; }")
        run_btn.clicked.connect(self.run_image)
        control_layout.addWidget(run_btn)
        
        clear_btn = QPushButton("🗑 Clear Output")
        clear_btn.clicked.connect(self.clear_output)
        control_layout.addWidget(clear_btn)
        
        control_layout.addStretch()
        main_layout.addLayout(control_layout)
        
        # Set central layout
        central_widget.setLayout(main_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def browse_file(self):
        """Open file dialog to select a PNG file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PNG Image",
            str(Path.home() / "Downloads"),
            "PNG Files (*.png);;All Files (*.*)"
        )
        
        if file_path:
            self.current_image = file_path
            self.file_label.setText(f"📄 {Path(file_path).name}")
            self.statusBar().showMessage(f"Loaded: {file_path}")
            self.display_code()
    
    def display_code(self):
        """Decode and display the Python code from the image."""
        if not self.current_image:
            return
        
        try:
            from PIL import Image
            image = Image.open(self.current_image)
            
            # Extract data
            pixels = list(image.getdata())
            data_bytes = bytearray()
            for r, g, b in pixels:
                data_bytes.append(r)
                data_bytes.append(g)
                data_bytes.append(b)
            
            # Trim padding
            original_size_str = image.info.get('original_size', None)
            if original_size_str:
                try:
                    original_size = int(original_size_str)
                    data_bytes = data_bytes[:original_size]
                except ValueError:
                    pass
            else:
                while data_bytes and data_bytes[-1] == 0:
                    data_bytes.pop()
            
            # Decode
            try:
                source_code = data_bytes.decode('utf-8')
            except UnicodeDecodeError:
                source_code = data_bytes.decode('latin-1')
            
            self.code_display.setText(source_code)
            self.statusBar().showMessage(f"Decoded {len(source_code)} characters")
        
        except Exception as e:
            self.code_display.setText(f"Error decoding image: {e}")
            self.statusBar().showMessage(f"Error: {e}")
    
    def run_image(self):
        """Execute the decoded Python code in a thread."""
        if not self.current_image:
            self.terminal_output.setText("❌ No image selected")
            return
        
        # Disable run button while executing
        self.sender().setEnabled(False)
        
        self.terminal_output.clear()
        self.terminal_output.append("🚀 Starting execution...\n")
        
        # Create and start execution thread
        self.execution_thread = ExecutionThread(self.current_image)
        self.execution_thread.output_signal.connect(self.append_output)
        self.execution_thread.error_signal.connect(self.append_error)
        self.execution_thread.finished_signal.connect(self.execution_finished)
        self.execution_thread.start()
    
    def append_output(self, text: str):
        """Append text to terminal output."""
        cursor = self.terminal_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.terminal_output.setTextCursor(cursor)
    
    def append_error(self, text: str):
        """Append error text to terminal output (in red)."""
        self.terminal_output.append(f"<span style='color: #ff4444;'>{text}</span>")
    
    def clear_output(self):
        """Clear the terminal output."""
        self.terminal_output.clear()
    
    def execution_finished(self):
        """Re-enable run button after execution completes."""
        run_btn = self.findChild(QPushButton, "")
        for btn in self.findChildren(QPushButton):
            if "Run" in btn.text():
                btn.setEnabled(True)
                break
        self.statusBar().showMessage("Execution completed")


def main():
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    window = ImgExecutorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

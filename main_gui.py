import sys
import os
import speech_recognition as sr
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QComboBox, QLabel, QTextEdit, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QDragEnterEvent, QDropEvent
import pyttsx3
import pyaudio  # Імпорт для коректної роботи speech_recognition
from uuid import uuid4

class AudioTranscriber(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio to Text Transcriber")
        self.setGeometry(100, 100, 600, 400)
        self.setAcceptDrops(True)
        self.audio_file = None
        self.init_ui()
        self.init_speech_engine()

    def init_ui(self):
        # Основний віджет та лейаут
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Налаштування (мова та тема)
        settings_layout = QHBoxLayout()
        self.language_combo = QComboBox()
        self.language_combo.addItems(["en-US", "uk-UA", "ru-RU"])
        self.language_combo.setToolTip("Select language for transcription")
        settings_layout.addWidget(QLabel("Language:"))
        settings_layout.addWidget(self.language_combo)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        settings_layout.addWidget(QLabel("Theme:"))
        settings_layout.addWidget(self.theme_combo)
        settings_layout.addStretch()
        main_layout.addLayout(settings_layout)

        # Область для drag-and-drop
        self.drop_label = QLabel("Drag & Drop Audio File Here\nor Click to Browse")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px; font-size: 16px;")
        self.drop_label.setMinimumHeight(100)
        self.drop_label.mousePressEvent = self.browse_file
        main_layout.addWidget(self.drop_label)

        # Кнопка обробки
        self.process_button = QPushButton("Process Audio")
        self.process_button.clicked.connect(self.process_audio)
        self.process_button.setEnabled(False)
        main_layout.addWidget(self.process_button)

        # Текстове поле для результату
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        main_layout.addWidget(self.result_text)

    def init_speech_engine(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()

    def change_theme(self, theme):
        if theme == "Dark":
            self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
            self.drop_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px; font-size: 16px; background-color: #3b3b3b; color: #ffffff;")
            self.result_text.setStyleSheet("background-color: #3b3b3b; color: #ffffff;")
        else:
            self.setStyleSheet("")
            self.drop_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px; font-size: 16px;")
            self.result_text.setStyleSheet("")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            self.audio_file = urls[0].toLocalFile()
            self.drop_label.setText(f"Selected File: {os.path.basename(self.audio_file)}")
            self.process_button.setEnabled(True)

    def browse_file(self, event):
        file, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "",
                                             "Audio Files (*.wav *.mp3 *.flac *.ogg)")
        if file:
            self.audio_file = file
            self.drop_label.setText(f"Selected File: {os.path.basename(self.audio_file)}")
            self.process_button.setEnabled(True)

    def process_audio(self):
        if not self.audio_file:
            self.result_text.setText("No audio file selected.")
            return

        self.result_text.setText("Processing...")
        self.process_button.setEnabled(False)
        QApplication.processEvents()

        try:
            with sr.AudioFile(self.audio_file) as source:
                audio = self.recognizer.record(source)
            language = self.language_combo.currentText()
            text = self.recognizer.recognize_google(audio, language=language)
            self.result_text.setText(text)
            # Озвучення результату
            self.tts_engine.say("Transcription complete")
            self.tts_engine.runAndWait()
        except sr.UnknownValueError:
            self.result_text.setText("Could not understand the audio.")
        except sr.RequestError as e:
            self.result_text.setText(f"Error: {str(e)}")
        except Exception as e:
            self.result_text.setText(f"Unexpected error: {str(e)}")
        finally:
            self.process_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioTranscriber()
    window.show()
    sys.exit(app.exec_())
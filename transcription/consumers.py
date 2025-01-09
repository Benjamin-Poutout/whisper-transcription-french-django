"""
consumers logic, loading model
"""

import tempfile
import os
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from pydub import AudioSegment
from transformers import pipeline, AutoProcessor, AutoModelForSpeechSeq2Seq
import torch
import soundfile as sf

# Modèle ASR (chargé au démarrage)
MODEL_ID = "bofenghuang/whisper-large-v3-french"
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
TORCH_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    MODEL_ID, TORCH_DTYPE=TORCH_DTYPE, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(DEVICE)
processor = AutoProcessor.from_pretrained(MODEL_ID)
model_pipeline = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    TORCH_DTYPE=TORCH_DTYPE,
    DEVICE=DEVICE,
)


class TranscriptionConsumer(AsyncWebsocketConsumer):
    """
    A Django Channels WebSocket consumer that handles audio transcription.

    Methods
    -------
    connect():
        Handles the WebSocket connection establishment.
    disconnect(close_code):
        Handles the WebSocket disconnection.
    receive(text_data=None, bytes_data=None):
        Receives audio data, converts it to WAV format, transcribes it, 
        and sends the transcription back to the client.
    convert_webm_to_wav(input_path, output_path):
        Converts an audio file from WebM format to WAV format.
    transcribe_audio(file_path):
        Transcribes the audio file using a pre-trained model.
    """

    async def connect(self):
        """Handles the WebSocket connection establishment."""
        await self.accept()
        logging.info("WebSocket connection established.")
    #pylint: disable=W0613
    #pylint: disable=W0237
    async def disconnect(self, close_code):
        """Handles the WebSocket disconnection."""
        logging.info("WebSocket connection closed.")

    async def receive(self, text_data=None, bytes_data=None):
        """
        Receives audio data, converts it to WAV format, transcribes it,
        and sends the transcription back to the client.

        Parameters
        ----------
        text_data : str, optional
            Text data received from the WebSocket.
        bytes_data : bytes, optional
            Binary data received from the WebSocket.
        """
        if bytes_data:
            # Sauvegarde temporaire des chunks audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
                tmp_file.write(bytes_data)
                tmp_file_path = tmp_file.name

            # Convertir et transcrire
            wav_path = tmp_file_path.replace(".webm", ".wav")
            self.convert_webm_to_wav(tmp_file_path, wav_path)
            transcription = self.transcribe_audio(wav_path)

            # Supprimer les fichiers temporaires
            os.remove(tmp_file_path)
            os.remove(wav_path)

            await self.send(text_data=transcription)

    def convert_webm_to_wav(self, input_path, output_path):
        """
        Converts an audio file from WebM format to WAV format.

        Parameters
        ----------
        input_path : str
            Path to the input WebM file.
        output_path : str
            Path to the output WAV file.
        """
        try:
            audio = AudioSegment.from_file(input_path, format="webm")
            audio = audio.set_frame_rate(16000)
            audio.export(output_path, format="wav")
        #pylint: disable=W0718
        except Exception as e:
            logging.error("Error converting WebM to WAV: %s", e)

    def transcribe_audio(self, file_path):
        """
        Transcribes the audio file using a pre-trained model.

        Parameters
        ----------
        file_path : str
            Path to the audio file to be transcribed.

        Returns
        -------
        str
            The transcription of the audio file.
        """
        try:
            audio_data, sample_rate = sf.read(file_path)
            if sample_rate != 16000:
                raise ValueError(f"Expected sample rate: 16000, but got: {sample_rate}")
            result = model_pipeline(audio_data)
            return result["text"]
        #pylint: disable=W0718
        except Exception as e:
            logging.error("Error during transcription: %s", e)
            return "Error during transcription"

import tempfile
import os
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from pydub import AudioSegment
from transformers import pipeline, AutoProcessor, AutoModelForSpeechSeq2Seq
import torch
import soundfile as sf

# Modèle ASR (chargé au démarrage)
model_id = "bofenghuang/whisper-large-v3-french"
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)
processor = AutoProcessor.from_pretrained(model_id)
model_pipeline = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)

class TranscriptionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        logging.info("WebSocket connection established.")

    async def disconnect(self, close_code):
        logging.info("WebSocket connection closed.")

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # Sauvegarde temporaire des chunks audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
                tmp_file.write(bytes_data)
                tmp_file_path = tmp_file.name
            
            # Convertir et transcrire
            wav_path = tmp_file_path.replace('.webm', '.wav')
            self.convert_webm_to_wav(tmp_file_path, wav_path)
            transcription = self.transcribe_audio(wav_path)

            # Supprimer les fichiers temporaires
            os.remove(tmp_file_path)
            os.remove(wav_path)

            await self.send(text_data=transcription)

    def convert_webm_to_wav(self, input_path, output_path):
        try:
            audio = AudioSegment.from_file(input_path, format="webm")
            audio = audio.set_frame_rate(16000)
            audio.export(output_path, format="wav")
        except Exception as e:
            logging.error(f"Error converting WebM to WAV: {e}")

    def transcribe_audio(self, file_path):
        try:
            audio_data, sample_rate = sf.read(file_path)
            if sample_rate != 16000:
                raise ValueError(f"Expected sample rate: 16000, but got: {sample_rate}")
            result = model_pipeline(audio_data)
            return result["text"]
        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            return "Error during transcription"
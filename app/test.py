import torch
model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                     model='silero_tts',
                                     language='ru',
                                     speaker='baya')
model.save_wav(text="Привет, как дела?", speaker='baya', sample_rate=48000, audio_path='test.wav')
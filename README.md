Morlunk Co. Web Infrastructure
===========

Morlunk.com's Django infrastructure, featuring various modules related to Morlunk Co. as well as APIs for Morlunk Co. products to interface with.

Create a settings.py file out of the settings.py example (settings.py.example) and run syncdb and you should be good to go.

Morlunk Radio Dependencies
===========

Because Morlunk Radio is a rather tricky piece of code, we require a few libraries/programs/tweaks for it to function.
- VLC for YouTube streaming
- espeak for TTS
- A system-wide pulseaudio session
- Python GData library for YouTube data retrieval
- Database must have UTF-8 encoding for foreign titles.
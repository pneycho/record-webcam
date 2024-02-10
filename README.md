# record-webcam
A CLI tool which records video and audio from the webcam and then combines them and stores each separately.
You will use this for only two reasons - 1) You hate OBS Studio. 2) You have to record a short video and you need the AV elements separately for some reaason.

*NOTE:*
  1. You might need to play with the output framerate(fps). Often, the webcam does not ACTUALLY record at the fps they advertise. 
  2. Your antivirus might prevent webcam access for Python. If the number of frames is 0. It will raise an error indicating you pause the antivirus.
---
## Installation

```
# Clone the project
git clone https://github.com/pneycho/record-webcam

# Install the requirements or set up a virtual environment if you prefer.
pip install -r requirements.txt
```
---
## Quickstart

```
# Run it in th terminal
python record_webcam.py <duration_in_seconds> <output_directory>

eg. python record_webcam.py 10 ../output/
```
---


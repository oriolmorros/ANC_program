import numpy as np
import pyaudio
import sys
import wave

#declare variables

record_secs=10

form_1 = pyaudio.paInt16
# Size of each read-in chunk
CHUNK = 1042
# Amount of channels of the live recording
CHANNELS = 1
# Sample width of the live recording
WIDTH = 2
# Sample rate in Hz of the live recording
SAMPLE_RATE = 44100
#PID parameters
KP=0.45484
KI=(1/44100)
k=0
M=[]
E=[]
frames=[]
pa = pyaudio.PyAudio()




stream = pa.open(
    format=pa.get_format_from_width(WIDTH),
    channels=CHANNELS,
    rate=SAMPLE_RATE,
    frames_per_buffer=CHUNK,
    input=True,
    output=True
)

stream2 = pa.open(
    format=pa.get_format_from_width(WIDTH),
    channels=CHANNELS,
    input_device_index=2,
    rate=SAMPLE_RATE,
    frames_per_buffer=CHUNK,
    input=True,

)


print("donne")
M.append(0)
E.append(0)

for i in range(0, int((SAMPLE_RATE/CHUNK)*record_secs)):
    k = k + 1
    
    #read from reference microphone
    reference = stream.read(CHUNK, exception_on_overflow=False)
    # read from error microphone
    error = stream2.read(CHUNK, exception_on_overflow=False)

    #ff controller
    intwave = np.frombuffer(reference, np.int16)
    intwave = np.invert(intwave)*0.6
    intwave = intwave.astype(np.int16)
    ffed = np.frombuffer(intwave, np.byte)

    #fb controller
    intwav = np.fromstring(error, np.int16)
    M.append(intwav)
    intwav = KI*intwav+M[k-1]+KP*(intwav-E[k-1])
    E.append(intwav)
    intwav=intwav.astype(np.int16)
    fbed = np.frombuffer(intwav, np.byte)

    #read the sum on the speakers
    stream.write(ffed+fbed, CHUNK)

stream.stop_stream()
stream.close()

stream2.stop_stream()
stream2.close()

pa.terminate()


wavefile = wave.open('error.wav','wb')
wavefile.setnchannels(CHANNELS)
wavefile.setsampwidth(pa.get_sample_size(form_1))
wavefile.setframerate(SAMPLE_RATE)
wavefile.writeframes(b''.join(frames))
wavefile.close()
print("donne")

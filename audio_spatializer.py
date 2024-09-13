import numpy as np
from scipy.io import wavfile


'''
Adds a spatial characteristic to an input .wav audio file

'''
def spatialize(input_path : str, output_path : str, span : int):
    if span < -100:
        print("Requested left channel span too large")
    if span > 100:
        print("Request right channel span too large")
    
    sample_rate, data = wavfile.read(input_path)
    audio_data = np.array(data, dtype=np.float32)

    if data.dtype == np.int16:
        audio_data = audio_data / 32768.0  # 16-bit audio normalization
    elif data.dtype == np.int32:
        audio_data = audio_data / 2147483648.0  # 32-bit audio normalization
    elif data.dtype == np.uint8:
        audio_data = (audio_data - 128) / 128.0  # 8-bit audio normalization

    sample_T = 1 / sample_rate # Period of sample (in s)

    time_delay = 0.0003 # Time delay to imitate audio traveling from one ear to the other
    sample_shift = int(time_delay / sample_T) # Number of samples we have to shift by

    # TO DO: Accomodate requests that fall between the span extremes

    if span != 100 and span != -100:
        goofy_rate, goofy_data = wavfile.read("beep-02.wav")
        goofy_data = np.array(goofy_data, dtype=np.float32)
        wavfile.write(output_path, goofy_rate, np.vstack((goofy_data, goofy_data)).transpose())
        return
    # Output should sound as though it is coming from the right 
    if span == 100:
        left_channel_padded = np.array([0. for _ in range(sample_shift)] + [audio_data[i] for i in range(len(audio_data))], dtype=np.float32)
        left_channel_padded = left_channel_padded * 0.66
        right_channel_padded = np.array([audio_data[i] for i in range(len(audio_data))] + [0. for _ in range(sample_shift)], dtype=np.float32)
    # Output should sound as though it is coming from the left
    else:
        right_channel_padded = np.array([0. for _ in range(sample_shift)] + [audio_data[i] for i in range(len(audio_data))], dtype=np.float32)
        right_channel_padded = right_channel_padded * 0.66
        left_channel_padded = np.array([audio_data[i] for i in range(len(audio_data))] + [0. for _ in range(sample_shift)], dtype=np.float32)
    
    tone_y_stereo=np.vstack((left_channel_padded, right_channel_padded))
    tone_y_stereo=tone_y_stereo.transpose()
    wavfile.write(output_path, sample_rate, tone_y_stereo)

spatialize("drum.wav", "output.wav", 100)
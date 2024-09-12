import numpy as np
from scipy.io import wavfile

# Step 1: Read the mono .wav file
sample_rate, data = wavfile.read('example.wav')

# Step 2: Check the sample rate and the shape of the data
print(f"Sample Rate: {sample_rate} Hz")
print(f"Shape of data: {data.shape}")

# Step 3: If the file is mono, the shape should be (n_samples,)
# Convert the audio data to a NumPy array
audio_data = np.array(data, dtype=np.float32)

# Step 4: Normalize the data if necessary (optional)
# Convert the data from its original format (e.g., int16) to a floating-point range between -1 and 1
if data.dtype == np.int16:
    audio_data = audio_data / 32768.0  # 16-bit audio normalization
elif data.dtype == np.int32:
    audio_data = audio_data / 2147483648.0  # 32-bit audio normalization
elif data.dtype == np.uint8:
    audio_data = (audio_data - 128) / 128.0  # 8-bit audio normalization

# Step 5: Print or inspect the resulting NumPy array
print(audio_data[:10])  # Print the first 10 samples for inspection

sample_T = 1 / sample_rate # Period of sample (in s)

time_delay = 0.0003 # Time delay to imitate audio traveling from one ear to the other
sample_shift = int(time_delay / sample_T) # Number of samples we have to shift by


#print(sample_T)
#print(sample_shift)

left_channel = audio_data

#print(len(left_channel))

nil_channel = np.array([0. for _ in range(len(left_channel))], dtype=np.float32)

right_channel = np.array([0. if i < len(left_channel) // 2 else left_channel[i] for i in range(len(left_channel))], dtype=np.float32)
right_channel_padded = np.array([0. for _ in range(sample_shift)] + [left_channel[i] for i in range(len(left_channel))], dtype=np.float32)
#left_channel = np.array(left_channel + [0. for _ in range(sample_shift)])

right_channel_diminished = right_channel_padded / 2

#print(right_channel_padded[:20])

#left_channel_padded = np.append(left_channel, [0. for _ in range(sample_shift)])

left_channel_padded = np.array([left_channel[i] for i in range(len(left_channel))] + [0. for _ in range(sample_shift)], dtype=np.float32)

print(f"Length of left channel : {len(left_channel_padded)}; length of right channel : {len(right_channel_padded)}")


# A 2D array where the left and right tones are contained in their respective rows
tone_y_stereo=np.vstack((left_channel_padded, right_channel_padded))

# Reshape 2D array so that the left and right tones are contained in their respective columns
tone_y_stereo=tone_y_stereo.transpose()

# Produce an audio file that contains stereo sound
wavfile.write('spatialAudio.wav', sample_rate, tone_y_stereo)

tone_y_stereo=np.vstack((left_channel_padded, right_channel_diminished))
tone_y_stereo=tone_y_stereo.transpose()
wavfile.write('diminishedAudio.wav', sample_rate, tone_y_stereo)


tone_y_stereo=np.vstack((left_channel, left_channel))
tone_y_stereo=tone_y_stereo.transpose()
wavfile.write('defaultAudio.wav', sample_rate, tone_y_stereo)

tone_y_stereo=np.vstack((left_channel, nil_channel))
tone_y_stereo=tone_y_stereo.transpose()
wavfile.write('justLeftAudio.wav', sample_rate, tone_y_stereo)



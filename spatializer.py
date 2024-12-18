import numpy as np
from scipy.io import wavfile
import math

# =======================================
# Constants
# =======================================

t_per_sample = 0.00002267573

sample_T = 1 / 44100 # Period of sample (in s)

# =======================================
# Parameters to tune for audio processing
# =======================================

g = 0.6 # Amplitude multiplier

# We use cartesian coordinates to model the motion of a point audio source
# around a listener centered around the origin

# The left ear is located at (-10, 0), the right ear at (10, 0)

left_ear_pos = np.array([-10, 0])
right_ear_pos = np.array([10, 0])

class RingBuf:
    # Constructor (initializer)
    def __init__(self):
        self.buf = [0. for _ in range(14)]
        self.l_ptr = 0
        self.r_ptr = 0
        self.w_ptr = 0

    def write(self, val : float, span):
        self.buf[self.w_ptr] = val
        left_sample_shift = 0
        right_sample_shift = 0
        if span >= 50:
            left_sample_shift = int(0.0003 * ((span - 50) / 50) / sample_T)
            self.r_ptr = (self.w_ptr) % len(self.buf)
            self.l_ptr = (self.w_ptr - left_sample_shift) % len(self.buf)
        else:
            right_sample_shift = int(0.0003 * ((50 - span) / 50) / sample_T)
            self.l_ptr = (self.w_ptr) % len(self.buf)
            self.r_ptr = (self.w_ptr - right_sample_shift) % len(self.buf)
        self.w_ptr = (self.w_ptr + 1) % len(self.buf)

    
    def read(self):
        #span = get_span_from_point(pos)
        return (self.buf[self.l_ptr], self.buf[self.r_ptr])
    
    def get_read_ptrs(self):
        return ((self.w_ptr - self.l_ptr) % len(self.buf), (self.w_ptr - self.r_ptr) % len(self.buf))


def get_span_from_point(point : np.ndarray):
    point = np.array(point)
    #dist = np.linalg.norm(left_ear_pos - point)
    r_dist = np.linalg.norm(right_ear_pos - point)
    l_dist = np.linalg.norm(left_ear_pos - point)

    diff = abs(r_dist - l_dist)
    diff = min(diff, 20)

    if r_dist <= l_dist:
        span = 50 + 50 * (diff / 20)
    else:
        span = 50 - (50 * (diff / 20))
    
    return span


def low_pass_divisor(theta):
    #print(theta)
    assert 0 <= theta <= math.pi 
    if 0 <= theta <= math.pi / 2:
        right = 1
        slope = (16 - 1) / (math.pi / 2)
        left = 1 + slope * -(theta - math.pi / 2)
    elif math.pi / 2 < theta <= math.pi:
        slope = (16 - 1) / (math.pi / 2)
        right = 1 + slope * (theta - math.pi / 2)
        left = 1

    #if theta == math.pi / 2:
    #    print(f"(left, right) {left}, {right}")
    return left, right


#=== Models particle traveling with circular motion around listener with a period of 4 seconds 
def circular_orbit(t):
    return (-10 * np.sin(2 * np.pi * t / 4), 10 * np.cos(2 * np.pi * t / 4))

def lorenz_orbit(t):
    return (0,0)


def spatialize_over_time(input_path : str, output_path : str, f):
    sample_rate, data = wavfile.read(input_path)
    audio_data = np.array(data, dtype=np.float32)

    if data.dtype == np.int16:
        audio_data = audio_data / 32768.0  # 16-bit audio normalization
    elif data.dtype == np.int32:
        audio_data = audio_data / 2147483648.0  # 32-bit audio normalization
    elif data.dtype == np.uint8:
        audio_data = (audio_data - 128) / 128.0  # 8-bit audio normalization

    sample_T = 1 / sample_rate # Period of sample (in s)

    # -100 = 0.0003
    # 0 = 0
    # 100 = 0.0003

    #print(audio_data.shape)

    # Known Issue: Sometimes audio data will duplicate samples into two columns

    if(len(audio_data.shape) > 1):
        print("whoopsy daisy")
        audio_data = audio_data[:, 0:1]
        audio_data = audio_data.flatten()

    channel_buf = RingBuf()
    #left = [0 for _ in range(13 + len(audio_data))]
    #right = [0 for _ in range(13 + len(audio_data))]
    left = []
    right = []

    left_filtered = []
    right_filtered = []

    dt = sample_T

    for i in range(len(audio_data)):
        #pos = pos_lst[i]
        pos = f(i * dt)
        span = get_span_from_point(pos)
        right_span = span
        left_span = 100 - span

        point = np.array(pos)
        r_dist = np.linalg.norm(right_ear_pos - point)
        l_dist = np.linalg.norm(left_ear_pos - point)
        #print(point)
        #return

        theta = math.atan2(pos[1], pos[0])

        # Find theta for vector reflected across x-axis if theta > pi (logic is equivalent)
        if theta < 0:
            theta = -theta

        channel_buf.write(audio_data[i], span)
        l, r = channel_buf.read()

        if span >= 50:
            r_ptr = i
            l_ptr = i + int(0.0003 * ((span - 50) / 50) / sample_T)
        else:
            l_ptr = i
            r_ptr = i + int(0.0003 * ((50 - span) / 50) / sample_T)
        

        left_amp_mult = (1 - l_dist / 20)
        right_amp_mult = (1 - r_dist / 20)


        left.append(float(l * left_amp_mult))
        right.append(float(r * right_amp_mult))

        left_divisor, right_divisor = low_pass_divisor(theta)


        if i == 0:
            left_filtered.append(left[i])
            right_filtered.append(right[i])
        elif i > 0:
            left_filtered_sample = left_filtered[-1] + ((left[i] - left_filtered[-1]) / left_divisor)
            left_filtered.append(left_filtered_sample)
            right_filtered_sample = right_filtered[-1] + ((right[i] - right_filtered[-1]) / right_divisor)
            right_filtered.append(right_filtered_sample)    

    left_channel = np.array(left_filtered, dtype=np.float32)
    right_channel = np.array(right_filtered, dtype=np.float32)


    assert len(left_channel) == len(right_channel)

    tone_y_stereo=np.vstack((left_channel, right_channel))
    tone_y_stereo=tone_y_stereo.transpose()
    wavfile.write(output_path, 44100, tone_y_stereo)

#spatialize_over_time("shorter_guitar.wav", "guitar_parametrized_function.wav", circular_orbit)
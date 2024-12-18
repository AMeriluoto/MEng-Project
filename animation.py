import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

plt.rcParams['animation.ffmpeg_path'] = r'C:\FFmpeg\bin\ffmpeg.exe' 
# Replace '/path/to/ffmpeg' with the actual path to your FFmpeg executable.

# Parameters
sampling_frequency = 44100  # Hz
fps = 30  # Frames per second for display purposes
time_per_frame = 1 / fps  # Time per frame in seconds
time_per_sample = 1 / sampling_frequency  # Time per sample in seconds
samples_per_frame = int(time_per_frame / time_per_sample)  # Number of samples per frame

# Generate a set of 3D points
# Simulate a trajectory
t = np.linspace(0, 2 * np.pi, 44100)  # Time points for one second of data
#x = np.sin(t)
#y = np.cos(t)
#z = np.sin(2 * t)
#points = np.column_stack((x, y, z))  # Nx3 array of points

# Initialize the figure and axes
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
dot, = ax.plot([], [], [], 'o', color='red')  # The moving dot

# Set the limits of the axes
ax.set_xlim(-20, 20)
ax.set_ylim(-20, 20)
ax.set_zlim(-1.5, 1.5)

# Animation update function
def update(frame):
    # Calculate the range of points for the current frame
    start_idx = frame * samples_per_frame
    end_idx = start_idx + samples_per_frame
    #if end_idx >= len(points):
    #    end_idx = len(points) - 1

    # Get the position of the dot for the current frame
    current_point = points[end_idx]
    print(current_point)

    # Update the position of the dot
    dot.set_data(current_point[0], current_point[1])
    dot.set_3d_properties(0)
    return dot,

sample_rate, data = wavfile.read("mid_tone.wav")
audio_data = np.array(data, dtype=np.float32)

# Create the animation
num_frames = len(data) // samples_per_frame
ani = FuncAnimation(fig, update, frames=num_frames, interval=1000 / fps, blit=True)
ani.save("dot_animation.mp4", writer="ffmpeg", fps=fps)
plt.show()


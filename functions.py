import numpy as np
import imageio 
import os
from qutip import *
from PIL import Image
from moviepy import ImageSequenceClip

#--------------------------------------------------------------------------------------------------
#Defining pulses:
#--------------------------------------------------------------------------------------------------

def rotation_H(x, y, z):
    """
    Define a hamiltonian that produxes a rotation around the given axes x, y, z.
    (input: pulse in radians)
    """
    H1 = 1/2 * x * sigmax()
    H2 = 1/2 * y * sigmay()
    H3 = 1/2 * z * sigmaz()
    H = QobjEvo(H1 + H2 + H3, tlist=None, args=None)
    return H

#--------------------------------------------------------------------------------------------------

def pulse_states(x, y, z, init, duration, resolution=20):
    """
    Define a pulse that produces a rotation around the given axes x, y, z for the given duration.
    (input: pulse in radians)
    """
    H = rotation_H(x, y, z)
    times = np.linspace(0, duration, resolution)  
    result = mesolve(H, init, times)
    return result.states

#--------------------------------------------------------------------------------------------------

def generate_pulses(list_of_pulses, init, duration, resolution=20):
    """
    Generates a list of states for each pulse in the list of pulses.
    """
    states = []
    for pulse in list_of_pulses:
        if states == []:
            states += (pulse_states(pulse[0]/duration, 
                                       pulse[1]/duration, 
                                       pulse[2]/duration, 
                                       init, duration, resolution))
        else:
            states += (pulse_states(pulse[0]/duration, 
                                       pulse[1]/duration, 
                                       pulse[2]/duration, 
                                       states[-1], duration, resolution))
    return states

#--------------------------------------------------------------------------------------------------
#Plotting functions:
#--------------------------------------------------------------------------------------------------

def add_points(sphere, states, color='b', marker='o', size=5):
    """
    Adds points to a Bloch sphere for each state in the list of states.
    """
    points = []
    for state in states:
        points.append([expect(sigmax(),state),expect(sigmay(),state),expect(sigmaz(),state)])
        #gets the coodinates individually, maybe there is a beter way but... it works
    for point in points:
        sphere.add_points(point)
    
    # * fix later: last call of the funct. sets the color, marker and size for all points
    sphere.point_color = [color]
    sphere.point_marker = [marker]
    sphere.point_size = [size]

#-------------------------------------------------------------------------------------------------

def save_frames(states, sphere):
    """
    Saves single frame of the Bloch sphere for each state in the list of states.
    """
    if not os.path.exists("frames"):
            os.makedirs("frames")
            
    i = 0
    for state in states:
        sphere.add_states(state)
        sphere.render()
        #sphere.fig.savefig(f"frames/frame_{i}.png", dpi=300, transparent=True)
        sphere.fig.savefig(f"frames/frame_{i}.png")
        i += 1
        #looks prettier with str(states.index(state)) but for some reason it skips some numbers?

        #clear sphere for next frame
        sphere.clear()
        add_points(sphere, states[:i])  # Add points for all previous states

#-------------------------------------------------------------------------------------------------

def make_video(states, sphere, filename="bloch.mp4", fps=10):

    save_frames(states, sphere)

    image_files = [f"frames/frame_{i}.png" for i in range(len(states))]
    clip = ImageSequenceClip(image_files, fps=fps)

    clip.write_videofile(filename, codec='libx264', bitrate="3000k")

    print("Video saved as", filename)

    for file in os.listdir("frames"):
        os.remove("frames/" + file)

#-------------------------------------------------------------------------------------------------

def make_gif(states, sphere, filename = "bloch.gif", duration=0.1):
    """
    Creates a gif from the list of states and saves it to the specified filename.
    """
    save_frames(states, sphere)

    images = []
    for i in range(len(states)):
        try:
            images.append(imageio.imread("frames/frame_" + str(i) + ".png"))
        except:
            print("Image frame_" + str(i) + ".png not found")
            
    imageio.mimsave(filename, images)
    print("Gif saved as " + filename)

    #delete everything from frames folder
    for file in os.listdir("frames"):
        os.remove("frames/" + file)

#-------------------------------------------------------------------------------------------------

def make_gif_pillow(states, sphere, filename="bloch.gif", duration=100):
    """
    Creates a GIF using Pillow that retains all frames and applies consistent timing.
    """
    save_frames(states, sphere)

    frames = []
    frame_paths = [f"frames/frame_{i}.png" for i in range(len(states))]

    for path in frame_paths:
        img = Image.open(path).convert("RGBA")
        frames.append(img)

    frames[0].save(
        filename,
        save_all=True,
        append_images=frames[1:],
        optimize=False,  #remove frame optimization
        duration=duration,
        loop=0
    )

    print("GIF saved as", filename)

    for file in os.listdir("frames"):
        os.remove("frames/" + file)

#-------------------------------------------------------------------------------------------------

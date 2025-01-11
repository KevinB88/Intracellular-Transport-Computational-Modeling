
# auxiliary print functions
import sys
from datetime import datetime


# Last updated on 9/13/24, 2:22 PM

def convert_bytes(num_bytes):
    units = ["bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "RB", "QB"]
    factor = 1024.0
    for unit in units:
        if num_bytes < factor:
            return f"{num_bytes:.2f}{unit}"
        num_bytes /= factor
    return f"{num_bytes:.2f} QB"


def pr_quantities(rings, rays, r, d, t, d_radius, d_theta, d_time, time_steps, phi_center, a, b, v, tube_placements):
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f'Current date of operation: {current_time}')
    print(f'Radial Curves: {rings}')
    print(f'Angular Rays: {rays}')
    print(f'Domain Radius: {r}')
    print(f'Diffusion Coefficient: {d}')
    print(f'Run Time: {t}')
    print(f'Delta Radius: {d_radius}')
    print(f'Delta Theta: {d_theta}')
    print(f'Delta Time: {d_time}')
    print(f'Time steps: {time_steps}')
    print(f'Initial Central Density: {phi_center}')
    print(f'a : {a}')
    print(f'b : {b}')
    print(f'Velocity: {v}')
    print(f'Microtubule placements: {tube_placements}')

    float_value = 0.0
    memory_size = sys.getsizeof(float_value)
    print(f'Volume of container: {convert_bytes(rings * rays * time_steps * memory_size)} (approximately)')
    print('(This will be the volume of the container after being completely filled with floating point values)')

    info_dict = {
        "Radial Curves": rings,
        "Angular Rays": rays,
        "Domain Radius": r,
        "Diffusion Coefficient": d,
        "Run Time": t,
        "Delta Radius": d_radius,
        "Delta Theta": d_theta,
        "Delta Time": d_time,
        "Time steps": time_steps,
        "Initial Central Density": phi_center,
        "a": a,
        "b": b,
        "Velocity": v,
        "Microtubule placements: ": tube_placements
    }
    return info_dict


def pr_progress(c, o):
    percent = (c / o) * 100
    print(f"\rProgress: {int(percent+1)}%", end='', flush=True)


def convert_time(seconds):
    if seconds < 60:
        if seconds == 1:
            return '1 second'
        return f'{seconds:.4f} seconds'
    elif seconds >= 60 ** 2:
        output = seconds / (60 ** 2)
        if output == 1:
            return '1 hour'
        else:
            return f'{output:.4f} hours'
    elif seconds >= 60:
        output = seconds / 60
        if output == 1:
            return '1 minute'
        else:
            return f'{output:.4f} minutes'





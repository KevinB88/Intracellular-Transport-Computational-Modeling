from . import np


def initialize_layers(rings, rays):
    diffusive_layer = np.zeros((2, rings, rays), dtype=np.float64)
    advective_layer = np.zeros((2, rings, rays), dtype=np.float64)
    return diffusive_layer, advective_layer

from pathlib import Path
import os
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None # alright careful with this lol
import torch
import torchvision.transforms as transforms


# TOWN-SPECIFIC MAP SETTINGS
SCALE = 1.0
PIXELS_PER_METER = 12.0
WORLD_OFFSET = {
    'Town01': (-52.059906005859375, -52.04996085166931),
    'Town02': (-57.45972919464111, 55.3907470703125),
    'Town03': (-199.0638427734375, -259.27125549316406),
    'Town04': (-565.26904296875, -446.1461181640625),
    'Town05': (-326.0445251464844, -257.8750915527344)
}

FILE_DIR = Path(__file__).parent.absolute()
MAP_IMAGE_PATHS = {
    'Town01': os.path.join(FILE_DIR, 'Town01.png'),
    'Town02': os.path.join(FILE_DIR, 'Town02.png'),
    'Town03': os.path.join(FILE_DIR, 'Town03.png'),
    'Town04': os.path.join(FILE_DIR, 'Town04.png'),
    'Town05': os.path.join(FILE_DIR, 'Town05.png')
}


class CarlaMapViz:
    def __init__(self, town='Town01'):
        self.town = town
        map_image_path = MAP_IMAGE_PATHS[self.town]
        self.map_image = transforms.functional.pil_to_tensor(Image.open(map_image_path))
        # self.map_image_pil = Image.open(map_image_path)

    def get_image_from_world(self, location, yaw, radius):
        location = self.world_to_pixel(location)
        radius = self.world_to_pixel_length(radius)

        # rotated_image = self.map_image_pil.rotate(np.degrees(yaw), center=tuple(location))
        # cropped_image = rotated_image.crop((location[0]-radius,location[1]-radius,location[0]+radius,location[1]+radius))
        # cropped_image = transforms.functional.pil_to_tensor(cropped_image)

        # crop before rotate is faster than just rotate because image is huge
        image = transforms.functional.crop(self.map_image.clone(), int(location[1]-(radius*1.5)), int(location[0]-(radius*1.5)), 3*radius, 3*radius)
        image = transforms.functional.rotate(image, np.degrees(yaw.item()))
        image = transforms.functional.center_crop(image, 2*radius)

        return image

    def world_to_pixel(self, location):
        x = SCALE * PIXELS_PER_METER * (location[0] - WORLD_OFFSET[self.town][0])
        y = SCALE * PIXELS_PER_METER * (location[1] - WORLD_OFFSET[self.town][1])
        return np.array([int(x), int(y)])

    def pixel_to_world(self, location):
        x = location[0] + WORLD_OFFSET[self.town][0] / SCALE / PIXELS_PER_METER
        y = location[1] + WORLD_OFFSET[self.town][1] / SCALE / PIXELS_PER_METER
        return np.array([x,y])

    def world_to_pixel_length(self, length):
        return int(SCALE * PIXELS_PER_METER * length)

    def pixel_to_world_length(self, length):
        return length / SCALE / PIXELS_PER_METER


if __name__ == '__main__':
    viz = CarlaMapViz()
    image = viz.get_image_from_world([0,0], 0, 50)
    image.show()

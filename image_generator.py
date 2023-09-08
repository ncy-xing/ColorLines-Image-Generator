from PIL import Image, ImageColor
import PIL
import numpy as np
import os.path

class ImageGenerator():
    def __init__(self, color_matrix=None):
        self.color_matrix = color_matrix
        self.colors = list(color_matrix.keys())

    def generate_image(self, filename, height=100, width=100, start_pixel="#000000"):
        '''
        Generates an image given a filename, dimensions, and transition matrix of RBG values probability of the following colors.
        '''
        image = Image.new(mode="RGB", size=(width, height))
        pixel_map = image.load()
        current_pixel = start_pixel

        for w in range(width):
            for h in range(height):
                next_pixel = self.get_next_pixel(current_pixel)
                # Convert hex to RGB and add as a pixel to the image
                pixel_map[w, h] = ImageColor.getcolor(next_pixel, "RGB")
                current_pixel = next_pixel
        
        image.save(os.path.join("output", filename), format="png")
    
    def get_next_pixel(self, current_pixel):
        '''
        Given a pixel, generates the following pixel color using the matrix probabilities. 
        '''
        probabilities = []
        for next_color in self.colors:
            if self.color_matrix[current_pixel].get(next_color):
                probabilities.append(self.color_matrix[current_pixel][next_color])
            else:
                probabilities.append(0)
        # probabilities = [self.color_matrix[current_pixel][next_color] for next_color in self.colors]
        return np.random.choice(
            self.colors, p=probabilities
            )

def generate_matrix(filename):
    '''
    Given the filename of an image, reduces the number of colors in image and converts into a transition matrix. 
    '''
    image = Image.open(os.path.join("input", filename))
    # Reduce the amount of colors in matrix
    image = image.quantize(colors=50).convert('RGB')

    width, height = image.size
    matrix = {}
    current_hex = '#%02x%02x%02x' % image.getpixel((0, 0))

    # Get counts of every color
    for w in range(1, width):
        for h in range(1, height):
            r, g, b = image.getpixel((w, h))
            next_hex = '#%02x%02x%02x' % (r, g, b)

            if matrix.get(current_hex):
            # Update if current color exists
                if matrix[current_hex].get(next_hex):
                    matrix[current_hex][next_hex] += 1
                else:
                    matrix[current_hex].update({next_hex : 1})
            # Add new color as key to matrix
            else:
                matrix.update({current_hex : {next_hex : 1}})

            current_hex = next_hex

    # Convert next color counts into probabilities 
    for hex, counts in matrix.items():
        total_counts = sum(counts.values())
        for next_color, c in counts.items():
            matrix[hex].update({next_color : c / total_counts})

    return matrix

if __name__ == "__main__":

    matrix = generate_matrix("grumbot.png")
    gen = ImageGenerator(color_matrix=matrix)
    # Set a random starting color
    starting_color = np.random.choice(list(matrix.keys()))
    gen.generate_image("grumbot-test.png", 100, 100, starting_color)

    # Matrix format
    # matrix = {
    #     "000000" : {"000000" : 0.7, "FFFFFF" : 0.2, "FF00FF" : 0.1},
    #     "FFFFFF" : {"000000" : 0.7, "FFFFFF" : 0.2, "FF00FF" : 0.1},
    #     "FF00FF" : {"000000" : 0.7, "FFFFFF" : 0.2, "FF00FF" : 0.1}
    # }


from PIL import Image, ImageColor
import PIL
import numpy as np
import os.path



class ImageGenerator():

    def __init__(self, filename=None):
        self.filename = filename
        self.image = Image.open(os.path.join("input", self.filename))
        self.width, self.height = self.image.size
        self.color_matrix = self.generate_matrix()
        self.colors = list(self.color_matrix.keys())

    def generate_image(self):
        '''
        Generates an image given a filename, dimensions, and transition matrix of RBG values probability of the following colors.
        '''
        starting_color = np.random.choice(list(self.color_matrix.keys()))

        image = Image.new(mode="RGB", size=(self.width, self.height))
        pixel_map = image.load()
        bw_map = self.image.convert('1', dither=Image.NONE).load()
        lesser_color = self.lesser_color(bw_map)
        current_pixel = starting_color

        # Generate colors from matrix
        for w in range(image.width):
            next_pixel = self.get_next_pixel(current_pixel)
            # Convert hex to RGB and add as a pixel to the image
            next_color = ImageColor.getcolor(next_pixel, "RGB")    
            for h in range(image.height):
                if bw_map[w,h] == lesser_color:
                    pixel_map[w, h] = (255, 255, 255)
                else:
                    pixel_map[w, h] = next_color
                current_pixel = next_pixel
        
        # Apply white dither
        image.save(os.path.join("output", "generated_" + self.filename), format="png")
    
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

    def generate_matrix(self):
        '''
        Given the filename of an image, reduces the number of colors in image and converts into a transition matrix. 
        '''
        
        # Reduce the amount of colors in matrix
        reduced_image = self.image.quantize(colors=50).convert('RGB')

        matrix = {}
        current_hex = '#%02x%02x%02x' % reduced_image.getpixel((0, 0))

        # Get counts of every color
        for w in range(1, self.width):
            for h in range(1, self.height):
                r, g, b = reduced_image.getpixel((w, h))
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
    
    def lesser_color(self, bw_map):
        white_count = 0
        for w in range(self.image.width):
            for h in range(self.image.height):
                if bw_map[w, h] == 255:
                    white_count += 1
        return 255 if white_count <= (self.image.height * self.image.width) / 2 else 0

if __name__ == "__main__":
    
    print("Generating images...")
    for filename in os.listdir("input"):
        if os.path.splitext(filename)[1] in [".jpg", ".png", ".JPG", ".PNG"]:
            gen = ImageGenerator(filename)
            gen.generate_image()
    print("Image generation complete.")

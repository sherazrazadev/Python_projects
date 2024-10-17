import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Function to capture clicks and get coordinates
def onclick(event):
    global coords
    # Check if 4 points are already captured
    if len(coords) < 4:
        x, y = event.xdata, event.ydata
        coords.append((x, y))
        print(f"Point {len(coords)}: ({x:.2f}, {y:.2f})")
        # Mark the point on the image
        plt.plot(x, y, 'ro')
        plt.draw()

        # If we have captured 4 points, disconnect the event
        if len(coords) == 4:
            plt.gcf().canvas.mpl_disconnect(cid)
            plt.close()

# Image path input
image_path = "2.jpg"

# Load and display the image
img = mpimg.imread(image_path)
plt.imshow(img)
plt.title('Click to select 4 points')

# Initialize a list to store coordinates
coords = []

# Connect the click event to the onclick function
cid = plt.gcf().canvas.mpl_connect('button_press_event', onclick)

# Show the image and wait for clicks
plt.show()

# Print the captured coordinates
print("Captured Coordinates:")
for i, coord in enumerate(coords, start=1):
    print(f"Point {i}: {coord}")

import pygame
import math
import sys

vectors = []
filename = 'output.txt'

# Read from the text file
with open(filename, 'r') as file:
    for line in file:
        # Split each line into parts, convert to integers, and add as a tuple to the list
        parts = line.strip().split()
        vectors.append((float(parts[0]), float(parts[1])))


#vectors = [(7.2772, 13.6451), (-13.9084, -1.7512), (-5.0869, 16.3309), (-11.7979, -3.6206), (-17.6697, -4.3589), (-0.9162, -4.5217), (-3.1566, -10.3254), (-0.8754, -7.5877), (9.0232, 5.0451), (3.475, -5.9641), (2.4576, 15.243), (-2.3636, 6.623), (-13.1967, 1.5876), (9.1522, 9.4259), (-24.6393, -2.7501), (1.4226, 3.28), (-1.121, -3.2547), (-4.8342, -10.173), (-1.8799, 21.5382), (7.0181, -12.4367), (-8.7996, -1.7844), (11.552, 30.058), (-8.6258, -1.2038), (-20.4885, 7.628), (16.9342, 9.4306), (-46.7804, 9.8435), (39.9425, 0.2306), (-60.3412, -13.4341), (67.2215, 23.4871), (-16.0712, 48.6034), (-23.4232, 13.4289), (-41.0541, 77.6105), (-27.6493, 49.1955), (-142.5409, -9.2976), (-139.0786, 6.377), (1.9059, -115.8902), (-136.3605, -123.0095), (113.554, -1.4793), (-178.3022, -211.0675), (388.9479, 38.2053), (-232.2855, -61.6152), (89.3318, 140.9238), (112.5342, -142.7107), (-48.4444, -210.5927), (314.9326, 666.004), (-235.5584, 277.4166), (-818.0671, -925.8307), (377.7691, 1095.7279), (2109.8041, 633.4393), (13291.9224, -463.036), (0, 0), (1087.4871, 2334.3749), (848.5668, 2281.3068), (-982.0751, -651.612), (4.8855, 301.5443), (281.477, 688.8087), (-493.894, -384.9499), (-26.8724, -1.635), (276.7455, 233.8254), (-12.902, -160.8482), (-77.0205, 352.957), (57.3221, 16.9443), (-112.4083, 141.4367), (-131.3489, 81.9729), (-175.0252, -4.4085), (-28.6402, -81.9898), (-55.0321, -43.6967), (-46.9419, -45.2387), (54.6957, -45.6999), (-5.2952, -19.5096), (28.6959, -14.1242), (-13.6036, 66.2251), (20.1226, -79.8473), (-27.954, 49.7816), (38.9089, -9.1874), (-25.5839, -8.5286), (23.9517, 7.7374), (5.028, 7.8691), (4.0274, 20.0604), (3.9491, 8.4524), (-21.0283, 12.2079), (20.3692, 18.7491), (-32.8898, 13.811), (-6.0215, -6.196), (-16.1574, 20.3613), (-0.6815, -18.88), (-24.3441, 4.3459), (11.7061, -4.4452), (-3.0195, -13.1962), (7.2697, 14.6649), (1.9793, 2.2758), (-4.5217, 9.9531), (1.2498, 13.8049), (-20.2719, 5.2795), (-7.4513, 2.1815), (-10.2804, -0.0864), (-7.8938, -13.1798), (0.5032, 6.553), (4.2472, -9.4946), (-3.2308, 5.9817), (7.2772, 13.6451)]

base_angle_vectors = []
last_angle_vectors = []
for vector in vectors:
    base_angle_vectors.append(0)
    last_angle_vectors.append(0)

# Initialize pygame
pygame.init()
zoom_sensitivity = 0.2
# Get fullscreen display mode
infoObject = pygame.display.Info()
width, height = infoObject.current_w, infoObject.current_h # 1920, 1080
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
unit = 10000  # 1000 milliseconds
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Initial scale and origin offset
scale = 100  # Pixels per unit
origin_x, origin_y = width // 2, height // 2

# Arrowhead size as a percentage of the vector length
arrowhead_percentage = 0.15

# Function to draw an arrow
def draw_arrow(screen, start, end, color, thickness=2):
    pygame.draw.line(screen, color, start, end, thickness)
    rotation = math.atan2(end[1]-start[1], end[0]-start[0])
    arrowhead_length = arrowhead_percentage * math.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
    arrow_angle = math.pi / 6
    for direction in (1, -1):
        dx = arrowhead_length * math.cos(rotation + direction * arrow_angle)
        dy = arrowhead_length * math.sin(rotation + direction * arrow_angle)
        pygame.draw.line(screen, color, end, (end[0]-dx, end[1]-dy), thickness)

# Function to rotate a vector
def rotate_vector(vector, angle):
    """Rotate a vector by a given angle in radians."""
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    x, y = vector
    rotated_x = x * cos_angle - y * sin_angle
    rotated_y = x * sin_angle + y * cos_angle
    return (rotated_x, rotated_y)

movement = False
mousedx, mousedy = 0, 0
# Main loop
running = True

# Slider dimensions and position
slider_x = width - 200  # Adjust as needed
slider_y = height - 50  # Adjust as needed
slider_width = 150
slider_height = 20
slider_min = 10
slider_max = 100000
slider_value = unit  # Initial value set to unit

# Function to draw the slider
def draw_slider(screen, x, y, width, height, value, min_value, max_value):
    # Draw slider bar
    pygame.draw.rect(screen, GREY, (x, y, width, height))
    # Calculate handle position based on value
    handle_position = (value - min_value) / (max_value - min_value) * width
    # Draw handle
    pygame.draw.rect(screen, WHITE, (x + handle_position - 5, y - 5, 10, height + 10))

# Define the Clear button dimensions and position
clear_button_x = slider_x
clear_button_y = slider_y - 35  # Position above the slider
clear_button_width = slider_width
clear_button_height = 25

# Function to draw the Clear button
def draw_clear_button(screen, x, y, width, height, text):
    pygame.draw.rect(screen, GREY, (x, y, width, height))  # Button rectangle
    font = pygame.font.Font(None, 24)  # Adjust font size as needed
    text_surf = font.render(text, True, WHITE)  # Render the text
    text_rect = text_surf.get_rect(center=(x + width / 2, y + height / 2))  # Center text
    screen.blit(text_surf, text_rect)  # Draw text

# Define the Clear button dimensions and position
move_cam_button_x = clear_button_x
move_cam_button_y = clear_button_y - 35  # Position above the slider
move_cam_button_width = slider_width
move_cam_button_height = 25

# Function to draw the Clear button
def draw_move_cam_button(screen, x, y, width, height, text):
    pygame.draw.rect(screen, GREY, (x, y, width, height))  # Button rectangle
    font = pygame.font.Font(None, 24)  # Adjust font size as needed
    text_surf = font.render(text, True, WHITE)  # Render the text
    text_rect = text_surf.get_rect(center=(x + width / 2, y + height / 2))  # Center text
    screen.blit(text_surf, text_rect)  # Draw text

# Function to update the slider value based on mouse position
def update_slider_value(x, y, width, min_value, max_value, mouse_x):
    if mouse_x < x:
        mouse_x = x
    elif mouse_x > x + width:
        mouse_x = x + width
    return min_value + (mouse_x - x) / width * (max_value - min_value)

slider_dragging = False
path_points = []  # Initialize empty list to store path points
movecambool = False
# Initialize a reference time for rotations
rotation_reference_time = pygame.time.get_ticks()

while running:
    for event in pygame.event.get():
        if event.type in [pygame.QUIT, pygame.KEYDOWN]:
            running = False
        elif event.type == pygame.KEYDOWN:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.pos[0] >= slider_x and event.pos[0] <= slider_x + slider_width and event.pos[1] >= slider_y and event.pos[1] <= slider_y + slider_height:
                slider_dragging = True
                slider_value = update_slider_value(slider_x, slider_y, slider_width, slider_min, slider_max, event.pos[0])
                unit = slider_value  # Update unit based on slider value
            elif event.pos[0] >= clear_button_x and event.pos[0] <= clear_button_x + clear_button_width and event.pos[1] >= clear_button_y and event.pos[1] <= clear_button_y + clear_button_height:
                path_points.clear()  # Clear the path points
            elif event.pos[0] >= move_cam_button_x and event.pos[0] <= move_cam_button_x + move_cam_button_width and event.pos[1] >= move_cam_button_y and event.pos[1] <= move_cam_button_y + move_cam_button_height:
                movecambool = False if movecambool else True
            elif event.button == 2:  # Middle mouse button
                movement = True
                mousedx, mousedy = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            slider_dragging = False
            if event.button == 2:  # Middle mouse button
                movement = False
        elif event.type == pygame.MOUSEWHEEL:
            # Get mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Calculate zoom factor; adjust these values as needed
            zoom_factor = 1 + zoom_sensitivity if event.y > 0 else 1 - zoom_sensitivity

            # Adjust the scale
            scale *= zoom_factor

            # Adjust the origin so that it zooms towards/away from the mouse cursor
            origin_x = mouse_x - (mouse_x - origin_x) * zoom_factor
            origin_y = mouse_y - (mouse_y - origin_y) * zoom_factor

            for i in range(len(path_points)):
                path_points[i] = (mouse_x - (mouse_x - path_points[i][0]) * zoom_factor, mouse_y - (mouse_y - path_points[i][1]) * zoom_factor)

        # Inside the event loop, update the reference time when the unit changes
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
            if slider_dragging:
                old_unit = unit
                slider_value = update_slider_value(slider_x, slider_y, slider_width, slider_min, slider_max, event.pos[0])
                unit = slider_value  # Update unit based on slider value
                if old_unit != unit:
                    for i in range(len(vectors)):
                        base_angle_vectors[i] = last_angle_vectors[i]
                    rotation_reference_time = pygame.time.get_ticks()


    if movement:
        new_mouse_x, new_mouse_y = pygame.mouse.get_pos()
        origin_x += new_mouse_x - mousedx
        origin_y += new_mouse_y - mousedy
        for i in range(len(path_points)):
            path_points[i] = (path_points[i][0] + new_mouse_x - mousedx, path_points[i][1] + new_mouse_y - mousedy)

        mousedx, mousedy = new_mouse_x, new_mouse_y

    # Fill the background
    screen.fill(BLACK)

    draw_slider(screen, slider_x, slider_y, slider_width, slider_height, slider_value, slider_min, slider_max)
    draw_clear_button(screen, clear_button_x, clear_button_y, clear_button_width, clear_button_height, "Clear")
    draw_move_cam_button(screen, move_cam_button_x, move_cam_button_y, move_cam_button_width, move_cam_button_height, "Move Cam")

    # Draw the axes
    pygame.draw.line(screen, GREY, (origin_x, 0), (origin_x, height))
    pygame.draw.line(screen, GREY, (0, origin_y), (width, origin_y))

    # Time-based rotation
    current_time = pygame.time.get_ticks()  # Get current time in milliseconds
    start_x, start_y = origin_x, origin_y  # Start from the origin
    end_x, end_y = start_x, start_y
    middle_index = len(vectors) // 2  # Find the middle index

    for i in range(len(vectors)):
        index = middle_index + (math.ceil(i / 2) * (-1)**i)
        vector = vectors[index]
        rotation_speed = ((i+1)//2) * (-1)**i  # Calculate rotation speed
        # Continue from rotation speed calculation
        # Inside the main loop, where you calculate the angle for rotation
        elapsed_time = pygame.time.get_ticks() - rotation_reference_time  # Calculate elapsed time since the reference time
        angle = rotation_speed * (2 * math.pi) * (elapsed_time / unit) + base_angle_vectors[index]
        last_angle_vectors[index] = angle
        rotated_vector = rotate_vector(vector, angle)

        # Scale and draw the rotated vector
        end_x = start_x + rotated_vector[0] * scale
        end_y = start_y - rotated_vector[1] * scale  # Negative for screen coordinates
        draw_arrow(screen, (start_x, start_y), (end_x, end_y), RED)
        start_x, start_y = end_x, end_y  # Update start for the next vector

    if (end_x, end_y) not in path_points:
        path_points.append((end_x, end_y))  # Add end point to path_points list
    # Draw path
    if len(path_points) > 1:
        pygame.draw.lines(screen, YELLOW, False, path_points, 2)  # Draw yellow line

    # Update the display
    pygame.display.flip()

    # After calculating end_x and end_y for all vectors
    if movecambool:
        # Calculate the midpoint of the screen to center the camera
        screen_mid_x, screen_mid_y = width // 2, height // 2
        dx = screen_mid_x - end_x - origin_x
        dy = screen_mid_y - end_y - origin_y
        # Adjust the origin to center the end of the arrow path
        origin_x += dx
        origin_y += dy

        # Optionally, adjust path_points if they are being displayed relative to the origin
        path_points = [(x + dx, y + dy) for x, y in path_points]


# Quit pygame
pygame.quit()
sys.exit()


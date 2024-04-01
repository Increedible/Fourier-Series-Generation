import pygame
import math
import sys
from svgpathtools import svg2paths
import numpy as np
import threading

vectors = []
filename = 'output.txt'

# Read from the text file
with open(filename, 'r') as file:
    for line in file:
        # Split each line into parts, convert to integers, and add as a tuple to the list
        parts = line.strip().split()
        vectors.append((float(parts[0]), float(parts[1])))

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
beginscale = 0.003
scale = beginscale  # Pixels per unit
origin_x, origin_y = width // 2, height // 2

# Arrowhead size as a percentage of the vector length
arrowhead_percentage = 0.15

def pointborderdist(point, maxdist):
    val = math.sqrt(point[0]**2 + point[1]**2)/maxdist
    if val > 1:
        return 1
    return val

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
clear_button_y = slider_y - 105  # Position above the slider
clear_button_width = slider_width
clear_button_height = 25

# Function to draw the Clear button
def draw_clear_button(screen, x, y, width, height, text):
    pygame.draw.rect(screen, GREY, (x, y, width, height))  # Button rectangle
    font = pygame.font.Font(None, 24)  # Adjust font size as needed
    text_surf = font.render(text, True, WHITE)  # Render the text
    text_rect = text_surf.get_rect(center=(x + width / 2, y + height / 2))  # Center text
    screen.blit(text_surf, text_rect)  # Draw text

move_cam_button_x = clear_button_x
move_cam_button_y = clear_button_y + 35
move_cam_button_width = slider_width
move_cam_button_height = 25

def draw_move_cam_button(screen, x, y, width, height, text):
    pygame.draw.rect(screen, GREY, (x, y, width, height))  # Button rectangle
    font = pygame.font.Font(None, 24)  # Adjust font size as needed
    text_surf = font.render(text, True, WHITE)  # Render the text
    text_rect = text_surf.get_rect(center=(x + width / 2, y + height / 2))  # Center text
    screen.blit(text_surf, text_rect)  # Draw text

slow_button_x = slider_x
slow_button_y = slider_y - 35
slow_button_width = slider_width
slow_button_height = 25

# Function to draw the Clear button
def draw_slow_button(screen, x, y, width, height, text):
    pygame.draw.rect(screen, GREY, (x, y, width, height))  # Button rectangle
    font = pygame.font.Font(None, 24)  # Adjust font size as needed
    text_surf = font.render(text, True, WHITE)  # Render the text
    text_rect = text_surf.get_rect(center=(x + width / 2, y + height / 2))  # Center text
    screen.blit(text_surf, text_rect)  # Draw text

# Function to update the slider value based on mouse position
def update_slider_value(x, width, min_value, max_value, mouse_x):
    if mouse_x < x:
        mouse_x = x
    elif mouse_x > x + width:
        mouse_x = x + width
    return min_value + (mouse_x - x) / width * (max_value - min_value)

def clear(screen):
    screen.fill(BLACK)
    pygame.draw.line(screen, GREY, (origin_x, 0), (origin_x, height))
    pygame.draw.line(screen, GREY, (0, origin_y), (width, origin_y))

slider_dragging = False
path_points = []  # Initialize empty list to store path points
movecambool = False
# Initialize a reference time for rotations
rotation_reference_time = pygame.time.get_ticks()
slowbool = False
drawing = False

fullvectors = []
drawpoints = []

def getF(t):
    bar = t * len(drawpoints)
    ni = math.floor(bar)
    prog = bar - ni
    ndx = (drawpoints[(ni+1) % len(drawpoints)][0] - drawpoints[ni][0])
    ndy = (drawpoints[(ni+1) % len(drawpoints)][1] - drawpoints[ni][1])
    return drawpoints[ni][0] + prog * ndx, drawpoints[ni][1] + prog * ndy

# for i in range(8):
#     print(getF(i * 0.125))
# exit()

def generateVectors(nrange):
    dt = 1/(nrange * 2)

    for nn in range(nrange * 2 + 1):
        n = (math.ceil(nn / 2) * (-1)**nn)
        vx = 0
        vy = 0
        for k in range(int(1/dt)):
            a,b = getF(k*dt)
            c = math.cos(-n*2*math.pi*k*dt)
            d = math.sin(-n*2*math.pi*k*dt)
            vx += a * c - b * d
            vy += b * c + a * d
        # if n == 0:
        #     vx, vy = 0, 0
        fullvectors.append((vx, vy))

numdrawvectors = 350

while running:
    for event in pygame.event.get():
        if event.type in [pygame.QUIT, pygame.KEYDOWN]:
            running = False
        elif event.type == pygame.KEYDOWN:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not drawing:
            if slider_x <= event.pos[0] <= slider_x + slider_width and slider_y <= event.pos[1] <= slider_y + slider_height:
                slider_dragging = True
                slider_value = update_slider_value(slider_x, slider_width, slider_min, slider_max, event.pos[0])
                unit = slider_value  # Update unit based on slider value
            elif clear_button_x <= event.pos[0] <= clear_button_x + clear_button_width and clear_button_y <= event.pos[1] <= clear_button_y + clear_button_height:
                path_points.clear()  # Clear the path points
            elif move_cam_button_x <= event.pos[0] <= move_cam_button_x + move_cam_button_width and move_cam_button_y <= event.pos[1] <= move_cam_button_y + move_cam_button_height:
                movecambool = False if movecambool else True
            elif slow_button_x <= event.pos[0] <= slow_button_x + slow_button_width and slow_button_y <= event.pos[1] <= slow_button_y + slow_button_height:
                if slowbool:
                    slowbool = False
                    unit /= 100
                    slider_max /= 100
                    slider_value /= 100
                else:
                    slowbool = True
                    unit *= 100
                    slider_max *= 100
                    slider_value *= 100
                for i in range(len(vectors)):
                    base_angle_vectors[i] = last_angle_vectors[i]
                    rotation_reference_time = pygame.time.get_ticks()
            elif event.button == 2:  # Middle mouse button
                movement = True
                mousedx, mousedy = event.pos
            elif not drawing:
                drawing = True
                drawpoints = []
                clear(screen)
        elif event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                drawing = False
                if len(drawpoints) > 2:
                    fullvectors = []
                    drawpoints = [((point[0] - origin_x) * (beginscale/scale), -(point[1] - origin_y) * (beginscale/scale)) for point in drawpoints]
                    t = threading.Thread(target=generateVectors, args=(numdrawvectors,))
                    t.start()
                    while len(fullvectors) < numdrawvectors * 2 + 1:
                        clear(screen)
                        start_x, start_y = origin_x, origin_y  # Start from the origin
                        end_x, end_y = start_x, start_y
                        copy_fullvectors = fullvectors.copy()
                        for i in range(len(copy_fullvectors)):
                            vector = copy_fullvectors[i]

                            # Scale and draw the rotated vector
                            end_x = start_x + vector[0] * scale
                            end_y = start_y - vector[1] * scale  # Negative for screen coordinates

                            draw_arrow(screen, (start_x, start_y), (end_x, end_y), (255, 0, 0))
                            start_x, start_y = end_x, end_y  # Update start for the next vector
                        pygame.display.flip()

                    t.join()
                    vectors = []
                    for i in range(numdrawvectors * 2 + 1):
                        vectors.append((0, 0))
                    for nn in range(numdrawvectors * 2 + 1):
                        vectors[numdrawvectors + (math.ceil(nn / 2) * (-1)**nn)] = fullvectors[nn]

                    base_angle_vectors = []
                    last_angle_vectors = []
                    for vector in vectors:
                        base_angle_vectors.append(0)
                        last_angle_vectors.append(0)
                    path_points = []
                    rotation_reference_time = pygame.time.get_ticks()

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
                slider_value = update_slider_value(slider_x, slider_width, slider_min, slider_max, event.pos[0])
                unit = slider_value  # Update unit based on slider value
                if old_unit != unit:
                    for i in range(len(vectors)):
                        base_angle_vectors[i] = last_angle_vectors[i]
                    rotation_reference_time = pygame.time.get_ticks()

    if drawing:
        drawpoints.append(pygame.mouse.get_pos())
        if len(drawpoints) > 1:
            pygame.draw.lines(screen, YELLOW, False, drawpoints[-2:], 4)
        pygame.display.flip()
        continue

    if movement:
        new_mouse_x, new_mouse_y = pygame.mouse.get_pos()
        origin_x += new_mouse_x - mousedx
        origin_y += new_mouse_y - mousedy
        for i in range(len(path_points)):
            path_points[i] = (path_points[i][0] + new_mouse_x - mousedx, path_points[i][1] + new_mouse_y - mousedy)

        mousedx, mousedy = new_mouse_x, new_mouse_y

    clear(screen)

    draw_slider(screen, slider_x, slider_y, slider_width, slider_height, slider_value, slider_min, slider_max)
    draw_clear_button(screen, clear_button_x, clear_button_y, clear_button_width, clear_button_height, "Clear")
    draw_move_cam_button(screen, move_cam_button_x, move_cam_button_y, move_cam_button_width, move_cam_button_height, "Move Cam")
    draw_slow_button(screen, slow_button_x, slow_button_y, slow_button_width, slow_button_height, "100x Slow")

    # Time-based rotation
    current_time = pygame.time.get_ticks()  # Get current time in milliseconds
    start_x, start_y = origin_x, origin_y  # Start from the origin
    end_x, end_y = start_x, start_y
    middle_index = len(vectors) // 2  # Find the middle index
    trenddown = True
    r = 255
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
        #fulldist = math.sqrt(width**2 + height**2) * 0.8

        #r = 100 + (1 - (pointborderdist((start_x, start_y), fulldist) + pointborderdist((end_x, end_y), fulldist)) / 2) * 155
        draw_arrow(screen, (start_x, start_y), (end_x, end_y), (r, 0, 0))
        start_x, start_y = end_x, end_y  # Update start for the next vector


    if (end_x, end_y) not in path_points:
        path_points.append((end_x, end_y))  # Add end point to path_points list

    # Draw path
    if len(path_points) > 1:
        pygame.draw.lines(screen, YELLOW, False, path_points, 4)  # Draw yellow line

    # Update the display
    pygame.display.flip()

    # After calculating end_x and end_y for all vectors
    if movecambool:
        # Calculate the midpoint of the screen to center the camera
        screen_mid_x, screen_mid_y = width // 2, height // 2
        dx = screen_mid_x - end_x
        dy = screen_mid_y - end_y
        # Adjust the origin to center the end of the arrow path
        origin_x += screen_mid_x - end_x
        origin_y += screen_mid_y - end_y

        # Optionally, adjust path_points if they are being displayed relative to the origin
        path_points = [(x + dx, y + dy) for x, y in path_points]




# Quit pygame
pygame.quit()
sys.exit()


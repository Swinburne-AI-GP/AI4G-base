import random
import json
import numpy as np
from scipy.stats import skewnorm
import math

maps = []
skewed_random_numbers = []
next_random_number = 0

number_of_maps = 10

def generate_skewed_random_numbers():
	skewness = 15  # Negative values create left-skewed distribution
	min_value = 2  # The lower bound of your range
	max_value = 100  # The upper bound of your range
	# Generate random numbers
	random_numbers = skewnorm.rvs(skewness, size=number_of_maps)
	random_numbers = min_value + (max_value - min_value) * (random_numbers - np.min(random_numbers)) / (np.max(random_numbers) - np.min(random_numbers))
	return random_numbers

def get_skewed_random_number(i=None):
	global next_random_number, skewed_random_numbers
	if i:
		return skewed_random_numbers[i]
	else:
		if next_random_number >= len(skewed_random_numbers):
			skewed_random_numbers = generate_skewed_random_numbers()
			next_random_number = 0
		return skewed_random_numbers[next_random_number]

def generate_planets(num_planets, sector_size=2*np.pi, sector_number=0):
	planets = []
	for _ in range(num_planets):
		radius = random.uniform(0, 1)
		sector_start_angle = sector_number * sector_size
		sector_end_angle = (sector_number + 1) * sector_size
		angle = random.uniform(sector_start_angle, sector_end_angle)
		x = radius * np.cos(angle)
		y = radius * np.sin(angle)
		growth = random.randint(0, 8)
		ships = random.randint(1, 1000)

		planet = {
			"x": (x+1)/2,
			"y": y,
			"growth": growth,
			"ships": ships
		}
		planets.append(planet)
	return planets

def rotate_objects(objects, angle_rad):
	rotated_objects = []
	for obj in objects:
		x = obj['x']
		y = obj['y']
		# Apply rotation transformation
		new_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
		new_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
		# Create a new object with rotated coordinates
		rotated_obj = {
			'x': new_x,
			'y': new_y,
			'growth': obj['growth'],
			'ships': obj['ships']
		}
		rotated_objects.append(rotated_obj)
	return rotated_objects

def rescale_planets(planets):
	# Rescale planets to fit in the 0-1 range
	for planet in planets:
		planet['x'] = (planet['x'] + 1) / 2
		planet['y'] = (planet['y'] + 1) / 2
	return planets

def cull_planets(planets, minimum_planet_distance=0.15):
	# Remove planets that are too close to each other
	ok_planets = []
	for planet in planets:
		# Check if planet is too close to any other planet
		too_close = False
		for other_planet in ok_planets:
			dx = planet['x'] - other_planet['x']
			dy = planet['y'] - other_planet['y']
			distance = math.sqrt(dx**2 + dy**2)
			if distance < minimum_planet_distance:
				too_close = True
				break
		# Add planet to culled list if it is not too close
		if not too_close:
			ok_planets.append(planet)
	return ok_planets

for i in range(number_of_maps):
	num_sectors = i+1
	sector_angle = 2 * np.pi / num_sectors
	num_planets = int(get_skewed_random_number())
	initial_planets = generate_planets(num_planets,sector_angle)
	planets = []
	for sector_num in range(num_sectors):
		planets.extend(rotate_objects(initial_planets, sector_angle*sector_num))

	planets = rescale_planets(planets)

	planets = cull_planets(planets)
	map_data = {
		"planets": planets
	}

	# Write map data to file
	filename = f"maps/map{i+11:03}.json"
	with open(filename, "w") as file:
		json.dump(map_data, file)


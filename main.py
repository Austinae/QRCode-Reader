from PIL import Image
from math import floor

#only functions with version 1 assuming reading patterns are in correct orientation (top left, bottom left and top right)
#I would very much enjoy creating a program that can detect all kinds of qr codes

PILImage = Image.open('aaaaaaaa.png')
list_PILImage = list(PILImage.getdata()) 

grid = []
bitvalues_desc = [128, 64, 32, 16, 8, 4, 2, 1]
bitvalues_asc = [1, 2, 4, 8, 16, 32, 64, 128]

def getSizeAndReadingOrientation():
	counter = 0
	size = 0
	orientation = -1

	left = 0
	right = PILImage.size[0]-1
	i = 0

	while left < right:
		if list_PILImage[left][0] != 0 and orientation != 0:
			if counter == 0:
				counter = 1
				orientation = 0
			if counter == 2:
				counter = 3
		if list_PILImage[right][0] != 0  and orientation != 1:
			if counter == 0:
				counter = 1
				orientation = 1
			if counter == 2:
				counter = 3
		if list_PILImage[(PILImage.size[1]-1) * PILImage.size[0]  + left][0] != 0  and orientation != 2:
			if counter == 0:
				counter = 1
				orientation = 2
			if counter == 2:
				counter = 3
		if list_PILImage[(PILImage.size[1]-1) * PILImage.size[0]  + right][0] != 0  and orientation != 3:
			if counter == 0:
				counter = 1
				orientation = 3
			if counter == 2:
				counter = 3
		if counter == 1:
				i = (orientation + 1) % 4
				counter = 2
		if counter == 3:
			size = left + 1
			break

		left+=1
		right-=1

	return [size, orientation] 


def fillGrid(orientation):
	startRow = -1
	stopRow = -1
	stepRow = -1
	startColumn = -1
	stopColumn = -1
	stepColumn = -1

	if orientation == 0:
		startRow = PILImage.size[0]-1
		stopRow = -1
		stepRow = -1
		startColumn = PILImage.size[1]-1
		stopColumn = -1
		stepColumn = -1
	if orientation == 1:
		startRow = 0
		stopRow = PILImage.size[0]
		stepRow = 1
		startColumn = PILImage.size[1]-1
		stopColumn = -1
		stepColumn = -1
	if orientation == 2:
		startRow = PILImage.size[0]-1
		stopRow = -1
		stepRow = -1
		startColumn = 0
		stopColumn = PILImage.size[1]
		stepColumn = 1
	if orientation == 3:
		startRow = 0
		stopRow = PILImage.size[1]
		stepRow = 1
		startColumn = 0
		stopColumn = PILImage.size[0]
		stepColumn = 1


	for row in range(startColumn, stopColumn, stepColumn):
		r = []
		for column in range(startRow, stopRow, stepRow):
			if list_PILImage[row * PILImage.size[0] + column][0] == 0:
				r.append("#")
			else:
				r.append(".")
		grid.append(r)


def fetchInformation(size):
	ecl_val = 0
	if grid[size][0] == "#":
		ecl_val += 2
	if grid[size][1] == "#":
		ecl_val += 1
	ecl = [30, 25, 15, 7][ecl_val] #error correction level

	mask = 0 #mask pattern
	if grid[size][2] == "#":
		mask += 4
	if grid[size][3] == "#":
		mask += 2
	if grid[size][4] == "#":
		mask += 1

	fec = 0 #format error correction
	if grid[size][5] == "#":
		fec += 2
	if grid[size][6] == "#":
		fec += 1

	return [ecl, mask, fec]


def hideReadingPatterns(size):
	for i in range(3):
		toremove_x = size
		toremove_y = size
		if i == 0: #top left
			sp_x = 0
			sp_y = 0
			toremove_x += 1
			toremove_y += 1
		if i == 1: #top right
			sp_x = PILImage.size[0] - size
			sp_y = 0
			toremove_y += 1
		if i == 2:
			sp_x = 0
			sp_y = PILImage.size[1] - size
			toremove_x += 1

		for i in range(sp_y, toremove_y + sp_y, 1):
			for j in range(sp_x, toremove_x + sp_x, 1):
				grid[i][j] = "X"

	for i in range(len(grid)): # for the spacers (eg: #.#.# for width 21 qr code)
		grid[size-2][i] = "X"
	for i in range(len(grid)):
		grid[i][size-2] = "X"


def unmask(mask, i, j):
	if mask == 0:
		if (i+j)%2 == 0:
			return True
	if mask == 1:
		if i%2 == 0: 
			return True
	if mask == 2:
		if j%3 == 0:
			return True
	if mask == 3:
		if (i+j)%3 == 0:
			return True
	if mask == 4:
		if (floor(i/2) + floor(j/3))%2 == 0:
			return True
	if mask == 5:
		if ((i*j)%2 + (i*j)%3) == 0:
			return True
	if mask == 6:
		if ((i*j)%2+(i*j)%3)%2 == 0:
			return True
	if mask == 7:
		if ((i*j)%3+(i+j)%2)%2 == 0:
			return True
	return False

def travelGrid(size, mask):
	blocks = []

	buffer = []

	up = True
	swivel = True

	counter = 0

	x = len(grid)-1
	y = len(grid)-1
	while True:
		# print(x, y, grid[x][y])
		if len(buffer) == 4 and counter == 0:
			counter += 1
			blocks.append(buffer)
			buffer = []
		if len(buffer) == 8:
			blocks.append(buffer)
			buffer = []
		if grid[x][y] != 'X':
			if unmask(mask, x, y) is True:
				if grid[x][y] == '.':
					buffer.append(True)
				else:
					buffer.append(False)
			else:
				if grid[x][y] == '#':
					buffer.append(True)
				else:
					buffer.append(False)
		if up is True:
			if swivel is True:
				y -= 1
			else:
				x -= 1
				y += 1
		else:
			if swivel is True:
				y -= 1
			else:
				x += 1
				y += 1

		swivel = not swivel

		if x == -1 or x == len(grid):
			if up is True:
				x += 1
				y -= 2
			else:
				x -= 1
				y -= 2
			if y == size-2:
				y -= 1
			up = not up
			if y < 0:
				break
	if len(buffer) > 0:
		blocks.append(buffer)
	return blocks

def drawGrid():
	for row in grid:
		for square in row:
			print(square, end=" ")
		print()
	print()

form = getSizeAndReadingOrientation() #size, orientation
fillGrid(form[1])
qrInfo = fetchInformation(form[0]) #ecl, mask, fec
print(qrInfo)
hideReadingPatterns(form[0])
drawGrid()
blocks = travelGrid(form[0], qrInfo[1])
for i in blocks:
	print(i)


import cv2

# Load image
img = cv2.imread("C:\\Users\\HP\\Documents\\rpi\\fake_1.jpg")

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Save the grayscale image to disk
cv2.imwrite("C:\\Users\\HP\\Documents\\rpi\\gray_saved.jpg", gray)

print("Image saved as gray_saved.jpg")
import cv2

# Load image in grayscale directly
img = cv2.imread("C:\\Users\\HP\\Documents\\rpi\\fake_1.jpg", 1)

# Detect edges using Canny algorithm
edges = cv2.Canny(img, 100, 200)

# Show detected edges
cv2.imshow("Edges", edges)
cv2.waitKey(0)
cv2.destroyAllWindows()
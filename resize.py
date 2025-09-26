import cv2

# Load image
img = cv2.imread("C:\\Users\\HP\\Documents\\rpi\\fake_1.jpg")

# Resize image to 300x200 pixels
resized = cv2.resize(img, (300, 200))

# Show resized image
cv2.imshow("Resized", resized)
cv2.waitKey(0)
cv2.destroyAllWindows()
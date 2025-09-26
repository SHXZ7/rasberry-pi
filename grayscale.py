import cv2

# Load a color image
img = cv2.imread("C:\\Users\\HP\\Documents\\rpi\\fake_1.jpg")

# Convert the image from BGR to Grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Show the grayscale image
cv2.imshow("Gray", gray)
cv2.waitKey(0)
cv2.destroyAllWindows()
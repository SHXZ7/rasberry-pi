import cv2

# Load image
img = cv2.imread("C:\\Users\\HP\\Documents\\rpi\\fake_1.jpg")

# Draw a green rectangle (x1,y1) to (x2,y2)
cv2.rectangle(img, (50, 50), (200, 200), (0, 255, 0), 3)

# Draw a filled blue circle
cv2.circle(img, (300, 200), 50, (255, 0, 0), -1)

# Draw a red line from top-left to bottom-right
cv2.line(img, (0, 0), (400, 400), (0, 0, 255), 5)

# Show the image with shapes
cv2.imshow("Shapes", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
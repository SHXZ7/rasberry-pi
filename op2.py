import cv2

# Load image
img = cv2.imread("C:\\Users\\HP\\Documents\\rpi\\fake_1.jpg")

# Write text on the image
cv2.putText(img, "umb", (50, 50),    # Position (x,y)
            cv2.FONT_HERSHEY_SIMPLEX,           # Font type
            2,                                  # Font scale (size)
            (255, 105, 180),                    # Color (pink)
            3)                                  # Thickness

# Show image with text
cv2.imshow("Text", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
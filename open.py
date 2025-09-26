import cv2
import matplotlib.pyplot as plt

img = cv2.imread("C:\\Users\\HP\\Documents\\rpi\\fake_1.jpg")

if img is None:
    raise ValueError("Image not found!")

# Show using matplotlib (avoids cv2.imshow issue)
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.axis("off")
plt.show()

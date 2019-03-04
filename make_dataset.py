import cv2
import glob
import numpy as np
from PIL import Image
def make_image_dataset(image_path):
    # np.random.seed(0)
    images =[]
    #for i in range(num_group):
    data  = sorted(glob.glob(image_path+'/*.png'))
    for j in data:
        k = cv2.imread(j, cv2.IMREAD_COLOR)
        k =cv2.cvtColor(k ,cv2.COLOR_RGB2BGR)
        image = Image.fromarray(np.array(k))
        flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = np.array(list(flipped_image.getdata()), np.uint8)
        images.append(img_data)

    np.save("full_working.npy", images)

    return images


make_image_dataset('tero image ko path hal')
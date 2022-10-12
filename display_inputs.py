import os
import cv2 as cv
import numpy as np
from datasets.load_dataset import load_data


if __name__ == "__main__":
    train_dataset, train_dataloader = load_data("data/Drone", "Drone", "sample",
                                                img_size=1248, sample_size=640, batch_size=1,
                                                augment=False, mosaic=False, multiscale=False)

    for i, (img_path, imgs, targets) in enumerate(train_dataloader):
        print(targets)
        img = imgs.squeeze(0).numpy().transpose(1, 2, 0)
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
        targets = np.array(targets)

        for p in targets:
            x, y, w, h, theta = p[2] * img.shape[1], p[3] * img.shape[1], p[4] * img.shape[1], p[5] * img.shape[1], p[6]

            bbox = cv.boxPoints(((x, y), (w, h), theta / np.pi * 180))
            bbox = np.int0(bbox)
            cv.drawContours(img, [bbox], 0, (255, 0, 0), 1)

        # cv.imshow('My Image', img)
        cv.waitKey(0)
        cv.destroyAllWindows()

        img[:, 1:] = img[:, 1:] * 255.0
        output_path = os.path.join("outputs", "display_gt")
        if not os.path.exists(output_path):
            os.mkdir(output_path) 
        filename = os.path.join(output_path, img_path[0].split('\\')[-1])
        cv.imwrite(filename, img)

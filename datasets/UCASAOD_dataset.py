import os
import numpy as np
import torch
import glob
from tqdm import tqdm

from datasets.base_dataset import BaseDataset


class UCASAODDataset(BaseDataset):
    def __init__(self, data_dir, class_names, img_size=416, sample_size=600, augment=True, mosaic=True, multiscale=True, normalized_labels=False):
        super().__init__(img_size, sample_size, augment, mosaic, multiscale, normalized_labels)
        self.img_files = sorted(glob.glob(os.path.join(data_dir, "images/*.png")))
        self.label_files = [path.replace("images", "labels").replace("png", "txt") for path in tqdm(self.img_files)]
        self.category = {}
        for i, name in enumerate(class_names):
            self.category[name.replace(" ", "-")] = i

    def load_files(self, label_path):
        lines = open(label_path, 'r').readlines()

        x1, y1, x2, y2, x3, y3, x4, y4, label = [], [], [], [], [], [], [], [], []
        for line in lines:
            line = line.split('\t')
            x1.append(float(line[0]))
            y1.append(float(line[1]))
            x2.append(float(line[2]))
            y2.append(float(line[3]))
            x3.append(float(line[4]))
            y3.append(float(line[5]))
            x4.append(float(line[6]))
            y4.append(float(line[7]))
            label.append(float(line[13]))

        num_targets = len(label)
        if not num_targets:
            return None, None, None, None, None, None, 0

        x1 = torch.tensor(x1)
        y1 = torch.tensor(y1)
        x2 = torch.tensor(x2)
        y2 = torch.tensor(y2)
        x3 = torch.tensor(x3)
        y3 = torch.tensor(y3)
        x4 = torch.tensor(x4)
        y4 = torch.tensor(y4)
        label = torch.tensor(label)

        x = ((x1 + x3) / 2 + (x2 + x4) / 2) / 2
        y = ((y1 + y3) / 2 + (y2 + y4) / 2) / 2
        w = torch.sqrt(torch.pow((x1 - x2), 2) + torch.pow((y1 - y2), 2))
        h = torch.sqrt(torch.pow((x2 - x3), 2) + torch.pow((y2 - y3), 2))

        theta = ((y2 - y1) / (x2 - x1 + 1e-16) + (y3 - y4) / (x3 - x4 + 1e-16)) / 2
        theta = torch.atan(theta)
        theta = torch.stack([t if t != -(np.pi / 2) else t + np.pi for t in theta])

        return x, y, w, h, theta, label, num_targets
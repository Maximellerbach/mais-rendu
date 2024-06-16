from torch.utils.data import Dataset
from scene.cameras import Camera
import numpy as np
from utils.general_utils import PILtoTorch
from utils.graphics_utils import fov2focal, focal2fov
import torch
from utils.camera_utils import loadCam
from utils.graphics_utils import focal2fov


class FourDGSdataset(Dataset):
    def __init__(self, dataset, args, dataset_type):
        self.dataset = dataset
        self.args = args
        self.dataset_type = dataset_type

    def __getitem__(self, index):
        # breakpoint()

        if self.dataset_type != "PanopticSports":
            try:
                image, w2c, time = self.dataset[index]
                R, T = w2c
                FovX = focal2fov(self.dataset.focal[0], image.shape[2])
                FovY = focal2fov(self.dataset.focal[0], image.shape[1])
                mask = None
            except:
                caminfo = self.dataset[index]
                image = caminfo.image
                R = caminfo.R
                T = caminfo.T
                FovX = caminfo.FovX
                FovY = caminfo.FovY
                time = caminfo.time

                mask = caminfo.mask
            return Camera(
                colmap_id=index,
                R=R,
                T=T,
                FoVx=FovX,
                FoVy=FovY,
                image=image,
                gt_alpha_mask=None,
                image_name=f"{index}",
                uid=index,
                data_device=torch.device("cuda"),
                time=time,
                mask=mask,
            )
        else:
            return self.dataset[index]

    def __len__(self):

        return len(self.dataset)


def get_cam_info(dataset, index):
    caminfo = dataset[index]
    image = caminfo.image
    R = caminfo.R
    T = caminfo.T
    FovX = caminfo.FovX
    FovY = caminfo.FovY
    time = caminfo.time

    mask = caminfo.mask

    return {
        "colmap_id": index,
        "R": R,
        "T": T,
        "image": image,
        "FovX": FovX,
        "FovY": FovY,
        "time": time,
        "mask": mask,
        "image_name": str(index),
        "uid": index,
        "data_device": torch.device("cuda"),
        "time": time,
        "mask": mask,
    }


class VideoCamera:
    def __init__(self, dataset, num_frames=400):
        self.dataset = dataset
        self.num_frames = num_frames
        self.offset_x = 0
        self.offset_y = 0
        self.offset_z = 0

    def get(self, index, directions=[]):
        if index >= self.num_frames:
            raise IndexError

        # lerp between beginning and end
        t = index / (self.num_frames - 1)

        prev_index = int(t * (len(self.dataset) - 1))
        next_index = prev_index + 1
        cam_info_begin = get_cam_info(self.dataset, prev_index)
        cam_info_end = get_cam_info(self.dataset, next_index)

        t = t * (len(self.dataset) - 1) - prev_index
        #t = 0.5

        R = cam_info_begin["R"] * (1 - t) + cam_info_end["R"] * t
        T = cam_info_begin["T"] * (1 - t) + cam_info_end["T"] * t
        for dir in directions:
            if dir == 1:
                print("going left")
                self.offset_x += 1
            if dir == 2:
                print("going right")
                self.offset_x -= 1
            if dir == 3:
                print("going back")
                self.offset_z += 1
            if dir == 4:
                print("going front")
                self.offset_z -= 1
            if dir == 5:
                print("going up")
                self.offset_y += 1
            if dir == 6:
                print("going down")
                self.offset_y -= 1

        T[0] += self.offset_x
        T[1] += self.offset_y
        T[2] += self.offset_z

        FovX = cam_info_begin["FovX"] * (1 - t) + cam_info_end["FovX"] * t
        FovY = cam_info_begin["FovY"] * (1 - t) + cam_info_end["FovY"] * t
        time = cam_info_begin["time"] * (1 - t) + cam_info_end["time"] * t

        return Camera(
            cam_info_begin["colmap_id"],
            R,
            T,
            FovX,
            FovY,
            image=cam_info_begin["image"],
            gt_alpha_mask=None,
            image_name=cam_info_begin["image_name"],
            uid=cam_info_begin["uid"],
            data_device=cam_info_begin["data_device"],
            time=time,
            mask=cam_info_begin["mask"],
        )

    def __len__(self):
        return len(self.dataset)
        # return self.num_frames


class GroundTruth:
    def __init__(self, dataset, args, dataset_type):
        self.dataset = dataset

    def __getitem__(self, index):
        caminfo = self.dataset[index]
        image = caminfo.image
        R = caminfo.R
        T = caminfo.T
        FovX = caminfo.FovX
        FovY = caminfo.FovY
        time = caminfo.time
        mask = caminfo.mask

        return Camera(
            colmap_id=index,
            R=R,
            T=T,
            FoVx=FovX,
            FoVy=FovY,
            image=image,
            gt_alpha_mask=None,
            image_name=f"{index}",
            uid=index,
            data_device=torch.device("cuda"),
            time=time,
            mask=mask,
        )

    def __len__(self):
        return len(self.dataset)

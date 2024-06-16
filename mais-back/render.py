#
# Copyright (C) 2023, Inria
# GRAPHDECO research group, https://team.inria.fr/graphdeco
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use
# under the terms of the LICENSE.md file.
#
# For inquiries contact  george.drettakis@inria.fr
#
import imageio
import numpy as np
import torch
from scene import Scene
import os
import cv2
from tqdm import tqdm
from os import makedirs
from gaussian_renderer import render
import torchvision
from utils.general_utils import safe_state
from argparse import ArgumentParser
from arguments import ModelParams, PipelineParams, get_combined_args, ModelHiddenParams
from gaussian_renderer import GaussianModel
from time import time
import socket
import base64

from flask import Flask, request, jsonify

import matplotlib.pyplot as plt

# import torch.multiprocessing as mp
import threading
import concurrent.futures
import asyncio
import websockets
from PIL import Image
from io import BytesIO

#app = Flask(__name__)

# current_image = None

# # GET request
# @app.route('/', methods=['GET'])
# def get_item():
#     return jsonify({"param": "prout"})

# # POST request
# @app.route('/items/', methods=['POST'])
# def create_item():
#     param = request.form.get('param')
#     return jsonify({"param": param})

# app.run(host="0.0.0.0", port=8000)



def multithread_write(image_list, path):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=None)

    def write_image(image, count, path):
        try:
            torchvision.utils.save_image(
                image, os.path.join(path, "{0:05d}".format(count) + ".png")
            )
            return count, True
        except:
            return count, False

    tasks = []
    for index, image in enumerate(image_list):
        tasks.append(executor.submit(write_image, image, index, path))
    executor.shutdown()
    for index, status in enumerate(tasks):
        if status == False:
            write_image(image_list[index], index, path)


to8b = lambda x: (255 * np.clip(x.cpu().numpy(), 0, 1)).astype(np.uint8)


def render_set(
    model_path, name, iteration, views, gaussians, pipeline, background, cam_type
):
    render_path = os.path.join(model_path, name, "ours_{}".format(iteration), "renders")
    gts_path = os.path.join(model_path, name, "ours_{}".format(iteration), "gt")

    makedirs(render_path, exist_ok=True)
    makedirs(gts_path, exist_ok=True)
    render_images = []
    gt_list = []
    render_list = []
    # breakpoint()
    print("point nums:", gaussians._xyz.shape[0])
    for idx, view in enumerate(tqdm(views, desc="Rendering progress")):
        if idx == 0:
            time1 = time()
        # breakpoint()

        rendering = render(view, gaussians, pipeline, background, cam_type=cam_type)[
            "render"
        ]
        # torchvision.utils.save_image(rendering, os.path.join(render_path, '{0:05d}'.format(idx) + ".png"))
        render_images.append(to8b(rendering).transpose(1, 2, 0))
        # print(to8b(rendering).shape)
        render_list.append(rendering)
        if name in ["train", "test"]:
            if cam_type != "PanopticSports":
                gt = view.original_image[0:3, :, :]
            else:
                gt = view["image"].cuda()
            # torchvision.utils.save_image(gt, os.path.join(gts_path, '{0:05d}'.format(idx) + ".png"))
            gt_list.append(gt)
        # if idx >= 10:
        # break
    time2 = time()
    print("FPS:", (len(views) - 1) / (time2 - time1))
    # print("writing training images.")

    multithread_write(gt_list, gts_path)
    print("writing rendering images.")

    multithread_write(render_list, render_path)

    imageio.mimwrite(
        os.path.join(model_path, name, "ours_{}".format(iteration), "video_rgb.mp4"),
        render_images,
        fps=30,
    )





def render_sets(
    dataset: ModelParams,
    hyperparam,
    iteration: int,
    pipeline: PipelineParams,
    skip_train: bool,
    skip_test: bool,
    skip_video: bool,
):
    with torch.no_grad():
        gaussians = GaussianModel(dataset.sh_degree, hyperparam)
        scene = Scene(dataset, gaussians, load_iteration=iteration, shuffle=False)
        cam_type = scene.dataset_type
        bg_color = [1, 1, 1] if dataset.white_background else [0, 0, 0]
        background = torch.tensor(bg_color, dtype=torch.float32, device="cuda")

        if not skip_train:
            render_set(
                dataset.model_path,
                "train",
                scene.loaded_iter,
                scene.getTrainCameras(),
                gaussians,
                pipeline,
                background,
                cam_type,
            )

        if not skip_test:
            render_set(
                dataset.model_path,
                "test",
                scene.loaded_iter,
                scene.getTestCameras(),
                gaussians,
                pipeline,
                background,
                cam_type,
            )
        if not skip_video:
            # render_set(
            #     dataset.model_path,
            #     "video",
            #     scene.loaded_iter,
            #     scene.getVideoCameras(),
            #     gaussians,
            #     pipeline,
            #     background,
            #     cam_type,
            # )
            views = scene.getVideoCameras()
            #conn.sendall(b"Welcome to the server")

            print("point nums:", gaussians._xyz.shape[0])
            keyMap = {
                ord('a'): 1, # left 
                ord('d'): 2, # right 
                ord('s'): 3, # back 
                ord('w'): 4, # front
                ord('q'): 5, # up
                ord('e'): 6, # down
            }
            messageMap = {
                "LEFT": 1,
                "RIGHT": 2,
                "BACK": 3,
                "FRONT": 4,
                "UP": 5,
                "DOWN": 6,
            }

            async def handler(websocket, path):
                print("Connected")
                i = 0
                k = -1
                directions = []
                while True:
                    try:
                        #view = views.get(i, directions)
                        view = views.get(i, directions)
                    except:
                        i = 0
                        view = views.get(i)
                    rendering = render(view, gaussians, pipeline, background, cam_type=cam_type)[
                        "render"
                    ]

                    # tensor to numpy array
                    rendering = rendering.cpu().detach().numpy().transpose(1, 2, 0)
                    rendering = (rendering.clip(0, 1) * 255).astype(np.uint8)
                    #rendering = cv2.cvtColor(rendering, cv2.COLOR_RGB2BGR)

                    # to base64
                    received = ""
                    async for message in websocket:
                        if message != b"":
                            received = message
                            break
                    
                    if received:
                        print(bytes(received, 'utf-8'))

                    #try:
                    #    received = conn.recv(1024)
                    #except:
                    #    received = b""

                    #received = received.decode("utf-8")
                    if received:
                       directions = [messageMap.get(received, -1)]
                    else:
                       directions = []

                    # cv2.imshow("rendering", rendering)
                    output = Image.fromarray(rendering)
                    buffer = BytesIO()
                    output.save(buffer, format="JPEG")
                    rendering = base64.b64encode(buffer.getvalue()).decode("utf-8")

                    await websocket.send(rendering)
                    # k = cv2.waitKey(1)

                    # if k in keyMap:
                    #     k = keyMap[k]

                    if k == 27:
                        break

                    i += 1
            return handler

if __name__ == "__main__":
    # Set up command line argument parser
    parser = ArgumentParser(description="Testing script parameters")
    model = ModelParams(parser, sentinel=True)
    pipeline = PipelineParams(parser)
    hyperparam = ModelHiddenParams(parser)
    parser.add_argument("--iteration", default=-1, type=int)
    parser.add_argument("--skip_train", action="store_true")
    parser.add_argument("--skip_test", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--skip_video", action="store_true")
    parser.add_argument("--configs", type=str)
    args = get_combined_args(parser)
    print("Rendering ", args.model_path)
    if args.configs:
        import mmcv
        from utils.params_utils import merge_hparams

        config = mmcv.Config.fromfile(args.configs)
        args = merge_hparams(args, config)
    # Initialize system state (RNG)
    safe_state(args.quiet)
    print("Rendering ", args.model_path)

    handler = render_sets(
        model.extract(args),
        hyperparam.extract(args),
        args.iteration,
        pipeline.extract(args),
        args.skip_train,
        args.skip_test,
        args.skip_video,
    )

    server = websockets.serve(handler, "0.0.0.0", 8765)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
    print("Server started")

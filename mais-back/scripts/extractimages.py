import os
import sys
import shutil

folder_path = sys.argv[1]

colmap_path = "./colmap_tmp"
images_path = os.path.join(colmap_path, "images")
os.makedirs(images_path, exist_ok=True)
i=0

dir1=os.path.join("data",folder_path)
for folder_name in sorted(os.listdir(dir1)):
    dir2=os.path.join(dir1,folder_name)
    if not os.path.isdir(dir2):
        continue

    for file_name in os.listdir(dir2):
        if file_name.endswith(".jpg"):
            i+=1
            src_path = os.path.join(dir2, file_name)
            dst_path = os.path.join(images_path, "{:08d}.jpg".format(i))
            shutil.copyfile(src_path, dst_path)

print("End！")

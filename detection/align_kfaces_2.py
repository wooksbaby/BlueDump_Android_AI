import os
import cv2 as cv
import numpy as np
import errno
import argparse
from alignment import warp_and_crop_face, get_reference_facial_points
from retinaface.detector import RetinafaceDetector


"""
    ###################################################################

    K-Face : Korean Facial Image AI Training Dataset
    url    : http://www.aihub.or.kr/aidata/73

    Directory structure : High-ID-Accessories-Lux-Emotion
    ID example          : '19062421' ... '19101513' len 400
    Accessories example : 'S001', 'S002' .. 'S006'  len 6
    Lux example         : 'L1', 'L2' .. 'L30'       len 30
    Emotion example     : 'E01', 'E02', 'E03'       len 3
    S001 - L1, every emotion folder contains an information txt file
    (ex. bbox, facial landmark) 
    
    ###################################################################
"""


def mkdir_if_missing(directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


def create_range(prefix, start, end, pad=3):
    return [f"{prefix}{str(i).zfill(pad)}" for i in range(start, end + 1)]


def create_aligned_kface_dataset(ori_data_path, 
                                 copy_data_path,
                                 detector,
                                 output_img_size=(112,112)):

    accessories = create_range('S', 1, 6)
    luces = create_range('L', 1, 30)
    expressions = create_range('E', 1, 3, pad=2)
    poses = create_range('C', 1, 20)

    print('Accessories:', accessories)
    print('Lux:', luces)
    print('Expression:', expressions)
    print('Pose:', poses)

    identity_lst = os.listdir(ori_data_path)
    
    for i, idx in enumerate(identity_lst):
        print(f"{i+1} preprocessing...")
        
        for p in poses:
            for a in accessories:
                for l in luces:
                    for e in expressions:
                        ori_image_path = os.path.join(ori_data_path, idx, a, l, e, p) + '.jpg'
                        copy_dir = os.path.join(copy_data_path, idx, a, l, e)
                        mkdir_if_missing(copy_dir)
                        
                        copy_image_path = os.path.join(copy_dir, p) + '.jpg'
                        
                        # 이미지 읽기
                        raw = cv.imread(ori_image_path)
                        if raw is None:
                            print(f"Image not found: {ori_image_path}")
                            continue  # 이미지가 없는 경우 건너뛰기

                        if os.path.exists(copy_image_path):
                            print(f"File already exists: {copy_image_path}, skipping.")
                            continue  # 이미 파일이 있으면 건너뛰기
                        
                        # 얼굴 검출
                        result, facial5points = detector.detect_faces(raw)
                        if result is None or len(facial5points) == 0:
                            print(f"Face not detected in: {ori_image_path}")
                            continue  # 얼굴이 검출되지 않으면 건너뛰기
                        
                        # 검출된 모든 얼굴에 대해 처리
                        for j, face in enumerate(facial5points):
                            facial5points_i = np.reshape(face, (2, 5))  # 각 얼굴에 대해 처리
                            
                            # 정렬 및 크롭
                            default_square = True
                            inner_padding_factor = 0.25
                            outer_padding = (0, 0)

                            # get the reference 5 landmarks position in the crop settings
                            reference_5pts = get_reference_facial_points(
                                output_img_size, inner_padding_factor, outer_padding, default_square)

                            dst_img = warp_and_crop_face(raw, facial5points_i, reference_pts=reference_5pts, crop_size=output_img_size)
                            
                            # 얼굴마다 별도로 저장
                            image_save_path = os.path.join(copy_dir, f"{p}_face_{j}.jpg")
                            cv.imwrite(image_save_path, dst_img)


def parser():   
    parser = argparse.ArgumentParser(description='KFACE detection and alignment')
    parser.add_argument('--ori_data_path', type=str, default='/data/data_server/jju/datasets/FACE/kface-retinaface-112x112', help='raw KFACE path')
    parser.add_argument('--detected_data_path', type=str, default='kface-retinaface-test', help='output path')
    args = parser.parse_args()
    
    return args


if __name__ == "__main__":
    opt = parser()
    detector = RetinafaceDetector()
    create_aligned_kface_dataset(ori_data_path=opt.ori_data_path, 
                                 copy_data_path=opt.detected_data_path,
                                 detector=detector,
                                 output_img_size=(112,112))

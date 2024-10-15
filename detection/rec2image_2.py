import os
import sys
import mxnet as mx
import cv2
import numpy as np
import argparse
from retinaface.detector import RetinafaceDetector  # 얼굴 검출 모델 사용 가정

def extract_face_embedding(image, detector):
    # 얼굴 검출 모델 사용
    result, facial5points = detector.detect_faces(image)
    if result is None or len(facial5points) == 0:
        return None, []  # 얼굴이 없는 경우
    
    # 각 얼굴의 임베딩 생성
    embeddings = []
    for face in facial5points:
        # 얼굴 정렬 및 임베딩 생성 로직 추가 필요
        # 예: 얼굴 부분만 추출, 임베딩 모델 적용
        # 임시로 각 얼굴의 좌표를 임베딩으로 사용 (실제 임베딩 생성 로직으로 대체 필요)
        embeddings.append(face)
    
    return embeddings  # 여러 얼굴의 임베딩 반환

def main(args):
    include_datasets = args.include.split(',')
    rec_list = []
    
    # 얼굴 임베딩과 사진 매핑 구조 초기화
    photo_to_embeddings = {}
    detector = RetinafaceDetector()  # 얼굴 검출 모델 초기화

    for ds in include_datasets:
        path_imgrec = os.path.join(ds, 'train.rec')
        path_imgidx = os.path.join(ds, 'train.idx')
        imgrec = mx.recordio.MXIndexedRecordIO(path_imgidx, path_imgrec, 'r')
        rec_list.append(imgrec)

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    for ds_id in range(len(rec_list)):
        imgrec = rec_list[ds_id]
        s = imgrec.read_idx(0)
        header, _ = mx.recordio.unpack(s)
        assert header.flag > 0
        header0 = (int(header.label[0]), int(header.label[1]))
        seq_identity = range(int(header.label[0]), int(header.label[1]))
        pp = 0

        for identity in seq_identity:
            id_dir = os.path.join(args.output, "%d_%d" % (ds_id, identity))
            os.makedirs(id_dir)
            pp += 1
            if pp % 10 == 0:
                print('processing id', pp)
            s = imgrec.read_idx(identity)
            header, _ = mx.recordio.unpack(s)
            imgid = 0
            for _idx in range(int(header.label[0]), int(header.label[1])):
                s = imgrec.read_idx(_idx)
                _header, _img = mx.recordio.unpack(s)
                _img = mx.image.imdecode(_img).asnumpy()[:, :, ::-1]  # to bgr
                
                # 얼굴 임베딩 생성 (여러 얼굴 처리)
                embeddings = extract_face_embedding(_img, detector)
                if embeddings:
                    # 사진과 임베딩 매핑
                    if f"photo{identity}.jpg" not in photo_to_embeddings:
                        photo_to_embeddings[f"photo{identity}.jpg"] = []
                    photo_to_embeddings[f"photo{identity}.jpg"].extend(embeddings)  # 여러 얼굴 추가
                
                # 이미지 저장
                image_path = os.path.join(id_dir, "%d.jpg" % imgid)
                cv2.imwrite(image_path, _img)
                imgid += 1

    # 클러스터링 결과 (임베딩 -> 클러스터 ID 매핑)
    embedding_to_cluster = {
        # 클러스터링 로직 추가 필요
    }

    # 클러스터 -> 사진 매핑 생성
    cluster_to_photos = {}

    for photo, embeddings in photo_to_embeddings.items():
        for embedding in embeddings:
            cluster_id = embedding_to_cluster.get(embedding)
            if cluster_id is not None:
                if cluster_id not in cluster_to_photos:
                    cluster_to_photos[cluster_id] = []
                if photo not in cluster_to_photos[cluster_id]:
                    cluster_to_photos[cluster_id].append(photo)

    # 결과 출력
    print("Cluster to photos mapping:", cluster_to_photos)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='do dataset merge')
    # general
    parser.add_argument('--include', default='/data/data_server/jju/datasets/FACE/ms1m-retinaface-t1/', type=str, help='')
    parser.add_argument('--output', default='ms1m-retinaface', type=str, help='')
    args = parser.parse_args()
    main(args)

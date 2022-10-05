# -*- coding: utf-8 -*-

from cmath import nan
import copy
from csv import list_dialects
from genericpath import isfile
import open3d as o3d
import numpy as np

import os
import glob
from math import degrees, sqrt
from scipy.spatial.transform import Rotation as R

from logging import DEBUG, INFO, getLogger, StreamHandler, Formatter
logger = getLogger(__name__)
logger.setLevel(INFO)
ch = StreamHandler()
ch.setLevel(INFO)
formatter = Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s", datefmt='%Y/%m/%d %H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)


def preprocess(cloud, voxel_size, max_nn_normal, max_nn_fpfh):
    """粗位置合わせを行うための前処理を実行します.

    Args:
        cloud (open3d.geometry.PointCloud): 計算対象の点群
        voxel_size (float): ボクセルサイズ
        max_nn_normal (int): 法線計算の為の最大近傍点数
        max_nn_fpfh (int): FPFH特徴計算のための最大近傍点数

    Returns:
        open3d.geometry.PointCloud, open3d.pipelines.registration.Feature: ダウンサンプリングされた点群とFPFH特徴
    """
    logger.info("Downsample with a voxel size {}.".format(voxel_size))
    down = cloud.voxel_down_sample(voxel_size)

    n_radius = 2 * voxel_size
    logger.info("Estimate normal with search radius {} and max_nn {}.".format(n_radius, max_nn_normal))
    down.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=n_radius, max_nn = max_nn_normal))

    f_radius = 5 * voxel_size
    logger.info("Compute FPFH feature with search radius {}.".format(f_radius))
    fpfh = o3d.pipelines.registration.compute_fpfh_feature(down,
        o3d.geometry.KDTreeSearchParamHybrid(radius=f_radius, max_nn = max_nn_fpfh))

    return down, fpfh



def corse_registration(source, target, voxel_size, max_nn_normal, max_nn_fpfh, n_ransac):
    """RANSACを用いて粗い位置合わせを実行します。

    Args:
        source (open3d.geometry.PointCloud): 元点群. この点群をtargetに合わせる.
        target (open3d.geometry.PointCloud): 先点群. 位置合わせ先の点群.
        voxel_size (float): ボクセルサイズ.
        max_nn_normal (int): 法線ベクトルを求める際の近傍点の数
        max_nn_fpfh (int): FPFH特徴を求める際の近傍点の数
        n_ransac (int): RANSACの回数

    Returns:
        np.array((4, 4), float): 位置合わせのための剛体変換行列
    """

    # ダウンサンプリング& FPFH特徴を取得
    srcdown, srcfpfh = preprocess(source, voxel_size, max_nn_normal, max_nn_fpfh)
    trgdown, trgfpfh = preprocess(target, voxel_size, max_nn_normal, max_nn_fpfh)
    
    #trgdown.paint_uniform_color([0, 0.651, 0.929])
    #o3d.visualization.draw_geometries([trgdown])

    distance_threshold = 1.5 * voxel_size
    logger.info("RANSAC registration on downsampled point clouds.")
    logger.info("  voxel_size = {}".format(voxel_size))
    logger.info("  distance_threshold = {}".format(distance_threshold))
    logger.info("  n_ransac = {}".format(n_ransac))

    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        srcdown, trgdown, srcfpfh, trgfpfh, False, distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        4, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(
                0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(
                distance_threshold)
        ], o3d.pipelines.registration.RANSACConvergenceCriteria(n_ransac, 500)) 

    logger.info(f"  {result}")
    return result.transformation



def fine_registration(source, target, init_rt = None, distance_threshold = 1.0):
    """ICPを用いて詳細位置合わせを実行します.

    Args:
        source (open3d.geometry.PointCloud): 元点群. この点群をtargetに合わせる.
        target (open3d.geometry.PointCloud): 先点群. 位置合わせ先の点群.
        init_rt (np.array(_type_, optional): RTの初期値. 与えられなければ単位行列が設定される. Defaults to None.
        distance_threshold (float, optional): ICPの距離の閾値. Defaults to 1.0.

    Returns:
        np.array((4, 4), float): _description_
    """
    assert (source.has_normals() and target.has_normals()), "PointCloud is not calcurated."
    
    if init_rt is None:
        init_rt = np.eye(4)

    
    logger.info("ICP registration is applied on original point cloud. distance_threshold = {}".format(distance_threshold))
    result = o3d.pipelines.registration.registration_icp(
        source, target, distance_threshold, init_rt,
        o3d.pipelines.registration.TransformationEstimationPointToPlane())
    
    logger.info(f"  {result}")
        
    return result



def corse_to_fine_registration(source, target, voxel_size, 
    n_normal = 30, n_fpfh = 100, ransac_iter = 4000000, distance_threshold = 0.5):

    # 粗位置合わせ
    RT = corse_registration(source, target, voxel_size, n_normal, n_fpfh, ransac_iter)

    # 法線ベクトルの推定
    # 詳細点群の法線ベクトル推定半径はボクセルサイズの半分とした
    if not source.has_normals():
        logger.info("source has no normals. run estimate normals.")
        source.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size, max_nn = n_normal))
    if not target.has_normals():
        logger.info("target has no normals. run estimate normals.")
        target.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size, max_nn = n_normal))


    # 詳細位置合わせ
    return  fine_registration(source, target, RT, distance_threshold)



def load_and_rm_noise(filename, nb_neighbors = 30, std_ratio = 3.0):
    """指定されたファイルから点群を読み込みノイズ除去をして返します。    

    Args:
        filename (str): 点群ファイル名
        nb_neighbors (int, optional): ノイズ除去時の近傍点数.指定された数のデータから統計値を取得する. Defaults to 30.
        std_ratio (float, optional): 標準偏差×この値よりも偏差が大きいデータを取り除く. Defaults to 2.0.

    Returns:
        open3d.geometry.PointCloud: 読み込み＆ノイズ除去された点群
    """
    # 読み込み
    #cloud_remove_nan = o3d.io.read_point_cloud(filename, remove_nan_points=True)
    cloud = o3d.io.read_point_cloud(filename, remove_nan_points=False)
    
    if not cloud.has_points():
        logger.error("{} : file read error.".format(filename))
        return o3d.geometry.PointCloud()

    logger.info("read point cloud from {}.".format(filename))

    # ノイズ除去(指定された個数の点群を取り出して統計処理を行い、与えられた係数×σから外れたデータを除去する)
    retcld, _ = cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    if not retcld.has_points():
        str_message = f"近隣点：{nb_neighbors}, 標準偏差：{std_ratio}"
        o3d.visualization.draw_geometries([cloud], window_name=str_message)
        return(cloud)
    else:
        return retcld



def load_only(filename):
    """指定されたファイルから点群を読み込みます。    

    Args:
        filename (str): 点群ファイル名
    Returns:
        open3d.geometry.PointCloud: 読み込みた点群
    """
    cloud = o3d.io.read_point_cloud(filename, remove_nan_points=False)
    
    if not cloud.has_points():
        logger.error("{} : file read error.".format(filename))
        return o3d.geometry.PointCloud()

    logger.info("read point cloud from {}.".format(filename))
    
    return(cloud)
    
    

def draw_registration_result(source, target, result, fn):
    """位置合わせ結果を描画します.(Debug用)

    Args:
        source (open3d.geometry.PointCloud): 位置合わせ元点群
        target (open3d.geometry.PointCloud): 位置合わせ先点群
        transformation (np.array((4, 4), float)): 位置合わせ用剛体変換行列
    """
    # 色を塗ったり、移動したりするので元の点群を破壊しないようにコピーする
    src = copy.deepcopy(source)
    trg = copy.deepcopy(target)
    trg.paint_uniform_color([1, 0.705, 0])      # targetは黄色
    src.paint_uniform_color([0, 0.651, 0.929])  # sourceは青色
    src.transform(result.transformation)
    
    str_message = f"ファイル名:{os.path.basename(fn)} {result}"
    o3d.visualization.draw_geometries([src, trg], window_name=str_message, width=1920, height=1080)
    

def estimate_score(RT):
    """estimate score of mask
        transform the cloud_master and erase cloud_mask then check if z is smaller than cloud_master at same x and y

    Args:
        RT (np.array((4, 4), float)): transformation matrix
    Returns:
        0.5*(|theta_x| + |theta_y|) +  0.5*height
    """
    
    # calculate euler angle from RT
    # get Rotation Matrix and transforme np.ndarray to list since Scipy needs list(important!!!)
    RM = RT[:3, :3].tolist()
    
    # lower case means static system = world coordinate
    euler_type = "xyz"
    
    # initial scipy.spatial.transform.Rotation 
    r = R.from_matrix(RM)

    # get euler angles
    theta_x, theta_y, _ =  r.as_euler(euler_type, degrees=True)

    logger.info(f"theta_x:{theta_x}\t theta_y:{theta_y}")

    score_pitch_yaw = abs(theta_x) + abs(theta_y)
    
    # height: use RT' z
    z = RT[2, 3]
    score_height = abs(z)

    score = 0.5 * score_pitch_yaw + 0.5 * score_height
    
    print(f"score_pitch_yaw:{score_pitch_yaw}\tscore_height:{score_height}")
    
    return(score)


# halfway since it is impossible to discriminate that nan is other backface mask or black part of itself
def estimate_score_with_check(cloud_master, cloud_mask, cloud_scene, RT):
    """estimate score of mask
        transform the cloud_master and erase cloud_mask then check if z is smaller than cloud_master at same x and y

    Args:
        cloud_master (open3d.geometry.PointCloud): master cloud
        cloud_mask (open3d.geometry.PointCloud): mask cloud
        cloud_scene (open3d.geometry.PointCloud): scene cloud
        RT (np.array((4, 4), float)): transformation matrix
    Returns:
        0:part work
        rotation*0.1 +  height*0.5 + position*0.4
    """
    
    # transform cloud_master
    cloud_transformed_master = cloud_master.transform(RT)
    print(np.asarray(cloud_transformed_master.points))
    
    # erase cloud_mask from cloud_master
    dists_mstr_msk = cloud_transformed_master.compute_point_cloud_distance(cloud_scene)
    dists_mstr_msk = np.asarray(dists_mstr_msk)
    idx_mstr = np.where(dists_mstr_msk > 2)[0]
    
    cloud_diff = cloud_transformed_master.select_by_index(idx_mstr)

    str_msg =  str(f"master:{cloud_transformed_master}  diff:{cloud_diff} ")
    
    cloud_diff.paint_uniform_color([0, 1, 0])
    o3d.visualization.draw_geometries([cloud_diff, cloud_scene], window_name=str_msg)
    
    # check if z of scane is smaller than cloud_diff at same x and y
    
    score=0
    return(score)


if __name__ == '__main__':
    import argparse
    import sys
    import quaternion

    parser = argparse.ArgumentParser(
        description='点群masterを基準として点群maskの位置合わせをして、and evalute the mask using the RT(transformation matrix)',
        epilog='位置合わせ結果を描画し、標準出力にscoreを表示します.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True
        )

    parser.add_argument('master_filename', metavar='master_filename', help='マスタデータファイル名')
    parser.add_argument('scene_filename', metavar='scene_filename', help='scene filename')
    parser.add_argument("mask_filename", metavar='mask_filename', help='mask filename')
    parser.add_argument('-v', '--voxel_size', help='ボクセルサイズ', action='store', type=float, default=3)
    parser.add_argument('-i', '--ransac_iter', help="RANSACの繰り返し回数", action='store', type=int, default=4000000)
    args = parser.parse_args(["../exp_data/ply/master/surface/out017_03_0.97912174_sum19556_notNan19185.ply", 
                              "../exp_data/ply/23_scene/out023.ply",
                              "../exp_data/ply/23_mask"])
    

    # master点群読み込み&ノイズ除去
    cloud_master = load_and_rm_noise(args.master_filename)
    
    # read scene pc
    cloud_scene = load_and_rm_noise(args.scene_filename)
    
    if not cloud_master.has_points():
        logger.error("{} : master file read error.".format(args.master_filename))
        sys.exit(1)
    if not cloud_scene.has_points():
        logger.error("{} : scene file read error.".format(args.scene_filename))
        sys.exit(1)
    
    if os.path.isfile(args.mask_filename):
        target_flist = [args.mask_filename]
    elif os.path.isdir(args.mask_filename):
        target_flist = glob.glob(f"{args.mask_filename}/*.ply")
    else:
        logger.error(f"{args.mask_filename} : mask file is not a file or dir.")
        sys.exit(1)
    
    num_mask = len(target_flist)
    list_score = np.zeros(num_mask, float)
    
    count_mask = 0
    for target_fn in target_flist:
                
        # read pc and remove noise
        cloud_mask = load_and_rm_noise(target_fn)
        
        if not cloud_mask.has_points():
            logger.error(f"{target_fn} : target file read error.")
            sys.exit(1)

        result = corse_to_fine_registration(cloud_master, cloud_mask, args.voxel_size,
            distance_threshold=args.voxel_size * 0.2, ransac_iter=args.ransac_iter)
        
        RT = result.transformation
        
        '''print(RT)
        print(quaternion.from_rotation_matrix(RT[:3, :3]))
        print(RT[:3, 3])'''
        
        list_score[count_mask] = estimate_score(RT)
        
        draw_registration_result(cloud_master, cloud_mask, result, target_fn)

        count_mask +=1        
        
"""赛题分数计算
参考： https://github.com/Tp0t-Team/Tp0tOJ/blob/master/server/utils/calculator/baseCalculator.go
"""
import math

HALF_LIFE = 20
BLOOD_REWARD = {
    0: 0.1,
    1: 0.08,
    2: 0.05
}


def curve(base_point: int, count: int, half_fife=HALF_LIFE) -> int:
    """
    题目分数算法，根据当前答题人数计算题目分数。

    @param base_point: 当前分数
    @param count: 答题人数
    @return: 题目分数
    """
    if count == 0:
        return base_point

    count -= 1
    coefficient = 1.8414 / half_fife * count
    result = math.floor(
        base_point / (coefficient + math.exp(-coefficient)))
    return result


def get_increment_point(point: int, index: int, blood_reward=BLOOD_REWARD) -> int:
    """
    额外奖励分数

    @param point: 题目分数
    @param index: 第 index 位完成题目。
    @return:
    """

    if index == 0:
        return math.floor(point * (1 + blood_reward[index]))
    elif index == 1:
        return math.floor(point * (1 + blood_reward[index]))
    elif index == 2:
        return math.floor(point * (1 + blood_reward[index]))
    else:
        return point


def get_delta_point_for_user(old_point: int, new_point: int, index: int) -> int:
    """
    计算需要减去的分数

    @param old_point: 原本的积分
    @param new_point: 新的积分
    @param index: 当前多少位完成
    @return:
    """

    return get_increment_point(old_point, index) - get_increment_point(new_point, index)

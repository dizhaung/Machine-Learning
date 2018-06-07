#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/1
# @Author  : Wenhao Shan
# @Dsc     : BP Neural Network training

import numpy as np
from math import sqrt
from PythonMachineLearning.functionUtils import PaintingWithMat, sig, partial_sig


def load_data(file_name: str):
    """
    导入数据
    :param file_name:
    :return: feature_data(mat): 特征
              label_data(mat): 标签
              n_class(int): 类别的个数
    """
    # 获取特征
    f = open(file_name)
    feature_data = list()
    label_tmp = list()
    for line in f.readlines():
        lines = line.strip().split("\t")
        feature_tmp = [float(lines[i]) for i in range(len(lines) - 1)]
        label_tmp.append(int(lines[-1]))
        feature_data.append(feature_tmp)
    f.close()

    # 获取标签
    m = len(label_tmp)
    class_number = len(set(label_tmp))  # 类别的个数

    label_data = np.mat(np.zeros((m, class_number)))
    for i in range(m):
        label_data[i, label_tmp[i]] = 1

    with PaintingWithMat(name="BP Train") as paint:
        paint.painting_with_no_offset(np.mat(feature_data), label_data)
    return np.mat(feature_data), label_data, class_number


def hidden_in(feature: np.mat, w0: np.mat, b0: np.mat):
    """
    计算隐含层的输入, 类似于wx + b这种形式, 不过是多层多网络形式的
    :param feature: 特征
    :param w0: 输入层到隐含层之间的权重
    :param b0: 输入层到隐含层之间的偏置
    :return: hidden_in(mat): 隐含层的输入
    """
    m = np.shape(feature)[0]
    hidden = feature * w0   # 各特征乘上其对应的权重
    for i in range(m):
        hidden[i, ] += b0   # 加上偏置项
    return hidden


def hidden_out(hidden_in: np.mat):
    """
    隐含层的输出
    :param hidden_in: 隐含层的输入
    :return: hidden_output(mat): 隐含层的输出
    """
    hidden_output = sig(hidden_in)     # 激活函数
    return hidden_output


def predict_in(hidden_out: np.mat, w1: np.mat, b1: np.mat):
    """
    计算输出层的输入
    :param hidden_out: 隐含层的输出
    :param w1: 隐含层到输出层之间的权重
    :param b1: 隐含层到输出层之间的偏置
    :return: predict_id(mat): 输出层的输入
    """
    m = np.shape(hidden_out)[0]
    predict = hidden_out * w1
    for i in range(m):
        predict[i, ] += b1
    return predict


def predict_out(predict_in: np.mat):
    """
    输出层的输出
    :param predict_in: 输出层的输入
    :return: result(mat): 输出层的输出
    """
    result = sig(predict_in)
    return result


def bp_train(feature: np.mat, label: np.mat, n_hidden: int, maxCycle: int, alpha: float, n_output: int):
    """
    计算隐含层的输入
    :param feature: 特征
    :param label: 标签
    :param n_hidden: 隐含层的节点个数
    :param maxCycle: 最大的迭代次数
    :param alpha: 学习率
    :param n_output: 输出层的节点个数
    :return: w0(mat): 输入层到隐含层之间的权重
              b0(mat): 输入层到隐含层之间的偏置
              w1(mat): 隐含层到输出层之间的权重
              b1(mat): 隐含层到输出层之间的偏置
    """
    m, n = np.shape(feature)
    # 1、 初始化, 从指定的区间中生成随机数
    w0 = np.mat(np.random.rand(n, n_hidden))    # np.random.rand(m, n)随机生成m * n维数组, 值在[0, 1]之间
    w0 = w0 * (8.0 * sqrt(6) / sqrt(n + n_hidden)) - np.mat(np.ones((n, n_hidden))) * \
        (4.0 * sqrt(6) / sqrt(n + n_hidden))
    b0 = np.mat(np.random.rand(1, n_hidden))
    b0 = b0 * (8.0 * sqrt(6) / sqrt(n + n_hidden)) - np.mat(np.ones((1, n_hidden))) * \
        (4.0 * sqrt(6)) / sqrt(n + n_hidden)
    w1 = np.mat(np.random.rand(n_hidden, n_output))
    w1 = w1 * (8.0 * sqrt(6) / sqrt(n_hidden + n_output)) - np.mat(np.ones((n_hidden, n_output))) * \
        (4.0 * sqrt(6) / sqrt(n_hidden + n_output))
    b1 = np.mat(np.random.rand(1, n_output))
    b1 = b1 * (8.0 * sqrt(6) / sqrt(n_hidden + n_output)) - np.mat(np.ones((1, n_output))) * \
        (4.0 * sqrt(6)) / sqrt(n_hidden + n_output)

    # 2、训练
    i = 0
    while i <= maxCycle:
        # 2.1、信号正向传播
        # 2.1.1、计算隐含层的输入
        hidden_input = hidden_in(feature, w0, b0)   # mXn_hidden
        # 2.1.2、计算隐含层的输出
        hidden_output = hidden_out(hidden_input)
        # 2.1.3、计算输出层的输入
        output_in = predict_in(hidden_output, w1, b1)   # mXn_output
        # 2.1.4、计算输出层的输出
        output_out = predict_out(output_in)

        # 2.2、误差的反向传播
        # 2.2.1、隐含层到输出层之间的残差
        delta_output = -np.multiply((label - output_out), partial_sig(output_in))
        # 2.2.2、输入层到隐含层之间的残差
        delta_hidden = np.multiply((delta_output * w1.T), partial_sig(hidden_input))

        # 2.3、修正权重和偏置
        w1 -= alpha * (hidden_output.T * delta_output)
        b1 -= alpha * np.sum(delta_output, axis=0) * (1.0 / m)
        w0 -= alpha * (feature.T * delta_hidden)
        b0 -= alpha * np.sum(delta_hidden, axis=0) * (1.0 / m)
        if i % 100 == 0:
            print("\t-----------------iter: ", "cost: ", (1.0 / 2) * get_cost(get_predict
                                                                              (feature, w0, w1, b0, b1) - label))
        i += 1
    return w0, w1, b0, b1


def get_cost(cost: np.mat):
    """
    计算当前损失函数的值
    :param cost: 预测值与标签之间的差
    :return: (double): 损失函数的值
    """
    m, n = np.shape(cost)

    cost_sum = 0.0
    for i in range(m):
        for j in range(n):
            cost_sum += cost[i, j] * cost[i, j]
    return cost_sum / m


def get_predict(feature: np.mat, w0: np.mat, w1: np.mat, b0: np.mat, b1: np.mat):
    """
    计算最终的预测
    :param feature:
    :param w0:
    :param w1:
    :param b0:
    :param b1:
    :return: 预测值
    """
    return predict_out(predict_in(hidden_out(hidden_in(feature, w0, b0)), w1, b1))


def save_model(w0: np.mat, w1: np.mat, b0: np.mat, b1: np.mat):
    """
    保存最终的模型
    :param w0:
    :param w1:
    :param b0:
    :param b1:
    :return:
    """
    def write_file(file_name: str, source: np.mat):
        f = open(file_name, "w")
        m, n = np.shape(source)
        for i in range(m):
            tmp = [str(source[i, j]) for j in range(n)]
            f.write("\t".join(tmp) + "\n")
        f.close()

    write_file("weight_w0", w0)
    write_file("weight_w1", w1)
    write_file("weight_b0", b0)
    write_file("weight_b1", b1)


def err_rate(label: np.mat, pre: np.mat):
    """
    计算训练样本上的错误率
    :param label:
    :param pre:
    :return:
    """
    m = np.shape(label)[0]
    err = 0.0
    for i in range(m):
        if label[i, 0] != pre[i, 0]:
            err += 1
    rate = err / m
    return rate


def BPTrain():
    """
    BP Training
    :return:
    """
    # 1、导入数据
    print("--------- 1.load data ------------")
    feature, label, n_class = load_data("data.txt")
    # 2、训练网络模型
    print("--------- 2.training ------------")
    import time
    t0 = time.time()
    w0, w1, b0, b1 = bp_train(feature, label, 20, 1000, 0.1, n_class)
    print("cost time", time.time() - t0)
    # 3、保存最终的模型
    print("--------- 3.save model ------------")
    save_model(w0, w1, b0, b1)
    # 4、得到最终的预测结果
    print("--------- 4.get prediction ------------")
    result = get_predict(feature, w0, w1, b0, b1)
    print("训练准确性为：", (1 - err_rate(np.argmax(label, axis=1), np.argmax(result, axis=1))))


if __name__ == '__main__':
    BPTrain()

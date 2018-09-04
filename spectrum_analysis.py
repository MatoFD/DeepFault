from keras import backend as K
from collections import defaultdict
import numpy as np
from utils import get_layer_outs

#Provide a seed for reproducability
np.random.seed(7)

def coarse_intersection_analysis(correct_classification_idx, misclassification_idx, layer_outs):

    for l_out in layer_outs[1:]:
        dominant = range(len(l_out[0][0]))
        test_idx = 0
        for l in l_out[0]:
            if test_idx not in misclassification_idx: continue
            dominant = np.intersect1d(dominant, np.where(l > 0))
            test_idx += 1
        dominant_neuron_idx.append(dominant)

    return dominant_neuron_idx


def tarantula_analysis(correct_classification_idx, misclassification_idx, layer_outs):

    scores = []
    num_cf = []
    num_uf = []
    num_cs = []
    num_us = []
    for l_out in layer_outs[1:]:
        num_cf.append(np.zeros(len(l_out[0][0])))
        num_uf.append(np.zeros(len(l_out[0][0])))
        num_cs.append(np.zeros(len(l_out[0][0])))
        num_us.append(np.zeros(len(l_out[0][0])))
        scores.append(np.zeros(len(l_out[0][0])))

    layer_idx = 0
    for l_out in layer_outs[1:]:
        all_neuron_idx = range(len(l_out[0][0]))
        test_idx = 0
        for l in l_out[0]:
            covered_idx   = list(np.where(l > 0)[0])
            uncovered_idx = list(set(all_neuron_idx)-set(covered_idx))

            if test_idx  in correct_classification_idx:
                for cov_idx in covered_idx:
                    num_cs[layer_idx][cov_idx] += 1
                for uncov_idx in uncovered_idx:
                    num_us[layer_idx][uncov_idx] += 1
            elif test_idx in misclassification_idx:
                for cov_idx in covered_idx:
                    num_cf[layer_idx][cov_idx] += 1
                for uncov_idx in uncovered_idx:
                    num_uf[layer_idx][uncov_idx] += 1
            test_idx += 1
        layer_idx += 1

    dominant_neuron_idx= [[] for i in range(len(layer_outs))]

    for i in range(len(scores)):
        for j in range(len(scores[i])):
            score =  float(float(num_cf[i][j]) / (num_cf[i][j] + num_uf[i][j])) / (float(num_cf[i][j]) / (num_cf[i][j] + num_uf[i][j]) + float(num_cs[i][j]) / (num_cs[i][j] + num_us[i][j]))
            scores[i][j] = score
            if score > 0.6:
                dominant_neuron_idx[i].append(j)

    return dominant_neuron_idx


def ochiai_analysis(correct_classification_idx, misclassification_idx, layer_outs):

    scores = []
    num_cf = []
    num_uf = []
    num_cs = []
    num_us = []
    for l_out in layer_outs[1:]:
        num_cf.append(np.zeros(len(l_out[0][0])))
        num_uf.append(np.zeros(len(l_out[0][0])))
        num_cs.append(np.zeros(len(l_out[0][0])))
        num_us.append(np.zeros(len(l_out[0][0])))
        scores.append(np.zeros(len(l_out[0][0])))

    layer_idx = 0
    for l_out in layer_outs[1:]:
        all_neuron_idx = range(len(l_out[0][0]))
        test_idx = 0
        for l in l_out[0]:
            covered_idx   = list(np.where(l > 0)[0])
            uncovered_idx = list(set(all_neuron_idx)-set(covered_idx))

            if test_idx  in correct_classification_idx:
                for cov_idx in covered_idx:
                    num_cs[layer_idx][cov_idx] += 1
                for uncov_idx in uncovered_idx:
                    num_us[layer_idx][uncov_idx] += 1
            elif test_idx in misclassification_idx:
                for cov_idx in covered_idx:
                    num_cf[layer_idx][cov_idx] += 1
                for uncov_idx in uncovered_idx:
                    num_uf[layer_idx][uncov_idx] += 1
            test_idx += 1
        layer_idx += 1


    dominant_neuron_idx= [[] for i in range(len(layer_outs))]

    for i in range(len(scores)):
        for j in range(len(scores[i])):
            score = float(num_cf[i][j]) / ((num_cf[i][j] + num_uf[i][j]) * (num_cf[i][j] + num_cs[i][j])) **(.5)
            scores[i][j] = score
            if score > 0.6:
                dominant_neuron_idx[i].append(j)

    return dominant_neuron_idx


def fine_intersection_analysis(model, predictions, true_classes,
                               prediction_tobe_analyzed,
                               true_tobe_analyzed=None):

    error_class_to_input= []
    idx = 1
    for pred, crrct in zip(predictions, true_classes):
        predicted_class = np.unravel_index(pred.argmax(), pred.shape)[0]
        true_class = np.unravel_index(crrct.argmax(), crrct.shape)[0]

        #if user does not specify the true class,  we consider all predictions that are equal to "given predicted class" and not correct
        if true_tobe_analyzed == None and predicted_class == prediction_tobe_analyzed and predicted_class != true_class:
            error_class_to_input.append(idx)
        #if user specifies a true class we consider predictions that are equal to "given predicted class" and expected to be "given true class"
        elif predicted_class == prediction_tobe_analyzed and true_class == true_tobe_analyzed and predicted_class != true_class:
            error_class_to_input.append(idx)

        idx += 1

    class_specific_test_set = np.ndarray(shape=(len(error_class_to_input),1,28,28))

    cnt = 0
    for test_input in error_class_to_input:
        class_specific_test_set[cnt] = test_input
        cnt += 1

    layer_outs = get_layer_outs(model, class_specific_test_set)

    dominant_neuron_idx= [[] for i in range(len(layer_outs))]

    for l_out in layer_outs[1:]:
        dominant = range(len(l_out[0][0]))
        for l in l_out[0]:
            dominant = np.intersect1d(dominant, np.where(l > 0))
        dominant_neuron_idx.append(dominant)

    return dominant_neuron_idx



import operator as op
import io
import os
import sys

import common
import experiment_input
from experiment_input import (load_qid_lines_csv_file_name,
                              load_ground_truth_num_items,
                              get_experiment_file_info,
                              Language_python)

pred_f = 'svmrank-pred.dat'


def nCr(n, r):
    r = min(r, n - r)
    if r == 0:
        return 1
    numer = reduce(op.mul, xrange(n, n - r, -1))
    demon = reduce(op.mul, xrange(1, r + 1))
    return numer // demon


def E_inspect(st, en, nf):
    expected = float(st)
    n = en - st + 1
    for k in xrange(1, n - nf + 1):
        term = float(nCr(n - k - 1, nf - 1) * k) / nCr(n, nf)
        expected += term
    return expected


# List = [
#   {
#       is_fault: 1 / 2,
#       score: 0.123
#   },
# ]
def get_E_inspect(lst):
    sorted_lst = sorted(lst, key=lambda f: f['score'], reverse=True)
    pos = -1
    for i, f in enumerate(sorted_lst):
        if f['is_fault'] == 1:
            pos = i
            pos_score = f['score']
            break
    if pos == -1:
        return -1
    start = 0
    end = len(sorted_lst) - 1
    for i in range(pos - 1, -1, -1):
        f = sorted_lst[i]
        if f['score'] != pos_score:
            start = i + 1
            break
    for i in range(pos + 1, len(sorted_lst)):
        f = sorted_lst[i]
        if f['score'] != pos_score:
            end = i - 1
            break
    count = 0
    for i in range(start, end + 1):
        if sorted_lst[i]['is_fault'] == 1:
            count += 1
    return E_inspect(start + 1, end + 1, count)


def get_python_e_inspect(lst, lines, ground_truth_num_items):
    e_inspect = get_E_inspect(lst)
    if e_inspect != -1:
        return e_inspect

    first_tie_item_rank = len(lst) + 1
    tie_size = lines - len(lst)
    end = first_tie_item_rank + tie_size - 1
    assert tie_size >= 2
    e_inspect = lines
    if ground_truth_num_items != 0:
        e_inspect = E_inspect(first_tie_item_rank, end, ground_truth_num_items)

    return e_inspect


def read_info_ranksvm(num):
    # data -> bug(qid) -> pos(line) -> score / is_fault
    data = {}
    curdir = 'data/cross_data'
    curdir = os.path.join(curdir, str(num))
    pred_file = os.path.join(curdir, pred_f)
    test_file = os.path.join(curdir, 'test.dat')
    with io.open(test_file) as f:
        test_data = f.readlines()
    with io.open(pred_file) as f:
        pred_data = f.readlines()
    for i in range(len(pred_data)):
        test_line = test_data[i]
        pred_line = pred_data[i]
        is_fault = int(test_line.split(' ', 1)[0])
        qid = test_line.split(' ', 2)[1]
        score = float(pred_line)
        if qid not in data:
            data[qid] = []
        item = {'score': score, 'is_fault': is_fault}
        data[qid].append(item)
    return data


def qid_to_lines():
    data = {}
    qid_lines_csv_file_name = load_qid_lines_csv_file_name()
    qid_lines_csv_path = os.path.join("data", qid_lines_csv_file_name)
    with io.open(qid_lines_csv_path) as f:
        raw = f.readlines()
        for line in raw:
            qid = int(line.split(',')[0])
            lines = int(line.split(',')[1])
            data[qid] = lines
    return data


def main():
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 10
    E_pos_list = []
    python_e_pos_list = []
    EXAM_list = []
    python_exam_list = []
    qid2line = qid_to_lines()
    (language_name,
     granularity_name,
     combination_name) = get_experiment_file_info()
    ground_truth_num_items = None
    if language_name == Language_python:
        ground_truth_num_items = load_ground_truth_num_items()
    for i in range(n):
        print '\r', 'Handle', i + 1, '/', n,
        sys.stdout.flush()
        data = read_info_ranksvm(i)
        for key in data.keys():
            # key: u'qid:117'
            qid = int(key.split(':')[1])
            lines = qid2line[qid]
            E_inspect = get_E_inspect(data[key])
            E_pos_list.append(E_inspect)
            python_e_inspect = -1
            if language_name == Language_python:
                python_e_inspect = get_python_e_inspect(data[key], lines, ground_truth_num_items[str(qid)])
            python_e_pos_list.append(python_e_inspect)
            # calc EXAM

            EXAM = E_inspect / float(lines)
            python_exam = python_e_inspect / float(lines)
            EXAM_list.append(EXAM)
            python_exam_list.append(python_exam)
    top = []
    top.append(len(filter(lambda item: item < 1.01 and item > 0, E_pos_list)))
    top.append(len(filter(lambda item: item < 3.01 and item > 0, E_pos_list)))
    top.append(len(filter(lambda item: item < 5.01 and item > 0, E_pos_list)))
    top.append(len(filter(lambda item: item < 10.01 and item > 0, E_pos_list)))

    number_of_bugs = len(qid2line)
    top_percent = [int(round(float(x * 100) / number_of_bugs)) for x in top]

    print '\nTop 1/3/5/10:', top
    print 'Top %1/%3/%5/%10:', top_percent
    EXAM_list = [e for e in EXAM_list if e > 0]
    avg_exam = sum(EXAM_list) / len(EXAM_list)
    avg_python_exam = sum(python_exam_list) / len(python_exam_list)
    avg_python_e_inspect = sum(python_e_pos_list) / len(python_e_pos_list)
    print 'EXAM: ', avg_exam
    print "PYTHON_EXAM: ", avg_python_exam

    file_name = experiment_input.get_results_file_name()
    results_dictionary = common.results_to_dictionary_object(top,
                                                             top_percent,
                                                             avg_exam,
                                                             avg_python_exam,
                                                             avg_python_e_inspect)
    common.save_object_to_json(results_dictionary, file_name)


if __name__ == '__main__':
    main()

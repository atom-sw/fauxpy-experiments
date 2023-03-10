import sys

from result_manager import get_result_manager


def main():
    result_manager = get_result_manager()
    result_manager.compute_all_metrics_for_all()
    result_manager.save_all_metrics_for_all()
    # csv_score_items = result_manager.get_all_csv_score_items()
    #
    # for item in csv_score_items:
    #     print(item, item.get_experiment_time_seconds())


if __name__ == '__main__':
    main()

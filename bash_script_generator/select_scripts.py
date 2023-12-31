import subject_script_generator as main_gen


def number_id(filename: str):
    num_id = filename.split("_")[0]
    return num_id


def get_pred_for_select(item):
    return (
            "st" in item and
            "sbfl" not in item and
            "mbfl" not in item and
            "ps" not in item and
            "function" in item
    )


def vertical_print(selected):
    for bash_script_item in selected:
        filename = bash_script_item.name
        print(number_id(filename))


def horizontal_print(selected):
    final_st = ""
    for bash_script_item in selected:
        filename = bash_script_item.name
        final_st += number_id(filename) + " "

    print(final_st)


def main():
    script_dir = main_gen.OUTPUT_DIRECTORY
    bash_scripts = script_dir.iterdir()

    selected = list(filter(lambda x: get_pred_for_select(x.name),
                           bash_scripts))
    selected.sort()

    print(len(selected))

    # vertical_print(selected)
    horizontal_print(selected)


if __name__ == '__main__':
    main()

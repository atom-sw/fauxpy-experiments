# $PLACE_HOLDER_GRANULARITY granularity

echo "------- Running SBFL with $PLACE_HOLDER_GRANULARITY granularity"
python -m pytest "${TEST_SUITE[@]}"\
                 --src "$TARGET_DIR"\
                 --exclude "$EXCLUDE_LIST"\
                 --granularity "$PLACE_HOLDER_GRANULARITY"\
                 --family "sbfl"\
                 --failing-list "$TARGET_FAILING_TESTS_LIST" || true

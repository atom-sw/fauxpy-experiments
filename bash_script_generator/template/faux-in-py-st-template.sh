# $PLACE_HOLDER_GRANULARITY granularity

echo "------- Running ST with $PLACE_HOLDER_GRANULARITY granularity"
python -m pytest "${TARGET_FAILING_TESTS[@]}"\
                 --src "$TARGET_DIR"\
                 --exclude "$EXCLUDE_LIST"\
                 --granularity "$PLACE_HOLDER_GRANULARITY"\
                 --family "st"\
                 --failing-list "$TARGET_FAILING_TESTS_LIST" || true

#! /usr/bin/bash

RESULTS="$HOME/results"
FAUXPY="$HOME/fauxpy-experiments/fauxpy_experiments"

for log in *.out; do
	 if [[ "$log" =~ ^([0-9]+)_([0-9]+)h_([0-9]+)g_([-a-zA-Z0-9]+)_([0-9]+)_([a-z]+)_([a-z]+)[.]sh[-]([0-9]+)[.]out$ ]]; then
		  N="${BASH_REMATCH[1]}"
		  TIME="${BASH_REMATCH[2]}"
		  MEM="${BASH_REMATCH[3]}"
		  PROJECT="${BASH_REMATCH[4]}"
		  BUG="${BASH_REMATCH[5]}"
		  FL="${BASH_REMATCH[6]}"
		  GRAN="${BASH_REMATCH[7]}"
		  PID="${BASH_REMATCH[8]}"
		  squeue --me | grep -qe "^[ ]*$PID"
		  RUNNING="$?"
		  if [ $RUNNING -eq 0 ]; then
				>&2 echo "Still running: $log"
				continue
		  fi
		  if tail -n 1 "$log" | grep -q "CANCELLED AT .\+ DUE TO TIME LIMIT"; then
				>&2 echo "Timed out: $log"
				TIMEOUT=1
		  else
				TIMEOUT=0
		  fi
		  DIRPATH="$FAUXPY/$PROJECT/B$BUG/FauxPyReport_""$PROJECT"_"$FL"_"$GRAN"_
		  OUTDIR="$RESULTS"/"$N"_"$TIME"h_"$MEM"g_"$PROJECT"_"$BUG"_"$FL"_"$GRAN"_"$PID"
		  if [ $TIMEOUT -eq 0 ]; then
				mkdir -p "$OUTDIR"
				# Move results
				mv "$DIRPATH"* "$OUTDIR/"
				# Move log
				mv "$log" "$OUTDIR/"
				# Move script
				mv "$FAUXPY/$N"_*.sh "$OUTDIR/"
		  else
				# Move log to Timeout directory
				mv "$log" "$RESULTS/Timeouts/"
		  fi
		  # Delete Slurm wrappers
		  rm "$FAUXPY/$N"_*.{cmd,err,out,time} "$FAUXPY/run_$N"*.sh
		  echo "Copied: $N"
	 else
		  >&2 echo "Skipping: $log"
	 fi
done

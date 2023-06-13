#! /usr/bin/env bash

THIS=$(basename $0)
COLLECT=0

SCRIPT_LOCATION="./bash_script_generator/scripts/"
SLURM_WORKDIR="/home/furia/fauxpy-experiments"

ARGS_NUMBER=0
ARGS_RANGE=1
ARGS_PATTERN=2
ARGS_OR=1

ARGS_AS=$ARGS_NUMBER


usage ()
{
	 echo -e "Usage: $THIS [-hcpra] P1 [P2 [P3 ...]]

By default, the positional arguments are interpreted as experiment
numbers. With option -r, the first two positional arguments are
interpreted as number ranges (from-to). With option -p the positional
arguments positional arguments are interpreted as patterns for find
(option -name); in this case, quote the arguments as needed.

By default, the positional arguments are interpreted in
disjunction. With option -a, they are interpreted in
conjunction.

Note that the script may misbehave if the matched script names include
whitespaces.

Optional arguments:
   -h             print this help notice
   -c             collect results of experiments that finished
   -p             interpret the positional arguments as patterns for find
   -r             interpret the positional arguments as a numeric range
   -a             interpret the positional arguments as conjunction ('and')
"
}


while getopts ":hcpra" opt; do
	 case $opt in
		  h)
				usage
				exit 0
				;;
		  c)
				COLLECT=1
				;;
		  p)
				ARGS_AS=$ARGS_PATTERN
				;;
		  r)
				ARGS_AS=$ARGS_RANGE
				;;
		  a)
				ARGS_OR=0
				;;
		  :)
				echo "Option: -$OPTARG requires an argument" >&2
				exit 1
				;;
		  \?)
				echo "Invalid option: -$OPTARG" >&2
				exit 1
				;;
	 esac
done
shift $(($OPTIND - 1))

# expand arguments to array
ARGS=("$@")

if [ $ARGS_OR -eq 1 ]; then 
	 FIND_OPT=" -o -name "
else
	 FIND_OPT=" -name "
fi

if [ $ARGS_AS -eq $ARGS_RANGE ]; then
	 if [ "$#" -ne 2 ]; then
		  echo "Option -r needs exactly two positional arguments" >&2
		  exit 1
	 fi
	 # Enumerate all numbers from first to second positional argument
	 ARGS=($(seq "$1" "$2"))
	 ARGS_AS="$ARGS_NUMBER"
fi

if [ $ARGS_AS -eq $ARGS_NUMBER ]; then
	 PATTERNS=$(printf "${FIND_OPT}'%s_*.sh'" "${ARGS[@]}")
elif [ $ARGS_AS -eq $ARGS_PATTERN ]; then
	 PATTERNS=$(printf "${FIND_OPT}'%s'" "${ARGS[@]}")
fi
# remove leading separator and add back the first -name
PATTERNS="\( -name ${PATTERNS:${#FIND_OPT}} \)"

FILES=$(bash -c "find $SCRIPT_LOCATION -type f $PATTERNS")

echo "$FILES"
read -p "Press enter to continue (or C-c to stop)"

echo "$FILES" | while read -d $'\n' f; do
	 fn="${f/#$SCRIPT_LOCATION/}";
	 [[ "$fn" =~ ^([0-9]+)_([0-9]+)h_([0-9]+)g_(.*)$ ]] && N="${BASH_REMATCH[1]}"; T="${BASH_REMATCH[2]}"; M="${BASH_REMATCH[3]}";
	 echo "Script: $fn";
	 if [ "$COLLECT" -eq 0 ]; then
		  cp "$f" .;
		  chmod u+x "$fn";
		  slurp --scratch --submit SBATCH --workdir "$SLURM_WORKDIR" "$fn" --time="$T:00:00" --mem="$M000" --output="$fn-%%j.out" --error="$fn-%%j.out";
	 else
		  # Collect results
		  slurp --collect --workdir "$SLURM_WORKDIR" "$fn"
		  mkdir -p ../logs
		  # Collect logs
		  # rsync -aquz -e 'ssh -p 22' furia@hpc.ics.usi.ch:/home/furia/*.out ../logs/
		  # No need to do it for all files
		  break
	 fi
done

for f in scripts/*.sh; do fn="${f/#scripts\//}"; echo "$fn"; cp "$f" .; slurp --scratch --submit SBATCH --workdir "/home/furia/fauxpy-experiments" "$fn"; done

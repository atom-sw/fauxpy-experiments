for f in scripts/*.sh; do fn="${f/#scripts\//}"; echo "$fn"; cp "$f" .; chmod u+x "$fn"; slurp --scratch --submit SBATCH --workdir "/home/furia/fauxpy-experiments" "$fn"; done

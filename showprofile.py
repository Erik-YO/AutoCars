import pstats

p = pstats.Stats('testprofile.txt')

p.strip_dirs().sort_stats(2).print_stats(60)

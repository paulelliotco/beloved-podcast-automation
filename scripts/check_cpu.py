import os
print(f"Total CPU cores: {os.cpu_count()}")
print(f"Workers that will be used (75%): {max(1, int(os.cpu_count() * 0.75))}")

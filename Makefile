present: CharlaComputacionLinguistica.ipynb
	jupyter nbconvert "$^" --to slides --post serve

.PHONY: present

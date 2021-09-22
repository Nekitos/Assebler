#!/usr/bin/env python
from controller.manipulator import Manipulator

try:
    root = Manipulator()
    root.custom_mainloop()
except Exception as e:
    print(str(e))
    exit(0)

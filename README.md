all api's should be placed here. pushing this file to preserve this dir. current dependencies
are marked under .gitignore


# Build

To build, make a directory under the main source dir and invoke CMake
```bash
$ mkdir build
$ cmake ..
$ make
$ ./src/money_bot
```

To run the tests after building, run ctest
```bash
$ ctest
```
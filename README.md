# Running the container

## Requirements

- Docker Desktop (Windows/Mac), or Docker Engine with the Compose plugin (Linux)
- Windows/Mac only: in Docker Desktop, enable host networking

## First run

Launch the container. Should lead to a command line with user "root" and working directory "/workspace".

`docker compose run --rm fair-alloc`

Then, we need to build the MMS module. Run the following commands:

`cmake -S MMS -B MMS/build -DCMAKE_BUILD_TYPE=Release`
`cmake --build MMS/build`

Now there should be a file named `_core.cpython-315-x86_64-linux-gnu.so` in the MMS directory.

To use the app run `python main.py`.

To exit the container from the terminal use `exit`.

## Later runs

Only need to start the container. You can skip building C++ code unless a change was made.

`docker compose run --rm fair-alloc`

## On code change

- Python: Synced automatically, no need to change anything
- C++ (MMS): Need to re-build the `_core.cpython-315-x86_64-linux-gnu.so` file. Run those two commands again from inside the container.
- dockerfile or requirements.txt: Close the container and run it again with `docker compose run --build --rm fair-alloc`.


# Running the container

Requirements:

- docker engine or other way to manage containers

Firstly, build the container image. 'fair-alloc' will be the name of the image and must match the end of the second command.

`docker build -t fair-alloc .`

Secondly, launch the container. Should lead to a command line with user "root" and working directory "/workspace".

`docker run --rm -it --mount "type=bind,source=$($PWD.Path),target=/workspace" -w /workspace fair-alloc`

Thirdly, we need to build the MMS module. Run the following commands:

`cmake -S MMS -B MMS/build -DCMAKE_BUILD_TYPE=Release`
`cmake --build MMS/build`

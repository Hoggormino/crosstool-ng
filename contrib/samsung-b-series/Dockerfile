FROM ubuntu:22.04@sha256:076e7bf82319619f28dd0aa9c02ab34b055ad37100395b4f49a2ffba04fb5e11
ARG BUILDER_UID=1000
ARG BUILDER_GID=1000
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential autoconf automake libtool libtool-bin bison flex gawk \
    patch unzip wget curl ca-certificates git python3 texinfo help2man \
    libncurses-dev pkg-config rsync xz-utils bzip2 file unifdef gettext \
    cmake ninja-build qemu-user rpcsvc-proto && rm -rf /var/lib/apt/lists/*
RUN groupadd --gid ${BUILDER_GID} builder && \
    useradd --uid ${BUILDER_UID} --gid ${BUILDER_GID} --create-home --shell /bin/bash builder
USER builder
ENV LANG=C LC_ALL=C

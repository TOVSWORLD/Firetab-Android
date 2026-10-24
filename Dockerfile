# Recipe only: not built in this session. Build on Linux x86_64 with a
# case-sensitive volume and sufficient resources. Apt packages are not locked.
FROM --platform=linux/amd64 ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    bc bison build-essential ca-certificates ccache curl flex g++-multilib \
    gcc-multilib git git-lfs gnupg gperf imagemagick lib32readline-dev \
    lib32z1-dev libelf-dev liblz4-tool libncurses-dev libsdl1.2-dev \
    libssl-dev libxml2 libxml2-utils lzop openjdk-11-jdk patchelf \
    python3 python-is-python3 rsync schedtool squashfs-tools unzip xsltproc \
    zip zlib1g-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /android
CMD ["bash"]

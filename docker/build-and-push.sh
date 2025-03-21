# Build and push a multi-platform (amd64, arm64) Docker image using Buildx. 

# Update 'yutianqin/dspaces-api:v3' as needed.
# '--no-cache' is used to ensure that no cached layers are utilized, forcing a fresh build.
# '-f ./Dockerfile' explicitly specifies the Dockerfile to be used.
# The final context for the build is the current directory ('.') (Ensure the build context is set to the root of 'dspaces-api' for proper usage.)

docker buildx build --platform linux/amd64,linux/arm64 -t yutianqin/dspaces-api:v4 --push --no-cache -f ./Dockerfile ..
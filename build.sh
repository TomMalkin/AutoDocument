#!/usr/bin/env bash
set -euo pipefail

# Ask for version
read -rp "Enter version (e.g. 0.4.0): " VERSION

USERNAME="tommalkin"

# Images
WEB_IMAGE="$USERNAME/autodocument"
WORKER_IMAGE="$USERNAME/autodocument-worker"

# Tag images
docker tag "$WEB_IMAGE:latest" "$WEB_IMAGE:$VERSION"
docker tag "$WORKER_IMAGE:latest" "$WORKER_IMAGE:$VERSION"

# Push both tags for each image
for IMAGE in "$WEB_IMAGE" "$WORKER_IMAGE"; do
  echo "Pushing $IMAGE:latest..."
  docker push "$IMAGE:latest"

  echo "Pushing $IMAGE:$VERSION..."
  docker push "$IMAGE:$VERSION"
done

echo "✅ Done! Pushed $WEB_IMAGE and $WORKER_IMAGE with tags: latest and $VERSION"


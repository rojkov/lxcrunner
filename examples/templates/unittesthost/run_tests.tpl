#!/bin/sh

BRANCH={{branch}}
echo "Let's test the branch '$BRANCH'"

DEREK_DIR=/home/derek/derek
cd $DEREK_DIR

echo "Fetching code..."
git fetch
echo "done."

echo "Reset to the branch '$BRANCH'..."
git checkout origin/$BRANCH || exit 1
echo "done."

echo "Recompile Derek..."
make compile || exit
echo "done."

echo "Run tests"
make alltests

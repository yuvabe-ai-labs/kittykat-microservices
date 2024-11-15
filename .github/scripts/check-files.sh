# Handling Merge base commits
if [[ $(git show --summary | grep 'Merge:') != "" ]]; then
    last_changes=$(git show --summary | grep Merge: | xargs | awk '{print($3".."$2)}')
    echo "Setting output for last merged commits ${last_changes}"
    echo "::set-output name=files::$(git diff --no-commit-id --name-only -r ${last_changes} | xargs)"
else
    # Handling direct or stashed commits
    commit_id=$(git rev-parse HEAD)
    echo "Setting output for last non merged commit ${commit_id}"
    echo "::set-output name=files::$(git diff-tree --no-commit-id --name-only -r ${commit_id} | xargs)"
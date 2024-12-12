if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <id>"
    exit 1
fi

id=$1

python run.py \
  --model berkeley/llama \
  --data_path /root/web_bench/realworld_masked/attempt${id}/README.md \
  --repo_path /root/web_bench/realworld_masked/attempt${id} \
  --config_file config/default_from_url_web_dev.yaml \
  --environment_setup config/environment_setup/realworld_flask.sh \
  --apply_patch_locally

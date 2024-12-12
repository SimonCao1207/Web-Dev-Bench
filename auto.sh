
#!/bin/bash

# Iterate over API IDs from 0 to 18
for id in {0..18}
do
    echo "Running flask_mask.py for API ID: $id"
    python realworld/flask_mask.py --api_ids $id
    if [ $? -ne 0 ]; then
        echo "Error occurred while running flask_mask.py for API ID: $id. Exiting."
        exit 1
    fi

    echo "Running run_web_dev.sh for API ID: $id"
    ./run_web_dev.sh $id
    if [ $? -ne 0 ]; then
        echo "Error occurred while running run_web_dev.sh for API ID: $id. Exiting."
        cd ..
        exit 1
    fi

done

echo "All commands executed successfully."

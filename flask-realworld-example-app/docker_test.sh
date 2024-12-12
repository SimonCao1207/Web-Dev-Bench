#!/bin/bash
flask run --with-threads &
sleep 10
cd custom_evaluation
python level2_test.py
while true; do
    sleep 60
done
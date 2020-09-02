echo "Initializing Script"
echo "Running Test 1"
python3 sim.py --config testdata/test1.config --log true --logdir test1
echo "Test 1 Finished"
echo "Running Test 2"
python3 sim.py --config testdata/test2.config --log true --logdir test2
echo "Test 2 Finished"
zip -r logs.zip test1 test2
echo "All tests finished"
echo "preapring working directory"
rm -rvf test1/*
rmdir test1
rm -rvf test2/*
rmdir test2
echo "Running Test 1"
python3 sim.py test normal 1
mkdir test1
cp sim-logs/* test1/
rm -rvf sim-logs/
rmdir sim-logs
echo "Test 1 Finished"
echo "Running Test 2"
python3 sim.py test uniform 1
mkdir test2
cp sim-logs/* test2/
rm -rvf sim-logs/
rmdir sim-logs
echo "Test 2 Finished"
zip -r logs.zip test1 test2
echo "All tests finished"
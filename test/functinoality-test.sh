echo "Starting Testing"
echo "Account Creation Test"
python3 test-script.py accountcreation-input.txt accountcreation-output.txt
echo "Account Creation Error Test"
python3 test-script.py accountcreationerror-input.txt accountcreationerror-output.txt
echo "Buy Order Test"
python3 test-script.py buyscript-input.txt buyscript-output.txt
#echo "Buy Order Fail Test"
#python3 test-script.py buyscripterror-input.txt buyscripterror-output.txt
##echo "Buy Order Query Test"
##python3 test-script.py queryscript-input.txt queryscript-output.txt
#echo "Buy Order Query Error Test"
#python3 test-script.py queryscripterror-input.txt queryscripterror-output.txt
#echo "Cancelling Buy Order Test"
#python3 test-script.py cancelscript-input.txt cancelscript-output.txt
#echo "Sell Order Test"
#python3 test-script.py sellscript-input.txt sellscript-output.txt
#echo "Sell Order Error Test"
#python3 test-script.py sellscripterror-input.txt sellscripterror-output.txt
#echo "Buy Order to Match Sell order Test"
#python3 test-script.py buyscript2-input.txt buyscript2-output.txt
##echo "Query Half matched order Test"
##python3 test-script.py queryscript2-input.txt queryscript2-output.txt
#echo "Cancel half matched order Test"
#python3 test-script.py cancelscript2-input.txt cancelscript2-output.txt